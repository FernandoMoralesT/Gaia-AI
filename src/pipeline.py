from noise.Unificacion_Y_Exportacion import fractal_noise_2d, exportar_para_godot, remap, clasificar_biomas, generar_y_exportar_terreno
from dataset.dem_dataset import DEMDataset
from dataset.cargar_dem import cargar_bach_dem
from dataset.procesamiento import recortar, normalizar_dem,generar_variantes

def pipeline_ruido_procedural(width, height, scale, octaves, seed, persistence, lacunarity):
    mapa_crudo, biomas = generar_y_exportar_terreno(width, height, scale, octaves, seed, persistence, lacunarity)
    return mapa_crudo, biomas

def pipeline_dataset_dem(carpeta_datos, size_recorte, batch_size):
    
    pass

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    tile = cargar_bach_dem("data/raw/")[0]  # ajusten el import si hace falta
    variantes = generar_variantes(tile)

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    titulos = ["Original", "Flip H", "Flip V", "Rot 90", "Rot 180", "Rot 270"]

    for ax, variante, titulo in zip(axes.flat, variantes, titulos):
        ax.imshow(variante, cmap="gray")
        ax.set_title(titulo)

    plt.tight_layout()
    plt.show()