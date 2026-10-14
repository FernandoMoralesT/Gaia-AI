from torch.utils.data import Dataset
import torch

CLASES = ["llanura", "lomas", "valle", "montaña", "meseta", "volcán"]
ID_CLASE = {nombre: i for i, nombre in enumerate(CLASES)}

class DEMDataset(Dataset):
    def __init__(self, heightmaps, clases):
        self.heightmaps = heightmaps
        self.clases = clases

    def __len__(self):
        return len(self.heightmaps)

    def __getitem__(self, idx):
        mapa = torch.from_numpy(self.heightmaps[idx].astype("float32")).unsqueeze(0)
        etiqueta = torch.tensor(self.clases[idx], dtype=torch.long)
        return mapa, etiqueta