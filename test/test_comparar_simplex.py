import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scrips"))
from comparar_simplex import mapa_simplex, rugosidad, variedad  # noqa: E402


def test_mapa_simplex_forma_tipo_y_rango():
    mapa = mapa_simplex(42)
    assert mapa.shape == (120, 120)
    assert mapa.dtype == np.float32
    assert mapa.min() == -1.0 and mapa.max() == 1.0


def test_mapa_simplex_depende_de_la_semilla():
    assert np.array_equal(mapa_simplex(7), mapa_simplex(7))
    assert not np.array_equal(mapa_simplex(7), mapa_simplex(8))


def test_rugosidad():
    assert rugosidad(np.zeros((4, 4))) == 0.0
    # 2 diferencias horizontales de 1 y 2 verticales de 0.
    assert rugosidad(np.array([[0.0, 1.0], [0.0, 1.0]])) == 0.5


def test_variedad():
    a = np.zeros((3, 3))
    assert variedad([a, a]) == 0.0
    assert variedad([a, np.ones((3, 3))]) == 1.0
