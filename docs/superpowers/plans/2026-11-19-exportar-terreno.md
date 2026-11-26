# Exportar el terreno Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Un botón "Exportar" en el visor que despliega un menú y guarda el terreno actual como PNG 8 bits (Roblox), RAW 16 bits (Unity) u OBJ (Blender), con LEEME; después, un `.exe` beta.

**Architecture:** `exportador.gd` (funciones `static`, sin estado) escribe los archivos; `interfaz.gd` solo conecta el `MenuButton` y muestra el resultado en `%Nota`. El menú usa el tema existente más un bloque `PopupMenu` hecho con recursos ya presentes en `tema.tres`.

**Tech Stack:** Godot 4.5.1 (GDScript), pruebas headless con `afirmar.gd`.

**Spec:** `docs/superpowers/specs/2026-11-19-exportar-terreno-design.md`

## Global Constraints

- Git: **no** usar add, commit, push, stash, reset, checkout, restore, rm, rebase, merge, tag, `gh pr`, `gh release`. Los archivos quedan sin confirmar (por eso este plan no tiene pasos de commit).
- Godot: `C:\Users\008lu\OneDrive\Escritorio\Godot_v4.5.1-stable_win64_console.exe` (no está en el PATH). En los comandos se escribe `GODOT`.
- Estilo del repo: **2 tabuladores por nivel de indentación**, nombres en español sin acentos en archivos, funciones de menos de 25 líneas, máximo 2 niveles de if/for, retornos tempranos, constantes con nombre (`STUDS_POR_PIXEL := 4`, `MAXIMO_16_BITS := 65535`), comentarios solo donde el porqué no es obvio.
- Sin colores ni fuentes nuevas: paleta noche (abismo #0A1235, índigo #33196B, noche #141B3D, borde #34408A, bruma #A9B6E0, ocre #E3AE48, musgo #4A8225, caliza #F4F0E6), Lilita One y Barlow Semi Condensed.
- Texto de los elementos del menú, exacto: `PNG 8 bits (Roblox)`, `RAW 16 bits (Unity)`, `OBJ (Blender)`.
- Nombre base: `<clase sin acentos>_<semilla>_s<sigma con %.1f>`, p. ej. `volcan_42_s2.0`. Archivos: `<base>_roblox.png`, `<base>_unity.raw`, `<base>_blender.obj`, `<base>_LEEME.txt`.
- Carpeta de salida en la interfaz: `OS.get_system_dir(OS.SYSTEM_DIR_DOCUMENTS) + "/Gaia-AI/exportaciones"`.
- No tocar `dist/Gaia-AI.exe` ni `export_presets.cfg` ni `.gitignore`.

## Review Focus

- Mapa con todos los valores iguales (max == min): sale todo en 0, sin NaN (Task 1/2).
- Clases con acento o ñ ("volcán", "montaña"): el nombre de archivo sale sin acentos (Task 1/2).
- Carpeta que no se puede crear: la función devuelve `""` y no revienta (Task 1/2).
- Mapa no cuadrado (4×3): ancho y alto no se confunden en PNG, RAW y OBJ (Task 1).
- Pulsar Exportar mientras se genera: el botón está deshabilitado (Task 3).

---

### Task 1: Prueba headless (debe fallar)

**Files:**
- Create: `godot/gaia-visor/pruebas/prueba_exportador.gd`

**Interfaces:**
- Consumes (aún inexistente): `Exportador.exportar_roblox/exportar_unity/exportar_blender(terreno: MeshInstance3D, info: Dictionary, carpeta: String) -> String`, con `info = {"clase": String, "semilla": int, "sigma": float}`.
- Produces: la prueba que define el contrato de las Tasks 2 y 3.

- [ ] **Step 1: Escribir la prueba**, `extends SceneTree`, `const Afirmar := preload("res://pruebas/afirmar.gd")`, `Afirmar.terminar("prueba_exportador")` al final, carpeta `user://prueba_exportador`. Un `terreno` como en `prueba_bloque.gd` (`load("res://terreno.gd").new()`) con `mapa_actual = {"ancho": 4, "alto": 3, "datos": ...}`, datos entre 0.2 y 0.8 con el máximo 0.8 en el índice 3 y el mínimo 0.2 en el índice 5 (para verificar la normalización). `info = {"clase": "montaña", "semilla": 42, "sigma": 2.0}`. Aserciones, cada una en una función corta (`_probar_png`, `_probar_raw`, `_probar_obj`, `_probar_caso_plano`, `_probar_carpeta_invalida`, `_limpiar`):
  - Las tres rutas devueltas terminan en `montana_42_s2.0_roblox.png`, `..._unity.raw`, `..._blender.obj` y existen.
  - PNG: `Image.load` lo abre; `get_width() == 4`, `get_height() == 3`, `get_format() == Image.FORMAT_L8`; `get_pixel(3, 0).r8 == 255`, `get_pixel(1, 1).r8 == 0`.
  - RAW: `FileAccess.get_file_as_bytes(ruta).size() == 4 * 3 * 2`; `decode_u16(3 * 2) == 65535`; `decode_u16(5 * 2) == 0`.
  - OBJ: el texto contiene `o terreno` y `o base` (en ese orden); entre ambos hay exactamente 12 líneas que empiezan con `v `; ningún carácter `,` en el archivo; cada línea `v ` cumple el `RegEx` `^v -?\d+\.\d+ -?\d+\.\d+ -?\d+\.\d+$`; todo índice de `f` está entre 1 y el total de `v` del archivo.
  - LEEME: tras cada una de las tres exportaciones existe `<base>_LEEME.txt` (es el mismo nombre en las tres; se borra entre exportaciones para comprobar que cada una lo escribe) y contiene "Roblox", "Unity", "Blender", `montaña`, `42`, `4 x 3`.
  - Caso plano: mapa 4×3 con todos los valores 0.5 → todos los píxeles del PNG valen 0 y todos los `u16` del RAW valen 0.
  - Carpeta inválida (`"user://prueba_exportador/archivo.txt/sub"`, donde `archivo.txt` es un archivo normal creado antes): las tres funciones devuelven `""`.
  - `_limpiar` borra los archivos y la carpeta con `DirAccess` y libera `terreno`.

- [ ] **Step 2: Ejecutar y confirmar que falla**

Run: `GODOT --headless --path godot/gaia-visor -s res://pruebas/prueba_exportador.gd`
Expected: error de script (`Exportador` no declarado) y código de salida distinto de 0. Mostrar la salida real.

---

### Task 2: `exportador.gd`

**Files:**
- Create: `godot/gaia-visor/exportador.gd`

**Interfaces:**
- Consumes: de `terreno`: `mapa_actual`, `escala_altura`, `multiplicador_altura`, `tamano_celda`, `construir_bloque(mapa) -> ArrayMesh`.
- Produces: `class_name Exportador extends RefCounted` con
  - `static func exportar_roblox(terreno: MeshInstance3D, info: Dictionary, carpeta: String) -> String`
  - `static func exportar_unity(...)` y `static func exportar_blender(...)`, misma firma. Devuelven la ruta escrita o `""`.

- [ ] **Step 1: Funciones compartidas**: `normalizar_alturas(datos: PackedFloat32Array) -> PackedFloat32Array` (min-max a 0..1; si max == min, todo 0), `_nombre_base(info) -> String` (clase con `á→a`, `é→e`, `í→i`, `ó→o`, `ú→u`, `ñ→n`, sigma `"%.1f"`), `_preparar(terreno, info, carpeta) -> String` (crea la carpeta con `DirAccess.make_dir_recursive_absolute`, escribe `<base>_LEEME.txt` y devuelve `carpeta + "/" + base`, o `""` si falla algo) y `_escribir_leeme(ruta, terreno, info) -> bool`. El texto del LEEME sale de constantes con los pasos de las tres herramientas y de los datos del mapa (clase, semilla, sigma, `ancho x alto`):
  - Roblox: Terrain Editor → Import; 1 píxel = `STUDS_POR_PIXEL` (4) studs; tamaño X = Z = ancho × 4; Y = `escala_altura × multiplicador_altura × 4`.
  - Unity: Terrain Settings → Import Raw → Depth 16 bit, Byte Order Windows, Width/Height = ancho/alto del mapa, Flip Vertically según se vea; tamaño X = Z = ancho × 1, Y = `escala_altura × multiplicador_altura`; si Unity exige 2ⁿ+1, usar 129 o 257 y dejar que remuestree.
  - Blender: File → Import → Wavefront (.obj), Forward -Z, Up Y (valores por defecto); no rotar.

- [ ] **Step 2: `exportar_roblox`**: `Image.create_from_data(ancho, alto, false, Image.FORMAT_L8, bytes)` con cada valor normalizado × `MAXIMO_8_BITS` (255) redondeado; `save_png`. Si falla, `""`.

- [ ] **Step 3: `exportar_unity`**: `FileAccess.open(..., WRITE)`, `store_16(roundi(valor * MAXIMO_16_BITS))` fila por fila, sin encabezado. Si no abre, `""`.

- [ ] **Step 4: `exportar_blender`**: construir el mapa normalizado (`{ancho, alto, datos}`), `terreno.construir_bloque(mapa)`, y para cada superficie 0 y 1 escribir `o terreno` / `o base`, luego `v`, `vt` (solo si hay `ARRAY_TEX_UV`), `vn` y `f` con `"%.5f"`. Los índices del OBJ son globales y empiezan en 1: llevar un desplazamiento acumulado de vértices, uv y normales entre objetos. Las caras son `v/vt/vn` o `v//vn` sin UV. **Invertir cada triángulo** (escribir índices en orden `0, 2, 1`) con un comentario del porqué: Godot tiene el frente en sentido horario y OBJ en antihorario. Separar en `_escribir_superficie(archivo, nombre, arrays, desplazamientos) -> Dictionary` (devuelve los desplazamientos nuevos) y `_escribir_cara(...)`.

- [ ] **Step 5: Ejecutar la prueba**

Run: `GODOT --headless --path godot/gaia-visor -s res://pruebas/prueba_exportador.gd`
Expected: `OK prueba_exportador`, código de salida 0. Si algo falla, usar `superpowers:systematic-debugging` antes de tocar el código.

---

### Task 3: Interfaz y tema

**Files:**
- Modify: `godot/gaia-visor/interfaz.tscn` (nodo `Exportar` en `FilaAjustes`, entre `Inspeccionar` y `Generar`)
- Modify: `godot/gaia-visor/interfaz.gd` (`_ready`, `generar`, `_terminar`, funciones nuevas)
- Modify: `godot/gaia-visor/tema.tres` (bloque `PopupMenu`)

**Interfaces:**
- Consumes: `Exportador.exportar_*` (Task 2), `info`, `terreno`, `ocupado`, `%Nota`.
- Produces: `func _al_exportar(id: int) -> void` en `interfaz.gd`.

- [ ] **Step 1: Nodo** `Exportar` (`MenuButton`, `unique_name_in_owner = true`, texto `Exportar`, `flat = false`, sin `theme_type_variation` para que pese igual que `Inspeccionar`), con los tres elementos `popup/item_0..2` (texto y `id` 0, 1, 2) del texto exacto de Global Constraints.

- [ ] **Step 2: `interfaz.gd`**: añadir `%Exportar` a la lista de controles sin foco en `_ready`; conectar `%Exportar.get_popup().id_pressed` a `_al_exportar`. `_al_exportar(id)`: crea la carpeta de Documentos + `/Gaia-AI/exportaciones`, llama a la función de `Exportador` según `id` (arreglo de tres `Callable`), y pone en `%Nota` `"Guardado en <ruta>"` o `"No se pudo exportar. Revisa que la carpeta Documentos sea accesible."`, con `%Nota.visible = true`. En `generar()` y `_terminar()` poner `%Exportar.disabled = true / false`. Nada de lógica de exportación aquí.

- [ ] **Step 3: `tema.tres`**: añadir `PopupMenu` con `styles/panel` (reusar `panel`), `styles/hover` (reusar `boton_hover`), `colors/font_color` y `font_hover_color` (caliza, mismo valor que `Button`), `fonts/font` (la misma fuente que `Button`) y una separación vertical de 6. Sin recursos nuevos de color o fuente.

- [ ] **Step 4: Verificar sin interfaz**: cargar `res://mundo.tscn` en headless y comprobar que `%Exportar` existe, es `MenuButton`, tiene 3 elementos con los textos exactos, `focus_mode == FOCUS_NONE`, y está deshabilitado mientras `ocupado` (agregar este caso a `prueba_exportador.gd` como `_probar_menu`, con el patrón de `prueba_desplegable.gd`; confirmar primero que falla).

Run: `GODOT --headless --path godot/gaia-visor -s res://pruebas/prueba_exportador.gd`
Expected: `OK prueba_exportador`.

---

### Task 4: Documentación

**Files:**
- Modify: `README.md` (sección "Exportar el terreno" tras "Visor en Godot")
- Modify: `docs/bitacora.md` (entrada nueva al final; incluye la línea del ejecutable beta del Task 5)
- Modify: `docs/ROADMAP_v2.md` (nota de avance bajo "v1.6.0: exportación")

- [ ] **Step 1: README**: sección con los tres formatos, la carpeta `Documentos/Gaia-AI/exportaciones`, y los pasos de importación (los mismos del LEEME).
- [ ] **Step 2: ROADMAP**: una línea de avance en v1.6.0: exportación básica desde el visor (PNG 8 bits, RAW 16 bits, OBJ) ya hecha, sin metros reales ni STL/GLB; sin inventar versión ni fecha de cierre.
- [ ] **Step 3: Bitácora**: entrada con qué se hizo, decisiones (mapa normalizado, triángulos invertidos, menú con `PopupMenu` en el tema) y lo no verificado. Dejar un marcador para la línea del `.exe` beta.

---

### Task 5: Regresión completa y ejecutable beta

**Files:**
- Create (ignorado por git): `dist/Gaia-AI_beta.exe`

- [ ] **Step 1: Correr las 10 pruebas existentes más la nueva**, una por una:
`GODOT --headless --path godot/gaia-visor -s res://pruebas/prueba_X.gd` para `bloque, camara, desplegable, esc_semilla, foco_visor, pantalla, perfil_clase, reloj_fondo, servidor_local, sombras`, y `exportador`. Expected: `OK <nombre>` en las 11. Mostrar la salida real.
- [ ] **Step 2: Tests de Python** (`python -m pytest test/`) solo para confirmar que no cambiaron (71 esperados).
- [ ] **Step 3: Ejecutable**: `GODOT --headless --path godot/gaia-visor --export-release "Windows Desktop" ../../dist/Gaia-AI_beta.exe`. Si falla, no instalar nada: reportar el error exacto y qué hay que instalar.
- [ ] **Step 4: Verificar** que `dist/Gaia-AI_beta.exe` existe (tamaño y fecha) y que `dist/Gaia-AI.exe` y `dist/Gaia-AI-v1.0.exe` no cambiaron de tamaño ni fecha (31 de octubre/2 de noviembre, 97639112 y 97644208 bytes). Anotarlo en la bitácora como "ejecutable beta con exportación (Roblox, Unity, Blender)", sin número de versión.
- [ ] **Step 5: Relectura final** de `exportador.gd` y los cambios de `interfaz.gd` como si fueran código ajeno; simplificar lo que se pueda y repetir Step 1.

---

## Self-review

- **Cobertura del diseño:** botón y menú (Task 3), tres formatos y LEEME (Task 2), nombre base y carpeta (Tasks 2 y 3), tema (Task 3), docs (Task 4), regresión y `.exe` (Task 5). Sin huecos.
- **Consistencia de tipos:** `exportar_*(terreno, info, carpeta) -> String` igual en las Tasks 1, 2 y 3; `info` con claves `clase`, `semilla`, `sigma`.
- **Proporción:** el plan fija firmas, valores y aserciones y deja los cuerpos al implementador.
- **Nota:** la petición dice a la vez "`<base>_LEEME.txt`" y "los tres LEEME existen". Como el nombre base es el mismo, el LEEME es un único archivo; la prueba comprueba que cada exportación lo deja escrito.
