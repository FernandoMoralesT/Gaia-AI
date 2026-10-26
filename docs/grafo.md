# Grafo del repositorio

Generado por `scrips/generar_grafo.py` a partir de los imports reales (módulo `ast`).
No editar a mano las secciones 1 y 3: volver a ejecutar el script.

## 1. Dependencias (archivo → archivo que importa)

- `src/dataset/cargar_dem.py` → `src/dataset/dem_dataset.py`
- `src/dataset/cargar_dem.py` → `src/dataset/procesamiento.py`
- `src/dataset/procesamiento.py` → `src/noise/Unificacion_Y_Exportacion.py`
- `src/descargar_lote.py` → `src/dataset/descargar_dem.py`
- `src/inferencia.py` → `src/dataset/dem_dataset.py`
- `src/inferencia.py` → `src/model/generador.py`
- `src/model/entrenar.py` → `src/dataset/dem_dataset.py`
- `src/pipeline.py` → `src/dataset/cargar_dem.py`
- `src/pipeline.py` → `src/dataset/dem_dataset.py`
- `src/pipeline.py` → `src/dataset/descargar_dem.py`
- `src/pipeline.py` → `src/dataset/procesamiento.py`
- `src/pipeline.py` → `src/model/discriminador.py`
- `src/pipeline.py` → `src/model/entrenar.py`
- `src/pipeline.py` → `src/model/generador.py`
- `src/pipeline.py` → `src/noise/Unificacion_Y_Exportacion.py`
- `scrips/exportar_generador.py` → `src/model/discriminador.py`
- `scrips/exportar_generador.py` → `src/model/entrenar.py`
- `scrips/exportar_generador.py` → `src/model/generador.py`
- `scrips/probar_checkpoint.py` → `src/dataset/dem_dataset.py`
- `scrips/probar_checkpoint.py` → `src/model/discriminador.py`
- `scrips/probar_checkpoint.py` → `src/model/entrenar.py`
- `scrips/probar_checkpoint.py` → `src/model/generador.py`
- `test/test_inferencia.py` → `src/dataset/dem_dataset.py`
- `test/test_inferencia.py` → `src/inferencia.py`

Sin dependencias internas: `scrips/Practicatensores.py`, `scrips/comprobacion.py`, `scrips/comprobacion_reduccion.py`, `scrips/generar_grafo.py`, `scrips/resumen_dataset.py`, `scrips/sanos.py`, `scrips/validar_nodata.py`, `scrips/ver_clase.py`, `scrips/ver_dudosos.py`, `scrips/ver_tile.py`, `src/__init__.py`, `src/dataset/__init__.py`, `src/model/__init__.py`, `src/noise/Comprobacion.py`, `src/noise/__init__.py`, `src/noise/noise2D.py`, `src/noise/normalizacionDeRangos.py`, `src/noise/tempCodeRunnerFile.py`.

## 2. Flujo de datos

```text
data/raw/*.tif + data/etiquetas.json
  → src/dataset/ (cargar_dem, procesamiento, dem_dataset)
  → src/pipeline.py + src/model/entrenar.py          (entrenamiento)
  → salidas/checkpoints/epoca_NNN.pt                  (local, gitignored)
  → scrips/exportar_generador.py
  → modelos/generador_epoca150.pt                     (versionado)
  → src/inferencia.py  (generar_terreno → suavizar → exportar_raw)
  → godot/gaia-visor/mapas/*.raw
  → visor de Godot (godot/gaia-visor/terreno.gd + terreno.gdshader)
```

## 3. Archivos clave

- `src/dataset/dem_dataset.py`: Dataset de PyTorch y orden canónico de clases (nunca reordenar CLASES). Exporta: `CLASES`, `ID_CLASE`, `DEMDataset`.
- `src/dataset/cargar_dem.py`: Lectura de los .tif con rasterio y de data/etiquetas.json. Exporta: `cargar_etiquetas`, `cargar_bach_dem`.
- `src/dataset/procesamiento.py`: Reducción a 120×120, normalización por tile, variantes y división por tile. Exporta: `recortar`, `normalizar_dem`, `flip_horizontal`, `flip_vertical`, `rotar_90`, `generar_variantes`, `dividir_tiles`, `reducir_tile`, `normalizar_tile`.
- `src/dataset/descargar_dem.py`: Descarga de un tile SRTM desde OpenTopography (clave en .env). Exporta: `nombre_tile`, `descargar_tile`.
- `src/descargar_lote.py`: Descarga por lotes de la lista de tiles. Exporta: `LADO`, `CARPETA`, `RUTA_ETIQUETAS`, `MAX_SOLICITUDES`, `ANTIGUOS`, `NUEVOS`, `LISTA`, `cargar_etiquetas`, `guardar_etiquetas`.
- `src/pipeline.py`: Punto de entrada del dataset y del entrenamiento (500 épocas). Exporta: `pipeline_ruido_procedural`, `procesar_tiles`, `pipeline_dataset_dem`.
- `src/model/generador.py`: Generador de la cGAN (ruido 100 + clase → 120×120). Exporta: `Generador`.
- `src/model/discriminador.py`: Discriminador de la cGAN (clase como canal extra). Exporta: `Discriminador`.
- `src/model/entrenar.py`: Ciclo de entrenamiento, muestras, checkpoints y su carga. Exporta: `paso_entrenamiento`, `entrenar`, `guardar_muestras`, `guardar_checkpoint`, `cargar_checkpoint`.
- `src/inferencia.py`: Inferencia local: terreno por clase y semilla, suavizado y exportación .raw. Exporta: `RUTA_MODELO`, `Z_DIM`, `normalizar`, `suavizar`, `generar_terreno`, `exportar_raw`.
- `src/noise/Unificacion_Y_Exportacion.py`: Generador clásico de ruido y exportación (Sprints 1-3). Exporta: `Noise2D`, `fractal_noise_2d`, `remap`, `clasificar_biomas`, `exportar_para_godot`, `generar_y_exportar_terreno`.
- `scrips/exportar_generador.py`: Extrae el generador de epoca_150.pt a modelos/generador_epoca150.pt. Script ejecutable.
- `scrips/generar_grafo.py`: Este script: regenera docs/grafo.md. Script ejecutable.
- `test/test_inferencia.py`: Tests de pytest de src/inferencia.py. Contiene 18 tests.
- `modelos/generador_epoca150.pt`: `state_dict` del generador de la época 150 (modelo del demo).
- `data/etiquetas.json`: fuente de verdad de la clase de cada tile.
- `godot/gaia-visor/terreno.gd`: lee el `.raw` y arma la malla; `terreno.gdshader` colorea por altura.
