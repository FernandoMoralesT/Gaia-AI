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


## Sprint 5 — Dataset final (augmentation + normalización)

### Normalización con rango global

Se evaluaron dos enfoques: normalizar cada tile con su propio min/max
individual, o con un rango global fijo. Se eligió rango global
(`0-9000`, aproximando el máximo plausible de elevación terrestre) para
preservar la relación real de altura entre tiles — normalizar por tile
individual habría hecho que un cerro pequeño y una montaña real se vieran
igual de "altos" tras normalizar, perdiendo justo la variedad que busca
demostrar la hipótesis del proyecto.

Se implementó `normalizar_dem()` en `preprocesamiento.py`, reutilizando
`remap()` ya existente. Verificado con el primer tile (17-274m reales):
resultado normalizado en rango `~4.7-26.4` — confirma que, con relieve
moderado, el rango global deja los valores concentrados en una porción
pequeña de 0-255. Queda anotado como punto a revisar si todos los tiles
futuros muestran el mismo patrón (podría ajustarse el límite superior).

### Augmentation

Con solo 3 tiles reales, se identificó la necesidad de generar más
muestras de entrenamiento sin inventar datos falsos. Se implementaron
flips horizontal/vertical y rotaciones de 90°/180°/270° (`numpy.fliplr`,
`numpy.flipud`, `numpy.rot90`) — únicas transformaciones geométricas que
preservan las dimensiones originales sin recortar ni dejar huecos
(rotaciones de ángulo arbitrario sí lo harían).

`generar_variantes()` produce 6 muestras por tile (original + 5
transformaciones). Verificado visualmente con matplotlib sobre un tile:
las 6 variantes se distinguen correctamente entre sí.

Decisión de orden en el pipeline: transformar primero, recortar después.
Como `recortar()` siempre toma la esquina fija `[:size, :size]`, recortar
antes de transformar habría dado 6 variantes de la misma región; transformar
primero hace que cada variante exponga una región distinta del tile en esa
esquina fija, maximizando la variedad real obtenida.

### Integración completa (`pipeline_dataset_dem`)

Flujo verificado de extremo a extremo: cargar tiles → generar variantes →
recortar → normalizar → `DEMDataset` → `DataLoader`.

Con 3 tiles × 6 variantes = 18 muestras y `batch_size=4`: 5 batches
(`[4,100,100]` × 4 + `[2,100,100]` × 1) — coincide exactamente con lo
calculado antes de correr el script.

**División train/val/test.** Se dividió por tile original (80/10/10, `random.Random(42)`), antes de generar variantes. Resultado: 11 / 1 / 2 tiles, 66 / 6 / 12 muestras y 17 / 2 / 3 lotes de 4, que coincide con la salida de `pipeline.py`.

**Errores resueltos.**
- `random.random(seed)` en lugar de `random.Random(seed)`: `random.random` es una función sin argumentos.
- `procesar_tiles` recibía una carpeta y volvía a cargar los tiles, que ya llegaban cargados.
- `procesar_tiles` devolvía una tupla y luego un `DEMDataset` con `batch_size`; el `batch_size` pertenece a `DataLoader`.

**Validación de `nodata`.** 0 píxeles con −32768 en los 14 tiles. Elevación de −8 m a 2941 m. Dos tiles costeros tienen mínimo negativo.

**Observación.** Con el rango global 0-9000 m, el máximo del dataset (2941 m) queda en ≈ 83 de 255.

**Decisión.** Se mantienen 14 tiles para cerrar el sprint. Ampliar el dataset se deja para más adelante, solo si el entrenamiento lo exige. Según la documentación de OpenTopography consultada el 5 de octubre de 2026, la cuota de la API para usuarios no académicos es de 50 trabajos por 24 horas; verificarla en la cuenta antes de planear descargas.

**Limitaciones.** El conjunto de validación tiene 1 tile (6 muestras). El recorte toma siempre la esquina `[:100, :100]`.

**Documentación.** `docs/dataset.md`, `README.md` y `requirements.txt` completados.

