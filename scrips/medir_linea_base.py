"""Línea base del entrenamiento: tiempo por época, CPU, RAM y entorno.

No llama a entrenar(): esa función escribe salidas/historial.csv y checkpoints en cada época.
Usa paso_entrenamiento() lote a lote con los mismos hiperparámetros del entrenamiento real.

Uso (desde cualquier carpeta):
    python scrips/medir_linea_base.py --nota "condiciones" --salida docs/linea_base.md
"""
import argparse
import os
import platform
import statistics
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import numpy as np
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
        self._cpu_proceso, self._cpu_sistema, self._rss, self._duracion = [], [], [], []

    def _muestra(self):
        ahora = time.perf_counter()
        self._duracion.append(ahora - self._anterior)  # cada muestra pesa lo que dura su ventana
        self._anterior = ahora
        self._cpu_proceso.append(self.proceso.cpu_percent(None))
        self._cpu_sistema.append(psutil.cpu_percent(None))
        self._rss.append(self.proceso.memory_info().rss)

    def _media_ponderada(self, valores):
        return sum(v * w for v, w in zip(valores, self._duracion)) / sum(self._duracion)

    def _ciclo(self):
        while not self._parar.wait(self.intervalo):
            self._muestra()

    def iniciar(self):
        # La primera lectura de cpu_percent siempre da 0.0: solo marca el punto de partida.
        self.proceso.cpu_percent(None)
        psutil.cpu_percent(None)
        self._anterior = time.perf_counter()
        self._hilo = threading.Thread(target=self._ciclo, daemon=True)
        self._hilo.start()

    def detener(self):
        self._parar.set()
        self._hilo.join()
        self._muestra()  # al menos una muestra aunque el tramo dure menos que el intervalo
        return {
            "cpu_proceso": self._media_ponderada(self._cpu_proceso),
            "cpu_sistema": self._media_ponderada(self._cpu_sistema),
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


def _nombre_cpu():
    if sys.platform == "win32":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as k:
                return winreg.QueryValueEx(k, "ProcessorNameString")[0].strip()
        except OSError:
            pass
    return platform.processor() or "desconocido"


def _commit():
    """Hash corto; con -dirty si hay cambios sin commit, para no atribuir el número a otro código."""
    try:
        h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ,
                           capture_output=True, text=True, check=True).stdout.strip()
        cambios = subprocess.run(["git", "status", "--porcelain"], cwd=RAIZ,
                                 capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconocido"
    return h + ("-dirty" if cambios else "")


def datos_entorno():
    return {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "commit": _commit(),
        "cpu": _nombre_cpu(),
        "nucleos_fisicos": psutil.cpu_count(logical=False),
        "nucleos_logicos": psutil.cpu_count(logical=True),
        "hilos_torch": torch.get_num_threads(),
        "hilos_interop": torch.get_num_interop_threads(),
        "ram_total": psutil.virtual_memory().total,
        "python": platform.python_version(),
        "torch": torch.__version__,
        "numpy": np.__version__,
        "so": platform.platform(),
    }


def _gib(n):
    return f"{n / 2**30:.2f} GiB"


def armar_informe(entorno, repeticiones, peak_wset, nota):
    """Informe en Markdown. `repeticiones` es una lista de (tiempos, recursos) de medir_repeticion()."""
    e = entorno
    epocas = len(repeticiones[0][0])
    nucleos = e["nucleos_logicos"]
    l = [
        "# Línea base del entrenamiento",
        "",
        "Generado por `scrips/medir_linea_base.py`. Todos los números salen de esta corrida.",
        "",
        "## Entorno",
        "",
        "| Dato | Valor |",
        "|---|---|",
        f"| Fecha | {e['fecha']} |",
        f"| Commit | `{e['commit']}` |",
        f"| CPU | {e['cpu']} |",
        f"| Núcleos físicos / lógicos | {e['nucleos_fisicos']} / {nucleos} |",
        f"| Hilos de torch (intra / interop) | {e['hilos_torch']} / {e['hilos_interop']} |",
        f"| RAM total | {_gib(e['ram_total'])} |",
        f"| Python / torch / numpy | {e['python']} / {e['torch']} / {e['numpy']} |",
        f"| Sistema operativo | {e['so']} |",
        "",
        "## Condiciones",
        "",
        nota or "(sin nota)",
        "",
        f"## Tiempo por época ({epocas} épocas por repetición: 1 de calentamiento y {epocas - 1} medidas)",
        "",
        "| Repetición | Calentamiento (s) | Media (s) | Mediana (s) | Mín. (s) | Máx. (s) |",
        "|---|---|---|---|---|---|",
    ]
    for i, (tiempos, _) in enumerate(repeticiones, 1):
        r = resumir_tiempos(tiempos)
        l.append(f"| {i} | {r['calentamiento']:.2f} | {r['media']:.2f} | {r['mediana']:.2f} | {r['min']:.2f} | {r['max']:.2f} |")
    todos = [t for tiempos, _ in repeticiones for t in tiempos[1:]]
    r = resumir_tiempos([None] + todos)
    l.append(f"| Todas ({r['n']} épocas) | — | {r['media']:.2f} | {r['mediana']:.2f} | {r['min']:.2f} | {r['max']:.2f} |")

    l += [
        "",
        "## CPU (durante las épocas medidas)",
        "",
        "| Repetición | Proceso (% de la máquina) | Proceso (núcleos equivalentes) | Sistema (%) | Muestras |",
        "|---|---|---|---|---|",
    ]
    for i, (_, rec) in enumerate(repeticiones, 1):
        l.append(f"| {i} | {cpu_a_maquina(rec['cpu_proceso'], nucleos):.1f} % | "
                 f"{cpu_a_nucleos(rec['cpu_proceso']):.2f} núcleos | {rec['cpu_sistema']:.1f} % | {rec['muestras']} |")
    l += [
        "",
        f"psutil mide el proceso en \"% de un núcleo\": 400 % son 4 núcleos ocupados. Dividido entre los "
        f"{nucleos} núcleos lógicos da el % de la máquina completa "
        f"(400 % en {nucleos} núcleos = {cpu_a_maquina(400, nucleos):.1f} %). "
        "El uso del sistema incluye a todos los programas: si es mucho mayor que el del proceso, "
        "había otros programas ocupando CPU.",
        "",
        "## RAM",
        "",
        f"- RSS máximo muestreado (épocas medidas): {_gib(max(rec['rss_max'] for _, rec in repeticiones))}",
        f"- Pico del proceso (`peak_wset`, toda la corrida, incluye la carga del dataset): "
        f"{_gib(peak_wset) if peak_wset is not None else 'no disponible'}",
        f"- RAM total de la máquina: {_gib(e['ram_total'])}",
        "",
        "## Qué se mide y qué no",
        "",
        "Se mide el ciclo de lotes de una época (cargar cada lote y `paso_entrenamiento()`), con los mismos "
        "hiperparámetros del entrenamiento real: lotes de 4, 72 lotes por época, Adam con lr 2e-4 y betas "
        "(0.5, 0.999), semilla 42. No se mide el guardado por época que hace `entrenar()` (historial, "
        "checkpoint y muestras), así que una época real de la v1.0 es un poco más lenta.",
        "",
        "## Cómo repetir",
        "",
        "```",
        f"python scrips/medir_linea_base.py --epocas {epocas} --repeticiones {len(repeticiones)} --nota \"...\"",
        "```",
        "",
    ]
    return "\n".join(l)


def _entero_minimo(minimo):
    def convertir(texto):
        n = int(texto)
        if n < minimo:
            raise argparse.ArgumentTypeError(f"debe ser al menos {minimo}")
        return n
    return convertir


def main(argv=None):
    parser = argparse.ArgumentParser(description="Mide la línea base del entrenamiento sin tocar salidas/.")
    parser.add_argument("--epocas", type=_entero_minimo(2), default=6,
                        help="épocas por repetición, incluida 1 de calentamiento (mínimo 2)")
    parser.add_argument("--repeticiones", type=_entero_minimo(1), default=3)
    parser.add_argument("--nota", default="", help="condiciones de la prueba")
    parser.add_argument("--salida", help="archivo Markdown, relativo a la raíz del repo; sin él solo imprime")
    args = parser.parse_args(argv)

    os.chdir(RAIZ)  # cargar_etiquetas() usa una ruta relativa a la raíz
    from pipeline import pipeline_dataset_dem
    loader_train, _, _ = pipeline_dataset_dem("data/raw", batch_size=4)
    if len(loader_train) != 72:
        sys.exit(f"se esperaban 72 lotes por época y hay {len(loader_train)}")

    entorno = datos_entorno()
    repeticiones = []
    for i in range(args.repeticiones):
        print(f"repetición {i + 1}/{args.repeticiones}...", file=sys.stderr)
        repeticiones.append(medir_repeticion(loader_train, args.epocas))
    peak_wset = getattr(psutil.Process().memory_info(), "peak_wset", None)

    informe = armar_informe(entorno, repeticiones, peak_wset, args.nota)
    print(informe)
    if args.salida:
        Path(args.salida).write_text(informe, encoding="utf-8")


if __name__ == "__main__":
    main()
