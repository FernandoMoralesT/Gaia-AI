"""Línea base del entrenamiento: tiempo por época, CPU, RAM y entorno.

No llama a entrenar(): esa función escribe salidas/historial.csv y checkpoints en cada época.
Usa paso_entrenamiento() lote a lote con los mismos hiperparámetros del entrenamiento real.

Uso (desde cualquier carpeta):
    python scrips/medir_linea_base.py --nota "condiciones" --salida docs/linea_base.md
"""
import statistics


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
