import pandas as pd

h = pd.read_csv("salidas/historial.csv")
h["D_media"] = h["D"].rolling(10).mean()
h["G_media"] = h["G"].rolling(10).mean()
h["D_std"] = h["D"].rolling(10).std()

sano = h[(h["D_media"] > 1.0) & (h["G_media"] < 2.5)]
print(sano[["epoca", "D_media", "G_media", "D_std"]].to_string())
print(h[h["epoca"].between(145, 155)][["epoca", "D_media", "G_media", "D_std"]])