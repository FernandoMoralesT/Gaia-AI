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
    assert len(m["bloques"]) == 25
    assert revisar_manifiesto(m) == []


def test_guardar_y_cargar_manifiesto(tmp_path):
    from descargar_bloques import cargar_manifiesto, guardar_manifiesto
    ruta = tmp_path / "m.json"
    m = {"bloques": [bloque("A", 0, 0.5, 0, 0.5)]}
    guardar_manifiesto(m, ruta)
    assert cargar_manifiesto(ruta) == m
    assert [p.name for p in tmp_path.iterdir()] == ["m.json"]  # no deja el temporal
