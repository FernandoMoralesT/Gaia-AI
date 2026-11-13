"""Muestra un bloque de data/bloques/ con relieve sombreado, para revisarlo a ojo.

Igual que ver_tile.py (colormap terrain y barra en metros), más el sombreado y los ejes en grados.

Uso:
    python scrips/ver_bloque.py B15                    # por id del manifiesto
    python scrips/ver_bloque.py data/bloques/x.tif     # por ruta
    python scrips/ver_bloque.py B15 --guardar b15.png  # guarda el PNG en lugar de abrir la ventana
"""
import argparse
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LightSource, Normalize

RAIZ = Path(__file__).resolve().parent.parent
NODATA = -32768


def figura_bloque(ruta, titulo):
    with rasterio.open(ruta) as src:
        z = src.read(1).astype(np.float64)
        b = src.bounds
        rx, ry = src.res
    hueco = z == NODATA
    if hueco.any():
        z[hueco] = z[~hueco].min()  # el sombreado no acepta huecos; el % de nodata lo reporta la verificación
    lat = math.radians((b.bottom + b.top) / 2)
    dy, dx = ry * 111_320, rx * 111_320 * math.cos(lat)  # metros por píxel, para que la pendiente sea real
    norma = Normalize(z.min(), z.max())
    rgb = LightSource(azdeg=315, altdeg=45).shade(z, cmap=plt.cm.terrain, norm=norma, blend_mode="soft",
                                                  vert_exag=1, dx=dx, dy=dy)
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.imshow(rgb, extent=(b.left, b.right, b.bottom, b.top))
    fig.colorbar(ScalarMappable(norm=norma, cmap=plt.cm.terrain), ax=ax, label="Elevación (m)")
    ax.set_title(titulo)
    ax.set_xlabel("Longitud (°)")
    ax.set_ylabel("Latitud (°)")
    return fig


def main(argv=None):
    p = argparse.ArgumentParser(description="Muestra un bloque con relieve sombreado.")
    p.add_argument("bloque", help="id del manifiesto (B15) o ruta a un .tif")
    p.add_argument("--guardar", help="ruta del PNG; sin esto abre la ventana")
    args = p.parse_args(argv)

    ruta, titulo = Path(args.bloque), args.bloque
    if not ruta.suffix:
        sys.path.insert(0, str(RAIZ / "scrips"))
        from descargar_bloques import CARPETA, RUTA_MANIFIESTO, cargar_manifiesto, nombre_bloque
        b = next(x for x in cargar_manifiesto(RUTA_MANIFIESTO)["bloques"] if x["id"] == args.bloque)
        ruta = CARPETA / nombre_bloque(b["sur"], b["norte"], b["oeste"], b["este"])
        titulo = f"{b['id']} · {b['sitio']} · esperado: {', '.join(b['clases_esperadas'])}"
    fig = figura_bloque(ruta, titulo)
    if args.guardar:
        fig.savefig(args.guardar, dpi=90, bbox_inches="tight")
    else:
        plt.show()


if __name__ == "__main__":
    main()
