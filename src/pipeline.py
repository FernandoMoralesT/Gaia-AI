from torch.utils.data import DataLoader
from noise.Unificacion_Y_Exportacion import fractal_noise_2d, exportar_para_godot, remap, clasificar_biomas, generar_y_exportar_terreno
from dataset.dem_dataset import DEMDataset
from dataset.cargar_dem import cargar_bach_dem
from dataset.procesamiento import recortar, normalizar_dem,generar_variantes, dividir_tiles
from dataset.descargar_dem import descargar_tile

def pipeline_ruido_procedural(width, height, scale, octaves, seed, persistence, lacunarity):
    mapa_crudo, biomas = generar_y_exportar_terreno(width, height, scale, octaves, seed, persistence, lacunarity)
    return mapa_crudo, biomas

def procesar_tiles(tiles, size_recorte, batch_size):
    todas_las_muestras = []
    for tile in tiles:
        variantes = generar_variantes(tile)
        for variante in variantes:
            recortada = recortar(variante, size=size_recorte)
            normalizada = normalizar_dem(recortada)
            todas_las_muestras.append(normalizada)

    dataset = DEMDataset(todas_las_muestras)
    return DataLoader(dataset, batch_size=batch_size)

def pipeline_dataset_dem(carpeta_datos, size_recorte, batch_size):
    todos_los_tiles = cargar_bach_dem(carpeta_datos)
    train_tiles, val_tiles, test_tiles =  dividir_tiles(todos_los_tiles)
    loader_train = procesar_tiles(train_tiles, size_recorte, batch_size)
    loader_val = procesar_tiles(val_tiles, size_recorte, batch_size)
    loader_test = procesar_tiles(test_tiles, size_recorte, batch_size)
    return loader_train, loader_val, loader_test

if __name__ == "__main__":
    loader_train, loader_val, loader_test = pipeline_dataset_dem("data/raw", size_recorte=100, batch_size=4)
    print(len(loader_train), len(loader_val), len(loader_test))