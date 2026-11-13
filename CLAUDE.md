# Gaia-AI

IA local que genera terreno procedural (mapas de altura) con una cGAN entrenada con elevación real (SRTM). Proyecto de Fernando (Ingeniería en Sistemas, FIMAZ-UAS, Mazatlán) con equipo de 3, para Estructura de Datos y una expo de IA. Nació como herramienta de mapas para su juego "A Stupid RPG" (en pausa).

Repo: github.com/FernandoMoralesT/Gaia-AI · La v1.0 se hizo en 10 sprints. Desde la v1.0.1 se trabaja por versiones X.Y.Z hacia la v2.0 (`docs/ROADMAP_v2.md`).

## Navegación (leer primero)
- Para saber qué depende de qué, lee `docs/grafo.md` (lo genera `scrips/generar_grafo.py`).
- Ubica con grep/glob antes de abrir archivos completos.
- No leas `godot/` ni `docs/` salvo que la tarea lo pida. No leas todo el repo al iniciar.
- Para trabajo de la v2.0, lee `docs/ROADMAP_v2.md`, solo la versión en curso.
- La carpeta de scripts se llama `scrips` (sin "t").

## Estado actual
- v1.1.0 concluida (limpieza de inconsistencias y línea base). Tags: `sprint-05` a `sprint-10`, `v1.0`, `v1.0.1` y `v1.1.0` (este último sobre `main` al fusionar el PR). Hoy: 71 tests de Python y 10 pruebas headless de Godot. Rama base: `main`.
- En curso: v1.2.0 (dataset v3), rama `Rama1.2.0` (en GitHub). Estado al 12/11/2026:
  - Paso 1 hecho: decisiones de datos en `docs/dataset_v3_decisiones.md`.
  - Paso 2 hecho: 48 bloques descargados en `data/bloques/` (204 MB, fuera de git): 46 de 0.5° y 2 de referencia de 1.2° (R1, R2; nunca para entrenar). Coordenadas verificadas por Fernando. 0 pendientes. Detalle en la bitácora (v1.2.0) y en `docs/superpowers/plans/2026-11-12-bloques-v3.md`.
  - **Siguiente (paso 3):** recortar los bloques en tiles a 60 m/px (promedio 2×2), etiquetarlos con las 6 reglas (`UMBRALES_60`), resolver mar y depresiones, tiles de Paricutín y Colima con el cono centrado (de B22 y B23), y división por bloque con más de un tile por clase en validación y prueba. Plan primero y visto bueno de Fernando.
- Modelo del demo: época 150 (`modelos/generador_epoca150.pt`, versionado). Respaldo: época 100. No se sobrescribe; los modelos nuevos de la v2.0 se guardan aparte.
- Fuera de la v1.0: el PDF del proyecto (no es necesario para la expo).

## Versionado (desde la v1.0.1)
- X.Y.Z. X = cambio mayor tras testeo y verificación. Y = cambios medios (funcionalidades en prueba, depuración, optimización). Z = cambios menores (como la 1.0.1, solo gráficos del visor).
- Cada versión cierra con tests en verde, entrada en `docs/bitacora.md`, commit y tag `vX.Y.Z`.

## v2.0 (resumen; el detalle está en docs/ROADMAP_v2.md)
- Terrenos de uso general, pensados para que otros los usen como base.
- Tamaños de 64×64 a 2048×2048: accesos rápidos 64, 128, 512, 1024 y 2048, tamaño personalizado (múltiplo de 8) y mapas rectangulares. Un mapa más grande es más territorio, no el mismo con más detalle.
- Mundos con más de una clase (mapa de clases) y dos clases nuevas: cañón (id 6) y duna (id 7), agregadas al final de `CLASES`.
- Dataset v3, generador totalmente convolucional, entrenamiento que aproveche el CPU al máximo, exportación PNG16/OBJ/STL/GLB y visor integral con descarga.
- Decidido (12/11/2026): 60 m/px, criterio de 6 reglas a 60 m (`UMBRALES_60` en `scrips/analizar_dataset_v3.py`), cañón y duna aceptadas como hipótesis, y normalización relativa a la mediana del tile con S = 2500 m.

