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

def fractal_noise_2d(width, height, scale, octaves=6, seed=42, base_frequency=1.0, persistence=0.5, lacunarity=2.0):
    noise = Noise2D(seed)
    mapa = numpy.zeros((height, width))
    amplitud_total = 0.0
    capas = []

    for octave in range (octaves):
        frequency = base_frequency * (lacunarity ** octave)
        amplitude = persistence ** octave
        amplitud_total += amplitude

        capa = numpy.zeros((height, width))
        for y in range(height):
            for x in range(width):
                nx = x / scale * frequency
                ny = y / scale * frequency
                capa[y][x] = noise.get_noise(nx, ny) * amplitude

        capas.append(capa)
        mapa += capa
    return mapa / amplitud_total, capas


mapa_final, capas = fractal_noise_2d(width, height, scale)

plt.figure(figsize=(10, 10))

plt.subplot(1, 2, 1)
plt.imshow(mapa_final, cmap='gray')
plt.title('Fractal Noise')

plt.subplot(1, 2, 2)
plt.imshow(capas[0] - capas[1], cmap='gray')
plt.title('Difference between first two octaves')

plt.show()