# Dataset de elevación de Gaia-AI (versión 2)

## 1. Resumen

| Campo                  | Valor |
| ---                    | --- |
| Fuente                 | NASA SRTM GL1 (30 m), distribuido por OpenTopography |
| Formato                | GeoTIFF, un canal, `int16` (metros) |
| Sistema de coordenadas | WGS84 (EPSG:4326) |
| Valor sin dato (`nodata`) | −32768 |
| Tamaño de tile         | 0.1° por lado (~11 km), 360 × 360 píxeles |
| Tiles                  | 60 |
| Clases                 | 6: llanura, lomas, valle, montaña, meseta, volcán |
| Etiquetas              | `data/etiquetas.json` (nombre de archivo → clase) |
| Tabla por tile         | `docs/dataset_tiles.md` (la genera `scrips/resumen_dataset.py`)|
| Versión anterior       | 14 tiles en `data/raw_v1/` (11 de 0.05° y 3 descargas manuales); no se usan en el entrenamiento |

## 2. Fuente y licencia

NASA Shuttle Radar Topography Mission (SRTM). (2013). *Shuttle Radar Topography Mission (SRTM) Global* [Conjunto de datos]. Distribuido por OpenTopography. https://doi.org/10.5069/G9445JDF

Los términos de uso de OpenTopography indican que los datos obtenidos por su API están libres de restricciones de copyright. Verificar el texto vigente antes de redistribuir los archivos.

## 3. Obtención

- API `globaldem` de OpenTopography, con `descargar_tile` (`src/dataset/descargar_dem.py`) y la lista de lugares de `src/descargar_lote.py`.
- Cada tile es un cuadro de 0.1° centrado en un lugar elegido por su tipo de terreno.
- Límite confirmado por el servidor: 50 llamadas por 24 horas. Se descargaron 48 tiles el 5 de octubre de 2026 y 12 el 7 de octubre.
- La descarga es reanudable: omite los archivos que ya existen, reintenta ante fallos de red y se detiene si el servidor rechaza la solicitud.
- Los nombres siguen el formato `dem_{sur}_{norte}_{oeste}_{este}.tif`, con las coordenadas redondeadas a 2 decimales.

## 4. Clases y etiquetado

| Clase | Descripción de referencia | Tiles |
| --- | --- | --- |
| Llanura | Casi sin relieve (rango aproximado menor de 150 m) | 10 |
| Lomas | Ondulaciones suaves de relieve medio | 11 |
| Valle | Fondo bajo con laderas a ambos lados | 8 |
| Montaña | Rango y pendientes altas (rango aproximado mayor de 1000 m) | 14 |
| Meseta | Superficie alta y plana con bordes abruptos | 8 |
| Volcán | Cono con cráter | 9 |
| **Total** | | **60** |

- La clase inicial se asignó por el nombre del lugar y por el rango de elevación.
- Cambios aplicados: `dem_23.57_23.68_-106.02_-105.92` de lomas a montaña (rango de 1121 m), `dem_23.18_23.28_-106.44_-106.34` de llanura a lomas (264 m) y descarte del tile de Table Mountain (incluye mar y ciudad).
- Etiquetas por confirmar visualmente (se conservaron sin cambio): `dem_24.77_24.88_-107.42_-107.33` y `dem_25.77_25.88_-108.97_-108.88` (llanura); `dem_24.81_24.91_-99.62_-99.52` y `dem_38.61_38.71_-96.54_-96.44` (lomas); `dem_19.14_19.25_-100.18_-100.08`, `dem_45.87_45.97_6.82_6.92`, `dem_46.54_46.64_7.86_7.96` y `dem_37.7_37.8_-119.64_-119.54` (valle); `dem_24.18_24.28_-105.52_-105.42` (meseta).

## 5. Validación

Resultados del script de validación sobre 48 de los 60 tiles:

- Tamaño: 360 × 360 en los 48.
- `nodata` (−32768): 0 píxeles en los 48.
- Elevación observada: de −30 m a 8748 m; el máximo es el tile del Everest.Etiquetas por clase: Counter({'montaña': 14, 'lomas': 11, 'llanura': 10, 'volcán': 9, 'valle': 8, 'meseta': 8})
Archivos en data/raw: 60 | Etiquetas: 60
Sin etiqueta: []
Etiqueta sin archivo: []