**Pendientes heredados.**
- Decidir el límite superior del rango global y el tratamiento de valores negativos.
- Recorte aleatorio en lugar de esquina fija.
- Registrar las coordenadas de los dos tiles manuales.

Tag de cierre: `sprint-05`.

## Sprint 6 — Arquitectura y datos para la cGAN (en curso) Licencia revisada: los términos de OpenTopography permiten el uso libre de los datos de su API; se cita el DOI del dataset.

### Decisión de arquitectura

Se compararon DCGAN, VAE y GAN condicional (cGAN) con las restricciones del proyecto: entrenamiento en CPU, muestras de 120×120 y pocas muestras de train. Se eligió **cGAN**, porque el objetivo es poder pedir el tipo de terreno ("montaña", "meseta") y recibirlo. Esto amplía el alcance del anteproyecto y agrega un objetivo específico: generar terreno según una clase solicitada. Riesgos registrados: la cGAN hereda la inestabilidad de las GAN; si no converge, queda el VAE condicional como alternativa.

### Clases

Se definieron 6 clases discretas: llanura, lomas, valle, montaña, meseta y volcán. Las cuatro primeras clases propuestas (por rango de elevación) se reemplazaron porque miden cuánto relieve hay y no qué forma tiene. Las clases de forma se etiquetan a mano; el id numérico de cada clase está fijo en `CLASES` (`dem_dataset.py`).

### Ampliación del dataset

- De 14 tiles de 0.05° (180 px) a 60 tiles de 0.1° (360 px, ~11 km). Los 14 anteriores quedaron en `data/raw_v1/`.
- Los lugares se eligieron por tipo de terreno (`src/descargar_lote.py`) y las etiquetas están en `data/etiquetas.json`.
- La API de OpenTopography respondió "API maximum rate limit reached (50 API calls/24hrs)" con código HTTP 401. Límite confirmado: 50 llamadas por 24 horas; la descarga tomó dos días (48 tiles el 5 de octubre y 12 el 7).
- El script es reanudable: omite archivos existentes y se detiene ante un rechazo del servidor.

**Errores resueltos**
- `JSONDecodeError` al leer `etiquetas.json`: el archivo existía vacío; la función ahora lee el texto y solo interpreta JSON si hay contenido.
- `ConnectionAbortedError 10053` y una descarga colgada: `requests.get` no tenía `timeout`; se agregó `timeout=(10, 120)` y hasta 3 reintentos ante fallos de red.
- `.env` apareció en `git status` porque `.gitingnore` tenía una errata en el nombre. Se detectó antes del commit; `git log --all -- .env` salió vacío, así que la clave nunca entró al historial.

### Etiquetas

Cambios sobre la propuesta inicial: `dem_23.57_23.68_-106.02_-105.92` de lomas a montaña (rango de 1121 m), `dem_23.18_23.28_-106.44_-106.34` de llanura a lomas (264 m) y descarte del tile de Table Mountain (incluye mar y ciudad). Conteo final: llanura 10, lomas 11, valle 8, montaña 14, meseta 8, volcán 9. Quedan 9 etiquetas dudosas por confirmar visualmente.

### Normalización y ventana de entrada

Se compararon normalización global (0-9000 m) y por tile. Con la global, una llanura (relieve de 19 a 274 m) ocupa menos del 1 % de la escala. Se eligió **normalizar por tile de −1 a 1**, porque el objetivo es un terreno vistoso y no a escala real. Consecuencia: la red no aprende la altura absoluta; el demo asignará la altura según la clase.

La ventana de entrada es el tile completo reducido de 360×360 a **120×120** por promedio de bloques de 3×3 (90 m por píxel). Cubre ~11 km y 120 = 15 × 2³, así que el generador parte de 15×15 y duplica tres veces. `recortar` y `normalizar_dem` quedan fuera de este flujo.

### Implementación y verificación

