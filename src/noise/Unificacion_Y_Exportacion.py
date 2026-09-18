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


def exportar_para_godot(mapa_float, formato):
    """
    Pieza 5 pendiente: esta rama NO debe pasar por array_uint8.
    Recibe el mapa float directo de fractal_noise_2d (antes del remap a 0-255).
    Aquí es donde decide tu equipo: PNG16 / EXR / raw.
    """
    pass

mapa_final, capas = fractal_noise_2d(width=256, height=256, scale=5.0, octaves=6, seed=42, persistence=0.5, lacunarity=2.0)
array_norm = remap(mapa_final, np.min(mapa_final), np.max(mapa_final), 0, 255)
array_uint8 = array_norm.astype(np.uint8)

biomas = clasificar_biomas(array_uint8, agua_umbral=85, tierra_umbral=170)


if __name__ == "__main__":
    width, height, scale = 256, 256, 5.0

    # 1. Generar heightmap crudo con fractal_noise_2d
    # 2. Rama A: remap -> uint8 -> clasificar_biomas -> visualizar (como script 1)
    # 3. Rama B: exportar_para_godot con el float crudo, sin pasar por uint8
    pass