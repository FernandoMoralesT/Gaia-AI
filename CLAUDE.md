# Gaia-AI

IA local que genera terreno procedural (mapas de altura) con una cGAN entrenada con elevación real (SRTM). Proyecto de Fernando (Ingeniería en Sistemas, FIMAZ-UAS, Mazatlán) con equipo de 3, para Estructura de Datos y una expo de IA. Nació como herramienta de mapas para su juego "A Stupid RPG" (en pausa).

Repo: github.com/FernandoMoralesT/Gaia-AI · La v1.0 se hizo en 10 sprints. Desde la v1.0.1 se trabaja por versiones X.Y.Z hacia la v2.0 (`ROADMAP_v2.md`).

## Navegación (leer primero)
- Para saber qué depende de qué, lee `docs/grafo.md` (lo genera `scrips/generar_grafo.py`).
- Ubica con grep/glob antes de abrir archivos completos.
- No leas `godot/` ni `docs/` salvo que la tarea lo pida. No leas todo el repo al iniciar.
- Para trabajo de la v2.0, lee `ROADMAP_v2.md` (raíz del repo), solo la versión en curso.
- La carpeta de scripts se llama `scrips` (sin "t").

## Estado actual
- v1.0.1 publicada. Tags: `sprint-05` a `sprint-10`, `v1.0` y `v1.0.1` (42 tests de Python y 10 pruebas headless de Godot). Rama base: `main`.
- En curso: v1.1.0 (limpieza de inconsistencias y línea base de rendimiento). Siguiente: v1.2.0 (dataset v3).
- Modelo del demo: época 150 (`modelos/generador_epoca150.pt`, versionado). Respaldo: época 100. No se sobrescribe; los modelos nuevos de la v2.0 se guardan aparte.
- Fuera de la v1.0: el PDF del proyecto (no es necesario para la expo).

## Versionado (desde la v1.0.1)
- X.Y.Z. X = cambio mayor tras testeo y verificación. Y = cambios medios (funcionalidades en prueba, depuración, optimización). Z = cambios menores (como la 1.0.1, solo gráficos del visor).
- Cada versión cierra con tests en verde, entrada en `docs/bitacora.md`, commit y tag `vX.Y.Z`.

## v2.0 (resumen; el detalle está en ROADMAP_v2.md)
- Terrenos de uso general, pensados para que otros los usen como base.
- Tamaños de 64×64 a 2048×2048: accesos rápidos 64, 128, 512, 1024 y 2048, tamaño personalizado (múltiplo de 8) y mapas rectangulares. Un mapa más grande es más territorio, no el mismo con más detalle.
- Mundos con más de una clase (mapa de clases) y dos clases nuevas: cañón (id 6) y duna (id 7), agregadas al final de `CLASES`.
- Dataset v3, generador totalmente convolucional, entrenamiento que aproveche el CPU al máximo, exportación PNG16/OBJ/STL/GLB y visor integral con descarga.
- Por decidir: escala 60 m/px (recomendada) o 90 m/px.

## v1.0: hecho
- Servidor local `src/servidor.py` (`127.0.0.1:8765`): `GET /salud` y `GET /terreno?clase=&semilla=&sigma=` (bytes del `.raw`; encabezados `X-Clase`, `X-Semilla`, `X-Sigma`). Compatible con `pythonw`.
- Visor en `godot/gaia-visor/`: `intro.tscn`, interfaz con selector de clase, semilla y suavizado, bloque sólido con escala vertical por clase, cámara orbital, sombras, F11, Salir y fondos animados. Chequea `/salud` cada 3 s; sin servidor usa `mapas/respaldo_<clase>.raw` (`scrips/generar_respaldos.py`).
- `dist/Gaia-AI-v1.0.exe` (ignorado en git) busca el repo y lanza/cierra el servidor con `pythonw`; requiere Python y dependencias instalados.
- `scrips/comparar_simplex.py` y `docs/comparacion_simplex.md`: cGAN contra Simplex y terreno real. `LICENSE` MIT, anteproyecto y `docs/release-v1.0.md`.
- Pruebas Godot: `godot --headless --path godot/gaia-visor -s res://pruebas/prueba_X.gd`.

## Stack
- Python 3.13 + PyTorch, CPU (GPU AMD Radeon, sin CUDA). numpy, rasterio, python-dotenv, scipy, pytest.
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
- El discriminador domina desde la época ~189. Por pérdidas la zona sana es la 10–115; la 150 se eligió por criterio visual (100/150/200). Está en la bitácora.
- Clases débiles: lomas, montaña y meseta se parecen. Claras: volcán, valle y llanura.
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
- v1.1.0, documentación: marcadores `[fecha]` y `[10/14/2026]` y la errata en `docs/dataset.md`; `preprocesamiento.py` en la bitácora del Sprint 4; llanura 10 y lomas 11 en la del Sprint 6 (son 9 y 12); "18 tests" en `grafo.md` (son 23); cuenta 260+170 en la bitácora y en `prueba_sombras.gd`.
- v1.1.0, código: import de `src.model.discriminador` en `pipeline.py`; `__main__` viejo de `cargar_dem.py`; `pandas` de `sanos.py` falta en `requirements.txt`; `notebooks/` vacío y 2 archivos versionados en `data/processed/`; restos `tempCodeRunnerFile.py` y `comprobacion_reduccion.py` (vacío).
- v1.1.0, línea base: segundos por época, % de CPU y RAM, con los datos de la máquina, en `docs/linea_base.md`.
- Visor (versión Z): F11 desde ventana maximizada vuelve a ventana; README y `export_presets` nombran `Gaia-AI.exe` y el vigente es `Gaia-AI-v1.0.exe`.
- Tiles de volcán donde el cono no domina el centro: Paricutín y Colima (v1.2.0).
- PDF del proyecto (no necesario para la expo).

## Cómo trabajar con Fernando
- Responder en español.
- Modo mentoría (editable): explicar el porqué y guiar con preguntas antes de dar el código completo. Si pide la solución directa, dársela.
- Antes de cambios significativos, explicar qué y cómo y esperar su visto bueno.
- Es estudiante: evitar jerga innecesaria y explicar los términos técnicos la primera vez.
