import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import numpy as np
import torch
from scipy.ndimage import gaussian_filter
from model.generador import Generador
from dataset.dem_dataset import ID_CLASE

RUTA_MODELO = RAIZ / "modelos" / "generador_epoca150.pt"
Z_DIM = 100

_generador = None

def _obtener_generador():
    global _generador
    if _generador is None:
        g = Generador()
        estado = torch.load(RUTA_MODELO, map_location="cpu", weights_only=True)
        g.load_state_dict(estado)
        g.eval()
        _generador=g
    return _generador

def normalizar(mapa):
    minimo, maximo = mapa.min(), mapa.max()
    if maximo - minimo < 1e-6:
        return np.zeros_like(mapa)
    return (mapa - minimo) / (maximo - minimo)

def suavizar(mapa, sigma):
    if sigma <= 0:
        return mapa
    minimo, maximo = mapa.min(), mapa.max()
    suave = gaussian_filter(mapa, sigma=sigma)
    s_min, s_max = suave.min(), suave.max()
    if s_max - s_min < 1e-6:
        return suave
    return (suave - s_min) / (s_max - s_min) * (maximo - minimo) + minimo

def generar_terreno(clase, semilla, sigma=2):
    if clase not in ID_CLASE:
        raise ValueError(f"Clase desconocida: {clase!r}. Validas: {list(ID_CLASE)}")
    id_clase = torch.tensor([ID_CLASE[clase]])
    gen = torch.Generator().manual_seed(semilla)
    z = torch.randn(1, Z_DIM, generator=gen)

    g = _obtener_generador()
    with torch.no_grad():
        salida = g(z, id_clase)
    return suavizar(salida.squeeze().numpy(), sigma)

def raw_a_bytes(mapa):
    mapa = normalizar(mapa)
    alto, ancho = mapa.shape
    encabezado = np.array([ancho, alto], dtype="<u4").tobytes()
    return encabezado + mapa.astype("<f4").tobytes()

def exportar_raw(mapa, ruta):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(raw_a_bytes(mapa))
    return ruta
