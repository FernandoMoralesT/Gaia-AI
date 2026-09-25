Semana 1: El ruido es la mejor manera de representar las formas naturales que comunmente se observan en la naturaleza, este dia observe como generar ruido virtual utilizando una matriz como base, ademas entendi como la frecuencia de este ruido puede aumentar el zoom y las octavas con nada mas que las capas solo que escaladas comunmente a X2 o X0.5

Semana 2 — Erosión (concepto, pendiente de implementación)
Investigado pero no implementado aún. Dos familias de algoritmos para hacer que el heightmap se vea geológicamente más creíble (el ruido puro da paisajes suaves sin valles ni crestas naturales):
Eroión térmica: simula el material deslizándose de zonas muy empinadas hacia zonas bajas vecinas. Suaviza pendientes extremas. Se aplica revisando, celda por celda, la diferencia de altura contra sus vecinas y moviendo una fracción del "exceso" cuando supera un ángulo de reposo.
Erosión hidráulica: simula gotas de agua que recorren el mapa siguiendo la pendiente descendente, erosionando material en el camino y depositándolo donde pierden velocidad. Produce patrones tipo cauce de río. Es iterativa: se simulan muchas gotas, una tras otra, sobre el mismo heightmap.
Ambas se aplican como **post-proceso** después de generar el heightmap base con ruido, no reemplazan la generación de ruido en sí.
Decisión pendiente: cuál implementar primero (o ambas) depende de qué tanto tiempo
quiera invertir aquí vs. avanzar a la Fase 2. Queda como candidato para retomar
más adelante, posiblemente ya con datos reales de por medio (Fase 2, semana 6).
Relación con Estructura de Datos: la erosión hidráulica en particular depende de
"vecindad" entre celdas — relevante para la decisión pendiente de qué estructura
usar para representar el heightmap (matriz vs. grafo de adyacencia).



## Sprint 3 — Unificación del pipeline y exportación para Godot

Se partió de dos scripts independientes que hacían, cada uno, una versión distinta
del mismo paso (generación de la matriz de ruido cruda): uno con normalización +
umbralización de biomas sobre una sola octava, y otro con combinación de octavas
(fBm) sin normalizar. Se unificaron en un solo pipeline con dos ramas de salida.

### Vectorización de `fractal_noise_2d`

La versión original recorría cada celda con dos `for` anidados (`width × height`
llamadas por octava). Se investigó si `OpenSimplex` soporta entrada vectorizada:
`dir(obj)` confirmó la existencia de `noise2array(x, y)` como método de instancia.

Se verificó empíricamente, antes de integrarlo, que:
- `noise2array` espera arrays 1D de x e y (no una malla 2D vía `meshgrid`).
- La forma del array resultante sigue la convención `(len(y), len(x))`.

Con eso, `fractal_noise_2d` quedó reescrita generando `x`/`y` una sola vez (fuera
del loop de octavas) y llamando a `get_noise_array` una sola vez por octava — sin
loops anidados de celdas ni de filas.

### `remap` — manejo del caso `a == b`

Se identificó que una matriz de entrada completamente plana produciría división
entre cero en `remap`. Se decidió, en vez de fallar de forma fatal, devolver un
valor por defecto: el punto medio del rango de salida (`(c + d) / 2`), usando
`numpy.full_like` para mantener la forma del array de entrada.

### `clasificar_biomas` como función reutilizable

Se extrajo la lógica de umbralización (agua/tierra/montaña) del script original a
una función independiente, parametrizada por los umbrales.

### Exportación a Godot

Se descartó pasar por `uint8` para la exportación, ya que pierde precisión
necesaria para `Format_RF` en Godot. Se optó por la opción de menor complejidad
de las tres evaluadas (PNG 16-bit / EXR / raw binario): **raw binario**, sin
dependencias externas.

Formato de archivo definido:
[width -> uint32, 4 bytes]
[height -> uint32, 4 bytes]
[datos -> width*height floats de 4 bytes (float32), en orden]


Se incluyó `width`/`height` como header dentro del mismo archivo (en vez de un
archivo de metadatos aparte o valores fijos) para mantener flexibilidad ante
heightmaps de distinto tamaño.

Se convirtió `mapa_crudo` de `float64` (default de NumPy) a `float32` antes de
exportar, por compatibilidad con Godot y menor tamaño de archivo.

### Verificación

Se comprobó el pipeline de punta a punta desde Python:
- Lectura de vuelta del `.raw` con `numpy.fromfile`, confirmando `shape == (height, width)`.
- Comparación numérica contra el array original (guardado aparte con `numpy.save`
  antes de exportar) mediante `numpy.allclose` → resultado `True`, confirmando que
  no hay pérdida de datos más allá de la esperada por la conversión a `float32`.

