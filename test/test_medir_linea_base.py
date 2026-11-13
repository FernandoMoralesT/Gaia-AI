import sys
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scrips"))
from medir_linea_base import (  # noqa: E402
    Muestreador, armar_informe, cpu_a_maquina, cpu_a_nucleos, datos_entorno, main, medir_repeticion,
    resumir_tiempos,
)


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


def loader_falso():
    """2 lotes de 4 mapas aleatorios de 120x120, con el mismo DEMDataset del entrenamiento real."""
    from dataset.dem_dataset import DEMDataset
    from torch.utils.data import DataLoader
    rng = np.random.default_rng(0)
    mapas = [rng.uniform(-1, 1, (120, 120)) for _ in range(8)]
    return DataLoader(DEMDataset(mapas, [i % 6 for i in range(8)]), batch_size=4)


def test_medir_repeticion_no_escribe_archivos(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tiempos, recursos = medir_repeticion(loader_falso(), epocas=2)
    assert len(tiempos) == 2 and all(t > 0 for t in tiempos)
    assert recursos["muestras"] >= 1
    assert list(tmp_path.iterdir()) == []


def test_epocas_menor_que_2_es_error():
    with pytest.raises(SystemExit):
        main(["--epocas", "1"])


def test_informe_contiene_secciones():
    entorno = {k: "x" for k in ["cpu", "python", "torch", "numpy", "so", "commit", "fecha"]}
    entorno.update(nucleos_fisicos=8, nucleos_logicos=16, hilos_torch=8, hilos_interop=8, ram_total=16 * 2**30)
    recursos = {"cpu_proceso": 400.0, "cpu_sistema": 30.0, "rss_max": 2**30, "muestras": 10}
    texto = armar_informe(entorno, [([9.0, 5.0, 5.0], recursos)], None, "enchufada")
    assert "25.0 %" in texto and "4.00 núcleos" in texto
    assert "enchufada" in texto and "no disponible" in texto
    assert "python scrips/medir_linea_base.py" in texto


def test_datos_entorno_tiene_claves():
    e = datos_entorno()
    assert e["nucleos_logicos"] >= e["nucleos_fisicos"] >= 1
    assert e["hilos_torch"] >= 1 and e["commit"]