- `reducir_tile`: `reshape(n, factor, n, factor)` y `mean(axis=(1, 3))`. Prueba: (360, 360) → (120, 120); rango de 2234.6 a 2768.9 m → −1.0 a 1.0 en `float32`.
- `cargar_bach_dem` ahora devuelve un diccionario nombre → array, y `cargar_etiquetas` lee el JSON.
- `dividir_tiles` reparte por clase (80/10/10, mínimo 1 tile en val y en test, semilla 42): 48 / 6 / 6 tiles, 1 de cada clase en val y en test, sin traslape.
- `DEMDataset` devuelve el par (mapa de forma [1, 120, 120], etiqueta `long`). Se conserva `astype("float32")` porque corrige los pasos negativos de las vistas de `fliplr`, `flipud` y `rot90`.
- `procesar_tiles` y `pipeline_dataset_dem` verificados: 72 / 9 / 9 lotes de 4, primer lote `[4, 1, 120, 120]`, mínimo −1.0, máximo 1.0, ids `[5, 4, 3, 3]`.

**Errores resueltos:** `np.reshape` con argumentos sueltos; `axis` con los cuatro ejes en lugar de (1, 3); `por_clase` construido al revés (nombre → clase) y rebanadas de test vacías en `dividir_tiles`; `etiqueta = ID_CLASE` (diccionario entero en lugar del id de la muestra); confusión entre las tres tablas `tiles`, `etiquetas` e `ID_CLASE`.

### Generador y discriminador (MVP del sprint)

**Generador** (`src/model/generador.py`). Recibe ruido z (100 números) y el id de la clase. `nn.Embedding(6, 10)` convierte la clase en 10 números que se pegan al ruido, y una capa lineal los estira a 128 × 15 × 15. Tres `ConvTranspose2d(4, 2, 1)` duplican el tamaño (15 → 30 → 60 → 120) y reducen los canales (128 → 64 → 32 → 1), con `BatchNorm2d` y `ReLU` entre capas. Termina en `Tanh`, que coincide con el rango −1 a 1 de la normalización por tile. Salida: `[B, 1, 120, 120]`.

**Discriminador** (`src/model/discriminador.py`). Recibe el mapa y el id de clase. La clase entra como una hoja extra de 120 × 120 (`nn.Embedding(6, 14400)`) apilada al mapa, así que la entrada tiene 2 canales. Tres `Conv2d(4, 2, 1)` reducen el tamaño (120 → 60 → 30 → 15) y duplican los canales (2 → 32 → 64 → 128), con `LeakyReLU(0.2)`, y `BatchNorm2d` desde la segunda capa. Una capa lineal final da un solo número por terreno, sin `Sigmoid`: la función de pérdida del Sprint 7 lo incluye.

**Tamaños.** `ConvTranspose2d` y `Conv2d` con kernel 4, paso 2 y relleno 1 duplican o reducen a la mitad el tamaño. Por eso la ventana es de 120 (= 15 × 2³).

**Parámetros.** Generador: 3,361,501, con el 95 % en la capa lineal inicial. Discriminador: 280,673. El generador pesa unas 12 veces más; es un punto a vigilar en el entrenamiento.

**Verificación.** Generador: `[4, 1, 120, 120]`, rango de −0.9999 a 0.9996. Discriminador: `[4, 1]`. Los conteos de parámetros coinciden con el cálculo a mano.

**Errores resueltos**
- `BatchNorm2d` con `canales // 4` y `canales // 2` en el discriminador: en el generador los canales se dividen, en el discriminador se multiplican; cada `BatchNorm2d` lleva los canales de la convolución inmediata anterior.
- `Linear` final con `canales * 15 * 15`: faltaba el factor 4 de las hojas que quedan tras las tres convoluciones.
- Canales escritos como números fijos en las convoluciones, en lugar de expresiones de `canales`.

**Conceptos trabajados:** canales como hojas apiladas, `nn.Embedding` para condicionar por clase, `Tanh` por el rango de salida.

Tag de cierre: `sprint-06`.

## Sprint 7: Ciclo de entrenamiento y selección del checkpoint

