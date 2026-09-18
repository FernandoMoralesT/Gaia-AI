import numpy as np
from opensimplex import OpenSimplex
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

class Noise2D:
    def __init__(self, seed=None):
        self.noise = OpenSimplex(seed)

    def get_noise(self, x, y):
        return self.noise.noise2(x, y)

    def get_noise_array(self, x, y):
        return self.noise.noise2array(x, y)


def fractal_noise_2d(width, height, scale, octaves, seed, persistence, lacunarity):
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

    return mapa / amplitud_total, capas


def remap(valor, a, b, c, d):
    """
    Pieza 4 pendiente: ¿qué haces si a == b?
    """
    pass


def clasificar_biomas(array_uint8, agua_umbral, tierra_umbral):
    """
    La lógica de umbralización que ya tenían en el script 1,
    ahora como función reutilizable en vez de código suelto.
    """
    pass


def exportar_para_godot(mapa_float, formato):
    """
    Pieza 5 pendiente: esta rama NO debe pasar por array_uint8.
    Recibe el mapa float directo de fractal_noise_2d (antes del remap a 0-255).
    Aquí es donde decide tu equipo: PNG16 / EXR / raw.
    """
    pass


if __name__ == "__main__":
    width, height, scale = 256, 256, 5.0

    # 1. Generar heightmap crudo con fractal_noise_2d
    # 2. Rama A: remap -> uint8 -> clasificar_biomas -> visualizar (como script 1)
    # 3. Rama B: exportar_para_godot con el float crudo, sin pasar por uint8
    pass