"""Análisis para decidir el dataset v3 (v1.2.0, paso 1): escala, criterio por clase y normalización.

Solo lee data/raw y data/etiquetas.json; no descarga nada. Imprime las tablas en Markdown
y guarda las gráficas en docs/img/dataset_v3/.

Uso (desde cualquier carpeta): python scrips/analizar_dataset_v3.py > salida.md
"""
import ast
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import rasterio  # noqa: E402
from scipy.ndimage import gaussian_filter  # noqa: E402
from scipy.stats import kruskal  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
from dataset.dem_dataset import CLASES  # noqa: E402
from dataset.procesamiento import reducir_tile  # noqa: E402

IMG = RAIZ / "docs" / "img" / "dataset_v3"
# Paleta categórica validada (skill dataviz, modo claro), en el orden canónico de CLASES.
COLORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]

# Los 9 tiles dudosos de docs/dataset.md (sección 4).
DUDOSOS = [
    "dem_25.77_25.88_-108.97_-108.88", "dem_24.81_24.91_-99.62_-99.52", "dem_38.61_38.71_-96.54_-96.44",
    "dem_19.14_19.25_-100.18_-100.08", "dem_45.87_45.97_6.82_6.92", "dem_46.54_46.64_7.86_7.96",
    "dem_37.7_37.8_-119.64_-119.54", "dem_24.18_24.28_-105.52_-105.42", "dem_23.18_23.28_-106.44_-106.34",
]
ALTIPLANO = "dem_-18.01_-17.91_-67.16_-67.06"

# Anillo del cráter de la v1.0: 4 a 20 px a 90 m/px, es decir 360 a 1800 m.
ANILLO_M = (360.0, 1800.0)


# ---------------------------------------------------------------- carga

def lugares():
    """(nombre, clase, lat, lon) de src/descargar_lote.py, leídos con ast para no importarlo (carga .env)."""
    arbol = ast.parse((RAIZ / "src" / "descargar_lote.py").read_text(encoding="utf-8"))
    lista = []
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and nodo.targets[0].id in ("ANTIGUOS", "NUEVOS"):
            lista += ast.literal_eval(nodo.value)
    return lista


def metros_por_grado(lat):
    """Metros por grado de latitud y de longitud (fórmulas estándar del elipsoide WGS84)."""
    f = np.radians(lat)
    m_lat = 111132.92 - 559.82 * np.cos(2 * f) + 1.175 * np.cos(4 * f)
    m_lon = 111412.84 * np.cos(f) - 93.5 * np.cos(3 * f)
    return m_lat, m_lon


def cargar_tiles():
    etiquetas = json.loads((RAIZ / "data" / "etiquetas.json").read_text(encoding="utf-8"))
    sitios = lugares()
    tiles = {}
    for archivo, clase in sorted(etiquetas.items()):
        with rasterio.open(RAIZ / "data" / "raw" / archivo) as src:
            z = src.read(1).astype(np.float64)
            b, (rx, ry) = src.bounds, src.res
        lat, lon = (b.bottom + b.top) / 2, (b.left + b.right) / 2
        m_lat, m_lon = metros_por_grado(lat)
        nombre = min(sitios, key=lambda s: (s[2] - lat) ** 2 + (s[3] - lon) ** 2)[0]
        tiles[archivo[:-4]] = {"z": z, "clase": clase, "lugar": nombre, "lat": lat,
                               "dy": ry * m_lat, "dx": rx * m_lon}
    return tiles


# ---------------------------------------------------------------- A. escala