### Pendiente para el siguiente sprint

- Lectura real del `.raw` desde GDScript en Godot (la verificación actual solo
  confirma que Python se lee correctamente a sí mismo, no que Godot interpreta
  el archivo igual).
- Definir si se documenta explícitamente el *endianness* usado, en caso de dar
  problemas al leer desde GDScript.

Tag de cierre: `sprint-03`.

## Sprint 4 — Entorno PyTorch y origen de datos reales (DEM)

### Verificación de entorno

Se confirmó instalación de PyTorch (`2.14.0+cu126`). `torch.cuda.is_available()`
devolvió `False`: el equipo cuenta con GPU AMD Radeon, no NVIDIA, por lo que el
build `cu126` (compilado para CUDA) no puede usar aceleración por hardware.
Decisión: entrenar en CPU por el momento; se deja `torch-directml` (backend
DirectX 12, compatible con AMD en Windows) como opción de optimización futura
solo si el tiempo de entrenamiento en CPU resulta un bloqueo real.

Se practicaron operaciones básicas de tensores (creación, operaciones
elemento a elemento, conversión desde/hacia NumPy) y el mecanismo de
diferenciación automática (`requires_grad`, `.backward()`, `.grad`), base de
cómo se entrenan redes neuronales sin derivar manualmente.

### Decisión: datos reales vs. sintéticos

Se evaluó entrenar el modelo con datos sintéticos (el propio `fractal_noise_2d`)
frente a datos reales de elevación (DEM). Se descartó la opción sintética: al
ser generados por la misma función de ruido procedural clásico contra la que
el proyecto busca comparar (según la hipótesis del anteproyecto), el modelo
no tendría de dónde aprender variedad adicional — el propio ruido clásico
sería el techo de lo que el modelo podría replicar.

Se decidió entrenar con datos reales de elevación (SRTM, vía OpenTopography),
reservando la comparación contra heightmaps de la comunidad geográfica como
evaluación cualitativa en el reporte final, no como fuente de entrenamiento.

### Obtención de datos

Se descartó USGS EarthExplorer por exceso de datos personales solicitados en
el registro. Se optó por OpenTopography (registro más ligero, API key
inmediata). Se descargaron 3 tiles SRTM GL1 (30m) de zonas con relieve
marcado cerca de la región de Mazatlán-Culiacán, en formato GeoTIFF.

Cita para bibliografía: NASA Shuttle Radar Topography Mission (SRTM) (2013).
Shuttle Radar Topography Mission (SRTM) Global. Distribuido por
OpenTopography. https://doi.org/10.5069/G9445JDF

### Lectura con `rasterio`

Se implementó `cargar_bach_dem()` en `src/dataset/cargar_dem.py`, leyendo
todos los `.tif` de `data/raw/` con `rasterio`.

Hallazgos relevantes sobre el formato:
- Los datos vienen en `int16` (metros enteros), no en floats como el ruido
  sintético — no es pérdida de precisión, es cómo SRTM almacena elevación de
  forma nativa.
- SRTM usa un valor centinela (`nodata = -32768`) para huecos de medición.
  En los tiles descargados no apareció (`min: 17, max: 274`, valores
  plausibles), pero se deja documentado como riesgo a validar en tiles
  futuros (Sprint 5), con `src.nodata` como forma de detectarlo.
- Los tres tiles descargados resultaron con dimensiones distintas entre sí
  (`278×408`, `494×751`, `141×184`), al no haber delimitado regiones de
  tamaño idéntico en OpenTopography.

### Recorte temporal y Dataset de PyTorch

Se implementó `recortar()` en `src/dataset/preprocesamiento.py` (archivo
separado, anticipando que ahí vivirán las funciones de augmentation/splits
del Sprint 5), como solución mínima al problema de tamaños inconsistentes:
recorte fijo a 100×100 sobre cada tile.

Se implementó `DEMDataset` (`torch.utils.data.Dataset`) envolviendo el batch
recortado, y se verificó su funcionamiento real con `DataLoader`
(`batch_size=2`), obteniendo tensores de forma `[2, 100, 100]` y
`[1, 100, 100]` — confirma el pipeline completo: DEM real → cargado →
recortado → Dataset → batches iterables.

### Pendiente para el Sprint 5

- El recorte fijo a 100×100 es una solución temporal, no augmentation real
  (no hay variabilidad ni manejo cuidadoso de qué región del tile se pierde).
- Validar manejo de `nodata` con tiles que sí lo contengan.
- División train/val/test.
- Documentar tamaño y licencia del dataset en `docs/dataset.md`.

Tag de cierre: `sprint-04`.