import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from rutas import ruta_recurso

MODELO = "modelos/generador_epoca150.pt"


def test_en_desarrollo_apunta_al_repo(monkeypatch):
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    ruta = ruta_recurso(MODELO)
    assert ruta == RAIZ / MODELO
    assert ruta.exists()


def test_congelado_apunta_a_meipass(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert ruta_recurso(MODELO) == tmp_path / MODELO
