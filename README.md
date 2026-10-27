# Gaia-AI

IA de ejecución local que genera terreno de forma procedural (mapas de altura), entrenada con elevación real. Proyecto para la materia de Estructura de Datos (FIMAZ-UAS) y para la expo de IA de las facultades de tecnología.

## Estado

Desarrollo con Scrum, 1 sprint por semana, 10 sprints en total.

| Sprint | Tema | Estado |
| --- | --- | --- |
| 1 | Ruido base | Concluido |
| 2 | Normalización y biomas | Concluido |
| 3 | Pipeline unificado y exportación a Godot | Concluido |
| 4 | Entorno PyTorch y datos reales | Concluido |
| 5 | Dataset final | Concluido |
| 6 | Arquitectura cGAN | Concluido |
| 7 | Entrenamiento y selección del checkpoint | Concluido |
| 8 | Inferencia local, postprocesado y visor en Godot | Concluido |
| 9 | Demo visual en Godot | Concluido |
| 10 | Documentación y entrega (v1.0) | Pendiente |

El modelo es una GAN condicional (cGAN) entrenada con 60 tiles SRTM en 6 clases de terreno: llanura, lomas, valle, montaña, meseta y volcán. El modelo del demo es el generador de la época 150 (`modelos/generador_epoca150.pt`), incluido en el repositorio.

## Requisitos

- Python 3.13
- Dependencias de `requirements.txt`
- Godot 4.5.1 (visor 3D); para crear el `.exe`, sus plantillas de exportación (*Editor → Manage Export Templates*)
- Cuenta en OpenTopography y su clave de API (solo para descargar tiles nuevos)

## Instalación

```powershell
git clone https://github.com/FernandoMoralesT/Gaia-AI.git
cd Gaia-AI
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crea en la raíz un archivo `.env` con tu clave. Cada integrante crea el suyo; el archivo no se versiona.

```text
OPENTOPO_API_KEY=tu_clave
```

Si `rasterio` falla al instalar en Windows, avisa en el equipo antes de seguir.

## Uso

Ejecuta siempre desde la raíz del proyecto.

### Dataset

`pipeline.py` es el punto de entrada del dataset:

```powershell
python src/pipeline.py
```

Esto lee los `.tif` de `data/raw/`, divide los tiles en train/val/test (80/10/10), genera las variantes, recorta, normaliza y crea los `DataLoader`. Imprime el número de lotes de cada conjunto.

Para descargar un tile nuevo se usa `descargar_tile(south, north, west, east)` de `src/dataset/descargar_dem.py`. El archivo queda en `data/raw/` con el nombre `dem_{sur}_{norte}_{oeste}_{este}.tif`.

### Generar terreno

```python
from inferencia import generar_terreno, exportar_raw   # con src/ en sys.path

mapa = generar_terreno("volcán", semilla=42)            # numpy float32 de 120×120
exportar_raw(mapa, "godot/gaia-visor/mapas/volcan_42.raw")
```

- `clase`: una de `llanura`, `lomas`, `valle`, `montaña`, `meseta`, `volcán`.
- `semilla`: la misma semilla da siempre el mismo mapa.
- `sigma` (opcional, 2 por defecto): suavizado gaussiano; `sigma=0` devuelve la salida cruda del modelo, de -1 a 1.
- `exportar_raw` normaliza a [0, 1] y escribe el formato del visor: `width` y `height` (`uint32`) y luego los datos (`float32`), little-endian.

Las alturas no están en metros: cada tile se normalizó por separado, así que la red aprende la forma y no la altura real. La escala vertical se ajusta en el visor.

### Servidor local

```powershell
python src/servidor.py
```

Escucha solo en `127.0.0.1:8765`:

- `GET /salud`: responde `{"estado": "ok"}`.
- `GET /terreno?clase=&semilla=&sigma=`: devuelve los bytes del `.raw`. Si falta `semilla`, se elige una al azar; la clase, la semilla y el sigma usados van en los encabezados `X-Clase`, `X-Semilla` y `X-Sigma`.

### Visor en Godot

1. Abre `godot/gaia-visor/project.godot` con Godot 4.5.1 y ejecuta el proyecto (F5). Empieza en la intro, con el menú *Explorar terrenos*, *Cómo funciona Gaia* y *Acerca de nosotros*.
2. Al abrirse, el visor enciende el servidor local si encuentra el repo y Python, y lo apaga al cerrar. Sin servidor, usa los mapas guardados de `mapas/respaldo_<clase>.raw` (se regeneran con `python scrips/generar_respaldos.py`).
3. Controles: W A S D o flechas para girar, rueda del mouse o Q y E para acercar y alejar, Esc para volver al menú.

### Demo (.exe)

Desde Godot o en terminal:

```powershell
godot --headless --path godot/gaia-visor --export-release "Windows Desktop" ../../dist/Gaia-AI.exe
```

`dist/Gaia-AI.exe` no se versiona. Debe quedarse dentro del repo (en `dist/`) para encontrar `src/servidor.py`, y necesita Python con las dependencias instaladas. Si se mueve a otra carpeta, funciona solo con los mapas guardados.

### Tests

```powershell
python -m pytest test/ -v
```

Pruebas del visor (una por archivo de `godot/gaia-visor/pruebas/`):

```powershell
godot --headless --path godot/gaia-visor -s res://pruebas/prueba_bloque.gd
```

## Estructura

```text
data/raw/        tiles originales (.tif)
data/processed/  salidas generadas (.raw, .npy), no versionadas
dist/            Gaia-AI.exe exportado (no versionado)
docs/            bitácora y documentación del dataset
godot/gaia-visor proyecto de Godot: intro, visor 3D, mapas de respaldo y pruebas
modelos/         generador exportado para inferencia (época 150)
notebooks/       exploración
salidas/         historial, muestras y checkpoints del entrenamiento (no versionado)
scrips/          scripts sueltos (exportar_generador.py, generar_respaldos.py, revisiones del dataset)
src/noise/       generador clásico de ruido y exportación (Sprints 1-3)
src/dataset/     descarga, carga y preprocesamiento de elevación
src/model/       generador, discriminador y entrenamiento de la cGAN
src/inferencia.py  generar_terreno, suavizado y exportación .raw
src/servidor.py  servidor local para la generación en vivo
src/pipeline.py  punto de entrada del dataset
test/            pruebas (pytest)
```

## Documentación

- [`docs/bitacora.md`](docs/bitacora.md): decisiones y problemas por sprint.
- [`docs/dataset.md`](docs/dataset.md): fuente, tiles, procesamiento y limitaciones del dataset.

## Datos

NASA SRTM GL1 (30 m), distribuido por OpenTopography. Cita:

NASA Shuttle Radar Topography Mission (SRTM). (2013). *Shuttle Radar Topography Mission (SRTM) Global* [Conjunto de datos]. OpenTopography. https://doi.org/10.5069/G9445JDF

https://opentopography.org/usageterms

## Equipo

- Aguillon Peinado Sebastian
- Garcia Mendoza Cristoff Salvador
- Morales Toledo Luis Fernando

## Flujo de trabajo

- Una rama por integrante y Pull Request hacia `main`, con revisión de otro integrante.
- Commits con el formato `feat:`, `fix:`, `docs:`, `refactor:`, `test:`.
- Un tag por sprint al cerrarlo: `sprint-01`, `sprint-02`, etc.

## Licencia

[Por definir]