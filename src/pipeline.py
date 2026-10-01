from torch.utils.data import DataLoader
from noise.Unificacion_Y_Exportacion import fractal_noise_2d, exportar_para_godot, remap, clasificar_biomas, generar_y_exportar_terreno
from dataset.dem_dataset import DEMDataset
from dataset.cargar_dem import cargar_bach_dem
from dataset.procesamiento import recortar, normalizar_dem,generar_variantes

def pipeline_ruido_procedural(width, height, scale, octaves, seed, persistence, lacunarity):
    mapa_crudo, biomas = generar_y_exportar_terreno(width, height, scale, octaves, seed, persistence, lacunarity)
    return mapa_crudo, biomas

def pipeline_dataset_dem(carpeta_datos, size_recorte, batch_size):
    tiles = cargar_bach_dem(carpeta_datos)

    todas_las_muestras = []
    for tile in tiles:
        variantes = generar_variantes(tile)
        for variante in variantes:
            recortada = recortar(variante, size=size_recorte)
            normalizada = normalizar_dem(recortada)
            todas_las_muestras.append(normalizada)

    dataset = DEMDataset(todas_las_muestras)
    loader = DataLoader(dataset, batch_size=batch_size)
    return loader

if __name__ == "__main__":
    loader = pipeline_dataset_dem("data/raw/", size_recorte=100, batch_size=4)
    for batch in loader:
        print(batch.shape)