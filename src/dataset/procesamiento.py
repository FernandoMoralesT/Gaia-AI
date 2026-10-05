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

def dividir_tiles(tiles, train_pct=0.8,val_pct=0.1, seed=42):
    random.Random(seed).shuffle(tiles)
    n = len(tiles)
    n_train = int(n*train_pct)
    n_val = int(n*val_pct)
    train = tiles[:n_train]
    val = tiles[n_train:n_train+n_val]
    test = tiles[n_train + n_val:]
    return train, val, test

