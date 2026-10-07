import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()  # Cargar variables de entorno desde el archivo .env

def nombre_tile(south, north, west, east):
    return f"dem_{round(south, 2)}_{round(north, 2)}_{round(west, 2)}_{round(east, 2)}.tif"

def descargar_tile(south, north, west, east, demtype="SRTMGL1"):
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
            if intento == 3:
                raise
            print(f"Intento {intento} falló ({type(err).__name__}); reintentando")
            time.sleep(5 * intento)
    if response.status_code != 200:
        raise Exception(f"Error al descargar el DEM: {response.status_code} - {response.text}")
    nombre_salida = nombre_tile(south, north, west, east)
    ruta_completa = os.path.join("data/raw", nombre_salida)
    with open(ruta_completa, "wb") as f:
        f.write(response.content)
    return ruta_completa