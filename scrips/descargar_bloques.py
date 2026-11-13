"""Descarga los bloques del dataset v3 listados en data/bloques.json (v1.2.0).

- Reanudable: si el .tif ya existe en data/bloques/, se verifica y se marca sin gastar llamada.
- Máximo 45 llamadas por corrida. Un 401 o un 429 detienen la corrida: se retoma al día siguiente.
- Nunca imprime la clave: pedir_dem() ya devuelve errores sin ella.

Uso (desde cualquier carpeta):
    python scrips/descargar_bloques.py --revisar          # solo valida el manifiesto, sin llamar a la API
    python scrips/descargar_bloques.py --ids B03,B15,B20  # descarga solo esos
    python scrips/descargar_bloques.py                    # descarga todos los pendientes
"""
import json
import math
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_MANIFIESTO = RAIZ / "data" / "bloques.json"
CARPETA = RAIZ / "data" / "bloques"
AREA_MAX_KM2 = 450_000  # límite de la API para datos de 30 m
PROPOSITOS = {"entrenamiento", "clase_pura", "referencia"}
ESTADOS = {"pendiente", "descargado", "fallido"}


def nombre_bloque(south, north, west, east):
    """Misma convención y redondeo que nombre_tile (dem_*.tif)."""
    return f"bloque_{round(south, 2)}_{round(north, 2)}_{round(west, 2)}_{round(east, 2)}.tif"


def cargar_manifiesto(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def guardar_manifiesto(m, ruta):
    """Escribe a un temporal y lo reemplaza, para que un corte no deje el JSON a medias."""
    ruta = Path(ruta)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    with open(temporal, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(temporal, ruta)


def area_km2(b):
    lat_media = math.radians((b["sur"] + b["norte"]) / 2)
    return (b["norte"] - b["sur"]) * 111.32 * (b["este"] - b["oeste"]) * 111.32 * math.cos(lat_media)


def _se_enciman(a, b):
    return a["sur"] < b["norte"] and a["norte"] > b["sur"] and a["oeste"] < b["este"] and a["este"] > b["oeste"]


def revisar_manifiesto(m):
    """Lista de problemas del manifiesto; vacía si está bien."""
    problemas = []
    vistos = set()
    bloques = m["bloques"]
    for b in bloques:
        if b["id"] in vistos:
            problemas.append(f"{b['id']}: id repetido")
        vistos.add(b["id"])
        if not (b["sur"] < b["norte"] and b["oeste"] < b["este"]):
            problemas.append(f"{b['id']}: límites invertidos")
        if area_km2(b) > AREA_MAX_KM2:
            problemas.append(f"{b['id']}: {area_km2(b):,.0f} km² pasa del límite de 450,000 km²")
        if b["proposito"] not in PROPOSITOS:
            problemas.append(f"{b['id']}: propósito desconocido {b['proposito']}")
        if b["estado"] not in ESTADOS:
            problemas.append(f"{b['id']}: estado desconocido {b['estado']}")
    for r in bloques:
        if r["proposito"] != "referencia":
            continue
        for b in bloques:
            if b is not r and _se_enciman(r, b):
                problemas.append(f"{r['id']}: la referencia se encima con {b['id']}")
    return problemas
