"""Zona sana del entrenamiento: medias móviles de 10 épocas de las pérdidas D y G.

Antes usaba pandas; se reescribió con csv y numpy para no sumar esa dependencia.
"""
import csv

import numpy as np

with open("salidas/historial.csv", encoding="utf-8") as f:
    filas = list(csv.DictReader(f))
epoca = np.array([int(r["epoca"]) for r in filas])
d = np.array([float(r["D"]) for r in filas])
g = np.array([float(r["G"]) for r in filas])


def movil(x, ventana=10):
    """Media y desviación (ddof=1, como pandas) de las últimas `ventana` épocas; NaN en las primeras."""
    v = np.lib.stride_tricks.sliding_window_view(x, ventana)
    relleno = np.full(ventana - 1, np.nan)
    return np.concatenate([relleno, v.mean(axis=1)]), np.concatenate([relleno, v.std(axis=1, ddof=1)])


d_media, d_std = movil(d)
g_media, _ = movil(g)


def imprimir(mascara):
    print(f"{'epoca':>5} {'D_media':>9} {'G_media':>9} {'D_std':>9}")
    for i in np.flatnonzero(mascara):
        print(f"{epoca[i]:>5} {d_media[i]:9.6f} {g_media[i]:9.6f} {d_std[i]:9.6f}")


imprimir((d_media > 1.0) & (g_media < 2.5))  # NaN compara como False, igual que en pandas
imprimir((epoca >= 145) & (epoca <= 155))
