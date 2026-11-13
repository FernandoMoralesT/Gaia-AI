"""Línea base del entrenamiento: tiempo por época, CPU, RAM y entorno.

No llama a entrenar(): esa función escribe salidas/historial.csv y checkpoints en cada época.
Usa paso_entrenamiento() lote a lote con los mismos hiperparámetros del entrenamiento real.

Uso (desde cualquier carpeta):
    python scrips/medir_linea_base.py --nota "condiciones" --salida docs/linea_base.md
"""
import statistics
import sys
import threading
import time
from pathlib import Path

import psutil
import torch
import torch.nn as nn

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
from model.discriminador import Discriminador  # noqa: E402
from model.entrenar import paso_entrenamiento  # noqa: E402
from model.generador import Generador  # noqa: E402

# Mismos valores que src/pipeline.py (entrenamiento real de la v1.0).
SEMILLA = 42
LR = 2e-4
BETAS = (0.5, 0.999)


def resumir_tiempos(tiempos):
    """El primer tiempo es el calentamiento; las estadísticas usan el resto."""
    medidos = tiempos[1:]
    if not medidos:
        raise ValueError("se necesita al menos una época medida además del calentamiento")
    return {
        "calentamiento": tiempos[0],
        "n": len(medidos),
        "media": statistics.mean(medidos),
        "mediana": statistics.median(medidos),
        "min": min(medidos),
        "max": max(medidos),
    }


def cpu_a_maquina(pct_proceso, nucleos_logicos):
    """psutil mide el proceso en % de un núcleo; dividido entre los núcleos da el % de la máquina."""
    return pct_proceso / nucleos_logicos


def cpu_a_nucleos(pct_proceso):
    """400 % de un núcleo equivale a 4 núcleos ocupados."""
    return pct_proceso / 100


class Muestreador:
    """Muestrea en un hilo aparte el CPU del proceso y del sistema, y la RAM (RSS) del proceso."""

    def __init__(self, intervalo=0.5):
        self.intervalo = intervalo
        self.proceso = psutil.Process()
        self._parar = threading.Event()
        self._cpu_proceso, self._cpu_sistema, self._rss = [], [], []

    def _muestra(self):
        self._cpu_proceso.append(self.proceso.cpu_percent(None))
        self._cpu_sistema.append(psutil.cpu_percent(None))
        self._rss.append(self.proceso.memory_info().rss)

    def _ciclo(self):
        while not self._parar.wait(self.intervalo):
            self._muestra()

    def iniciar(self):
        # La primera lectura de cpu_percent siempre da 0.0: solo marca el punto de partida.
        self.proceso.cpu_percent(None)
        psutil.cpu_percent(None)
        self._hilo = threading.Thread(target=self._ciclo, daemon=True)
        self._hilo.start()

    def detener(self):
        self._parar.set()
        self._hilo.join()
        self._muestra()  # al menos una muestra aunque el tramo dure menos que el intervalo
        return {
            "cpu_proceso": statistics.mean(self._cpu_proceso),
            "cpu_sistema": statistics.mean(self._cpu_sistema),
            "rss_max": max(self._rss),
            "muestras": len(self._rss),
        }


def medir_repeticion(loader, epocas):
    """Entrena `epocas` épocas lote a lote y devuelve (tiempos por época, recursos).

    El muestreo de CPU y RAM empieza después de la primera época (calentamiento).
    """
    torch.manual_seed(SEMILLA)
    g = Generador()
    d = Discriminador()
    criterio = nn.BCEWithLogitsLoss()
    opt_g = torch.optim.Adam(g.parameters(), lr=LR, betas=BETAS)
    opt_d = torch.optim.Adam(d.parameters(), lr=LR, betas=BETAS)

    tiempos = []
    muestreador = Muestreador()
    for epoca in range(epocas):
        if epoca == 1:
            muestreador.iniciar()
        inicio = time.perf_counter()
        for mapas, ids in loader:
            paso_entrenamiento(g, d, mapas, ids, criterio, opt_g, opt_d)
        tiempos.append(time.perf_counter() - inicio)
    return tiempos, muestreador.detener()
