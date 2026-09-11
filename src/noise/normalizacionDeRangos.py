import numpy
from opensimplex import OpenSimplex
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

class Noise2D:
    def __init__(self, seed=None):
        self.noise = OpenSimplex(seed)

    def get_noise(self, x, y):
        return self.noise.noise2(x, y)

width = 256
height = 256
scale = 5.0

value = [[0.0 for _ in range(width)] for _ in range(height)]

noise = Noise2D(seed=42)

for y in range(height):
    for x in range(width):
        nx = x / scale
        ny = y / scale
        value[y][x] = noise.get_noise(nx, ny)

array_value = numpy.array(value)
def remap(valor, a, b, c, d):
    return c + (valor - a)/(b - a) * (d - c)

array_norm = remap(array_value, numpy.min(array_value), numpy.max(array_value), 0, 255)

array_uint8 = array_norm.astype(numpy.uint8)

agua_umbral = 85
tierra_umbral = 170

biomas = numpy.zeros_like(array_norm, dtype=numpy.uint8)

biomas[array_uint8 < agua_umbral] = 0
biomas[(array_uint8 >= agua_umbral) & (array_uint8 < tierra_umbral)] = 1
biomas[array_uint8 >= tierra_umbral] = 2

colores = ['blue', 'green', 'gray']

cmap_biomas = ListedColormap(colores)

plt.figure(figsize=(10, 10))
plt.imshow(biomas, cmap=cmap_biomas)
plt.title('Biomas')
plt.show()