### Qué se construyó
- `paso_entrenamiento`: un paso de GAN (turno del discriminador con `falso.detach()`, luego turno del generador).
- `entrenar`: ciclo por épocas con `historial.csv`, muestras fijas cada 10 épocas, `ultimo.pt` cada época y checkpoints numerados cada 50.
- `cargar_checkpoint(g, d, ruta, opt_g=None, opt_d=None)`: restaura pesos y, opcionalmente, optimizadores; devuelve la época. Verificada: carga `epoca_150.pt`, imprime 150 y genera muestras.
- Rendimiento en CPU: ~5 s por época; 500 épocas ≈ 48 min.

### Corrida de referencia (500 épocas, semilla 42, etiquetas corregidas)
- D se mantuvo sobre 1.0 en valores individuales hasta ~época 186 y cayó de forma sostenida desde ~189.
- Final: D = 0.226, G = 4.457. El discriminador dominó y el generador dejó de recibir señal útil.

### Criterio numérico (media móvil de 10 épocas, D_media > 1.0 y G_media < 2.5)
- Zona sana: épocas 10 a 115.
- Mayor equilibrio (D ≈ 1.4–1.5, G ≈ 1.3): épocas 15 a 40.
- Deriva lenta hacia el discriminador: D_media baja de 1.50 (ép. 15) a 1.02 (ép. 114); G_media sube de 1.25 (ép. 24) a 1.95 (ép. 114).
- Época 150: D_media = 0.848, G_media = 2.279, D_std = 0.096 (fuera de la zona sana por criterio numérico; D_media ya está por debajo de 1.0).

### Criterio visual (épocas 100, 150 y 200, mismo z_fijo)
- Volcán y valle: estables y claros en las tres.
- Llanura: la 150 es la más plana (verde/amarillo); la 100 mezcla zonas de montaña y la 200 tiene más ruido.
- Montaña: ninguna es claramente buena.
- Sin artefactos de puntos rojos en 100, 150 ni 200 (aparecen en la 300).

### Decisión
Se usa `epoca_150.pt` como modelo del demo, por criterio visual.
Queda como respaldo `epoca_100.pt`, que sí está dentro de la zona sana (D_media = 1.064, G_media = 1.919).

**Salvedad:** el criterio numérico no coincide con el visual. Las pérdidas indican que el equilibrio más sano está en las primeras épocas (10–115), pero ahí el generador tiene menos entrenamiento. La 150 está fuera de la zona sana por pérdidas, aunque antes del colapso (~189). En una GAN la pérdida mide el equilibrio entre D y G, no la calidad del mapa; por eso se priorizó la inspección visual.

### Limitaciones detectadas
- Lomas: las muestras se parecen a valle (zonas azules grandes).
- Montaña y meseta: poco distinguibles entre sí.
- Checkpoints solo cada 50 épocas; no hay granularidad fina entre 100 y 200.

### Pendiente
- Opción B (retomar desde la 150 con D frenado) si sobra tiempo.

## Sprint 8: Inferencia local, postprocesado y visor en Godot

### Exportación del generador
- `scrips/exportar_generador.py` carga `epoca_150.pt` con `cargar_checkpoint` y guarda solo el `state_dict` del generador en `modelos/generador_epoca150.pt` (13,453,757 bytes, ~12.8 MB).
- Verificado: carga estricta sin llaves faltantes ni sobrantes, 3,361,501 parámetros y pesos idénticos a `epoca_150.pt["g"]`.
- **Decisión:** `modelos/` se versiona en git. Así cualquier integrante puede generar terreno sin tener los checkpoints de entrenamiento (`salidas/` sigue fuera de git).

### `src/inferencia.py`
- `generar_terreno(clase, semilla, sigma=2)` devuelve un `numpy` `float32` de 120×120.
- El modelo se carga una sola vez y queda en caché en una variable del módulo (`_obtener_generador`), en modo `eval()` y con `weights_only=True`.
- La inferencia corre dentro de `torch.no_grad()`.
- El ruido sale de un `torch.Generator` propio con la semilla; no se toca la semilla global de PyTorch.
- La clase se convierte con `ID_CLASE` (equivale a `CLASES.index`, verificado para las 6) y una clase desconocida lanza `ValueError` con las válidas.
- **Por qué `eval()`:** con un lote de 1 mapa, `BatchNorm2d` en modo `train()` usaría el promedio de ese único mapa. Comparado con el camino de `guardar_muestras` (lote de 18): en `eval()` la diferencia es de 5.4e-07 (redondeo); en `train()` sube a 0.21.

