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
scale = 10.0

value = [[0.0 for _ in range(height)] for _ in range(width)]
noise = Noise2D(seed=42)

for y in range(height):
    for x in range(width):
        nx = x / width - 0.5
        ny = y / height - 0.5
        value[y][x] = noise.get_noise(nx*scale, ny*scale)

array_value = numpy.array(value)

plt.imshow(array_value, cmap='gray')
plt.show()