## v1.0: hecho
- Servidor local `src/servidor.py` (`127.0.0.1:8765`): `GET /salud` y `GET /terreno?clase=&semilla=&sigma=` (bytes del `.raw`; encabezados `X-Clase`, `X-Semilla`, `X-Sigma`). Compatible con `pythonw`.
- Visor en `godot/gaia-visor/`: `intro.tscn`, interfaz con selector de clase, semilla y suavizado, bloque sólido con escala vertical por clase, cámara orbital, sombras, F11, Salir y fondos animados. Chequea `/salud` cada 3 s; sin servidor usa `mapas/respaldo_<clase>.raw` (`scrips/generar_respaldos.py`).
- `dist/Gaia-AI-v1.0.exe` (ignorado en git) busca el repo y lanza/cierra el servidor con `pythonw`; requiere Python y dependencias instalados.
- `scrips/comparar_simplex.py` y `docs/comparacion_simplex.md`: cGAN contra Simplex y terreno real. `LICENSE` MIT, anteproyecto y `docs/release-v1.0.md`.
- Pruebas Godot: `godot --headless --path godot/gaia-visor -s res://pruebas/prueba_X.gd`.

## Stack
- Python 3.13 + PyTorch, CPU (GPU AMD Radeon, sin CUDA). numpy, rasterio, python-dotenv, scipy, psutil, pytest.
- Datos: SRTM GL1 (30 m) vía OpenTopography; clave en `.env` (fuera de git). Límite: 50 llamadas por 24 h; la descarga es reanudable.
- Visor: Godot 4.5.1, renderer Compatibility.

## Archivos clave
Mapa completo en `docs/grafo.md`. Los más usados:
- `src/dataset/dem_dataset.py`: `CLASES` (orden canónico, NUNCA reordenar) e `ID_CLASE`.
- `src/model/entrenar.py`: entrenamiento y `cargar_checkpoint()`.
- `src/inferencia.py`: `generar_terreno(clase, semilla, sigma=2)`, `suavizar`, `normalizar`, `exportar_raw`.
- `test/`: `python -m pytest test/`.
- `data/etiquetas.json`: fuente de verdad de las etiquetas por tile.
- `docs/bitacora.md`, `docs/dataset.md`: decisiones y razones.
- `salidas/`: historial, muestras y `checkpoints/epoca_NNN.pt` (solo local, gitignored).
- v1.2.0: `data/bloques.json` (manifiesto de bloques, fuente de verdad para volver a descargar), `scrips/descargar_bloques.py` (`--revisar` valida sin llamar a la API; `--ids B03,B15`; tope de 45, se detiene ante 401/429/5xx), `scrips/ver_bloque.py` (relieve sombreado; `--zona=oeste,sur,este,norte`; `--guardar`), `scrips/analizar_dataset_v3.py` (métricas por tile, reglas y normalización), `pedir_dem()` y `ErrorAPI` en `src/dataset/descargar_dem.py` (no filtra la clave).

## Modelo v1.0 (cGAN)
- 6 clases definidas por forma, no por metros: llanura, lomas, valle, montaña, meseta, volcán.
- Cada tile se normaliza por separado a [-1, 1]; mapas de 120×120 (90 m/píxel).
- Generador: ruido 100 + embedding de clase 10 → lineal a 128×15×15 → 3 ConvTranspose2d con BatchNorm y ReLU → Tanh. 3,361,501 parámetros.
- Discriminador: clase como canal extra; 3 Conv2d con LeakyReLU(0.2); sin Sigmoid (BCEWithLogitsLoss). 280,673 parámetros.
- Dataset: 60 tiles, división 80/10/10 por tile (seed 42), 6 variantes por tile; 288/36/36 muestras.
- Entrenamiento: 500 épocas, Adam, ~5 s por época, seed 42.

## Inferencia y visor
- `generar_terreno`: modelo en caché, `eval()`, `no_grad`, `torch.Generator` local. Devuelve `float32` de 120×120.
- `suavizar`: `gaussian_filter` con reescalado al min/max original; `sigma=0` = salida cruda.
- `exportar_raw`: min-max a [0, 1]; encabezado `<u4` (ancho, alto) y datos `<f4` fila por fila.
- Las alturas no son metros. Escala vertical en Godot: `escala_altura` (por clase) × `multiplicador_altura` (3). Luz a 25°, cámara a 30°.

