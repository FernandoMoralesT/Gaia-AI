import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scrips"))
from medir_linea_base import Muestreador, cpu_a_maquina, cpu_a_nucleos, resumir_tiempos  # noqa: E402


def test_resumir_tiempos_separa_calentamiento():
    r = resumir_tiempos([9.0, 5.0, 4.0, 6.0, 5.0, 5.0])
    assert r["calentamiento"] == 9.0
    assert r["n"] == 5
    assert r["media"] == pytest.approx(5.0)
    assert r["mediana"] == 5.0
    assert (r["min"], r["max"]) == (4.0, 6.0)


def test_resumir_tiempos_exige_una_medida():
    with pytest.raises(ValueError):
        resumir_tiempos([9.0])


def test_cpu_maquina_y_nucleos():
    assert cpu_a_maquina(400.0, 16) == pytest.approx(25.0)
    assert cpu_a_nucleos(400.0) == pytest.approx(4.0)


def test_muestreador_toma_al_menos_una_muestra():
    m = Muestreador(intervalo=0.5)
    m.iniciar()
    sum(i * i for i in range(200_000))  # menos de 0.5 s de trabajo
    r = m.detener()
    assert r["muestras"] >= 1
    assert r["rss_max"] > 0
    assert r["cpu_proceso"] >= 0 and 0 <= r["cpu_sistema"] <= 100
