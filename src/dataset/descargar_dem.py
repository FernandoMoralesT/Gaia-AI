import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Cargar variables de entorno desde el archivo .env

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
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error al descargar el DEM: {response.status_code} - {response.text}")
    nombre_salida = f"dem_{round(south, 2)}_{round(north, 2)}_{round(west, 2)}_{round(east, 2)}.tif"
    ruta_completa = os.path.join("data/raw", nombre_salida)
    with open(ruta_completa, "wb") as f:
        f.write(response.content)