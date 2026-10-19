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

Licencia: los términos de uso de OpenTopography (https://opentopography.org/usageterms, consultados el [10/14/2026]) permiten el uso libre de los datos /btenidos por su API. La ficha del dataset muestra el campo de licencia/como "Not Provided", pero los términos generales del sitio son los que se aplican a la descarga.

Condiciones que se mantienen:
- Citar el dataset y OpenTopography como fuente.
- Cada integrante usa su propia clave de API; no se comparte.

## 3. Obtención

- API `globaldem` de OpenTopography, con `descargar_tile` (`src/dataset/descargar_dem.py`) y la lista de lugares de `src/descargar_lote.py`.
- Cada tile es un cuadro de 0.1° centrado en un lugar elegido por su tipo de terreno.
- Límite confirmado por el servidor: 50 llamadas por 24 horas. Se descargaron 48 tiles el 5 de octubre de 2026 y 12 el 7 de octubre.
- La descarga es reanudable: omite los archivos que ya existen, reintenta ante fallos de red y se detiene si el servidor rechaza la solicitud.
- Los nombres siguen el formato `dem_{sur}_{norte}_{oeste}_{este}.tif`, con las coordenadas redondeadas a 2 decimales.

## 4. Clases y etiquetado

| Clase | Descripción (por forma) | Tiles |
| --- | --- | --- |
| Llanura | Superficie casi plana, sin crestas ni drenaje marcado | 9 |
| Lomas | Ondulaciones suaves y repartidas, con drenaje visible | 12 |
| Valle | Fondo bajo con laderas altas a los lados (incluye cañones y valles glaciares) | 8 |
| Montaña | Crestas y pendientes pronunciadas, relieve alto y accidentado | 14 |
| Meseta | Superficie alta y plana con bordes abruptos (incluye mesetas disecadas por ríos) | 8 |
| Volcán | Cono con cráter | 9 |
| **Total** | | **60** |

Cada tile se normaliza de −1 a 1 por separado, así que la red no ve metros: las clases se definen por forma. Los rangos de elevación solo sirven de referencia al revisar.

- La clase inicial se asignó por el nombre del lugar y por el rango de elevación.
- Cambios aplicados: `dem_23.57_23.68_-106.02_-105.92` de lomas a montaña (rango de 1121 m), `dem_23.18_23.28_-106.44_-106.34` de llanura a lomas (264 m), `dem_24.77_24.88_-107.42_-107.33` de llanura a lomas (274 m, con drenaje y crestas visibles; mismo criterio que el anterior) y descarte del tile de Table Mountain (incluye mar y ciudad).
- Revisión visual de las 9 etiquetas dudosas ([fecha], `scrips/ver_dudosos.py` y `scrips/ver_clase.py`): 1 cambió y 8 se conservaron.
  - `dem_25.77_25.88_-108.97_-108.88` (llanura): casi plana; el rango lo inflan tres lomas pequeñas y el ruido de SRTM.
  - `dem_24.81_24.91_-99.62_-99.52` (lomas): ladera inclinada con una cresta rocosa; confianza baja.
  - `dem_38.61_38.71_-96.54_-96.44` (lomas): colinas con una superficie plana de borde recto, parece un embalse.
  - `dem_19.14_19.25_-100.18_-100.08`, `dem_45.87_45.97_6.82_6.92`, `dem_46.54_46.64_7.86_7.96` y `dem_37.7_37.8_-119.64_-119.54` (valle): fondo bajo con laderas a los lados; el último es un valle glaciar de paredes altas que parece cañón, y no hay clase cañón.
  - `dem_24.18_24.28_-105.52_-105.42` (meseta): meseta disecada por ríos, sin cima plana clara; es el tile más débil de la clase y se revisa con las muestras generadas del Sprint 7.
- Caso aparte: `dem_-18.01_-17.91_-67.16_-67.06` (meseta) es un altiplano al que el recuadro de 11 km le deja fuera el borde donde cae la altura.

## 5. Validación

Resultados de `scrips/resumen_dataset.py` sobre los 60 tiles:

- Tiles en `data/raw`: 60, y 60 etiquetas en `data/etiquetas.json`; ninguna sobra ni falta.
- Tamaño: 360 × 360 en todos.
- `nodata` (−32768): 0 píxeles en todos.
- Elevación observada: de −30 m a 8748 m (el máximo es el tile del Everest).
- Conteo por clase: llanura 9, lomas 12, valle 8, montaña 14, meseta 8, volcán 9.
- La tabla por tile está en `docs/dataset_tiles.md`. 


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

Cada clase aporta 1 tile a val y 1 a test. Train: llanura 7, lomas 10, valle 6, montaña 12, meseta 6, volcán 7.

La normalización es por tile, así que el modelo no aprende la altura absoluta; el demo asigna la altura según la clase.

## 7. Limitaciones

- Las etiquetas vienen del nombre del lugar y de una revisión visual de la forma; los 9 tiles dudosos se revisaron uno por uno, pero la clasificación sigue siendo subjetiva.
- Val y test tienen 1 tile por clase (6 muestras por clase), poco para evaluar una clase por separado.
- La distribución geográfica se concentra en México, el oeste de Estados Unidos, los Alpes y los Andes, con algunos puntos en otros continentes.
- A latitudes altas el píxel es más angosto en dirección este-oeste (a 46° N, unos 21 m en lugar de 30 m).
- Los conos volcánicos grandes quedan recortados en 11 km.
- Dos tiles pueden tocarse en una esquina (por ejemplo `dem_23.57_23.68_-106.02_-105.92` y `dem_23.68_23.78_-105.92_-105.83`) y caer en conjuntos distintos.
- Normalizar por tile amplifica el relieve de las llanuras: los escalones de 1 m de SRTM se vuelven visibles.
- El promedio de 3 × 3 suaviza los picos (en un tile de prueba recortó ~10 m en el mínimo y ~4 m en el máximo).
- No hay clase "cañón": los cañones y valles glaciares encajan en "valle".
- El recuadro de 11 km a veces deja fuera el borde de una meseta (altiplano de Bolivia) o incluye una zona plana artificial dentro de una clase ondulada (embalse en un tile de lomas).

## 8. Reproducir

1. Instalar las dependencias de `requirements.txt`.
2. Crear `.env` con `OPENTOPO_API_KEY` (cada integrante, con su propia clave).
3. Ejecutar `python src/descargar_lote.py` desde la raíz (puede necesitar dos días por el límite diario).
4. Ejecutar `python scrips/resumen_dataset.py` para validar y regenerar la tabla.
5. Ejecutar `python src/pipeline.py` para construir los loaders.

## 9. Pendientes

- Comparar las mesetas generadas con las reales después de la corrida larga; si salen disecadas y sin cima plana, revisar `dem_24.18_24.28_-105.52_-105.42` y el altiplano.
- Registrar las coordenadas de los 3 tiles manuales de `raw_v1`, si se van a conservar.
- Ampliar las clases con menos tiles si el entrenamiento lo exige.