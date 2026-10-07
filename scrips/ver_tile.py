import sys

import matplotlib.pyplot as plt
import rasterio

archivo = sys.argv[1]

with rasterio.open(f"data/raw/{archivo}") as src:
    data = src.read(1)

plt.imshow(data, cmap="terrain")
plt.colorbar(label="Elevación (m)")
plt.title(archivo)
plt.show()