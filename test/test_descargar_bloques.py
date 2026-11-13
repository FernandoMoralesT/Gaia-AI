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