dem_-13.36_-13.25_-72.17_-72.07.tif (360, 360) | nodata: 0 | min: 2825 | max: 4628 
dem_-18.01_-17.91_-67.16_-67.06.tif (360, 360) | nodata: 0 | min: 3700 | max: 4046 
dem_-32.7_-32.6_-70.06_-69.96.tif (360, 360) | nodata: 0 | min: 3764 | max: 6940 
dem_-35.71_-35.61_-63.81_-63.71.tif (360, 360) | nodata: 0 | min: 116 | max: 162 
dem_-50.99_-50.89_-73.46_-73.36.tif (360, 360) | nodata: 0 | min: 677 | max: 1890 
dem_17.01_17.11_-96.78_-96.68.tif (360, 360) | nodata: 0 | min: 1490 | max: 2057 
dem_17.72_17.82_-96.37_-96.27.tif (360, 360) | nodata: 0 | min: 51 | max: 998 
dem_17.94_18.04_-93.0_-92.9.tif (360, 360) | nodata: 0 | min: -9 | max: 34 
dem_18.97_19.07_-98.68_-98.58.tif (360, 360) | nodata: 0 | min: 2792 | max: 5406 
dem_18.98_19.08_-97.32_-97.22.tif (360, 360) | nodata: 0 | min: 3090 | max: 5595 
dem_19.06_19.16_-99.81_-99.71.tif (360, 360) | nodata: 0 | min: 3220 | max: 4662 
dem_19.14_19.25_-100.18_-100.08.tif (360, 360) | nodata: 0 | min: 1738 | max: 2409 
dem_19.18_19.28_-98.08_-97.98.tif (360, 360) | nodata: 0 | min: 2869 | max: 4424 
dem_19.44_19.54_-102.3_-102.2.tif (360, 360) | nodata: 0 | min: 2098 | max: 3558 
dem_19.46_19.56_-103.67_-103.57.tif (360, 360) | nodata: 0 | min: 1553 | max: 4247 
dem_20.64_20.74_-88.25_-88.15.tif (360, 360) | nodata: 0 | min: 16 | max: 35 
dem_20.77_20.87_-102.81_-102.71.tif (360, 360) | nodata: 0 | min: 1734 | max: 1960 
dem_20.92_21.02_-89.64_-89.54.tif (360, 360) | nodata: 0 | min: -3 | max: 46 
dem_20.9_21.0_-97.45_-97.35.tif (360, 360) | nodata: 0 | min: -10 | max: 57 
dem_21.07_21.18_-104.56_-104.46.tif (360, 360) | nodata: 0 | min: 930 | max: 2277 
dem_21.11_21.21_-100.98_-100.88.tif (360, 360) | nodata: 0 | min: 1887 | max: 2153 
dem_23.18_23.28_-106.44_-106.34.tif (360, 360) | nodata: 0 | min: -30 | max: 234 
dem_23.27_23.38_-106.12_-106.03.tif (360, 360) | nodata: 0 | min: 68 | max: 567 
dem_23.52_23.62_-106.42_-106.33.tif (360, 360) | nodata: 0 | min: 46 | max: 690 
dem_23.57_23.68_-106.02_-105.92.tif (360, 360) | nodata: 0 | min: 198 | max: 1319 
dem_23.68_23.78_-105.92_-105.83.tif (360, 360) | nodata: 0 | min: 346 | max: 1997 
dem_23.77_23.88_-105.77_-105.67.tif (360, 360) | nodata: 0 | min: 560 | max: 2744 
dem_23.88_23.98_-106.22_-106.12.tif (360, 360) | nodata: 0 | min: 311 | max: 1763 
dem_23.97_24.07_-105.62_-105.53.tif (360, 360) | nodata: 0 | min: 1081 | max: 2688 
dem_24.18_24.28_-105.52_-105.42.tif (360, 360) | nodata: 0 | min: 2224 | max: 2773 
dem_24.77_24.88_-107.42_-107.33.tif (360, 360) | nodata: 0 | min: 17 | max: 291 
dem_24.81_24.91_-99.62_-99.52.tif (360, 360) | nodata: 0 | min: 307 | max: 435 
dem_24.82_24.92_-100.27_-100.17.tif (360, 360) | nodata: 0 | min: 1884 | max: 3723 
dem_25.52_25.62_-108.52_-108.42.tif (360, 360) | nodata: 0 | min: -3 | max: 45 
dem_25.77_25.88_-108.97_-108.88.tif (360, 360) | nodata: 0 | min: -8 | max: 154 
dem_25.9_26.0_-107.08_-106.98.tif (360, 360) | nodata: 0 | min: 1206 | max: 3292 
dem_27.44_27.54_-109.99_-109.89.tif (360, 360) | nodata: 0 | min: 16 | max: 67 
dem_27.94_28.04_86.88_86.97.tif (360, 360) | nodata: 0 | min: 5148 | max: 8748 
dem_30.93_31.03_-115.47_-115.37.tif (360, 360) | nodata: 0 | min: 1129 | max: 3050 
dem_31.72_31.82_-113.53_-113.43.tif (360, 360) | nodata: 0 | min: 275 | max: 1189 
dem_32.03_32.13_-116.67_-116.57.tif (360, 360) | nodata: 0 | min: 274 | max: 803 
dem_32.57_32.67_-115.5_-115.4.tif (360, 360) | nodata: 0 | min: -16 | max: 20 
dem_35.31_35.41_138.68_138.78.tif (360, 360) | nodata: 0 | min: 1041 | max: 3759 
dem_35.83_35.93_-106.35_-106.25.tif (360, 360) | nodata: 0 | min: 2001 | max: 2816 
dem_36.53_36.63_-118.34_-118.24.tif (360, 360) | nodata: 0 | min: 2339 | max: 4412 
dem_36.95_37.05_-110.15_-110.05.tif (360, 360) | nodata: 0 | min: 1514 | max: 1979 
dem_37.13_37.23_-108.54_-108.44.tif (360, 360) | nodata: 0 | min: 1779 | max: 2342 
dem_37.7_37.8_-119.64_-119.54.tif (360, 360) | nodata: 0 | min: 1201 | max: 2620 
dem_38.41_38.51_-109.87_-109.77.tif (360, 360) | nodata: 0 | min: 1231 | max: 1908 
dem_38.46_38.56_-122.52_-122.42.tif (360, 360) | nodata: 0 | min: 42 | max: 823 
dem_38.61_38.71_-96.54_-96.44.tif (360, 360) | nodata: 0 | min: 364 | max: 443 
dem_39.01_39.11_-108.04_-107.94.tif (360, 360) | nodata: 0 | min: 2485 | max: 3413 
dem_43.27_43.37_11.28_11.38.tif (360, 360) | nodata: 0 | min: 169 | max: 394 
dem_43.69_43.79_-110.85_-110.75.tif (360, 360) | nodata: 0 | min: 2056 | max: 4071 
dem_45.87_45.97_6.82_6.92.tif (360, 360) | nodata: 0 | min: 986 | max: 3704 
dem_45.93_46.03_7.61_7.71.tif (360, 360) | nodata: 0 | min: 1959 | max: 4230 
dem_46.54_46.64_7.86_7.96.tif (360, 360) | nodata: 0 | min: 633 | max: 3576 
dem_46.68_46.78_-117.23_-117.13.tif (360, 360) | nodata: 0 | min: 686 | max: 832 
dem_46.98_47.08_4.79_4.89.tif (360, 360) | nodata: 0 | min: 189 | max: 424 
dem_5.09_5.19_-60.81_-60.71.tif (360, 360) | nodata: 0 | min: 1081 | max: 2748 


