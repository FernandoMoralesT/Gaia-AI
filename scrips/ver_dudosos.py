import json
import os

import matplotlib.pyplot as plt
import rasterio

CARPETA = "data/raw"
DUDOSOS = [
    "dem_24.77_24.88_-107.42_-107.33",   # llanura
    "dem_25.77_25.88_-108.97_-108.88",   # llanura
    "dem_24.81_24.91_-99.62_-99.52",     # lomas
    "dem_38.61_38.71_-96.54_-96.44",     # lomas
    "dem_19.14_19.25_-100.18_-100.08",   # valle
    "dem_45.87_45.97_6.82_6.92",         # valle
    "dem_46.54_46.64_7.86_7.96",         # valle
    "dem_37.7_37.8_-119.64_-119.54",     # valle
    "dem_24.18_24.28_-105.52_-105.42",   # meseta
]

with open("data/etiquetas.json", encoding="utf-8") as f:
    etiquetas = json.load(f)

fig, ejes = plt.subplots(3, 3, figsize=(13, 13))
for eje, nombre in zip(ejes.flat, DUDOSOS):
    archivo = nombre + ".tif"
    with rasterio.open(os.path.join(CARPETA, archivo)) as src:
        data = src.read(1).astype("float32")
    clase = etiquetas.get(archivo, "SIN ETIQUETA")
    rango = data.max() - data.min()
    im = eje.imshow(data, cmap="terrain")
    eje.set_title(f"{clase.upper()}\n{nombre[4:]}\n{data.min():.0f} a {data.max():.0f} m (rango {rango:.0f} m)",
                fontsize=9)
    eje.axis("off")
    plt.colorbar(im, ax=eje, fraction=0.046, pad=0.02)

plt.tight_layout()
os.makedirs("salidas", exist_ok=True)
fig.savefig("salidas/dudosos.png", dpi=100)
plt.show()