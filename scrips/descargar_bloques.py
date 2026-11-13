"""Descarga los bloques del dataset v3 listados en data/bloques.json (v1.2.0).

- Reanudable: si el .tif ya existe en data/bloques/, se verifica y se marca sin gastar llamada.
- Máximo 45 llamadas por corrida. Un 401 o un 429 detienen la corrida: se retoma al día siguiente.
- Nunca imprime la clave: pedir_dem() ya devuelve errores sin ella.

Uso (desde cualquier carpeta):
    python scrips/descargar_bloques.py --revisar          # solo valida el manifiesto, sin llamar a la API
    python scrips/descargar_bloques.py --ids B03,B15,B20  # descarga solo esos
    python scrips/descargar_bloques.py                    # descarga todos los pendientes
"""
import argparse
import json
import math
import os
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import rasterio
import requests
from rasterio.errors import RasterioIOError

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
from dataset.descargar_dem import ErrorAPI, pedir_dem  # noqa: E402  (carga .env)

MAX_LLAMADAS = 45     # igual que src/descargar_lote.py
DETIENEN = {401, 429}  # cuota agotada o demasiadas peticiones: se retoma al día siguiente
NODATA = -32768
RANGO_PLAUSIBLE = (-450, 8850)  # mar Muerto a Everest
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


def verificar_bloque(ruta, b):
    """Forma contra la esperada (1 segundo de arco por píxel, ±1 px), % de nodata y rango de elevación."""
    with rasterio.open(ruta) as src:
        datos = src.read(1)
    esperada = [round((b["norte"] - b["sur"]) * 3600), round((b["este"] - b["oeste"]) * 3600)]
    validos = datos[datos != NODATA]
    v = {
        "forma": list(datos.shape),
        "forma_esperada": esperada,
        "nodata_pct": round(100 * (datos.size - validos.size) / datos.size, 3),
        "min_m": int(validos.min()) if validos.size else None,
        "max_m": int(validos.max()) if validos.size else None,
    }
    forma_ok = all(abs(a - e) <= 1 for a, e in zip(v["forma"], esperada))
    v["plausible"] = validos.size > 0 and RANGO_PLAUSIBLE[0] <= v["min_m"] and v["max_m"] <= RANGO_PLAUSIBLE[1]
    v["ok"] = bool(forma_ok and v["plausible"])
    return v


def descargar_pendientes(m, carpeta, pedir=pedir_dem, max_llamadas=MAX_LLAMADAS, ids=None,
                         esperar=time.sleep, guardar=None):
    """Descarga los bloques en estado pendiente. Devuelve un resumen de la corrida."""
    carpeta = Path(carpeta)
    r = {"llamadas": 0, "descargados": [], "fallidos": [], "detenido_por": None}
    for b in m["bloques"]:
        if b["estado"] != "pendiente" or (ids is not None and b["id"] not in ids):
            continue
        ruta = carpeta / nombre_bloque(b["sur"], b["norte"], b["oeste"], b["este"])
        if not ruta.exists():
            if r["llamadas"] >= max_llamadas:
                r["detenido_por"] = "tope"
                break
            if r["llamadas"]:
                esperar(2)
            r["llamadas"] += 1
            try:
                contenido = pedir(b["sur"], b["norte"], b["oeste"], b["este"])
            except ErrorAPI as err:
                if err.status in DETIENEN:
                    r["detenido_por"] = err.status
                    break
                b["estado"], b["verificacion"] = "fallido", {"motivo": str(err)}
                r["fallidos"].append(b["id"])
                if guardar:
                    guardar(m)
                continue
            except (requests.ConnectionError, requests.Timeout) as err:
                r["detenido_por"] = f"red: {err}"
                break
            temporal = ruta.with_suffix(".tmp")
            temporal.write_bytes(contenido)
            try:
                verificar_bloque(temporal, b)
            except RasterioIOError:
                temporal.unlink()
                b["estado"], b["verificacion"] = "fallido", {"motivo": "la respuesta no es un GeoTIFF"}
                r["fallidos"].append(b["id"])
                if guardar:
                    guardar(m)
                continue
            os.replace(temporal, ruta)
        b["verificacion"] = verificar_bloque(ruta, b)
        b["estado"] = "descargado"
        b["fecha_descarga"] = b["fecha_descarga"] or date.today().isoformat()
        r["descargados"].append(b["id"])
        if guardar:
            guardar(m)
    return r


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Descarga los bloques pendientes de data/bloques.json.")
    p.add_argument("--ids", help="ids separados por coma (por ejemplo B03,B15,B20); sin esto, todos los pendientes")
    p.add_argument("--revisar", action="store_true", help="solo valida el manifiesto, sin llamar a la API")
    args = p.parse_args(argv)

    m = cargar_manifiesto(RUTA_MANIFIESTO)
    problemas = revisar_manifiesto(m)
    if problemas:
        print("El manifiesto tiene problemas:\n- " + "\n- ".join(problemas))
        sys.exit(1)
    ids = set(args.ids.split(",")) if args.ids else None
    if ids and ids - {b["id"] for b in m["bloques"]}:
        sys.exit(f"ids que no están en el manifiesto: {sorted(ids - {b['id'] for b in m['bloques']})}")
    pendientes = [b for b in m["bloques"] if b["estado"] == "pendiente" and (ids is None or b["id"] in ids)]
    print(f"Manifiesto sin problemas: {len(m['bloques'])} bloques, {len(pendientes)} pendientes en esta selección.")
    if args.revisar:
        return
    if not os.environ.get("OPENTOPO_API_KEY"):
        sys.exit("Falta OPENTOPO_API_KEY en .env")

    CARPETA.mkdir(parents=True, exist_ok=True)
    r = descargar_pendientes(m, CARPETA, ids=ids, guardar=lambda x: guardar_manifiesto(x, RUTA_MANIFIESTO))
    for b in m["bloques"]:
        if b["id"] in r["descargados"] or b["id"] in r["fallidos"]:
            print(f"{b['id']} {b['sitio']}: {b['estado']} {b['verificacion']}")
    print(f"Llamadas: {r['llamadas']}. Descargados: {len(r['descargados'])}. Fallidos: {len(r['fallidos'])}.")
    if r["detenido_por"] in DETIENEN:
        print(f"El servidor rechazó la llamada (HTTP {r['detenido_por']}): vuelve a ejecutar mañana.")
    elif r["detenido_por"] == "tope":
        print(f"Tope de {MAX_LLAMADAS} llamadas por corrida: vuelve a ejecutar mañana.")
    elif r["detenido_por"]:
        print(f"Detenido: {r['detenido_por']}")


if __name__ == "__main__":
    main()
