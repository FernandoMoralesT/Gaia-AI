import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import json
import threading
import urllib.error
import urllib.request
from urllib.parse import quote, unquote

import numpy as np
import pytest
from servidor import crear_servidor, HOST


@pytest.fixture(scope="module")
def url_base():
    # puerto 0: el sistema elige uno libre y no choca con un servidor abierto
    servidor = crear_servidor(puerto=0)
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    yield f"http://{HOST}:{servidor.server_port}"
    servidor.shutdown()
    servidor.server_close()


def pedir(url):
    """Devuelve (código, encabezados, cuerpo) también para respuestas 4xx."""
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read()


def leer_raw(datos):
    ancho, alto = np.frombuffer(datos[:8], dtype="<u4")
    mapa = np.frombuffer(datos[8:], dtype="<f4").reshape(alto, ancho)
    return ancho, alto, mapa


# --- /salud ------------------------------------------------------------------

def test_salud(url_base):
    codigo, _, cuerpo = pedir(f"{url_base}/salud")
    assert codigo == 200
    assert json.loads(cuerpo) == {"estado": "ok"}


# --- /terreno ----------------------------------------------------------------

def test_terreno_formato_raw(url_base):
    codigo, enc, cuerpo = pedir(f"{url_base}/terreno?clase=valle&semilla=7")
    assert codigo == 200
    assert len(cuerpo) == 8 + 120 * 120 * 4
    ancho, alto, mapa = leer_raw(cuerpo)
    assert (ancho, alto) == (120, 120)
    assert mapa.min() >= 0.0 and mapa.max() <= 1.0
    assert enc["X-Semilla"] == "7"
    assert enc["X-Sigma"] == "2.0"


def test_misma_semilla_mismos_bytes(url_base):
    _, _, a = pedir(f"{url_base}/terreno?clase=lomas&semilla=42")
    _, _, b = pedir(f"{url_base}/terreno?clase=lomas&semilla=42")
    _, _, c = pedir(f"{url_base}/terreno?clase=lomas&semilla=43")
    assert a == b
    assert a != c


def test_clase_con_acento(url_base):
    codigo, enc, _ = pedir(f"{url_base}/terreno?clase={quote('volcán')}&semilla=1")
    assert codigo == 200
    assert unquote(enc["X-Clase"]) == "volcán"


def test_semilla_aleatoria_se_reporta(url_base):
    codigo, enc, cuerpo = pedir(f"{url_base}/terreno?clase=llanura")
    assert codigo == 200
    semilla = enc["X-Semilla"]
    # pedir de nuevo con la semilla reportada reproduce el mismo terreno
    _, _, repetido = pedir(f"{url_base}/terreno?clase=llanura&semilla={semilla}")
    assert cuerpo == repetido


def test_sigma_cero_permitido(url_base):
    codigo, enc, _ = pedir(f"{url_base}/terreno?clase=meseta&semilla=3&sigma=0")
    assert codigo == 200
    assert enc["X-Sigma"] == "0.0"


# --- errores -----------------------------------------------------------------

@pytest.mark.parametrize("consulta", [
    "",                                   # sin clase
    "clase=desierto",                     # clase inválida
    "clase=valle&semilla=abc",            # semilla no numérica
    "clase=valle&semilla=-1",             # semilla negativa
    "clase=valle&sigma=abc",              # sigma no numérico
    "clase=valle&sigma=11",               # sigma fuera de rango
])
def test_parametros_invalidos_400(url_base, consulta):
    codigo, _, cuerpo = pedir(f"{url_base}/terreno?{consulta}")
    assert codigo == 400
    assert "error" in json.loads(cuerpo)


def test_ruta_desconocida_404(url_base):
    codigo, _, _ = pedir(f"{url_base}/otra")
    assert codigo == 404
