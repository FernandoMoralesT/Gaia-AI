import json
import os
import time

from dataset.descargar_dem import descargar_tile, nombre_tile

LADO = 0.1
CARPETA = "data/raw"
RUTA_ETIQUETAS = "data/etiquetas.json"
MAX_SOLICITUDES = 45  # margen bajo la cuota diaria

# (nombre, clase propuesta, lat centro, lon centro)
ANTIGUOS = [
    ("Lote 1", "montaña", 23.725, -105.875),
    ("Lote 2", "montaña", 23.825, -105.725),
    ("Lote 3", "montaña", 24.025, -105.575),
    ("Lote 4", "meseta", 24.225, -105.475),
    ("Lote 5", "lomas", 23.625, -105.975),
    ("Lote 6", "lomas", 23.325, -106.075),
    ("Lote 7", "montaña", 23.925, -106.175),
    ("Lote 8", "llanura", 23.225, -106.395),
    ("Lote 9", "llanura", 24.825, -107.375),
    ("Lote 10", "llanura", 25.825, -108.925),
    ("Prueba", "lomas", 23.57, -106.375),
]
NUEVOS = [  # (nombre, clase, lat, lon)
    # llanura
    ("Mérida", "llanura", 20.9674, -89.5926),
    ("Valladolid", "llanura", 20.6896, -88.2018),
    ("Villahermosa", "llanura", 17.9892, -92.9475),
    ("Mexicali", "llanura", 32.6245, -115.4523),
    ("Cd. Obregón", "llanura", 27.4864, -109.9408),
    ("Tuxpan", "llanura", 20.9544, -97.4010),
    ("Guasave", "llanura", 25.5706, -108.4693),
    ("General Pico, Argentina", "llanura", -35.6566, -63.7568),
    # lomas
    ("Tepatitlán", "lomas", 20.8189, -102.7633),
    ("Dolores Hidalgo", "lomas", 21.1561, -100.9317),
    ("Valle de Guadalupe, BC", "lomas", 32.0833, -116.6167),
    ("Linares, NL", "lomas", 24.8602, -99.5681),
    ("Siena, Italia", "lomas", 43.3186, 11.3306),
    ("Pullman (Palouse), EE. UU.", "lomas", 46.7298, -117.1817),
    ("Council Grove (Flint Hills), EE. UU.", "lomas", 38.6617, -96.4936),
    ("Beaune, Francia", "lomas", 47.0260, 4.8400),
    # valle
    ("Valle de Bravo", "valle", 19.1950, -100.1330),
    ("Valle de Oaxaca", "valle", 17.0594, -96.7253),
    ("Valle Nacional, Oaxaca", "valle", 17.7740, -96.3223),
    ("Yosemite", "valle", 37.7456, -119.5936),
    ("Napa (St. Helena)", "valle", 38.5052, -122.4703),
    ("Urubamba, Perú", "valle", -13.3050, -72.1170),
    ("Chamonix", "valle", 45.9237, 6.8694),
    ("Lauterbrunnen", "valle", 46.5936, 7.9086),
    # montaña
    ("Cerro El Potosí", "montaña", 24.8667, -100.2167),
    ("Picacho del Diablo", "montaña", 30.9843, -115.4208),
    ("Cerro Mohinora", "montaña", 25.9500, -107.0333),
    ("Matterhorn", "montaña", 45.9763, 7.6586),
    ("Grand Teton", "montaña", 43.7411, -110.8024),
    ("Monte Whitney", "montaña", 36.5786, -118.2923),
    ("Aconcagua", "montaña", -32.6532, -70.0109),
    ("Everest", "montaña", 27.9881, 86.9250),
    ("Torres del Paine", "montaña", -50.9423, -73.4068),
    # meseta
    ("Monument Valley", "meseta", 36.9980, -110.0985),
    ("Grand Mesa", "meseta", 39.0600, -107.9900),
    ("Island in the Sky", "meseta", 38.4600, -109.8200),
    ("Mesa Verde", "meseta", 37.1840, -108.4890),
    ("Table Mountain, Ciudad del Cabo", "meseta", -33.9628, 18.4098),
    ("Roraima", "meseta", 5.1433, -60.7619),
    ("Oruro (Altiplano)", "meseta", -17.9647, -67.1060),
    ("Meseta Pajarito, Los Álamos", "meseta", 35.8800, -106.3031),
    # volcán
    ("Popocatépetl", "volcán", 19.0225, -98.6278),
    ("Pico de Orizaba", "volcán", 19.0303, -97.2685),
    ("Nevado de Toluca", "volcán", 19.1083, -99.7583),
    ("La Malinche", "volcán", 19.2300, -98.0314),
    ("Volcán de Colima", "volcán", 19.5139, -103.6200),
    ("Paricutín", "volcán", 19.4931, -102.2514),
    ("Ceboruco", "volcán", 21.1250, -104.5083),
    ("El Pinacate", "volcán", 31.7667, -113.4833),
    ("Monte Fuji", "volcán", 35.3606, 138.7274),
]
LISTA = ANTIGUOS + NUEVOS


def cargar_etiquetas():
    if os.path.exists(RUTA_ETIQUETAS):
        with open(RUTA_ETIQUETAS, encoding="utf-8") as f:
            contenido = f.read().strip()
        if contenido:
            return json.loads(contenido)
    return {}


def guardar_etiquetas(etiquetas):
    with open(RUTA_ETIQUETAS, "w", encoding="utf-8") as f:
        json.dump(etiquetas, f, ensure_ascii=False, indent=2, sort_keys=True)


if __name__ == "__main__":
    etiquetas = cargar_etiquetas()
    hechas = 0
    for nombre, clase, lat, lon in LISTA:
        s, n = lat - LADO / 2, lat + LADO / 2
        w, e = lon - LADO / 2, lon + LADO / 2
        archivo = nombre_tile(s, n, w, e)
        if os.path.exists(os.path.join(CARPETA, archivo)):
            etiquetas.setdefault(archivo, clase)
            continue
        if hechas >= MAX_SOLICITUDES:
            print("Límite por corrida alcanzado; vuelve a ejecutar mañana")
            break
        try:
            descargar_tile(s, n, w, e)
            etiquetas[archivo] = clase
            hechas += 1
        except Exception as err:
            print("Falló", nombre, err)
            break
        time.sleep(2)
    guardar_etiquetas(etiquetas)