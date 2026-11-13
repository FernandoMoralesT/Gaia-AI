import sys
import traceback
from pathlib import Path

import pytest
import requests

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scrips"))
from dataset import descargar_dem  # noqa: E402

CLAVE = "CLAVE-SECRETA-123"


class Respuesta:
    def __init__(self, status, content=b"", text=""):
        self.status_code, self.content, self.text = status, content, text


def test_pedir_dem_no_filtra_la_clave_en_errores_de_red(monkeypatch):
    monkeypatch.setenv("OPENTOPO_API_KEY", CLAVE)

    def falla(url, params, timeout):
        raise requests.ConnectionError(f"Max retries exceeded with url: {url}?API_Key={params['API_Key']}")

    monkeypatch.setattr(descargar_dem.requests, "get", falla)
    monkeypatch.setattr(descargar_dem.time, "sleep", lambda s: None)
    with pytest.raises(requests.ConnectionError) as e:
        descargar_dem.pedir_dem(1, 2, 3, 4)
    assert CLAVE not in "".join(traceback.format_exception(e.value))


def test_pedir_dem_lanza_error_api_con_status_sin_la_clave(monkeypatch):
    monkeypatch.setenv("OPENTOPO_API_KEY", CLAVE)
    monkeypatch.setattr(descargar_dem.requests, "get",
                        lambda url, params, timeout: Respuesta(401, text=f"Unauthorized key {CLAVE}"))
    with pytest.raises(descargar_dem.ErrorAPI) as e:
        descargar_dem.pedir_dem(1, 2, 3, 4)
    assert e.value.status == 401
    assert CLAVE not in str(e.value)


# ---------------------------------------------------------------- manifiesto

def bloque(id_, s, n, w, e, proposito="entrenamiento", estado="pendiente"):
    return {"id": id_, "sitio": id_, "sur": s, "norte": n, "oeste": w, "este": e, "lado_grados": n - s,
            "clases_esperadas": ["llanura"], "proposito": proposito, "justificacion": "prueba",
            "verificar_coordenadas": True, "estado": estado, "fecha_descarga": None, "verificacion": None}


def test_nombre_bloque_sigue_la_convencion_de_dem():
    from descargar_bloques import nombre_bloque
    assert nombre_bloque(31.6, 32.1, -114.1, -113.6) == "bloque_31.6_32.1_-114.1_-113.6.tif"


def test_revisar_detecta_id_repetido_area_excesiva_y_referencia_encimada():
    from descargar_bloques import revisar_manifiesto
    m = {"bloques": [bloque("A", 0, 0.5, 0, 0.5), bloque("A", 10, 10.5, 10, 10.5),
                     bloque("G", 20, 30, 20, 30),
                     bloque("R", 0.2, 1.4, 0.2, 1.4, proposito="referencia")]}
    problemas = " ".join(revisar_manifiesto(m))
    assert "repetido" in problemas and "A" in problemas
    assert "450" in problemas and "G" in problemas
    assert "encima" in problemas and "R" in problemas


def test_manifiesto_real_no_tiene_problemas():
    from descargar_bloques import RUTA_MANIFIESTO, cargar_manifiesto, revisar_manifiesto
    m = cargar_manifiesto(RUTA_MANIFIESTO)
    assert len(m["bloques"]) == 48
    assert revisar_manifiesto(m) == []


def test_guardar_y_cargar_manifiesto(tmp_path):
    from descargar_bloques import cargar_manifiesto, guardar_manifiesto
    ruta = tmp_path / "m.json"
    m = {"bloques": [bloque("A", 0, 0.5, 0, 0.5)]}
    guardar_manifiesto(m, ruta)
    assert cargar_manifiesto(ruta) == m
    assert [p.name for p in tmp_path.iterdir()] == ["m.json"]  # no deja el temporal


# ---------------------------------------------------------------- cola de descarga

LADO = 0.01  # 36 px a 1 segundo de arco: tifs chicos para las pruebas


def tif_falso(s, n, w, e, nodata_pct=0.0):
    """Bytes de un GeoTIFF int16 como los de SRTM GL1, con la forma que tendría ese recuadro."""
    import numpy as np
    from affine import Affine
    from rasterio.io import MemoryFile
    filas, cols = round((n - s) * 3600), round((e - w) * 3600)
    datos = np.full((filas, cols), 100, dtype=np.int16)
    datos.flat[:int(datos.size * nodata_pct / 100)] = -32768
    # Affine directo: from_bounds dispara un aviso de rasterio por usar * en lugar de @.
    transformacion = Affine((e - w) / cols, 0, w, 0, -(n - s) / filas, n)
    with MemoryFile() as mem:
        with mem.open(driver="GTiff", height=filas, width=cols, count=1, dtype="int16", nodata=-32768,
                      crs="EPSG:4326", transform=transformacion) as dst:
            dst.write(datos, 1)
        return mem.read()


