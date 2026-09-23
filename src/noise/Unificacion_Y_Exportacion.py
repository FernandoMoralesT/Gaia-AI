import numpy as np
from opensimplex import OpenSimplex
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import time

class Noise2D:
    def __init__(self, seed=None):
        self.noise = OpenSimplex(seed)

    def get_noise(self, x, y):
        return self.noise.noise2(x, y)

    def get_noise_array(self, x, y):
        return self.noise.noise2array(x, y)


def fractal_noise_2d(width, height, scale, octaves, seed, persistence, lacunarity):
    print(time.perf_counter())
    noise = Noise2D(seed)
    mapa = np.zeros((height, width), dtype=float)
    amplitud_total = 0.0
    capas = []

    x = np.arange(width, dtype=float)
    y = np.arange(height, dtype=float)

    for octave in range(octaves):
        frequency = 1.0 * (lacunarity ** octave)
        amplitude = persistence ** octave
        amplitud_total += amplitude

        nx = x / scale * frequency
        ny = y / scale * frequency
        capa = noise.get_noise_array(nx, ny) * amplitude
        capas.append(capa)
        mapa += capa
    
    print(time.perf_counter())
    return mapa / amplitud_total, capas

def remap(valor, a, b, c, d):
    if a==b:
        return np.full_like(valor, (c+d)/2)
    return c + (valor - a)/(b - a) * (d - c)


def clasificar_biomas(array_uint8, agua_umbral, tierra_umbral):
    biomas = np.zeros_like(array_uint8)
    biomas[array_uint8 < agua_umbral] = 0
    biomas[(array_uint8 >= agua_umbral) & (array_uint8 < tierra_umbral)] = 1
    biomas[array_uint8 >= tierra_umbral] = 2
    return biomas


def exportar_para_godot(mapa_float, formato, width, height):
    with open("heightmap.raw", "wb") as f:
        np.array([width, height], dtype=np.uint32).tofile(f)
        mapa_float.astype(formato).tofile(f)

if __name__ == "__main__":
    width, height, scale = 256, 256, 50.0

    # 1. Generar heightmap crudo con fractal_noise_2d
    mapa_crudo, capas = fractal_noise_2d(width, height, scale, octaves=6, seed=42, persistence=0.5, lacunarity=1.5)
    np.save("heightmap_crudo.npy", mapa_crudo)

    # 2. Rama A: remap -> uint8 -> clasificar_biomas -> visualizar (como script 1)
    mapa_norm = remap(mapa_crudo, np.min(mapa_crudo), np.max(mapa_crudo), 0, 255)
    mapa_uint8 = mapa_norm.astype(np.uint8)

    biomas = clasificar_biomas(mapa_uint8, agua_umbral=85, tierra_umbral=170)
    colores = ['blue', 'green', 'gray']

    cmap_biomas = ListedColormap(colores)
    plt.figure(figsize=(10, 10))
    plt.imshow(biomas, cmap=cmap_biomas)
    plt.title('Unificacion y Exportacion - Biomas')
    plt.show()
    # 3. Rama B: exportar_para_godot con el float crudo, sin pasar por uint8
    exportar_para_godot(mapa_crudo, formato=np.float32, width=width, height=height)