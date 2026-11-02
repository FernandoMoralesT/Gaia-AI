import contextlib
import io
import itertools
import json
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from noise.Unificacion_Y_Exportacion import fractal_noise_2d
from dataset.procesamiento import reducir_tile, normalizar_tile

# Línea base del Sprint 3: 256x256 con scale 50. A 120 px se escala para
# conservar el tamaño de los rasgos respecto al mapa.
TAM = 120
ESCALA = 50.0 * TAM / 256
SEMILLAS = range(10)


def mapa_simplex(semilla, tam=TAM):
    # fractal_noise_2d imprime tiempos; se silencian.
    with contextlib.redirect_stdout(io.StringIO()):
        mapa, _ = fractal_noise_2d(tam, tam, ESCALA * tam / TAM, octaves=6, seed=semilla,
                                   persistence=0.5, lacunarity=1.5)
    return normalizar_tile(mapa)


def rugosidad(mapa):
    mapa = np.asarray(mapa, dtype=float)
    difs = np.concatenate([np.abs(np.diff(mapa, axis=0)).ravel(), np.abs(np.diff(mapa, axis=1)).ravel()])
    return float(difs.mean())


def variedad(mapas):
    pares = itertools.combinations(mapas, 2)
    return float(np.mean([np.abs(np.asarray(a, float) - np.asarray(b, float)).mean() for a, b in pares]))


def tiles_reales():
    import rasterio
    etiquetas = json.loads((RAIZ / "data" / "etiquetas.json").read_text(encoding="utf-8"))
    por_clase = {}
    for nombre, clase in etiquetas.items():
        with rasterio.open(RAIZ / "data" / "raw" / nombre) as tif:
            datos = tif.read(1).astype(np.float32)
        por_clase.setdefault(clase, []).append(normalizar_tile(reducir_tile(datos)))
    return por_clase


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from inferencia import generar_terreno
    from dataset.dem_dataset import CLASES

    reales = tiles_reales()
    simplex = [mapa_simplex(s) for s in SEMILLAS]
    filas = []
    for clase in CLASES:
        crudos = [generar_terreno(clase, s, sigma=0) for s in SEMILLAS]
        suaves = [generar_terreno(clase, s, sigma=2) for s in SEMILLAS]
        filas.append((clase, len(reales[clase]),
                      np.mean([rugosidad(m) for m in reales[clase]]), variedad(reales[clase]),
                      np.mean([rugosidad(m) for m in crudos]), np.mean([rugosidad(m) for m in suaves]),
                      variedad(suaves)))

    print("| Generador | Rugosidad | Variedad entre semillas |")
    print("| --- | --- | --- |")
    print(f"| Simplex (Sprint 3, sin clase) | {np.mean([rugosidad(m) for m in simplex]):.4f} | {variedad(simplex):.3f} |")
    print()
    print("| Clase | Tiles reales | Rugosidad real | cGAN σ=0 | cGAN σ=2 | Variedad real | Variedad cGAN σ=2 |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for clase, n, r_real, v_real, r_crudo, r_suave, v_suave in filas:
        print(f"| {clase} | {n} | {r_real:.4f} | {r_crudo:.4f} | {r_suave:.4f} | {v_real:.3f} | {v_suave:.3f} |")

    # Figura: Simplex, cGAN y real lado a lado.
    clases_fig = ["volcán", "valle", "montaña"]
    fig, ejes = plt.subplots(3, 3, figsize=(9, 9.6))
    paneles = [[(simplex[i], f"Simplex, semilla {i}") for i in range(3)],
               [(generar_terreno(c, 42, sigma=2), f"cGAN: {c}") for c in clases_fig],
               [(reales[c][0], f"Real: {c}") for c in clases_fig]]
    for fila, contenido in zip(ejes, paneles):
        for eje, (mapa, titulo) in zip(fila, contenido):
            eje.imshow(mapa, cmap="terrain", vmin=-1, vmax=1)
            eje.set_title(titulo, fontsize=10)
            eje.axis("off")
    fig.tight_layout()
    destino = RAIZ / "docs" / "img" / "comparacion_simplex.png"
    fig.savefig(destino, dpi=110)
    print(f"figura -> {destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