## 6. Procesamiento

Pipeline (`src/pipeline.py`):

1. `cargar_bach_dem` lee los `.tif` y los devuelve en un diccionario nombre → array.
2. `dividir_tiles` reparte por clase con semilla 42: 80/10/10 y mínimo de 1 tile en val y en test por clase.
3. `reducir_tile` pasa cada tile de 360 × 360 a 120 × 120 con el promedio de bloques de 3 × 3 (90 m por píxel).
4. `normalizar_tile` lleva cada tile de −1 a 1 con su propio mínimo y máximo, en `float32`.
5. `generar_variantes` produce 6 muestras por tile (original, dos volteos y tres rotaciones); todas heredan la clase del tile.
6. `DEMDataset` devuelve el par (mapa de forma [1, 120, 120], id de clase) y `DataLoader` agrupa en lotes de 4. Solo el loader de train mezcla las muestras.

| Conjunto | Tiles | Muestras | Lotes de 4 |
| --- | --- | --- | --- |
| Train | 48 | 288 | 72 |
| Val | 6 | 36 | 9 |
| Test | 6 | 36 | 9 |

Cada clase aporta 1 tile a val y 1 a test. Train: llanura 8, lomas 9, valle 6, montaña 12, meseta 6, volcán 7. Los ids de clase están fijos en `CLASES` (`src/dataset/dem_dataset.py`).

La normalización es por tile, así que el modelo no aprende la altura absoluta; el demo asigna la altura según la clase.

## 7. Limitaciones

- Las etiquetas vienen del nombre del lugar y de estadísticas de elevación, y 9 siguen sin confirmación visual.
- Val y test tienen 1 tile por clase (6 muestras por clase), poco para evaluar una clase por separado.
- La distribución geográfica se concentra en México, el oeste de Estados Unidos, los Alpes y los Andes, con algunos puntos en otros continentes.
- A latitudes altas el píxel es más angosto en dirección este-oeste (a 46° N, unos 21 m en lugar de 30 m).
- Los conos volcánicos grandes quedan recortados en 11 km.
- Dos tiles pueden tocarse en una esquina (por ejemplo `dem_23.57_23.68_-106.02_-105.92` y `dem_23.68_23.78_-105.92_-105.83`) y caer en conjuntos distintos.
- Normalizar por tile amplifica el relieve de las llanuras: los escalones de 1 m de SRTM se vuelven visibles.
- El promedio de 3 × 3 suaviza los picos (en un tile de prueba recortó ~10 m en el mínimo y ~4 m en el máximo).

## 8. Reproducir

1. Instalar las dependencias de `requirements.txt`.
2. Crear `.env` con `OPENTOPO_API_KEY` (cada integrante, con su propia clave).
3. Ejecutar `python src/descargar_lote.py` desde la raíz (puede necesitar dos días por el límite diario).
4. Ejecutar `python scrips/resumen_dataset.py` para validar y regenerar la tabla.
5. Ejecutar `python src/pipeline.py` para construir los loaders.

## 9. Pendientes

- Validar los 12 tiles de la segunda tanda y completar la sección 5.
- Confirmar visualmente las etiquetas dudosas.
- Registrar las coordenadas de los 3 tiles manuales de `raw_v1`, si se van a conservar.
- Confirmar la licencia de uso de los datos con el texto vigente de OpenTopography.
- Ampliar las clases con menos tiles si el entrenamiento lo exige.