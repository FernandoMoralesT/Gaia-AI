import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import torch
from model.generador import Generador
from model.discriminador import Discriminador
from model.entrenar import cargar_checkpoint

g = Generador()
d = Discriminador()
epoca = cargar_checkpoint(g, d, RAIZ / "salidas" / "checkpoints" / "epoca_150.pt")

destino = RAIZ / "modelos" / "generador_epoca150.pt"
destino.parent.mkdir(exist_ok=True)
torch.save(g.state_dict(), destino)

print(destino.stat().st_size / (1024*1024), "MB")