## Hallazgos
- Línea base v1.1.0 (`docs/linea_base.md`, `scrips/medir_linea_base.py`): mediana de 4.93 s por época, ~7.9 núcleos de 16 lógicos (torch usa 8 hilos) y 0.75 GiB de RAM. Es el punto de comparación de la v1.5.0 (medir en las mismas condiciones).
- El discriminador domina desde la época ~189. Por pérdidas la zona sana es la 10–115; la 150 se eligió por criterio visual (100/150/200). Está en la bitácora.
- Clases débiles: lomas, montaña y meseta se parecen. Claras: volcán, valle y llanura.
- Dataset v3 (60 tiles v1 a 60 m): las 6 reglas coinciden en 51 de 60 (optimista: umbrales ajustados a esos tiles). Meseta es la débil (3 de 8); por eso el v3 trae más mesetas claras. La "posición del centro" separa valle (≤ 0.27) de montaña (≥ 0.42). Promediar pierde sobre todo pendiente (llanura conserva 58.7 % a 60 m y 38.4 % a 90 m).
- El método de cráter de la v1.0 (anillo de 360–1800 m alrededor del centro del tile) da 3 de 9 en cualquier escala: no ve cráteres pequeños ni descentrados.
- Cráter (9 volcanes reales a 120×120): solo 3 dan profundidad positiva clara (Nevado de Toluca, El Pinacate y Colima), 1 marginal (Ceboruco) y 5 sin cráter. El modelo genera un cono sin hueco; no es culpa del suavizado (con sigma 0 ya daba +0.025): es resolución y datos.

## Reglas del repo
- Nunca reordenar `CLASES` ni cambiar `data/etiquetas.json` sin anotarlo en la bitácora.
- Claves y tokens solo en `.env`; nunca en git.
- Dividir siempre por tile, no por muestra. Checkpoints numerados; nunca sobrescribir el modelo del demo.
- Una rama por integrante y PR a `main` con revisión. Commits `feat:`, `fix:`, `docs:`, `refactor:`, `test:`; sin comillas internas (PowerShell las rompe).
- Confirmar con Fernando antes de hacer push.
- Godot reescribe `project.godot` al abrir el editor; no es un cambio real.

## Rutina de cierre de versión
1. Tests en verde (`python -m pytest test/` y las pruebas headless de Godot).
2. `python scrips/generar_grafo.py`.
3. Entrada en `docs/bitacora.md` y estado actualizado en este archivo.
4. Commit y tag `vX.Y.Z`.

## Pendientes
- `salidas/historial.csv` (local): la fila de la época 500 tiene `0.22 58` en D y hace fallar `scrips/sanos.py`; falta el valor real.
- Visor (versión Z): F11 desde ventana maximizada vuelve a ventana; README y `export_presets` nombran `Gaia-AI.exe` y el vigente es `Gaia-AI-v1.0.exe`.
- v1.2.0, notas de la revisión de bloques: Pinacate fuera de B18; dunas dudosas en B19 (Samalayuca) y B30 (White Sands, 10–15 m de relieve); mar en B39 (Teide); mínimos bajo el nivel del mar en B18, B25, B29 y B39 (B44, Valle de la Muerte, es depresión real).
- v1.2.0, descarga diaria: Fernando planea una tarea cada 24 h; necesita coordenadas nuevas en `data/bloques.json` (hoy 0 pendientes). El 12/11/2026 se usaron 48 de 50 llamadas.
- v1.2.0, 7 pendientes menores de la revisión del descargador: al final del plan de bloques.
- PDF del proyecto (no necesario para la expo).

## Cómo trabajar con Fernando
- Responder en español.
- Modo mentoría (editable): explicar el porqué y guiar con preguntas antes de dar el código completo. Si pide la solución directa, dársela.
- Antes de cambios significativos, explicar qué y cómo y esperar su visto bueno.
- Es estudiante: evitar jerga innecesaria y explicar los términos técnicos la primera vez.
- En cada tarea cargar las skills `andrej-karpathy-skills:karpathy-guidelines` y la de superpowers que aplique (writing-plans, executing-plans con test-driven-development, verification-before-completion).
