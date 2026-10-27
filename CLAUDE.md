# Gaia-AI

IA local que genera terreno procedural (mapas de altura) con una cGAN entrenada con elevación real (SRTM). Proyecto de Fernando (Ingeniería en Sistemas, FIMAZ-UAS, Mazatlán) con equipo de 3, para Estructura de Datos y una expo de IA. Nació como herramienta de mapas para su juego "A Stupid RPG" (en pausa).

Repo: github.com/FernandoMoralesT/Gaia-AI · Plan: 10 sprints de 1 semana.

## Navegación (leer primero)
- Para saber qué depende de qué, lee `docs/grafo.md` (lo genera `scrips/generar_grafo.py`).
- Ubica con grep/glob antes de abrir archivos completos.
- No leas `godot/` ni `docs/` salvo que la tarea lo pida. No leas todo el repo al iniciar.
- La carpeta de scripts se llama `scrips` (sin "t").

## Estado actual
- Sprints 1 a 9 concluidos. Último tag: `sprint-09` (demo en Godot con generación en vivo, 37 tests de Python y 6 pruebas headless). Rama de trabajo: `visor-expo` (sin fusionar a `main`).
- Sprint 10 pendiente: documentación, PDF y v1.0.
- Modelo del demo: época 150 (`modelos/generador_epoca150.pt`, versionado). Respaldo: época 100.

## Sprint 9: hecho
- Servidor local `src/servidor.py` (`127.0.0.1:8765`): `GET /salud` y `GET /terreno?clase=&semilla=&sigma=` (bytes del `.raw`; semilla aleatoria si falta; encabezados `X-Clase`, `X-Semilla`, `X-Sigma`). Compatible con `pythonw`.
- Visor: escena principal `intro.tscn` (título, menú, info, acerca de), interfaz con selector de clase, semilla y suavizado, botón Inspeccionar, bloque sólido con escala vertical por clase, cámara orbital (WASD/flechas, zoom con rueda o Q/E) y fondo "espacio latente". Chequeo de `/salud` cada 3 s; sin servidor usa `mapas/respaldo_<clase>.raw` (`scrips/generar_respaldos.py`).
- `dist/Gaia-AI.exe` (ignorado en git) busca el repo y lanza/cierra el servidor con `pythonw`; requiere Python y dependencias instalados. Reemplaza a `iniciar_demo.bat`.
- Pruebas Godot: `godot --headless --path godot/gaia-visor -s res://pruebas/prueba_X.gd`.

## Stack
- Python + PyTorch, CPU (GPU AMD Radeon, sin CUDA). numpy, rasterio, python-dotenv, scipy, pytest.
- Datos: SRTM GL1 (30 m) vía OpenTopography; la clave vive en `.env` (fuera de git).
- Visor: Godot 4.5, renderer Compatibility, en `godot/gaia-visor/`.

## Archivos clave
Mapa completo en `docs/grafo.md`. Los más usados:
- `src/dataset/dem_dataset.py`: `CLASES` (orden canónico, NUNCA reordenar) e `ID_CLASE`.
- `src/model/entrenar.py`: entrenamiento y `cargar_checkpoint()`.
- `src/inferencia.py`: `generar_terreno(clase, semilla, sigma=2)`, `suavizar`, `normalizar`, `exportar_raw`.
- `test/test_inferencia.py`: `python -m pytest test/`.
- `data/etiquetas.json`: fuente de verdad de las etiquetas por tile.
- `docs/bitacora.md`, `docs/dataset.md`: decisiones y razones por sprint.
- `salidas/`: historial, muestras y `checkpoints/epoca_NNN.pt` (solo local, gitignored).

## Modelo (cGAN)
- 6 clases definidas por forma, no por metros: llanura, lomas, valle, montaña, meseta, volcán.
- Cada tile se normaliza por separado a [-1, 1]; mapas de 120×120 (90 m/píxel).
- Generador: ruido 100 + embedding de clase 10 → lineal a 128×15×15 → 3 ConvTranspose2d con BatchNorm y ReLU → Tanh. 3,361,501 parámetros.
- Discriminador: clase como canal extra; 3 Conv2d con LeakyReLU(0.2); sin Sigmoid (BCEWithLogitsLoss). 280,673 parámetros.
- Dataset: 60 tiles, división 80/10/10 por tile (seed 42), 6 variantes por tile; 288/36/36 muestras.
- Entrenamiento: 500 épocas, Adam, ~5 s por época, seed 42.

## Inferencia y visor
- `generar_terreno`: modelo en caché, `eval()`, `no_grad`, `torch.Generator` local (no toca la semilla global). Devuelve `float32` de 120×120.
- `suavizar`: `gaussian_filter` con reescalado al min/max original; `sigma=0` = salida cruda.
- `exportar_raw`: min-max a [0, 1]; encabezado `<u4` (ancho, alto) y datos `<f4` fila por fila.
- Las alturas no son metros. Escala vertical en Godot: `escala_altura` (por clase) × `multiplicador_altura` (3). Luz a 25°, cámara a 30°.

## Hallazgos
- El discriminador domina desde la época ~189. Por pérdidas, la zona sana es la 10–115; la 150 se eligió por criterio visual (comparando 100/150/200). La discrepancia está en la bitácora.
- Clases débiles: lomas, montaña y meseta se parecen. Claras: volcán, valle y llanura.
- Cráter (medido en los 9 volcanes reales a 120×120): solo 3 dan profundidad positiva clara (Nevado de Toluca, El Pinacate y Colima), 1 es marginal (Ceboruco) y 5 no muestran cráter. En Colima la cima está a 60 px del centro, así que su valor puede venir de la ladera. El modelo genera un cono sin hueco. El suavizado no es la causa (con sigma 0 ya daba +0.025): es una limitación de resolución y de datos.

## Reglas del repo
- Nunca reordenar `CLASES` ni cambiar `data/etiquetas.json` sin anotarlo en la bitácora.
- Claves y tokens solo en `.env`; nunca en git.
- Dividir siempre por tile, no por muestra.
- Checkpoints numerados; nunca sobrescribir el modelo del demo.
- Mensajes de commit sin comillas internas (PowerShell los rompe).

## Rutina de cierre de sprint
1. `python scrips/generar_grafo.py`.
2. Entrada en `docs/bitacora.md` y estado actualizado en este archivo.
3. Commit y tag `sprint-NN`.

## Pendientes sueltos
- 3 tiles manuales en `data/raw_v1/` sin coordenadas registradas.
- El anteproyecto `.docx` aún describe el enfoque anterior al pivote cGAN.
- Visor: sombras, confirmar en 3D que sigma = 2 no deja granulado.
- Tiles de volcán donde el cono no domina el centro: Paricutín y Colima.
- Mejora opcional de entrenamiento (frenar al discriminador, menor tasa, label smoothing), solo si sobra tiempo tras el Sprint 10.

## Cómo trabajar con Fernando
- Responder en español.
- Modo mentoría (editable): explicar el porqué y guiar con preguntas antes de dar el código completo. Si pide la solución directa, dársela.
- Es estudiante: evitar jerga innecesaria y explicar los términos técnicos la primera vez.
