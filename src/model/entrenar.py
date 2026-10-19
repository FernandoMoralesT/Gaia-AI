import torch
import time
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dataset.dem_dataset import CLASES

def paso_entrenamiento(g, d, mapas, ids, criterio, opt_g, opt_d, z_dim=100):
    B = mapas.size(0)
    reales = torch.ones(B, 1)
    falsos = torch.zeros(B, 1)

    z = torch.randn(B, z_dim)
    falso = g(z, ids)
    perdida_d_real = criterio(d(mapas, ids), reales)
    perdida_d_falso = criterio(d(falso.detach(), ids), falsos)
    perdida_d = perdida_d_real + perdida_d_falso
    opt_d.zero_grad()
    perdida_d.backward()
    opt_d.step()

    perdida_g = criterio(d(falso, ids), reales)
    opt_g.zero_grad()
    perdida_g.backward()
    opt_g.step()

    return perdida_d.item(), perdida_g.item()

def entrenar(g, d, loader, epocas, criterio, opt_g, opt_d, z_dim = 100):
    historial = []
    ids_fijos = torch.arange(len(CLASES)).repeat_interleave(3)
    z_fijo = torch.randn(len(CLASES) * 3, z_dim)
    for epoca in range(epocas):
        inicio = time.perf_counter()
        suma_d, suma_g, n = 0.0, 0.0, 0
        for mapas, ids in loader:
            pd, pg = paso_entrenamiento(g, d, mapas, ids, criterio, opt_g, opt_d, z_dim)
            suma_d += pd
            suma_g += pg
            n += 1
        prom_d = suma_d/n
        prom_g = suma_g/n
        historial.append((prom_d, prom_g))
        print(f"epoca {epoca + 1}/{epocas} | D {prom_d:.3f} | G{prom_g:.3f} | {time.perf_counter()-inicio:.1f} s")
        if epoca == 0 or (epoca + 1) % 5 == 0:
            t = time.perf_counter()
            guardar_muestras(g, epoca + 1, z_fijo, ids_fijos)
            print(f"  muestras: {time.perf_counter() - t:.1f} s")
        t = time.perf_counter()
        guardar_checkpoint(g, d, opt_g, opt_d, epoca + 1)
        print(f"  checkpoint: {time.perf_counter() - t:.1f} s")
    return historial

def guardar_muestras(g, epoca, z_fijo, ids_fijos, carpeta="salidas/muestras"):
    os.makedirs(carpeta, exist_ok=True)
    g.eval()                              
    with torch.no_grad():
        mapas = g(z_fijo, ids_fijos)    
    g.train()                             

    fig, ejes = plt.subplots(len(CLASES), 3, figsize=(6, 12))
    for k in range(len(CLASES) * 3):
        eje = ejes[k // 3, k % 3]
        eje.imshow(mapas[k, 0].numpy(), cmap="terrain", vmin=-1, vmax=1)    
        eje.axis("off")
        if k % 3 == 0:
            eje.set_title(CLASES[k // 3], fontsize=8)
    fig.suptitle(f"Época {epoca}")
    fig.savefig(os.path.join(carpeta, f"epoca_{epoca:03d}.png"), dpi=80)
    plt.close(fig)


def guardar_checkpoint(g, d, opt_g, opt_d, epoca, ruta="salidas/checkpoints/ultimo.pt"):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    torch.save({
        "epoca": epoca,
        "g": g.state_dict(),
        "d": d.state_dict(),
        "opt_g": opt_g.state_dict(),
        "opt_d": opt_d.state_dict(),
        "clases": CLASES,
    }, ruta)