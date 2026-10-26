"""Genera docs/grafo.md con las dependencias reales entre archivos de src/, scrips/ y test/.

Uso (desde la raíz): python scrips/generar_grafo.py
"""
import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETAS = ["src", "scrips", "test"]
SALIDA = RAIZ / "docs" / "grafo.md"

# Descripción escrita a mano de los archivos clave. Los nombres exportados se leen del código.
CLAVE = {
    "src/dataset/dem_dataset.py": "Dataset de PyTorch y orden canónico de clases (nunca reordenar CLASES).",
    "src/dataset/cargar_dem.py": "Lectura de los .tif con rasterio y de data/etiquetas.json.",
    "src/dataset/procesamiento.py": "Reducción a 120×120, normalización por tile, variantes y división por tile.",
    "src/dataset/descargar_dem.py": "Descarga de un tile SRTM desde OpenTopography (clave en .env).",
    "src/descargar_lote.py": "Descarga por lotes de la lista de tiles.",
    "src/pipeline.py": "Punto de entrada del dataset y del entrenamiento (500 épocas).",
    "src/model/generador.py": "Generador de la cGAN (ruido 100 + clase → 120×120).",
    "src/model/discriminador.py": "Discriminador de la cGAN (clase como canal extra).",
    "src/model/entrenar.py": "Ciclo de entrenamiento, muestras, checkpoints y su carga.",
    "src/inferencia.py": "Inferencia local: terreno por clase y semilla, suavizado y exportación .raw.",
    "src/noise/Unificacion_Y_Exportacion.py": "Generador clásico de ruido y exportación (Sprints 1-3).",
    "scrips/exportar_generador.py": "Extrae el generador de epoca_150.pt a modelos/generador_epoca150.pt.",
    "scrips/generar_grafo.py": "Este script: regenera docs/grafo.md.",
    "test/test_inferencia.py": "Tests de pytest de src/inferencia.py.",
}

FLUJO = """\
```text
data/raw/*.tif + data/etiquetas.json
  → src/dataset/ (cargar_dem, procesamiento, dem_dataset)
  → src/pipeline.py + src/model/entrenar.py          (entrenamiento)
  → salidas/checkpoints/epoca_NNN.pt                  (local, gitignored)
  → scrips/exportar_generador.py
  → modelos/generador_epoca150.pt                     (versionado)
  → src/inferencia.py  (generar_terreno → suavizar → exportar_raw)
  → godot/gaia-visor/mapas/*.raw
  → visor de Godot (godot/gaia-visor/terreno.gd + terreno.gdshader)
```"""


def archivos():
    for carpeta in CARPETAS:
        for ruta in sorted((RAIZ / carpeta).rglob("*.py")):
            if "__pycache__" not in ruta.parts:
                yield ruta


def resolver(modulo, origen):
    """Convierte un nombre de módulo en un archivo del repo, o None si es externo."""
    partes = modulo.split(".")
    # Bases en el orden en que Python las encontraría: carpeta del script, src/ (sys.path.insert), raíz.
    for base in (origen.parent, RAIZ / "src", RAIZ):
        archivo = base.joinpath(*partes).with_suffix(".py")
        if archivo.is_file():
            return archivo
        paquete = base.joinpath(*partes, "__init__.py")
        if paquete.is_file():
            return paquete
    return None


def imports_de(ruta):
    arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=str(ruta))
    destinos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                destinos.add(resolver(alias.name, ruta))
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.level:  # import relativo
                base = ruta.parent
                for _ in range(nodo.level - 1):
                    base = base.parent
                modulo = ".".join(filter(None, [*base.relative_to(RAIZ / "src").parts, nodo.module or ""])) \
                    if (RAIZ / "src") in base.parents or base == RAIZ / "src" else nodo.module or ""
            else:
                modulo = nodo.module or ""
            destino = resolver(modulo, ruta)
            # `from paquete import submodulo`
            for alias in nodo.names:
                sub = resolver(f"{modulo}.{alias.name}", ruta) if modulo else None
                if sub is not None and sub.name != "__init__.py":
                    destinos.add(sub)
                    destino = destino if destino and destino.name != "__init__.py" else None
            destinos.add(destino)
    destinos.discard(None)
    destinos.discard(ruta)
    return sorted(destinos)


def exportados(ruta):
    """Funciones, clases y constantes públicas de primer nivel (sin RAIZ, que es solo una ruta)."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    if ruta.parts[-2] == "test":
        n = sum(isinstance(x, ast.FunctionDef) and x.name.startswith("test_") for x in arbol.body)
        return [f"{n} tests"]
    if ruta.parts[-2] == "scrips":
        return []
    nombres = []
    for nodo in arbol.body:
        if isinstance(nodo, (ast.FunctionDef, ast.ClassDef)) and not nodo.name.startswith("_"):
            nombres.append(nodo.name)
        elif isinstance(nodo, ast.Assign):
            for t in nodo.targets:
                if isinstance(t, ast.Name) and t.id.isupper() and t.id != "RAIZ":
                    nombres.append(t.id)
    return nombres


def rel(ruta):
    return ruta.relative_to(RAIZ).as_posix()


def main():
    aristas = []
    for ruta in archivos():
        for destino in imports_de(ruta):
            if destino.name == "__init__.py" and destino.stat().st_size == 0:
                continue  # paquete vacío: no aporta dependencia real
            aristas.append((rel(ruta), rel(destino)))

    lineas = [
        "# Grafo del repositorio",
        "",
        "Generado por `scrips/generar_grafo.py` a partir de los imports reales (módulo `ast`).",
        "No editar a mano las secciones 1 y 3: volver a ejecutar el script.",
        "",
        "## 1. Dependencias (archivo → archivo que importa)",
        "",
    ]
    lineas += [f"- `{a}` → `{b}`" for a, b in aristas]
    sin_aristas = sorted({rel(r) for r in archivos()} - {a for a, _ in aristas} - {b for _, b in aristas})
    if sin_aristas:
        lineas += ["", "Sin dependencias internas: " + ", ".join(f"`{x}`" for x in sin_aristas) + "."]
    lineas += ["", "## 2. Flujo de datos", "", FLUJO, "", "## 3. Archivos clave", ""]
    for archivo, descripcion in CLAVE.items():
        ruta = RAIZ / archivo
        if not ruta.is_file():
            continue
        nombres = exportados(ruta)
        if not nombres:
            lineas.append(f"- `{archivo}`: {descripcion} Script ejecutable.")
        elif nombres[0].endswith(" tests"):
            lineas.append(f"- `{archivo}`: {descripcion} Contiene {nombres[0]}.")
        else:
            lineas.append(f"- `{archivo}`: {descripcion} Exporta: " + ", ".join(f"`{n}`" for n in nombres) + ".")
    lineas += [
        "- `modelos/generador_epoca150.pt`: `state_dict` del generador de la época 150 (modelo del demo).",
        "- `data/etiquetas.json`: fuente de verdad de la clase de cada tile.",
        "- `godot/gaia-visor/terreno.gd`: lee el `.raw` y arma la malla; `terreno.gdshader` colorea por altura.",
        "",
    ]
    SALIDA.write_text("\n".join(lineas), encoding="utf-8")
    print(f"{len(aristas)} aristas -> {rel(SALIDA)}")


if __name__ == "__main__":
    main()
