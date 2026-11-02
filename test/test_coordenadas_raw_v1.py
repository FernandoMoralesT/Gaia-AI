import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_bounds

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scrips"))
from coordenadas_raw_v1 import limites_tif  # noqa: E402


def test_limites_tif(tmp_path):
    ruta = tmp_path / "tile.tif"
    transformacion = from_bounds(-106.5, 23.0, -106.4, 23.05, 20, 10)
    with rasterio.open(ruta, "w", driver="GTiff", width=20, height=10, count=1,
                       dtype="int16", crs="EPSG:4326", transform=transformacion) as tif:
        tif.write(np.zeros((1, 10, 20), dtype="int16"))

    assert limites_tif(ruta) == {"lat_min": 23.0, "lat_max": 23.05, "lon_min": -106.5,
                                 "lon_max": -106.4, "ancho": 20, "alto": 10}