def manifiesto(n):
    return {"bloques": [bloque(f"B{i:02d}", i, i + LADO, 0, LADO) for i in range(n)]}


class PedirFalso:
    def __init__(self, falla_en=None, status=None, cuerpo=None, intentos=1):
        self.llamadas, self.falla_en, self.status, self.cuerpo = 0, falla_en, status, cuerpo
        self.intentos = intentos  # peticiones HTTP por bloque (reintentos incluidos)

    def __call__(self, s, n, w, e, al_intentar=None):
        for _ in range(self.intentos):
            if al_intentar:
                al_intentar()
        self.llamadas += 1
        if self.llamadas == self.falla_en:
            raise descargar_dem.ErrorAPI(self.status, "rechazado")
        return self.cuerpo if self.cuerpo is not None else tif_falso(s, n, w, e)


def descargar(m, carpeta, pedir, **kw):
    from descargar_bloques import descargar_pendientes
    return descargar_pendientes(m, carpeta, pedir=pedir, esperar=lambda s: None, **kw)


def test_reanuda_sin_gastar_llamadas(tmp_path):
    from descargar_bloques import nombre_bloque
    m = manifiesto(1)
    b = m["bloques"][0]
    (tmp_path / nombre_bloque(b["sur"], b["norte"], b["oeste"], b["este"])).write_bytes(
        tif_falso(b["sur"], b["norte"], b["oeste"], b["este"]))
    pedir = PedirFalso()
    r = descargar(m, tmp_path, pedir)
    assert pedir.llamadas == 0 and r["llamadas"] == 0
    assert b["estado"] == "descargado" and b["verificacion"]["ok"]


def test_tope_de_45(tmp_path):
    m = manifiesto(50)
    pedir = PedirFalso()
    r = descargar(m, tmp_path, pedir)
    assert pedir.llamadas == 45 and r["detenido_por"] == "tope"
    assert sum(b["estado"] == "pendiente" for b in m["bloques"]) == 5


def test_401_detiene_y_guarda(tmp_path):
    from descargar_bloques import cargar_manifiesto, guardar_manifiesto
    ruta = tmp_path / "m.json"
    m = manifiesto(5)
    r = descargar(m, tmp_path, PedirFalso(falla_en=3, status=401), guardar=lambda x: guardar_manifiesto(x, ruta))
    assert r["detenido_por"] == 401
    estados = [b["estado"] for b in cargar_manifiesto(ruta)["bloques"]]
    assert estados == ["descargado", "descargado", "pendiente", "pendiente", "pendiente"]
    assert cargar_manifiesto(ruta)["bloques"][0]["fecha_descarga"] is not None


def test_400_marca_fallido_y_sigue(tmp_path):
    m = manifiesto(3)
    r = descargar(m, tmp_path, PedirFalso(falla_en=2, status=400))
    assert [b["estado"] for b in m["bloques"]] == ["descargado", "fallido", "descargado"]
    assert "400" in m["bloques"][1]["verificacion"]["motivo"]
    assert r["detenido_por"] is None


def test_respuesta_no_geotiff_detiene_y_queda_pendiente(tmp_path):
    m = manifiesto(2)
    pedir = PedirFalso(cuerpo=b"<html>error</html>")
    r = descargar(m, tmp_path, pedir)
    assert pedir.llamadas == 1 and r["detenido_por"] == "respuesta no GeoTIFF"
    assert [b["estado"] for b in m["bloques"]] == ["pendiente", "pendiente"]
    assert list(tmp_path.glob("*.tif")) == [] and list(tmp_path.glob("*.tmp")) == []


def test_ids_limita_a_los_pedidos(tmp_path):
    m = manifiesto(4)
    pedir = PedirFalso()
    descargar(m, tmp_path, pedir, ids={"B01", "B03"})
    assert pedir.llamadas == 2
    assert [b["estado"] for b in m["bloques"]] == ["pendiente", "descargado", "pendiente", "descargado"]


