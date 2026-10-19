from torch.utils.data import DataLoader
from noise.Unificacion_Y_Exportacion import fractal_noise_2d, exportar_para_godot, remap, clasificar_biomas, generar_y_exportar_terreno
from dataset.dem_dataset import DEMDataset, ID_CLASE
from dataset.cargar_dem import cargar_bach_dem, cargar_etiquetas
from dataset.procesamiento import recortar, normalizar_dem, normalizar_tile, reducir_tile,generar_variantes, dividir_tiles
from dataset.descargar_dem import descargar_tile
from model.generador import Generador
from src.model.discriminador import Discriminador
from model.entrenar import paso_entrenamiento, entrenar
import torch

def pipeline_ruido_procedural(width, height, scale, octaves, seed, persistence, lacunarity):
    mapa_crudo, biomas = generar_y_exportar_terreno(width, height, scale, octaves, seed, persistence, lacunarity)
    return mapa_crudo, biomas

def procesar_tiles(nombres, tiles, etiquetas, batch_size, shuffle=False):
    muestras, clases = [], []
    for nombre in nombres:
        reducido = reducir_tile(tiles[nombre])       
        normalizado = normalizar_tile(reducido)    
        id_clase = ID_CLASE[etiquetas[nombre]]   
        for variante in generar_variantes(normalizado):
            muestras.append(variante)
            clases.append(id_clase)
    dataset = DEMDataset(muestras, clases)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

def pipeline_dataset_dem(carpeta_datos, batch_size):
    tiles = cargar_bach_dem(carpeta_datos)
    etiquetas = cargar_etiquetas()
    train, val, test = dividir_tiles(tiles, etiquetas)
    loader_train = procesar_tiles(train, tiles, etiquetas, batch_size, shuffle=True)
    loader_val = procesar_tiles(val, tiles, etiquetas, batch_size)
    loader_test = procesar_tiles(test, tiles, etiquetas, batch_size)
    return loader_train, loader_val, loader_test

if __name__ == "__main__":
    import torch
    import torch.nn as nn

    loader_train, loader_val, loader_test = pipeline_dataset_dem("data/raw", batch_size=4)

    torch.manual_seed(42)
    g = Generador()
    d = Discriminador()
    criterio = nn.BCEWithLogitsLoss()
    opt_g = torch.optim.Adam(g.parameters(), lr=2e-4, betas=(0.5, 0.999))
    opt_d = torch.optim.Adam(d.parameters(), lr=2e-4, betas=(0.5, 0.999))

    historial = entrenar(g, d, loader_train, 500, criterio, opt_g, opt_d)