import json
import math
import os
import sys

import matplotlib.pyplot as plt
import rasterio

CARPETA = "data/raw"
clase = sys.argv[1] if len(sys.argv) > 1 else "meseta"
RESALTAR = {"dem_24.18_24.28_-105.52_-105.42.tif"}   # tiles dudosos: se marcan en rojo

with open("data/etiquetas.json", encoding="utf-8") as f:
    etiquetas = json.load(f)

archivos = sorted(a for a, c in etiquetas.items() if c == clase)
if not archivos:
    print(f"No hay tiles de la clase '{clase}'. Clases: {sorted(set(etiquetas.values()))}")
    sys.exit(1)

columnas = 3
filas = math.ceil(len(archivos) / columnas)
fig, ejes = plt.subplots(filas, columnas, figsize=(5 * columnas, 5 * filas),
                        squeeze=False, layout="constrained")
ejes = list(ejes.flat)

for eje, archivo in zip(ejes, archivos):
    with rasterio.open(os.path.join(CARPETA, archivo)) as src:
        data = src.read(1).astype("float32")
    dudoso = archivo in RESALTAR
    im = eje.imshow(data, cmap="terrain")
    eje.set_title(f"{'DUDOSO  ' if dudoso else ''}{archivo[4:-4]}\n"
                f"{data.min():.0f} a {data.max():.0f} m (rango {data.max() - data.min():.0f} m)",
                fontsize=9, color="red" if dudoso else "black")
    eje.set_xticks([])
    eje.set_yticks([])
    for borde in eje.spines.values():
        borde.set_color("red" if dudoso else "gray")
        borde.set_linewidth(4 if dudoso else 0.5)
    fig.colorbar(im, ax=eje, fraction=0.046, pad=0.02)

for eje in ejes[len(archivos):]:
    eje.set_visible(False)

fig.suptitle(f"Clase: {clase} ({len(archivos)} tiles)")
os.makedirs("salidas", exist_ok=True)
fig.savefig(f"salidas/clase_{clase}.png", dpi=100)
print(f"{len(archivos)} tiles de '{clase}' en salidas/clase_{clase}.png")
plt.show()