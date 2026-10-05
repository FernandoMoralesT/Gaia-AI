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
| 5 | Dataset final | En curso |
| 6-10 | Arquitectura, entrenamiento, inferencia local, demo y entrega | Pendiente |

El modelo generativo todavía no está entrenado. Hoy el repositorio contiene el generador clásico de ruido, la exportación a Godot y el pipeline de datos de elevación.

## Requisitos

- Python 3.13
- Dependencias de `requirements.txt`
- Godot 4 (solo para el visor 3D)
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

Ejecuta siempre desde la raíz del proyecto, con `pipeline.py` como único punto de entrada:

```powershell
python src/pipeline.py
```

Esto lee los `.tif` de `data/raw/`, divide los tiles en train/val/test (80/10/10), genera las variantes, recorta, normaliza y crea los `DataLoader`. Imprime el número de lotes de cada conjunto.

Para descargar un tile nuevo se usa `descargar_tile(south, north, west, east)` de `src/dataset/descargar_dem.py`. El archivo queda en `data/raw/` con el nombre `dem_{sur}_{norte}_{oeste}_{este}.tif`.

Visor en Godot: el script lee `heightmap.raw` con una ruta absoluta escrita en el código. Cada integrante debe ajustar esa ruta a su equipo.

## Estructura

```text
data/raw/        tiles originales (.tif)
data/processed/  salidas generadas (.raw, .npy), no versionadas
docs/            bitácora y documentación del dataset
notebooks/       exploración
scrips/          pruebas sueltas
src/noise/       generador clásico de ruido y exportación
src/dataset/     descarga, carga y preprocesamiento de elevación
src/model/       arquitectura del modelo (Sprint 6)
src/pipeline.py  punto de entrada
test/            pruebas
```

## Documentación

- [`docs/bitacora.md`](docs/bitacora.md): decisiones y problemas por sprint.
- [`docs/dataset.md`](docs/dataset.md): fuente, tiles, procesamiento y limitaciones del dataset.

## Datos

NASA SRTM GL1 (30 m), distribuido por OpenTopography. Cita:

NASA Shuttle Radar Topography Mission (SRTM). (2013). *Shuttle Radar Topography Mission (SRTM) Global* [Conjunto de datos]. OpenTopography. https://doi.org/10.5069/G9445JDF

La página del dataset muestra la licencia como no provista. Verificar los términos de uso antes de redistribuir los archivos.

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