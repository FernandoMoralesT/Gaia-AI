from noise.Unificacion_Y_Exportacion import remap
import numpy as np
import random
def recortar(data, size=100):
    return data[:size, :size]

def normalizar_dem(data, elevacion_min=0, elevacion_max=9000):
    return remap(data, elevacion_min, elevacion_max, 0, 255)

def flip_horizontal(data):
    return np.fliplr(data)

def flip_vertical(data):
    return np.flipud(data)

def rotar_90(data, veces = 1):
    return np.rot90(data, k = veces)

def generar_variantes(data):
    variantes = [data]
    variantes.append(flip_horizontal(data))
    variantes.append(flip_vertical(data))
    variantes.append(rotar_90(data, 1))
    variantes.append(rotar_90(data, 2))
    variantes.append(rotar_90(data, 3))
    return variantes

def dividir_tiles(tiles, etiquetas, val_pct=0.1, test_pct=0.1, seed=42):
    por_clase = {}
    for nombre in sorted(tiles):
        clase = etiquetas[nombre]
        por_clase.setdefault(clase, []).append(nombre)  # agrega `nombre` a la lista de su clase

    rng = random.Random(seed)
    train, val, test = [], [], []
    for clase in sorted(por_clase):
        nombres = por_clase[clase]
        rng.shuffle(nombres)
        n_val = max(1, round(val_pct * len(nombres)))
        n_test = max(1, round(test_pct * len(nombres)))
        val += nombres[:n_val]
        test += nombres[n_val:n_val + n_test]    # los siguientes n_test nombres
        train += nombres[n_val + n_test:]   # todos los que quedan
    return train, val, test

def reducir_tile(data, factor = 3):
    n = data.shape[0] // factor
    bloque = data.reshape(n, factor, n, factor)
    resultado = bloque.mean(axis =(1,3))
    return resultado

def normalizar_tile(data):
    resultado = remap(data, data.min(),data.max(), -1, 1)
    return resultado.astype(np.float32)