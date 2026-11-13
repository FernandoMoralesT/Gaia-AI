import rasterio
import os
import json

def cargar_etiquetas(ruta="data/etiquetas.json"):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)



def cargar_batch_dem(carpeta):
    heightmaps = {}
    for archivo in sorted(os.listdir(carpeta)):
        if archivo.endswith(".tif"):
            with rasterio.open(os.path.join(carpeta, archivo)) as src:
                data = src.read(1)
                heightmaps[archivo] = data
    return heightmaps
