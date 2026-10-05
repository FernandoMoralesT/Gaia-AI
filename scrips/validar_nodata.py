import os
import numpy as np
import rasterio

carpeta = "data/raw"

for archivo in sorted(os.listdir(carpeta)):
    if not archivo.endswith(".tif"):
        continue
    with rasterio.open(os.path.join(carpeta, archivo)) as src:
        data = src.read(1)
        nodata = src.nodata

        if nodata is None:
            print(archivo, "no declara nodata")
            continue

        mascara = data == nodata
        n_nodata = np.count_nonzero(mascara)
        validos = data[~mascara]
        print(archivo, data.shape, "nodata:", nodata, "| píxeles nodata:", n_nodata,
            "| min:", validos.min(), "| max:", validos.max())