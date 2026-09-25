from torch.utils.data import Dataset
import torch

class DEMDataset(Dataset):
    def __init__(self, heightmaps):
        self.heightmaps = heightmaps

    def __len__(self):
        return len(self.heightmaps)

    def __getitem__(self, idx):
        return torch.from_numpy(self.heightmaps[idx].astype("float32"))