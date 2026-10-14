from torch.utils.data import DataLoader
from noise.Unificacion_Y_Exportacion import fractal_noise_2d, exportar_para_godot, remap, clasificar_biomas, generar_y_exportar_terreno
from dataset.dem_dataset import DEMDataset, ID_CLASE
from dataset.cargar_dem import cargar_bach_dem, cargar_etiquetas
from dataset.procesamiento import recortar, normalizar_dem, normalizar_tile, reducir_tile,generar_variantes, dividir_tiles
from dataset.descargar_dem import descargar_tile
from model.generador import Generador
from model.discrimidador import Discriminador
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
    g = Generador()
    z = torch.randn(4, 100)
    etiquetas = torch.tensor([0, 1, 2, 3])
    salida = g(z, etiquetas)

    d = Discriminador()
    puntaje = d(salida, etiquetas)    # `salida` y `etiquetas` son las de la prueba del generador
    print(puntaje.shape)
    print(sum(p.numel() for p in g.parameters()), "parámetros en G")
    print(sum(p.numel() for p in d.parameters()), "parámetros en D")
