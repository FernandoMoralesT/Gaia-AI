import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from inferencia import generar_terreno, exportar_raw
from dataset.dem_dataset import CLASES

# Mapas que el visor usa si el servidor no responde.
# Nombres sin acentos para evitar problemas de rutas al exportar el .exe.
SEMILLA = 42
SIGMA = 2
DESTINO = RAIZ / "godot" / "gaia-visor" / "mapas"

def nombre_archivo(clase):
    return "respaldo_" + clase.replace("á", "a").replace("ñ", "n") + ".raw"

for clase in CLASES:
    ruta = exportar_raw(generar_terreno(clase, SEMILLA, SIGMA), DESTINO / nombre_archivo(clase))
    print(f"{clase:8s} -> {ruta.relative_to(RAIZ)}")
