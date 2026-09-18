from opensimplex import OpenSimplex
import numpy as np

obj = OpenSimplex(seed=42)
print([m for m in dir(obj) if 'noise' in m.lower()])

with open("heightmap.raw", "rb") as f:
    w, h = np.fromfile(f, dtype=np.uint32, count=2)
    datos = np.fromfile(f, dtype=np.float32).reshape((h, w))

print(w, h, datos.shape, datos.dtype)

mapa_crudo = np.load("heightmap_crudo.npy")
print(np.allclose(datos, mapa_crudo.astype(np.float32)))