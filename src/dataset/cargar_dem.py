import rasterio
import os
import json
import random

def cargar_etiquetas(ruta="data/etiquetas.json"):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)



def cargar_bach_dem(carpeta):
    heigthmaps = {}
    for archivo in sorted(os.listdir(carpeta)):
        if archivo.endswith(".tif"):
            with rasterio.open(os.path.join(carpeta, archivo)) as src:
                data = src.read(1)
                heigthmaps[archivo] = data
    return heigthmaps
