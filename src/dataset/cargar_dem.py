import rasterio
import os
from procesamiento import recortar

def cargar_bach_dem(carpeta):
    heigthmaps = []
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".tif"):
            with rasterio.open(os.path.join(carpeta, archivo)) as src:
                data = src.read(1)
                heigthmaps.append(data)
    return heigthmaps

if __name__ == "__main__":
    batch = cargar_bach_dem("data/raw/")
    print(len(batch))
    batch_recortado = []
    for h in batch:
        print(h.shape, h.dtype, "Sin recortar")
        batch_recortado.append(recortar(h))

    for h in batch_recortado:
        print(h.shape, h.dtype, "Recortado")