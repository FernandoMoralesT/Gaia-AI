# Gaia-AI

IA local que genera terreno procedural (mapas de altura) con una cGAN entrenada con elevación real (SRTM). Proyecto de Fernando (Ingeniería en Sistemas, FIMAZ-UAS, Mazatlán) con equipo de 3, para Estructura de Datos y una expo de IA. Nació como herramienta de mapas para su juego "A Stupid RPG" (en pausa).

Repo: github.com/FernandoMoralesT/Gaia-AI
Plan: 10 sprints de 1 semana (reestructurado de 16 a 10 semanas).

## Estado actual
- Sprints 1 a 8: concluidos (último tag: `sprint-08`).
- Sprint 9: demo visual en Godot (siguiente). Sprint 10: documentación, PDF y v1.0.
- Modelo demo elegido: época 150 (`epoca_150.pt`), por criterio visual.

## Stack
- Python + PyTorch, entrenamiento en CPU (la GPU es AMD Radeon; no hay CUDA).
- numpy, rasterio (lectura de .tif SRTM), python-dotenv, scipy (suavizado), pytest (tests).
- Datos: SRTM GL1 (30 m) vía API globaldem de OpenTopography. La clave vive en `.env` (fuera de git).
- Visor 3D en Godot 4.5, renderer Compatibility, en `godot/gaia-visor/`.

## Archivos clave
- `src/dataset/dem_dataset.py`: dataset y `CLASES` (orden canónico, NUNCA reordenar).
- `src/model/entrenar.py`: ciclo de entrenamiento y `cargar_checkpoint()`.
- `src/inferencia.py`: `generar_terreno(clase, semilla, sigma=2)`, `suavizar`, `normalizar`, `exportar_raw`.
- `scrips/exportar_generador.py`: exporta solo el generador (la carpeta se llama `scrips`, sin "t").
- `test/test_inferencia.py`: 23 tests de pytest (`python -m pytest test/`).
- `godot/gaia-visor/`: `terreno.gd` (lee el `.raw` y arma la malla), `terreno.gdshader` (color por altura), `mundo.tscn`, `mapas/` (`.raw` de ejemplo, versionados).
- `data/etiquetas.json`: fuente de verdad de las etiquetas por tile.
- `docs/bitacora.md`, `docs/dataset.md`: decisiones y razones por sprint.
- `salidas/historial.csv`: curva de pérdida de 500 épocas (gitignored, solo local).
- `salidas/checkpoints/epoca_NNN.pt`: copias cada 50 épocas.
- `modelos/generador_epoca150.pt`: checkpoint solo-generador (~12.8 MB), versionado en git.

## Modelo (cGAN)
- 6 clases: llanura, lomas, valle, montaña, meseta, volcán (definidas por forma, no por metros).
- Cada tile se normaliza por separado a [-1, 1]. Mapas de 120×120.
- Generador: ruido (100) + clase (embedding de 10) → capa lineal a 128×15×15 → 3 bloques ConvTranspose2d (30, 60, 120 px) con BatchNorm y ReLU → Tanh. 3,361,501 parámetros.
- Discriminador: la clase entra como canal extra de 120×120; 3 Conv2d con LeakyReLU(0.2); sin Sigmoid porque se usa BCEWithLogitsLoss. 280,673 parámetros.
- Dataset: 60 tiles SRTM (0.1°), división estratificada 80/10/10 por tile (seed 42), augmentation de 6 variantes (original, 2 volteos, 3 rotaciones). 288/36/36 muestras.
- Entrenamiento: 500 épocas, Adam, ~5 s por época en CPU, seed 42.

## Resultados conocidos
- El discriminador domina desde la época ~189 (D final 0.226, G final 4.457).
- Por pérdidas (media móvil de 10 épocas) la zona sana va de la 10 a la ~115; la 150 queda fuera, pero se eligió por comparación visual (épocas 100/150/200). La 100 es el respaldo. La discrepancia está documentada en la bitácora.
- Débiles: lomas, montaña y meseta se parecen entre sí. Claros: volcán, valle y llanura.

## Inferencia y visor (Sprint 8)
- `generar_terreno`: modelo en caché, `eval()`, `no_grad`, ruido con `torch.Generator` local (no toca la semilla global). Devuelve `float32` 120×120.
- `suavizar`: `gaussian_filter` y reescalado al min/max original; `sigma=0` = salida cruda en [-1, 1].
- `exportar_raw`: normaliza min-max a [0, 1]; encabezado `<u4` (ancho, alto) + datos `<f4` fila por fila.
- Las alturas no son metros (normalización por tile). La escala vertical se decide en Godot: `escala_altura` (por clase) × `multiplicador_altura` (3).
- Escena: luz direccional a 25° de elevación, cámara a 30°.

## Reglas del repo
- Nunca reordenar `CLASES` ni cambiar `data/etiquetas.json` sin anotarlo en la bitácora.
- Cada sprint cierra con entrada en `docs/bitacora.md`, commit y tag `sprint-NN`.
- Claves y tokens solo en `.env`; nunca en git.
- Dividir siempre por tile, no por muestra, para evitar fuga de datos.
- Guardar checkpoints numerados; nunca sobrescribir el modelo demo.

## Pendientes sueltos
- 3 coordenadas de tiles manuales en `data/raw_v1/` (anteriores al Sprint 6) sin registrar.
- El anteproyecto `.docx` aún describe el enfoque anterior; falta actualizarlo al pivote cGAN.
- Visor: tabla de escala vertical por clase, sombras y confirmar en 3D que sigma = 2 no deja granulado.
- Mejora opcional de entrenamiento (frenar al discriminador, menor tasa de aprendizaje, label smoothing), solo si sobra tiempo tras el Sprint 10.

## Cómo trabajar con Fernando
- Responder en español.
- Modo mentoría (editable): explicar el porqué y guiar con preguntas antes de dar el código completo. Si pide la solución directa, dársela.
- Es estudiante: evitar jerga innecesaria y explicar los términos técnicos la primera vez.