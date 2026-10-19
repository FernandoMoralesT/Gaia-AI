import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import torch
from model.generador import Generador
from model.discriminador import Discriminador
from model.entrenar import cargar_checkpoint, guardar_muestras
from dataset.dem_dataset import CLASES
import torch

g = Generador()
d = Discriminador()
ids_fijos =torch.arange(len(CLASES)).repeat_interleave(3)
z_fijo = torch.randn(len(CLASES)*3, 100)
epoca = cargar_checkpoint(g, d, "salidas/checkpoints/epoca_100.pt")
print(epoca)
g.eval()
guardar_muestras(g, epoca, z_fijo, ids_fijos, carpeta="salidas/pruebas")