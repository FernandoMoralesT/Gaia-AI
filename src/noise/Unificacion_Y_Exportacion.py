import numpy
from opensimplex import OpenSimplex
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

class Noise2D:
    def __init__(self, seed=None):
        self.noise = OpenSimplex(seed)

    def get_noise(self, x, y):
        return self.noise.noise2(x, y)


def fractal_noise_2d(width, height, scale, octaves, seed, persistence, lacunarity):
    """
    Genera el heightmap crudo combinando octavas (fBm).
    Devuelve un array float en rango aprox [-1, 1], SIN pasar por uint8.
    Decisión pendiente (pieza 3): ¿vectorizado o loops anidados como antes?
    Decisión pendiente (pieza 2): ¿sigue devolviendo 'capas' o ya no las necesitas aquí?
    """
    pass


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