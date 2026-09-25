import rasterio
import os

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
    for h in batch:
        print(h.shape, h.dtype)