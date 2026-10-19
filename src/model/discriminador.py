import torch
import torch.nn as nn


class Discriminador(nn.Module):
    def __init__(self, n_clases=6, tam=120, canales=32):
        super().__init__()
        self.tam = tam
        self.embed = nn.Embedding(n_clases, tam * tam)   # la clase como una hoja de 120×120
        self.bloques = nn.Sequential(
            nn.Conv2d(2, canales, 4, 2, 1),               # 120 -> 60   (2 -> 32)
            nn.LeakyReLU(0.2),
            nn.Conv2d(canales, canales*2,4, 2, 1),                                          # 60 -> 30: ¿qué canales de entrada y salida?
            nn.BatchNorm2d(canales * 2),
            nn.LeakyReLU(0.2),
            nn.Conv2d(canales*2, canales*4, 4, 2, 1),                                          # 30 -> 15: duplica los canales otra vez
            nn.BatchNorm2d(canales * 4),
            nn.LeakyReLU(0.2),
        )
        self.salida = nn.Linear(canales* 4* 15* 15, 1)                   # ¿cuántos números salen de las capas?

    def forward(self, mapa, etiquetas):
        e = self.embed(etiquetas)                         # (B, 120*120)
        e = e.view(-1, 1, self.tam, self.tam)             # (B, 1, 120, 120)
        x = torch.cat([mapa, e], dim=1)                   # (B, 2, 120, 120)
        x = self.bloques(x)                               # (B, 128, 15, 15)
        x = x.view(x.size(0), -1)                         # (B, 128 * 15 * 15)
        return self.salida(x)                             # (B, 1)