def test_verificar_reporta_nodata_y_forma(tmp_path):
    from descargar_bloques import verificar_bloque
    b = bloque("A", 10, 10 + LADO, 0, LADO)
    ruta = tmp_path / "a.tif"
    ruta.write_bytes(tif_falso(b["sur"], b["norte"], b["oeste"], b["este"], nodata_pct=10))
    v = verificar_bloque(ruta, b)
    assert v["forma"] == v["forma_esperada"] == [36, 36]
    assert v["nodata_pct"] == pytest.approx(10, abs=1)
    assert v["min_m"] == 100 and v["plausible"]


# ---------------------------------------------------------------- ver_bloque

def test_figura_bloque_tiene_imagen_y_titulo(tmp_path):
    import matplotlib
    matplotlib.use("Agg")
    from ver_bloque import figura_bloque
    ruta = tmp_path / "a.tif"
    ruta.write_bytes(tif_falso(10, 10 + LADO, 0, LADO))
    fig = figura_bloque(ruta, "Prueba")
    ax = fig.axes[0]
    assert ax.get_images() and ax.get_title() == "Prueba"
    assert ax.get_images()[0].get_extent() == pytest.approx([0, LADO, 10, 10 + LADO])



# ---------------------------------------------------------------- arreglos de la revisión final

def test_clave_cortada_por_el_recorte_no_se_filtra(monkeypatch):
    monkeypatch.setenv("OPENTOPO_API_KEY", CLAVE)
    cuerpo = "x" * 190 + CLAVE + " fin"  # la clave cruza el límite de 200 caracteres
    monkeypatch.setattr(descargar_dem.requests, "get", lambda url, params, timeout: Respuesta(401, text=cuerpo))
    with pytest.raises(descargar_dem.ErrorAPI) as e:
        descargar_dem.pedir_dem(1, 2, 3, 4)
    assert CLAVE[:10] not in str(e.value)


def test_cada_reintento_cuenta_para_el_tope(tmp_path):
    m = manifiesto(30)
    r = descargar(m, tmp_path, PedirFalso(intentos=2))  # cada bloque gasta 2 peticiones
    assert r["llamadas"] <= 45 and r["detenido_por"] == "tope"
    assert sum(b["estado"] == "descargado" for b in m["bloques"]) == 22


def test_pedir_dem_avisa_cada_intento(monkeypatch):
    monkeypatch.setenv("OPENTOPO_API_KEY", CLAVE)
    respuestas = iter([requests.Timeout("lento"), Respuesta(200, content=b"ok")])

    def get(url, params, timeout):
        r = next(respuestas)
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setattr(descargar_dem.requests, "get", get)
    monkeypatch.setattr(descargar_dem.time, "sleep", lambda s: None)
    intentos = []
    assert descargar_dem.pedir_dem(1, 2, 3, 4, al_intentar=lambda: intentos.append(1)) == b"ok"
    assert len(intentos) == 2


def test_error_5xx_detiene_y_queda_pendiente(tmp_path):
    m = manifiesto(3)
    r = descargar(m, tmp_path, PedirFalso(falla_en=2, status=503))
    assert r["detenido_por"] == 503
    assert [b["estado"] for b in m["bloques"]] == ["descargado", "pendiente", "pendiente"]


def test_verificacion_fallida_se_reporta(tmp_path):
    m = manifiesto(1)
    b = m["bloques"][0]
    r = descargar(m, tmp_path, PedirFalso(cuerpo=tif_falso(b["sur"], b["norte"], 0, LADO * 2)))  # forma mal
    assert b["verificacion"]["ok"] is False
    assert r["revisar"] == [b["id"]]


def test_figura_bloque_con_zona_recorta_y_ajusta_el_color(tmp_path):
    import matplotlib
    matplotlib.use("Agg")
    from ver_bloque import figura_bloque
    ruta = tmp_path / "a.tif"
    ruta.write_bytes(tif_falso(10, 10 + LADO, 0, LADO))
    zona = (0.002, 10.002, 0.006, 10.006)  # oeste, sur, este, norte
    fig = figura_bloque(ruta, "Zona", zona=zona)
    imagen = fig.axes[0].get_images()[0]
    assert imagen.get_extent() == pytest.approx([0.002, 0.006, 10.002, 10.006], abs=1 / 3600)  # se ajusta a la rejilla
    assert all(abs(n - 0.004 * 3600) <= 1 for n in imagen.get_array().shape[:2])  # 14.4 px, a un píxel
