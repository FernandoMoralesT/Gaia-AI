import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()  # Cargar variables de entorno desde el archivo .env

def nombre_tile(south, north, west, east):
    return f"dem_{round(south, 2)}_{round(north, 2)}_{round(west, 2)}_{round(east, 2)}.tif"

class ErrorAPI(Exception):
    """Respuesta distinta de 200 del servidor. `status` permite distinguir un 401 (cuota) de un 400."""

    def __init__(self, status, mensaje):
        super().__init__(f"Error al descargar el DEM: {status} - {mensaje}")
        self.status = status


def pedir_dem(south, north, west, east, demtype="SRTMGL1"):
    """Pide un recorte a la API y devuelve los bytes del GeoTIFF, sin escribir en disco.

    Ningún error que salga de aquí lleva la clave: los de red se relanzan sin la URL.
    """
    api_key = os.environ.get("OPENTOPO_API_KEY")
    url = "https://portal.opentopography.org/API/globaldem"
    params = {
        "demtype": demtype,
        "south": south,
        "north": north,
        "west": west,
        "east": east,
        "outputFormat": "GTiff",
        "API_Key": api_key,
    }
    response = None
    for intento in range(1, 4):
        try:
            response = requests.get(url, params=params, timeout=(10, 120))
            break
        except (requests.ConnectionError, requests.Timeout) as err:
            tipo = type(err)
            if intento == 3:
                # El mensaje original de requests incluye la URL con la clave: no se encadena.
                raise tipo(f"{tipo.__name__} al pedir el DEM tras 3 intentos") from None
            print(f"Intento {intento} falló ({tipo.__name__}); reintentando")
            time.sleep(5 * intento)
    if response.status_code != 200:
        texto = response.text[:200]
        if api_key:
            texto = texto.replace(api_key, "***")
        raise ErrorAPI(response.status_code, texto)
    return response.content


def descargar_tile(south, north, west, east, demtype="SRTMGL1"):
    contenido = pedir_dem(south, north, west, east, demtype)
    nombre_salida = nombre_tile(south, north, west, east)
    ruta_completa = os.path.join("data/raw", nombre_salida)
    with open(ruta_completa, "wb") as f:
        f.write(contenido)
    return ruta_completa