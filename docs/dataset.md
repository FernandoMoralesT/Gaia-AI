# Dataset de elevación de Gaia-AI

## 1. Resumen

| Campo | Valor |
| --- | --- |
| Fuente | NASA SRTM GL1 (30 m), distribuido por OpenTopography |
| Formato original | GeoTIFF, un canal, `int16` (metros) |
| Sistema de coordenadas | WGS84 (EPSG:4326) |
| Valor sin dato (`nodata`) | −32768 |
| Tiles | 14 (3 descargados de forma manual y 11 por API) |
| Muestras tras augmentation | 84 (14 tiles × 6 variantes) |
| Tamaño de muestra | 100 × 100 píxeles |
| División | 80/10/10 por tile: 11 / 1 / 2 tiles |

## 2. Fuente y licencia

NASA Shuttle Radar Topography Mission (SRTM). (2013). *Shuttle Radar Topography Mission (SRTM) Global* [Conjunto de datos]. Distribuido por OpenTopography. https://doi.org/10.5069/G9445JDF

- Primera descarga (manual): 25 de septiembre de 2026.
- La página del dataset en OpenTopography muestra la licencia como no provista. Verificar los términos de uso antes de redistribuir los archivos y antes del reporte final.

## 3. Tiles

### 3.1 Descarga manual (Bulk Download, GeoTIFF)

| Archivo | Alto × ancho | Coordenadas |
| --- | --- | --- |
| `output_SRTMGL1.tif` | 141 × 184 | S 23.4753, N 23.5143, O −106.4880, E −106.4368 |
| Otros dos archivos `output_SRTMGL1(n).tif` | 278 × 408 y 494 × 751 | No registradas |

### 3.2 Descarga automática (API `globaldem`, función `descargar_tile`)

Los archivos se nombran `dem_{sur}_{norte}_{oeste}_{este}.tif`, con las coordenadas redondeadas a 2 decimales.

| Tile | Sur | Norte | Oeste | Este | Alto × ancho |
| --- | --- | --- | --- | --- | --- |
| Prueba | 23.55 | 23.59 | −106.40 | −106.35 | 144 × 180 |
| Lote 1 | 23.70 | 23.75 | −105.90 | −105.85 | 180 × 180 |
| Lote 2 | 23.80 | 23.85 | −105.75 | −105.70 | 180 × 180 |
| Lote 3 | 24.00 | 24.05 | −105.60 | −105.55 | 180 × 180 |
| Lote 4 | 24.20 | 24.25 | −105.50 | −105.45 | 180 × 180 |
| Lote 5 | 23.60 | 23.65 | −106.00 | −105.95 | 180 × 180 |
| Lote 6 | 23.30 | 23.35 | −106.10 | −106.05 | 180 × 180 |
| Lote 7 | 23.90 | 23.95 | −106.20 | −106.15 | 180 × 180 |
| Lote 8 | 23.20 | 23.25 | −106.42 | −106.37 | 180 × 180 |
| Lote 9 | 24.80 | 24.85 | −107.40 | −107.35 | 180 × 180 |
| Lote 10 | 25.80 | 25.85 | −108.95 | −108.90 | 180 × 180 |

Las coordenadas se eligieron para cubrir zonas de sierra, piedemonte y costa. El relieve real de cada tile no se ha clasificado.

## 4. Procesamiento

1. `cargar_bach_dem` lee todos los `.tif` de `data/raw/`.
2. `dividir_tiles` mezcla los tiles con `random.Random(42)` y los reparte 80/10/10.
3. `generar_variantes` produce 6 muestras por tile: original, volteo horizontal, volteo vertical y rotaciones de 90°, 180° y 270°.
4. `recortar` toma `[:100, :100]` de cada variante.
5. `normalizar_dem` remapea de forma lineal el rango fijo 0-9000 m a 0-255.
6. `DEMDataset` convierte cada muestra a `float32` y `DataLoader` las agrupa en lotes de 4.

La división ocurre antes de generar las variantes, así que las 6 variantes de un tile quedan siempre en el mismo conjunto.

## 5. División

| Conjunto | Tiles | Muestras | Lotes de 4 |
| --- | --- | --- | --- |
| Train | 11 | 66 | 17 |
| Val | 1 | 6 | 2 |
| Test | 2 | 12 | 3 |
| Total | 14 | 84 | |

Los conteos de lotes (17, 2 y 3) coinciden con la salida de `pipeline.py`. La división es por tile para evitar que variantes del mismo terreno queden en conjuntos distintos. La semilla fija (42) hace la división reproducible.

## 6. Valores observados

- `nodata` (−32768): ausente en los 14 tiles (0 píxeles).
- Elevación mínima del dataset: −8 m. Máxima: 2941 m.
- Dos tiles costeros tienen mínimo negativo (−8 y −6 m).
- Con el rango global 0-9000 m, el máximo observado queda en ≈ 83 de 255.

| Tile                          | Mín (m) | Máx (m) |
| ---                           | ---     | ---     |
| dem_23.2_23.25_-106.42_-106.37| −8      | 121     |
| dem_23.3_23.35_-106.1_-106.05 | 82      | 403     |
| dem_23.55_23.59_-106.4_-106.35| 113     | 647     |
| dem_23.6_23.65_-106.0_-105.95 | 330     | 986     |
| dem_23.7_23.75_-105.9_-105.85 | 494     | 1921    |
| dem_23.8_23.85_-105.75_-105.7 | 1076    | 2635    |
| dem_23.9_23.95_-106.2_-106.15 | 497     | 1555    |
| dem_24.0_24.05_-105.6_-105.55 | 1286    | 2572    |
| dem_24.2_24.25_-105.5_-105.45 | 2274    | 2586    |
| dem_24.8_24.85_-107.4_-107.35 | 28      | 132     |
| dem_25.8_25.85_-108.95_-108.9 | −6      | 79      |
| output_SRTMGL1                | 17      | 274     |
| output_SRTMGL1(1)             | 167     | 932     |
| output_SRTMGL1(2)             | 1285    | 2941    |

## 7. Limitaciones conocidas

- El conjunto de validación tiene 1 tile (6 muestras).
- El recorte `[:100, :100]` toma siempre la esquina superior izquierda de cada variante.
- El rango global 0-9000 m concentra los valores en la parte baja de la escala; revisar el límite superior.
- El augmentation es geométrico: reordena elevaciones reales y no crea valores nuevos.
- Todas las coordenadas están en el noroeste de México.

## 8. Cómo reproducirlo

1. Instalar las dependencias de `requirements.txt`.
2. Guardar la clave de OpenTopography en `.env` como `OPENTOPO_API_KEY` (el archivo no se versiona).
3. Descargar con `descargar_tile(south, north, west, east)`.
4. Ejecutar `python src/pipeline.py` desde la raíz del proyecto.

Los `.tif` de `data/raw/` se versionan por su tamaño pequeño (el primero pesó 29.5 KB). Revisar esta decisión si el tamaño total crece.

## 9. Pendientes

- Registrar las coordenadas de los otros dos tiles manuales.
- Decidir el límite superior del rango global y el tratamiento de valores negativos.
- Confirmar la licencia de uso de los datos.