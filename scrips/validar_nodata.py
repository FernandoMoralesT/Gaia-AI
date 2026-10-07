import collections
import json
import os

import numpy as np
import rasterio

carpeta = "data/raw"

with open("data/etiquetas.json", encoding="utf-8") as f:
    etiquetas = json.load(f)

archivos = {a for a in os.listdir(carpeta) if a.endswith(".tif")}

print("Etiquetas por clase:", collections.Counter(etiquetas.values()))
print("Archivos en data/raw:", len(archivos), "| Etiquetas:", len(etiquetas))
print("Sin etiqueta:", sorted(archivos - set(etiquetas)))
print("Etiqueta sin archivo:", sorted(set(etiquetas) - archivos))
print()

for archivo in sorted(archivos):
    with rasterio.open(os.path.join(carpeta, archivo)) as src:
        data = src.read(1)
        nodata = src.nodata

        if nodata is None:
            print(archivo, "no declara nodata")
            continue

        mascara = data == nodata
        n_nodata = np.count_nonzero(mascara)
        validos = data[~mascara]
        if validos.size == 0:
            print(archivo, "todo el tile es nodata")
            continue

        aviso = "" if data.shape == (360, 360) else "  <-- tamaño distinto de 360x360"
        print(archivo, data.shape, "| nodata:", n_nodata,
            "| min:", validos.min(), "| max:", validos.max(), aviso)