from noise.Unificacion_Y_Exportacion import fractal_noise_2d, exportar_para_godot, remap, clasificar_biomas, generar_y_exportar_terreno
from dataset.dem_dataset import DEMDataset
from dataset.cargar_dem import cargar_bach_dem
from dataset.procesamiento import recortar, normalizar_dem

def pipeline_ruido_procedural(width, height, scale, octaves, seed, persistence, lacunarity):
    mapa_crudo, biomas = generar_y_exportar_terreno(width, height, scale, octaves, seed, persistence, lacunarity)
    return mapa_crudo, biomas

def pipeline_dataset_dem(carpeta_datos, size_recorte, batch_size):
    
    pass

if __name__ == "__main__":
    data = cargar_bach_dem("data/raw/")[0]
    normalizado = normalizar_dem(data)
    print(normalizado.min(), normalizado.max())