import collections
import json
import os

import numpy as np
import rasterio

CARPETA = "data/raw"
SALIDA = "docs/dataset_tiles.md"

with open("data/etiquetas.json", encoding="utf-8") as f:
    etiquetas = json.load(f)

archivos = sorted(a for a in os.listdir(CARPETA) if a.endswith(".tif"))
filas = []

for archivo in archivos:
    with rasterio.open(os.path.join(CARPETA, archivo)) as src:
        data = src.read(1)
        nodata = src.nodata
    mascara = (data == nodata) if nodata is not None else np.zeros(data.shape, dtype=bool)
    validos = data[~mascara]
    if validos.size == 0:
        filas.append((archivo, etiquetas.get(archivo, "SIN ETIQUETA"), data.shape, int(mascara.sum()), None, None))
        continue
    filas.append((archivo, etiquetas.get(archivo, "SIN ETIQUETA"), data.shape,
                int(mascara.sum()), int(validos.min()), int(validos.max())))

print("Tiles en data/raw:", len(archivos))
print("Por clase:", dict(collections.Counter(f[1] for f in filas)))
print("Sin etiqueta:", [f[0] for f in filas if f[1] == "SIN ETIQUETA"])
print("Etiqueta sin archivo:", sorted(set(etiquetas) - set(archivos)))
print("Tamaño distinto de 360x360:", [f[0] for f in filas if f[2] != (360, 360)])
print("Con píxeles nodata:", [f[0] for f in filas if f[3] > 0])
minimos = [f[4] for f in filas if f[4] is not None]
maximos = [f[5] for f in filas if f[5] is not None]
print("Elevación global:", min(minimos), "a", max(maximos), "m")

with open(SALIDA, "w", encoding="utf-8") as f:
    f.write("| Tile | Clase | Tamaño | Píxeles nodata | Mín (m) | Máx (m) |\n")
    f.write("| --- | --- | --- | --- | --- | --- |\n")
    for a, c, forma, n, mn, mx in sorted(filas, key=lambda x: (x[1], x[0])):
        f.write(f"| {a[:-4]} | {c} | {forma[0]}×{forma[1]} | {n} | {mn} | {mx} |\n")