def profundidad_crater(mapa, r_min, r_max):
    """Método de la v1.0: máximo del anillo [r_min, r_max] px alrededor del centro geométrico,
    menos el promedio de los 2x2 píxeles centrales. Positivo = hay un hueco en el centro."""
    n = mapa.shape[0]
    c = (n - 1) / 2
    y, x = np.indices(mapa.shape)
    d = np.hypot(y - c, x - c)
    centro = mapa[n // 2 - 1:n // 2 + 1, n // 2 - 1:n // 2 + 1].mean()
    return mapa[(d >= r_min) & (d <= r_max)].max() - centro


def escalas(z):
    """{metros nominales por píxel: mapa} para 30 m (nativo), 60 m (2x2) y 90 m (3x3)."""
    return {30: z, 60: reducir_tile(z, 2), 90: reducir_tile(z, 3)}


def seccion_crater(tiles):
    volcanes = [(k, t) for k, t in tiles.items() if t["clase"] == "volcán"]
    print("## A1. Profundidad del cráter por escala\n")
    print(f"Anillo de {ANILLO_M[0]:.0f} a {ANILLO_M[1]:.0f} m: 12–60 px a 30 m, 6–30 px a 60 m y 4–20 px a 90 m.\n")
    print("| Volcán | Tile | 30 m (m) | 60 m (m) | 90 m (m) |")
    print("|---|---|---|---|---|")
    filas = []
    for k, t in volcanes:
        p = {e: profundidad_crater(m, ANILLO_M[0] / e, ANILLO_M[1] / e) for e, m in escalas(t["z"]).items()}
        filas.append((t["lugar"], k, p))
        print(f"| {t['lugar']} | `{k}` | {p[30]:+.0f} | {p[60]:+.0f} | {p[90]:+.0f} |")
    print()
    for umbral in (100, 50):
        cuenta = {e: sum(p[e] >= umbral for _, _, p in filas) for e in (30, 60, 90)}
        print(f"- Con profundidad >= {umbral} m: 30 m → {cuenta[30]}, 60 m → {cuenta[60]}, 90 m → {cuenta[90]} de {len(filas)}.")
    print()
    figura_volcanes(volcanes)
    return filas


def figura_volcanes(volcanes):
    fig, ejes = plt.subplots(len(volcanes), 3, figsize=(7.5, 2.3 * len(volcanes)))
    for i, (k, t) in enumerate(volcanes):
        mapas = escalas(t["z"])
        semi = 2400.0  # recorte de ±2.4 km alrededor del centro, para ver el anillo completo
        vmin, vmax = None, None
        for j, (e, m) in enumerate(mapas.items()):
            n = m.shape[0]
            c, r = (n - 1) / 2, int(semi / e)
            sub = m[n // 2 - r:n // 2 + r, n // 2 - r:n // 2 + r]
            if vmin is None:
                vmin, vmax = sub.min(), sub.max()
            ax = ejes[i, j]
            ax.imshow(sub, cmap="terrain", vmin=vmin, vmax=vmax, extent=(-semi, semi, semi, -semi))
            for radio in ANILLO_M:
                ax.add_patch(plt.Circle((0, 0), radio, fill=False, color="white", lw=1, ls="--"))
            ax.set_xticks([]), ax.set_yticks([])
            if i == 0:
                ax.set_title(f"{e} m/px", fontsize=10)
            if j == 0:
                ax.set_ylabel(t["lugar"], fontsize=9)
    fig.suptitle("Centro de los volcanes (±2.4 km) y anillo de 360–1800 m", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(IMG / "crater_escalas.png", dpi=90)
    plt.close(fig)


def seccion_recortes(tiles):
    dy = [t["dy"] for t in tiles.values()]
    dx = [t["dx"] for t in tiles.values()]
    print("## A2. Recortes de 128 px\n")
    print(f"- Píxel nativo norte-sur: {min(dy):.1f} a {max(dy):.1f} m; este-oeste: {min(dx):.1f} a {max(dx):.1f} m "
          "(se angosta con la latitud).")
    print(f"- Lado norte-sur de un tile de 0.1°: {min(dy) * 360 / 1000:.2f} a {max(dy) * 360 / 1000:.2f} km.")
    for f, e in ((2, 60), (3, 90)):
        lado = 360 // f
        print(f"- A {e} m/px el tile mide {lado} px; un recorte de 128 px cubre {128 * e / 1000:.2f} km nominales.")
        if lado < 128:
            print(f"  No cabe: faltan {128 - lado} px.")
            continue
        libres = lado - 128
        print(f"  Sin solape caben {(lado // 128) ** 2}. Con solape: posiciones distintas = "
              f"({libres} + 1)² = {(libres + 1) ** 2}; con paso de {libres} px caben 2 × 2 = 4 "
              f"(solape de {128 - libres} px, {100 * (128 - libres) / 128:.0f} %).")
    print()


def seccion_perdida(tiles):
    print("## A3. Lo que se pierde por el promedio (60 contra 90 m/px)\n")
    print("Respecto del tile nativo de 30 m. Relieve = percentil 99 menos percentil 1; "
          "la pendiente se recalcula con el píxel de cada escala.\n")
    print("| Clase | Pérdida de máximo a 60 m (m, mediana / peor) | a 90 m | Relieve conservado 60 m | 90 m "
          "| Pendiente media conservada 60 m | 90 m |")
    print("|---|---|---|---|---|---|---|")
    for clase in CLASES:
        perd, cons, pend = ({60: [], 90: []} for _ in range(3))
        for t in tiles.values():
            if t["clase"] != clase:
                continue
            m = escalas(t["z"])
            r30 = relieve(m[30])
            p30 = pendiente_grados(m[30], t["dy"], t["dx"])[0].mean()
            for e, f in ((60, 2), (90, 3)):
                perd[e].append(m[30].max() - m[e].max())
                cons[e].append(relieve(m[e]) / r30 * 100)
                pend[e].append(pendiente_grados(m[e], t["dy"] * f, t["dx"] * f)[0].mean() / p30 * 100)
        print(f"| {clase} | {np.median(perd[60]):.0f} / {max(perd[60]):.0f} | {np.median(perd[90]):.0f} / "
              f"{max(perd[90]):.0f} | {np.median(cons[60]):.1f} % | {np.median(cons[90]):.1f} % | "
              f"{np.median(pend[60]):.1f} % | {np.median(pend[90]):.1f} % |")
    print()


# ---------------------------------------------------------------- B. métricas

def relieve(z):
    p1, p99 = np.percentile(z, [1, 99])
    return p99 - p1


def pendiente_grados(z, dy, dx):
    gy, gx = np.gradient(z, dy, dx)
    return np.degrees(np.arctan(np.hypot(gx, gy))), gx, gy


def anisotropia(gx, gy):
    """0 = las pendientes miran a todas partes; 1 = todas en una sola dirección (tensor de estructura)."""
    j = np.array([[np.mean(gx * gx), np.mean(gx * gy)], [np.mean(gx * gy), np.mean(gy * gy)]])
    l1, l2 = sorted(np.linalg.eigvalsh(j), reverse=True)
    return (l1 - l2) / (l1 + l2)


def periodicidad(z):
    """Fracción de la energía del espectro que se lleva el pico más fuerte, sin las ondas
    más largas que medio tile. Un campo de dunas regular concentra la energía en un pico."""
    n = z.shape[0]
    y, x = np.indices(z.shape)
    a = np.c_[x.ravel(), y.ravel(), np.ones(z.size)]
    plano = a @ np.linalg.lstsq(a, z.ravel(), rcond=None)[0]
    p = np.abs(np.fft.fftshift(np.fft.fft2(z - plano.reshape(z.shape)))) ** 2
    k = np.hypot(y - n // 2, x - n // 2)
    banda = p[k >= 2]
    return banda.max() * 2 / banda.sum()  # x2: el espectro de una señal real es simétrico


def metricas(t):
    z = t["z"]
    pend, gx, gy = pendiente_grados(z, t["dy"], t["dx"])
    p1, p99 = np.percentile(z, [1, 99])
    h = (z - p1) / (p99 - p1)  # altura relativa dentro del tile
    plano = pend < 2
    suave = gaussian_filter(z, 5)
    cima = np.unravel_index(np.argmax(suave), z.shape)
    yy, xx = np.indices(z.shape)
    dist = np.hypot(yy - cima[0], xx - cima[1])
    return {
        "relieve_m": p99 - p1,
        "pendiente_deg": pend.mean(),
        "rugosidad_m": (np.abs(np.diff(z, axis=0)).mean() + np.abs(np.diff(z, axis=1)).mean()) / 2,
        "frac_plana": plano.mean(),
        "hipsometria": (z.mean() - p1) / (p99 - p1),
        "plano_alto": (plano & (h > 0.7)).mean(),
        "plano_bajo": (plano & (h < 0.3)).mean(),
        "conicidad": -np.corrcoef(suave.ravel(), dist.ravel())[0, 1],
        # Altura relativa del tercio central: cada tile está centrado en el accidente elegido.
        "posicion_centro": h[z.shape[0] // 3:2 * z.shape[0] // 3, z.shape[1] // 3:2 * z.shape[1] // 3].mean(),
        "anisotropia": anisotropia(gx, gy),
        "periodicidad": periodicidad(z),
    }


NOMBRES = {
    "relieve_m": ("Relieve (m)", "{:.0f}"), "pendiente_deg": ("Pendiente media (°)", "{:.1f}"),
    "rugosidad_m": ("Rugosidad (m)", "{:.1f}"), "frac_plana": ("Fracción casi plana", "{:.2f}"),
    "hipsometria": ("Integral hipsométrica", "{:.2f}"), "plano_alto": ("Plano alto", "{:.2f}"),
    "plano_bajo": ("Plano bajo", "{:.2f}"), "conicidad": ("Conicidad", "{:.2f}"),
    "posicion_centro": ("Posición del centro", "{:.2f}"),
    "anisotropia": ("Anisotropía", "{:.2f}"), "periodicidad": ("Periodicidad", "{:.3f}"),
}


def seccion_metricas(tiles):
    for t in tiles.values():
        t["m"] = metricas(t)
    claves = list(NOMBRES)

    print("## B1. Métricas por tile\n")
    print("Calculadas sobre el tile nativo (30 m nominales; el píxel real se toma de la latitud).\n")
    print("| Tile | Lugar | Clase | " + " | ".join(NOMBRES[c][0] for c in claves) + " |")
    print("|---" * (3 + len(claves)) + "|")
    for k, t in sorted(tiles.items(), key=lambda kv: (CLASES.index(kv[1]["clase"]), kv[0])):
        marca = " (dudoso)" if k in DUDOSOS else ""
        print(f"| `{k}` | {t['lugar']}{marca} | {t['clase']} | "
              + " | ".join(NOMBRES[c][1].format(t["m"][c]) for c in claves) + " |")
    print()

    print("## B2. Mínimo / mediana / máximo por clase\n")
    print("| Métrica | " + " | ".join(CLASES) + " | H de Kruskal-Wallis |")
    print("|---" * (len(CLASES) + 2) + "|")
    separacion = {}
    for c in claves:
        grupos = [[t["m"][c] for t in tiles.values() if t["clase"] == cl] for cl in CLASES]
        separacion[c] = kruskal(*grupos).statistic
        f = NOMBRES[c][1]
        celdas = [f"{f.format(min(g))} / {f.format(np.median(g))} / {f.format(max(g))}" for g in grupos]
        print(f"| {NOMBRES[c][0]} | " + " | ".join(celdas) + f" | {separacion[c]:.1f} |")
    print()
    print("H más alto = la métrica ordena mejor a las 6 clases (prueba por rangos, robusta a valores extremos).\n")

    seccion_solape(tiles, claves)
    seccion_reglas(tiles)
    figura_metricas(tiles, claves)


def clase_por_reglas(m):
    """Criterio candidato, en orden. Cada umbral sale de un hueco entre clases en la tabla B2."""
    if m["relieve_m"] < 50:
        return "llanura"   # llanura llega a 37 m y lomas empieza en 66 m
    if m["conicidad"] >= 0.80 and m["relieve_m"] >= 700 and m["pendiente_deg"] <= 22:
        return "volcán"    # mínimos y máximos de los 9 volcanes
    if m["posicion_centro"] < 0.30 and m["relieve_m"] >= 500:
        return "valle"     # valles <= 0.27 y montañas >= 0.42; 500 m deja fuera a lomas (máx. 478)
    if m["relieve_m"] < 500:
        return "lomas"
    if m["posicion_centro"] >= 0.40 and m["pendiente_deg"] >= 17:
        return "montaña"   # las mesetas no pasan de 15.1°
    return "meseta"


def seccion_reglas(tiles):
    print("## B3. Criterio candidato aplicado a los 60 tiles\n")
    print("| Etiqueta \\ Regla | " + " | ".join(CLASES) + " |")
    print("|---" * (len(CLASES) + 1) + "|")
    fallos = []
    for real in CLASES:
        fila = {c: 0 for c in CLASES}
        for k, t in tiles.items():
            if t["clase"] == real:
                pred = clase_por_reglas(t["m"])
                fila[pred] += 1
                if pred != real:
                    fallos.append((k, t, pred))
        print(f"| {real} | " + " | ".join(str(fila[c]) for c in CLASES) + " |")
    print(f"\nCoinciden {len(tiles) - len(fallos)} de {len(tiles)}. No coinciden:\n")
    for k, t, pred in fallos:
        print(f"- `{k}` ({t['lugar']}): etiqueta {t['clase']}, la regla dice {pred}.")
    print()

    # Clases nuevas: no hay tiles, así que solo se mide qué tiles actuales caerían en la regla (falsos positivos).
    lomas = [t["m"] for t in tiles.values() if t["clase"] == "lomas"]
    per_max = max(m["periodicidad"] for m in lomas)
    ani_max = max(m["anisotropia"] for m in lomas)
    print("## B4. Reglas candidatas de cañón y duna sobre los tiles actuales\n")
    print("- Cañón: posición del centro < 0.30, relieve >= 500 m e integral hipsométrica >= 0.5 "
          "(la mayor parte del área arriba: una meseta cortada).")
    print(f"- Duna: relieve < 500 m y periodicidad > {per_max:.4f} o anisotropía > {ani_max:.4f} "
          "(los máximos exactos de lomas).\n")
    for k, t in tiles.items():
        m = t["m"]
        if m["posicion_centro"] < 0.30 and m["relieve_m"] >= 500 and m["hipsometria"] >= 0.5:
            print(f"- Caería en cañón: `{k}` ({t['lugar']}, {t['clase']}).")
        if m["relieve_m"] < 500 and (m["periodicidad"] > per_max or m["anisotropia"] > ani_max):
            print(f"- Caería en duna: `{k}` ({t['lugar']}, {t['clase']}), periodicidad {m['periodicidad']:.3f}, "
                  f"anisotropía {m['anisotropia']:.2f}.")
    print()


def seccion_solape(tiles, claves):
    """Centroide más cercano dejando fuera el propio tile, con las métricas estandarizadas
    (relieve y rugosidad en logaritmo, porque van de metros a kilómetros)."""
    nombres = list(tiles)
    x = np.array([[np.log10(tiles[k]["m"][c]) if c in ("relieve_m", "rugosidad_m") else tiles[k]["m"][c]
                   for c in claves] for k in nombres])
    x = (x - x.mean(0)) / x.std(0)
    clases = np.array([tiles[k]["clase"] for k in nombres])
    print("## B2b. Tiles en zona de solapamiento\n")
    print("Se asigna cada tile a la clase cuyo centro (promedio de métricas) le queda más cerca, "
          "calculando los centros sin ese tile. Si no coincide con su etiqueta, está en zona de solapamiento.\n")
    print("| Tile | Lugar | Etiqueta | Más cerca de | Dudoso en dataset.md |")
    print("|---|---|---|---|---|")
    aciertos = 0
    for i, k in enumerate(nombres):
        otros = np.arange(len(nombres)) != i
        centros = {cl: x[otros & (clases == cl)].mean(0) for cl in CLASES}
        pred = min(centros, key=lambda cl: np.linalg.norm(x[i] - centros[cl]))
        if pred == clases[i]:
            aciertos += 1
        else:
            print(f"| `{k}` | {tiles[k]['lugar']} | {clases[i]} | {pred} | {'sí' if k in DUDOSOS else 'no'} |")
    print(f"\nCoinciden {aciertos} de {len(nombres)} tiles.\n")
    print("Los 9 dudosos de dataset.md:\n")
    for k in DUDOSOS:
        i = nombres.index(k)
        otros = np.arange(len(nombres)) != i
        dist = sorted((np.linalg.norm(x[i] - x[otros & (clases == cl)].mean(0)), cl) for cl in CLASES)
        print(f"- `{k}` ({tiles[k]['lugar']}, {clases[i]}): más cerca de {dist[0][1]} "
              f"({dist[0][0]:.2f}), luego {dist[1][1]} ({dist[1][0]:.2f}).")
    print()


def figura_metricas(tiles, claves):
    fig, ejes = plt.subplots(2, 6, figsize=(19, 7))
    ejes.ravel()[-1].axis("off")
    rng = np.random.default_rng(0)
    for ax, c in zip(ejes.ravel(), claves):
        for i, cl in enumerate(CLASES):
            ks = [k for k, t in tiles.items() if t["clase"] == cl]
            v = np.array([tiles[k]["m"][c] for k in ks])
            xs = i + rng.uniform(-0.18, 0.18, len(v))
            ax.scatter(xs, v, s=36, color=COLORES[i], edgecolor="white", linewidth=0.8, zorder=3)
            dud = [j for j, k in enumerate(ks) if k in DUDOSOS]
            ax.scatter(xs[dud], v[dud], s=110, facecolor="none", edgecolor="#333333", linewidth=1.2, zorder=4)
            ax.hlines(np.median(v), i - 0.3, i + 0.3, color="#333333", linewidth=2, zorder=5)
        ax.set_xticks(range(len(CLASES)), CLASES, rotation=40, fontsize=8)
        ax.set_title(NOMBRES[c][0], fontsize=10)
        if c in ("relieve_m", "rugosidad_m"):
            ax.set_yscale("log")
        ax.grid(axis="y", color="#e5e5e5", linewidth=0.6)
        ax.set_axisbelow(True)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    fig.suptitle("Métricas por tile (raya = mediana de la clase; círculo = tile dudoso)", fontsize=12)
    fig.tight_layout()
    fig.savefig(IMG / "metricas_por_clase.png", dpi=90)
    plt.close(fig)


# ---------------------------------------------------------------- C. normalización

def seccion_normalizacion(tiles):
    a60 = {k: reducir_tile(t["z"], 2) for k, t in tiles.items()}  # a 60 m, la escala candidata
    gmin = min(m.min() for m in a60.values())
    gmax = max(m.max() for m in a60.values())
    rel_max = max(m.max() - m.min() for m in a60.values())
    rel_med = max(max(m.max() - np.median(m), np.median(m) - m.min()) for m in a60.values())
    k_max = max(a60, key=lambda k: a60[k].max() - a60[k].min())
    print("## C. Normalización (sobre los tiles a 60 m/px)\n")
    print(f"- Elevación global: {gmin:.0f} a {gmax:.0f} m.")
    print(f"- Relieve máximo de un tile (máx − mín): {rel_max:.0f} m, en `{k_max}` ({tiles[k_max]['lugar']}).")
    print(f"- Desviación máxima respecto de la mediana del tile: {rel_med:.0f} m.\n")
    escala = float(np.ceil(rel_max / 500) * 500)
    escala_med = float(np.ceil(rel_med / 500) * 500)
    print(f"Escalas globales (redondeadas hacia arriba a 500 m): (b1) S = {escala:.0f} m, para que el relieve "
          f"máximo quepa en [−1, 1]; (b2) S = {escala_med:.0f} m, para que la desviación máxima respecto de la "
          "mediana quepa en [−1, 1].\n")

    def opciones(m):
        med = np.median(m)
        return {
            "por tile (hoy)": (2 / (m.max() - m.min()), -1.0, 1.0),
            "(a) global absoluta": (2 / (gmax - gmin), 2 * (m.min() - gmin) / (gmax - gmin) - 1,
                                    2 * (m.max() - gmin) / (gmax - gmin) - 1),
            "(b1) relativa al mínimo": (2 / escala, -1.0, 2 * (m.max() - m.min()) / escala - 1),
            "(b2) relativa a la mediana": (1 / escala_med, (m.min() - med) / escala_med, (m.max() - med) / escala_med),
        }

    print("Rango que ocupa cada tile dentro de [−1, 1] y tamaño de un escalón de 1 m de SRTM en unidades de la red.\n")
    cols = ["(a) global absoluta", "(b1) relativa al mínimo", "(b2) relativa a la mediana"]
    print("| Tile | Lugar | Clase | Relieve (m) | Por tile: 1 m = | " + " | ".join(f"{c}: rango | 1 m =" for c in cols) + " |")
    print("|---" * (5 + 2 * len(cols)) + "|")
    elegidos = [k for k, t in tiles.items() if t["clase"] in ("llanura", "montaña")] + [ALTIPLANO]
    filas = []
    for k in elegidos:
        m = a60[k]
        o = opciones(m)
        filas.append((k, o))
        print(f"| `{k}` | {tiles[k]['lugar']} | {tiles[k]['clase']} | {m.max() - m.min():.0f} | "
              f"{o['por tile (hoy)'][0]:.4f} | "
              + " | ".join(f"{o[c][1]:+.3f} a {o[c][2]:+.3f} | {o[c][0]:.5f}" for c in cols) + " |")
    print()
    figura_normalizacion(tiles, filas)


def figura_normalizacion(tiles, filas):
    fig, ejes = plt.subplots(1, 4, figsize=(17, 0.32 * len(filas) + 1.6), sharey=True)
    titulos = ["por tile (hoy)", "(a) global absoluta", "(b1) relativa al mínimo", "(b2) relativa a la mediana"]
    for ax, titulo in zip(ejes, titulos):
        for i, (k, o) in enumerate(filas):
            cl = tiles[k]["clase"]
            _, a, b = o[titulo]
            ax.hlines(i, a, b, color=COLORES[CLASES.index(cl)], linewidth=4)
        ax.set_xlim(-1.05, 1.05)
        ax.set_title(titulo, fontsize=10)
        ax.grid(axis="x", color="#e5e5e5", linewidth=0.6)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    ejes[0].set_yticks(range(len(filas)), [f"{tiles[k]['lugar']} ({tiles[k]['clase']})" for k, _ in filas],
                       fontsize=8)
    ejes[0].invert_yaxis()
    fig.suptitle("Rango que ocupa cada tile en [−1, 1] (llanuras, montañas y el altiplano)", fontsize=12)
    fig.tight_layout()
    fig.savefig(IMG / "normalizacion.png", dpi=90)
    plt.close(fig)


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # en Windows, la salida redirigida usa cp1252
    IMG.mkdir(parents=True, exist_ok=True)
    tiles = cargar_tiles()
    print(f"<!-- Generado por scrips/analizar_dataset_v3.py sobre {len(tiles)} tiles -->\n")
    seccion_crater(tiles)
    seccion_recortes(tiles)
    seccion_perdida(tiles)
    seccion_metricas(tiles)
    seccion_normalizacion(tiles)


if __name__ == "__main__":
    main()
