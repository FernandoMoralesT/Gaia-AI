import numpy
from opensimplex import OpenSimplex
import matplotlib.pyplot as plt

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

plt.figure(figsize=(10, 10))
plt.imshow(array_norm, cmap='gray')
plt.title('2D Noise')
plt.show()