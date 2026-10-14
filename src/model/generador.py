import torch
import torch.nn as nn


class Generador(nn.Module):
    def __init__(self, z_dim=100, n_clases=6, embed_dim=10, canales=128):
        super().__init__()
        self.canales = canales
        self.embed = nn.Embedding(n_clases, embed_dim)
        self.proyeccion = nn.Linear(z_dim + embed_dim, canales * 15 * 15)
        self.bloques = nn.Sequential(
            nn.ConvTranspose2d(canales, canales // 2, 4, 2, 1),  
            nn.BatchNorm2d(canales // 2),
            nn.ReLU(),
            nn.ConvTranspose2d(canales // 2, canales // 4, 4, 2, 1),  
            nn.BatchNorm2d(canales // 4),
            nn.ReLU(),
            nn.ConvTranspose2d(canales // 4, 1, 4, 2, 1),   
            nn.Tanh(),   
        )

    def forward(self, z, etiquetas):
        e = self.embed(etiquetas)            
        x = torch.cat([z, e], dim=1)         
        x = self.proyeccion(x)               
        x = x.view(-1, self.canales, 15, 15)
        return self.bloques(x)

