import sys
from pathlib import Path

# Raíz del repo cuando se corre como código normal (src/ está un nivel abajo)
RAIZ_REPO = Path(__file__).resolve().parent.parent


def ruta_recurso(relativa):
    """Ruta absoluta de un archivo de datos (por ejemplo el modelo).

    Congelado con PyInstaller, los datos viven en sys._MEIPASS
    (la carpeta _internal junto a gaia-servidor.exe). En desarrollo,
    en la raíz del repo. `relativa` es igual en los dos casos.
    """
    base = getattr(sys, "_MEIPASS", None)
    if base is None:
        return RAIZ_REPO / relativa
    return Path(base) / relativa