### Postprocesado
- `normalizar(mapa)`: min-max a [0, 1]. Se aplica **al exportar**, no en `generar_terreno`, para poder probar la salida del modelo en [-1, 1]. Reproduce la convención del dataset, donde cada tile iba exactamente de -1 a 1.
- `suavizar(mapa, sigma)`: `gaussian_filter` de scipy y reescalado al min/max original. `sigma=0` devuelve la salida cruda.
- Comparación con volcán, semilla 42 (rugosidad = diferencia media entre píxeles vecinos):

| sigma | rugosidad | media |
| --- | --- | --- |
| 0 | 0.147 | -0.292 |
| 1 | 0.037 | -0.295 |
| 1.5 | 0.031 | -0.289 |
| 2 | 0.029 | -0.281 |
| 3 | 0.027 | -0.268 |

- Sigma 1 ya quita ~75 % del granulado; después la mejora es pequeña. Efecto secundario del reescalado: la cima se ensancha al subir sigma. Se fijó **sigma = 2** por defecto.
- **Alturas:** la red no conoce metros (normalización por tile), así que no hay altura real que recuperar. La escala vertical se decide en Godot.

### Exportación `.raw` para Godot
- `exportar_raw(mapa, ruta)`: encabezado `width`, `height` como `uint32` little-endian (`<u4`), luego los datos `float32` little-endian (`<f4`) fila por fila. 120×120 → 57,608 bytes.
- Se abre en modo `"wb"`: en modo texto, Windows convertiría cada byte `0x0A` en `0x0D 0x0A` y corrompería los datos.

### Visor en Godot (`godot/gaia-visor`)
- Godot 4.5, renderer *Compatibility*.
- `terreno.gd` lee el `.raw` (valida que el tamaño sea 8 + ancho × alto × 4), arma la malla con `SurfaceTool` (dos triángulos por celda, en sentido horario) y calcula normales.
- Parámetros editables: `escala_altura` (20, pensada para la escala por clase), `multiplicador_altura` (3, exageración general) y `tamano_celda`.
- `terreno.gdshader` colorea por altura normalizada (llega como color de vértice): verde, café desde 0.35 y gris claro desde 0.75, con transición suave.
- Escena: luz direccional a 25° de elevación y cámara a 30° sobre el terreno.
- Los mapas de ejemplo de `godot/gaia-visor/mapas/` se versionan como excepción al `*.raw` del `.gitignore`.

### Tests (`test/test_inferencia.py`)
23 pruebas con pytest, todas pasan: forma y tipo, las 6 clases, rango crudo, determinismo por semilla, semillas y clases distintas, clase inválida, semilla global intacta, modelo en `eval()` y en caché, pesos iguales al checkpoint (se omite si no existe `salidas/`), `normalizar`, `suavizar` y el formato `.raw` (incluido un mapa de 2×3 para detectar ancho y alto invertidos).

### Errores resueltos
- El código de inferencia se guardó en `scrips/exportar_generador.py` y reemplazó al script de exportación; `src/inferencia.py` quedó vacío (`ImportError`). Se movió y se restauró el script.
- `torch.rand` en lugar de `torch.randn`: ruido uniforme de 0 a 1 en vez de la normal con la que se entrenó. No da error; solo se nota en los mapas.
- Godot `error 7` (`ERR_FILE_NOT_FOUND`): `mapas/` quedó fuera de la carpeta del proyecto; `res://` apunta a la carpeta de `project.godot`.

### Pendiente
- Tabla de escala vertical por clase en Godot (llanura baja, montaña y volcán altas), ajustada a ojo.
- Probar sombras de la luz direccional.
- Confirmar en 3D que sigma = 2 no deja granulado visible.

Tag de cierre: `sprint-08`.
