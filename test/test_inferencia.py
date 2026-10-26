import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import numpy as np
import pytest
import torch
from inferencia import (generar_terreno, normalizar, suavizar, exportar_raw,
                        _obtener_generador, RUTA_MODELO)
from dataset.dem_dataset import CLASES


# --- generar_terreno ---------------------------------------------------------

def test_forma_y_tipo():
    mapa = generar_terreno("volcán", 7)
    assert mapa.shape == (120, 120)
    assert mapa.dtype == np.float32


@pytest.mark.parametrize("clase", CLASES)
def test_todas_las_clases_generan(clase):
    mapa = generar_terreno(clase, 0)
    assert mapa.shape == (120, 120)
    assert np.isfinite(mapa).all()


def test_rango_crudo():
    mapa = generar_terreno("volcán", 7, sigma=0)
    assert mapa.min() >= -1.0
    assert mapa.max() <= 1.0


def test_misma_semilla_mismo_mapa():
    a = generar_terreno("volcán", 7)
    b = generar_terreno("volcán", 7)
    assert np.array_equal(a, b)


def test_semillas_distintas_mapas_distintos():
    a = generar_terreno("volcán", 7)
    b = generar_terreno("volcán", 8)
    assert not np.allclose(a, b)


def test_clases_distintas_mapas_distintos():
    # Si la clase se ignorara, misma semilla daría el mismo mapa.
    a = generar_terreno("volcán", 7)
    b = generar_terreno("llanura", 7)
    assert not np.allclose(a, b)


def test_clase_invalida():
    with pytest.raises(ValueError, match="montana"):
        generar_terreno("montana", 7)


def test_no_altera_semilla_global():
    torch.manual_seed(0)
    esperado = torch.rand(3)
    torch.manual_seed(0)
    generar_terreno("volcán", 7)
    assert torch.equal(torch.rand(3), esperado)


def test_suavizado_conserva_rango_del_crudo():
    crudo = generar_terreno("volcán", 42, sigma=0)
    suave = generar_terreno("volcán", 42, sigma=2)
    assert suave.min() == pytest.approx(crudo.min(), abs=1e-5)
    assert suave.max() == pytest.approx(crudo.max(), abs=1e-5)


# --- modelo ------------------------------------------------------------------

def test_modelo_en_eval_y_en_cache():
    g1 = _obtener_generador()
    g2 = _obtener_generador()
    assert g1 is g2
    assert not g1.training


def test_pesos_coinciden_con_checkpoint_150():
    ruta = RAIZ / "salidas" / "checkpoints" / "epoca_150.pt"
    if not ruta.exists():
        pytest.skip("epoca_150.pt solo existe en local (salidas/ está en .gitignore)")
    ckpt = torch.load(ruta, map_location="cpu", weights_only=True)
    exportado = torch.load(RUTA_MODELO, map_location="cpu", weights_only=True)
    assert exportado.keys() == ckpt["g"].keys()
    for k in exportado:
        assert torch.equal(exportado[k], ckpt["g"][k]), k


# --- normalizar ----------------------------------------------------------------

def test_normalizar_valores_conocidos():
    mapa = np.array([[2., 4.], [6., 8.]], dtype=np.float32)
    esperado = np.array([[0., 1/3], [2/3, 1.]], dtype=np.float32)
    assert np.allclose(normalizar(mapa), esperado)


def test_normalizar_mapa_plano():
    mapa = np.full((5, 5), 0.7, dtype=np.float32)
    resultado = normalizar(mapa)
    assert np.array_equal(resultado, np.zeros((5, 5)))
    assert resultado.dtype == np.float32


# --- suavizar ------------------------------------------------------------------

def test_suavizar_sigma_cero_no_cambia():
    mapa = np.random.default_rng(0).uniform(-1, 1, (20, 20)).astype(np.float32)
    assert suavizar(mapa, 0) is mapa


def test_suavizar_reduce_rugosidad_y_conserva_rango():
    mapa = np.random.default_rng(0).uniform(-1, 1, (40, 40)).astype(np.float32)
    suave = suavizar(mapa, 2)
    rugosidad = lambda m: np.abs(np.diff(m, axis=0)).mean()
    assert rugosidad(suave) < rugosidad(mapa)
    assert suave.min() == pytest.approx(mapa.min(), abs=1e-5)
    assert suave.max() == pytest.approx(mapa.max(), abs=1e-5)
    assert suave.dtype == np.float32


def test_suavizar_mapa_plano():
    mapa = np.full((10, 10), 0.3, dtype=np.float32)
    assert np.allclose(suavizar(mapa, 2), 0.3)


# --- exportar_raw --------------------------------------------------------------

def test_exportar_raw_formato(tmp_path):
    mapa = generar_terreno("volcán", 7)
    ruta = exportar_raw(mapa, tmp_path / "sub" / "volcan.raw")
    datos = ruta.read_bytes()
    assert len(datos) == 8 + 120 * 120 * 4
    assert list(np.frombuffer(datos[:8], "<u4")) == [120, 120]
    alturas = np.frombuffer(datos[8:], "<f4").reshape(120, 120)
    assert np.allclose(alturas, normalizar(mapa))
    assert alturas.min() == 0.0
    assert alturas.max() == 1.0


def test_exportar_raw_ancho_antes_que_alto(tmp_path):
    # Mapa no cuadrado: detecta si se invierten ancho y alto en el encabezado.
    mapa = np.arange(6, dtype=np.float32).reshape(2, 3)   # alto 2, ancho 3
    datos = exportar_raw(mapa, tmp_path / "rect.raw").read_bytes()
    assert list(np.frombuffer(datos[:8], "<u4")) == [3, 2]
    filas = np.frombuffer(datos[8:], "<f4").reshape(2, 3)
    assert np.allclose(filas, normalizar(mapa))
