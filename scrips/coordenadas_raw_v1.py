from pathlib import Path

import rasterio
from rasterio.warp import transform_bounds

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "data" / "raw_v1"

# Los 3 tiles manuales de raw_v1 no traen las coordenadas en el nombre,
# pero el GeoTIFF guarda sus límites; aquí se leen para documentarlos.


def limites_tif(ruta):
    with rasterio.open(ruta) as tif:
        izq, abajo, der, arriba = tif.bounds
        if tif.crs is not None and tif.crs.to_epsg() != 4326:
            izq, abajo, der, arriba = transform_bounds(tif.crs, "EPSG:4326", izq, abajo, der, arriba)
        return {"lat_min": round(abajo, 4), "lat_max": round(arriba, 4),
                "lon_min": round(izq, 4), "lon_max": round(der, 4),
                "ancho": tif.width, "alto": tif.height}


if __name__ == "__main__":
    print("| Archivo | Latitud | Longitud | Píxeles |")
    print("| --- | --- | --- | --- |")
    for ruta in sorted(CARPETA.glob("output_SRTMGL1*.tif")):
        l = limites_tif(ruta)
        print(f"| `{ruta.name}` | {l['lat_min']} a {l['lat_max']} | {l['lon_min']} a {l['lon_max']} "
              f"| {l['ancho']}×{l['alto']} |")
