# Visor de expo: bloque sólido, cámara, fondo, intro y .exe — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convertir el visor en el demo de la expo: terreno como bloque sólido recortado, giro con teclado y zoom, fondo de "entorno IA", escena de introducción con menú (info, acerca de nosotros, visor) y un `.exe` que enciende solo el servidor del repo.

**Architecture:** Godot sigue siendo el visor; el `.exe` no empaqueta Python (PyTorch pesa GB): vive en `dist/` dentro del repo, busca `src/servidor.py` subiendo carpetas y lo lanza con `pythonw` como proceso hijo, que mata al cerrar. Un autoload (`ServidorLocal`) hace eso una vez para todas las escenas. Si no hay Python o repo, el visor usa los respaldos de `mapas/` sin mostrar errores (comportamiento ya existente en `interfaz.gd`).

**Tech Stack:** Godot 4.5.1 (Compatibility), GDScript, shaders `spatial`/`sky`/`canvas_item`; Python 3.13 + `http.server`; pytest.

**Spec:** el pedido de Fernando del 2026-10-26 (resumido en "Requisitos" abajo) y la sección "Sprint 9" de `CLAUDE.md`.

## Requisitos (del pedido)

1. El terreno deja de ser una hoja: bloque sólido recortado (superficie + 4 paredes + fondo).
2. Girar la figura con flechas o W/A/S/D.
3. Acercar y alejar el mapa generado.
4. Fondo que no sea gris: entorno IA, morado o azul marino; mejorar UI y fondo con criterio de diseño (skill frontend-design).
5. Escena de introducción: nombre de la IA con tipografía caricaturesca, aspecto de tierra con pasto arriba.
6. Menú con: información de la IA (con desplegables), "Acerca de nosotros" en tono coloquial, y botón al visualizador.
7. `.exe` que al abrirse enciende el servidor del repo y empieza en la intro.
8. Colores de la interfaz menos apagados (la distribución se queda igual).
9. Escala vertical por clase.
10. El volcán con roca negra en la cima en lugar de nieve.

## Global Constraints

- Godot 4.5.1, renderer `gl_compatibility`; nada que requiera Forward+.
- Servidor solo en `127.0.0.1:8765`; no se cambian sus rutas ni el formato `.raw`.
- Modelo del demo: `modelos/generador_epoca150.pt`; nunca sobrescribirlo.
- `CLASES` en el orden de `src/dataset/dem_dataset.py`; nunca reordenar.
- Textos de la interfaz en español, en minúsculas de oración, sin mayúsculas sostenidas.
- Nada de errores técnicos visibles: si algo falla se usa el respaldo y una nota en lenguaje normal.
- Fuentes solo con licencia OFL, con su `OFL.txt` al lado.
- Mensajes de commit sin comillas internas.
- Sangría de GDScript: dos tabs por nivel (estilo actual de `terreno.gd` e `interfaz.gd`).
- Las alturas no son metros; ningún texto debe decir lo contrario.

## Dirección de diseño (pasada de frontend-design)

**Idea:** *la tierra es lo cálido, la IA lo frío.* El bloque de terreno es una muestra de tierra cálida que flota en el espacio frío donde "piensa" la IA. La interfaz pasa de basalto a noche para que el único objeto cálido de la pantalla sea el terreno; los acentos ocre y musgo se conservan como hilo con la tierra.

| Token | Hex | Uso |
|---|---|---|
| Abismo | `#0A1235` | Fondo, parte baja del degradado |
| Índigo | `#33196B` | Fondo, parte alta del degradado |
| Noche | `#141B3D` (alfa 0.9) | Fondo de paneles |
| Bruma | `#A9B6E0` | Texto secundario (sustituye a liquen) |
| Borde | `#34408A` | Bordes de paneles y botones secundarios |
| Ocre | `#E3AE48` | Clase seleccionada, foco, marca de la cima (antes `#C9A15A`, más vivo) |
| Musgo | `#4A8225` | Botón "Generar" (antes `#4F6B34`, más vivo; contraste ≥ 4.5 con texto blanco) |
| Caliza | `#F4F0E6` | Texto principal |

Fernando pidió colores menos apagados (requisito 8): los tokens de acento ya son los vivos de esta tabla; no se cambia la distribución.

**Fondo:** degradado abismo→índigo con una retícula de puntos muy tenue que deriva despacio (el "espacio latente" de la IA). Sin brillos neón ni partículas por todos lados.

**Tipografía:** Barlow Semi Condensed se queda para la interfaz. Título: *Lilita One* (OFL), redonda y gruesa, rellena de tierra con pasto que crece en el borde superior.

**Lo memorable va en un solo lugar:** el título de tierra y pasto. Su única animación es el pasto creciendo una vez al abrir (0.8 s). El resto de la intro es sobrio.

**Revisión contra lo genérico:** se descartó el "negro con acento verde ácido" (cliché 2): el fondo es azul-morado profundo, y el verde aparece solo como pasto. Los botones del menú no son tarjetas iguales: uno principal ("Explorar terrenos") y dos secundarios.

```
Intro (1152×648 de referencia, todo alineado a la izquierda en el tercio izquierdo)
┌───────────────────────────────────────────────────────┐
│                                                       │
│   ᵥᵥᵥᵥᵥᵥᵥᵥᵥᵥᵥᵥᵥᵥ                                      │
│   G A I A - A I     (tierra + pasto, Lilita ~140px)   │
│   Terrenos que nunca existieron, dibujados por una IA │
│                                                       │
│   [ Explorar terrenos ]                               │
│   Cómo funciona Gaia                                  │
│   Acerca de nosotros                                  │
│                                     · · · · · · ·     │
└───────────────────────────────────────────────────────┘
```

## Review Focus

1. **Escribir la semilla con el teclado no debe girar el bloque**: con el `LineEdit` enfocado, W/A/S/D y flechas no mueven la cámara. Prueba en la Tarea 3.
2. **Servidor ya encendido** (por ejemplo, abierto a mano): el `.exe` no lanza otro ni mata uno que no lanzó. Prueba en la Tarea 5.
3. **El `.exe` fuera del repo o sin Python**: arranca normal, usa respaldos, sin diálogos de error. Prueba en la Tarea 5.
4. **Cerrar la ventana deja el puerto 8765 libre**: con el alias de la Store, el PID de `pythonw` puede ser el del alias y no el del proceso real; por eso se resuelve la ruta real de Python. Verificación en la Tarea 8.
5. **Pantalla completa 1920×1080 en la expo**: los paneles se reacomodan y el zoom no deja la cámara dentro del bloque. Verificación con capturas en las Tareas 4 y 7.

---

## Estructura de archivos

Todo en `godot/gaia-visor/` salvo donde se indique (el proyecto ya usa archivos planos; se mantiene).

| Archivo | Responsabilidad |
|---|---|
| `terreno.gd` (mod) | Construye el bloque: superficie + paredes + fondo, en 2 superficies |
| `estratos.gdshader` (nuevo) | Color de las paredes: capas de tierra y franja de pasto arriba |
| `camara_orbital.gd` (nuevo) | Giro con teclado, zoom con rueda y Q/E, límites |
| `fondo.gdshaderinc` (nuevo) | Función común `color_fondo()` |
| `fondo_cielo.gdshader` / `fondo_2d.gdshader` (nuevos) | El fondo en 3D (cielo) y en 2D (menús), ambos usando el include |
| `tema.tres` (mod) | Paleta noche |
| `servidor_local.gd` (nuevo, autoload `ServidorLocal`) | Encontrar el repo, lanzar y cerrar el servidor |
| `titulo.gdshader` + `titulo.tscn` (nuevos) | Título de tierra con pasto |
| `desplegable.tscn` / `desplegable.gd` (nuevos) | Botón que despliega un texto |
| `intro.tscn` / `intro.gd`, `info.tscn`, `acerca.tscn`, `pagina.gd` (nuevos) | Menú y páginas |
| `fuentes/LilitaOne-Regular.ttf` (nuevo) | Fuente del título |
| `pruebas/*.gd` (nuevos) | Pruebas headless; excluidas del `.exe` |
| `export_presets.cfg` (nuevo) | Preset "Windows Desktop" |
| `src/servidor.py`, `test/test_servidor.py` (mod) | Registrar sin consola (`pythonw`) |
| `.gitignore` raíz (mod) | `dist/` |

**Cómo se corren las pruebas de Godot:** cada `pruebas/prueba_*.gd` extiende `SceneTree`, usa `pruebas/afirmar.gd` (`static func afirmar(cond: bool, msg: String)` que imprime `FALLO: msg` y llama `quit(1)`), imprime `OK <nombre>` y termina con `quit(0)`.

```
G="/c/Users/008lu/OneDrive/Escritorio/Godot_v4.5.1-stable_win64_console.exe"
"$G" --headless --path godot/gaia-visor -s res://pruebas/prueba_X.gd
```

---

### Task 0: Commit del paso 2 (interfaz)

Fernando ya revisó y aprobó la distribución del paso 2 (los colores se corrigen en la Tarea 4).

- [ ] **Step 1:** `python -m pytest test/ -q` → `36 passed`.
- [ ] **Step 2: Commit**

```bash
git add godot/gaia-visor scrips/generar_respaldos.py docs/superpowers/plans/2026-10-26-visor-expo.md
git commit -m "feat: interfaz del visor con selector, inspeccion, mini mapa y respaldos por clase"
```

### Task 1: Servidor compatible con `pythonw`

`pythonw` no tiene consola: `sys.stderr` es `None` y `BaseHTTPRequestHandler.log_message` truena en cada petición.

**Files:** Modify `src/servidor.py` · Test `test/test_servidor.py`

**Interfaces:** Produces: `ManejadorGaia.log_message(formato, *args)` que no escribe si `sys.stderr is None`.

- [ ] **Step 1: Write the failing test**

```python
def test_sin_consola_no_truena(url_base, monkeypatch):
    monkeypatch.setattr(sys, "stderr", None)
    codigo, _, _ = pedir(f"{url_base}/salud")
    assert codigo == 200
```

- [ ] **Step 2:** `python -m pytest test/test_servidor.py::test_sin_consola_no_truena -v` → FAIL (conexión cerrada o error 500).
- [ ] **Step 3:** Sobrescribir `log_message` en `ManejadorGaia`: si `sys.stderr is None`, `return`; si no, `super().log_message(formato, *args)`. En `__main__`, envolver el `print` de arranque igual.
- [ ] **Step 4:** `python -m pytest test/ -q` → `37 passed`.
- [ ] **Step 5: Commit** `fix: servidor sin consola para lanzarlo con pythonw`

### Task 2: Bloque sólido recortado

**Files:** Modify `terreno.gd`, `mundo.tscn`, `interfaz.gd` (minimapa) · Create `estratos.gdshader`, `pruebas/afirmar.gd`, `pruebas/prueba_bloque.gd`

**Interfaces:**
- Produces: `terreno.gd`: `@export var profundidad_base := 14.0`, `@export var material_superficie: ShaderMaterial`, `@export var material_paredes: ShaderMaterial`, `func construir_bloque(mapa: Dictionary) -> ArrayMesh` (superficie 0 = terreno, superficie 1 = paredes + fondo). `construir_malla` se renombra a `construir_bloque`; `cargar_bytes` lo usa.
- `interfaz.gd` lee los colores de `terreno.material_superficie` (ya no de `material_override`, que se quita de `mundo.tscn`).

- [ ] **Step 1: Write the failing test** `pruebas/prueba_bloque.gd`: arma un mapa 4×3 de prueba (`datos` = 12 valores con 0.0 y 1.0 en posiciones conocidas), llama `construir_bloque`, y afirma:
  - `malla.get_surface_count() == 2`
  - superficie 0: 12 vértices (4×3)
  - superficie 1: el menor `y` de sus vértices es `-profundidad_base`
  - superficie 1: el mayor `y` es igual a `1.0 * escala_altura * multiplicador_altura`
  - superficie 1: hay normales que apuntan a ±X y ±Z (4 paredes) y una que apunta a −Y (fondo)
- [ ] **Step 2:** Correrla → `FALLO` (no existe `construir_bloque`).
- [ ] **Step 3: Implementar `construir_bloque`.** Superficie 0 = la malla actual. Superficie 1 con un segundo `SurfaceTool`: por cada uno de los 4 bordes, una tira de quads entre el vértice del borde (altura `h`) y su copia en `y = -profundidad_base`; luego un quad de fondo. Cada vértice de pared lleva `set_color(Color(v, v, v))` con la `v` del borde de arriba (también en el vértice de abajo), para que el shader sepa a qué altura está la superficie. Orden de vértices con las caras hacia afuera; `generate_normals()`. Asignar `surface_set_material(0, material_superficie)` y `(1, material_paredes)`.
- [ ] **Step 4: `estratos.gdshader`** (`spatial`): `uniform float escala_vertical` (= `escala_altura * multiplicador_altura`, lo pone `terreno.gd`), `uniform float grosor_pasto = 1.2`. `superficie = COLOR.r * escala_vertical`; `d = superficie - VERTEX.y` (usar `varying` desde `vertex()`). Si `d < grosor_pasto` → musgo `#4F6B34`; si no, capas con `floor((VERTEX.y + ruido) / 4.0)` alternando `#6B4429`, `#5B3A24`, `#7A5233`, `#4A2F1D`, con ruido de valor 2D sobre `(x+z, y)` de amplitud 0.8 para que las capas ondulen. Fondo (normal −Y): `#2B1C12`. `ROUGHNESS = 1.0`.
- [ ] **Step 5:** Correr la prueba → `OK prueba_bloque`. Captura (script de capturas de la sesión anterior) → se ve un bloque con paredes en capas.
- [ ] **Step 6: Commit** `feat: terreno como bloque solido con paredes de estratos`

### Task 2B: Escala vertical por clase y volcán de roca negra

**Files:** Modify `terreno.gd`, `interfaz.gd` · Create `pruebas/prueba_perfil_clase.gd`

**Interfaces:**
- Consumes: `construir_bloque`, `material_superficie`, `estratos` con `escala_vertical` (Task 2).
- Produces en `terreno.gd`: `const PERFILES := {clase: {"escala": float, "color_alto": Color}}` y `func aplicar_clase(clase: String) -> void` que fija `escala_altura`, pone `color_alto` en `material_superficie` y actualiza `escala_vertical` en `material_paredes`. Clase desconocida → no cambia nada.
- Valores (`multiplicador_altura` sigue en 3): llanura 4, lomas 8, valle 14, montaña 22, meseta 12, volcán 20. `color_alto`: nieve `#D9D9D1` para todas salvo volcán = roca negra `#2A2624`.
- `interfaz.gd` llama `terreno.aplicar_clase(clase)` antes de `cargar_bytes`/`cargar_archivo`, tanto en vivo como en respaldo; el `_ready` del terreno usa el perfil de volcán. El mini mapa toma `color_alto` del material, así que el volcán también sale negro ahí.

- [ ] **Step 1: Write the failing test** `pruebas/prueba_perfil_clase.gd`: tras `aplicar_clase("llanura")`, `escala_altura == 4.0`; tras `aplicar_clase("volcán")`, `escala_altura == 20.0` y `material_superficie.get_shader_parameter("color_alto")` ≈ `Color("2A2624")`; tras `aplicar_clase("montaña")` el `color_alto` vuelve a ser `Color("D9D9D1")`; `aplicar_clase("desierto")` no cambia `escala_altura`.
- [ ] **Step 2:** Correr → `FALLO`. Implementar. Correr → `OK prueba_perfil_clase`.
- [ ] **Step 3:** Capturas de llanura, montaña y volcán en vivo: la llanura se ve baja, la montaña alta y el volcán con cima negra.
- [ ] **Step 4: Commit** `feat: escala vertical por clase y volcan de roca negra`

### Task 3: Giro con teclado y zoom

**Files:** Create `camara_orbital.gd`, `pruebas/prueba_camara.gd` · Modify `mundo.tscn` (nodo `Pivote` en el origen con `Camara` hija), `project.godot` (acciones)

**Interfaces:**
- Acciones en `project.godot`: `girar_izq` (A, ←), `girar_der` (D, →), `subir` (W, ↑), `bajar` (S, ↓), `acercar` (E, +), `alejar` (Q, −). La rueda del mouse se maneja en `_unhandled_input`.
- `camara_orbital.gd` (en `Pivote`): `@export var velocidad_giro := 90.0` (°/s), `inclinacion := 30.0`, `inclinacion_min := 10.0`, `inclinacion_max := 80.0`, `distancia := 170.0`, `distancia_min := 70.0`, `distancia_max := 260.0`, `paso_rueda := 12.0`. `static func limitar(inclinacion: float, distancia: float, lim: Dictionary) -> Vector2`, `func teclado_libre() -> bool`.
- El sol no se mueve: girar la cámara alrededor del bloque se ve igual que girar el bloque y la luz sigue a 25°.

- [ ] **Step 1: Write the failing test** `pruebas/prueba_camara.gd`:
  - `limitar(95, 300, …) == Vector2(80, 260)` y `limitar(0, 10, …) == Vector2(10, 70)`
  - Con un `LineEdit` en el árbol y con foco (`grab_focus()`), `teclado_libre()` es `false`; sin foco, `true`.
  - Después de `_process(1.0)` con `Input.action_press("girar_der")`, el giro aumentó 90°; con el `LineEdit` enfocado no cambió.
- [ ] **Step 2:** Correrla → `FALLO`.
- [ ] **Step 3:** Implementar. `_process`: si `teclado_libre()`, aplicar `Input.get_axis` a giro e inclinación (× `velocidad_giro * delta`) y a la distancia. Luego `limitar`, y colocar la cámara con `rotation_degrees = Vector3(-inclinacion, giro, 0)` en `Pivote` y `Camara.position = Vector3(0, 0, distancia)`. `teclado_libre()`: `not (get_viewport().gui_get_focus_owner() is LineEdit)`.
- [ ] **Step 4:** Correr → `OK prueba_camara`. Captura a 3 ángulos distintos.
- [ ] **Step 5:** En el panel de controles, agregar una `Nota` fija: "Gira con W A S D o las flechas · acerca con la rueda o Q y E".
- [ ] **Step 6: Commit** `feat: camara orbital con teclado y zoom`

### Task 4: Fondo IA y paleta noche

**Files:** Create `fondo.gdshaderinc`, `fondo_cielo.gdshader`, `fondo_2d.gdshader` · Modify `mundo.tscn` (WorldEnvironment), `tema.tres`, `project.godot` (quitar `default_clear_color`)

**Interfaces:** Produces: `vec3 color_fondo(vec2 uv, float t)` en `fondo.gdshaderinc`; uv en [0,1] con y=0 abajo.

- [ ] **Step 1: `color_fondo`:** degradado vertical abajo `#0B1026`, arriba `#24164A`. Retícula: celda de 0.035 en uv, punto de radio 0.06 de la celda, brillo 0.10 con color `#9AA6C8`, desplazada `t * 0.004` en x. Desvanecer la retícula hacia abajo (×uv.y).
- [ ] **Step 2:** `fondo_cielo.gdshader` (`shader_type sky`): `uv = vec2(atan(EYEDIR.x, EYEDIR.z) / TAU + 0.5, EYEDIR.y * 0.5 + 0.5)`; `COLOR = color_fondo(uv, TIME)`. `fondo_2d.gdshader` (`canvas_item`): `COLOR.rgb = color_fondo(vec2(UV.x, 1.0 - UV.y), TIME)`.
- [ ] **Step 3:** `WorldEnvironment` en `mundo.tscn`: fondo = cielo con ese shader; luz ambiental de color `#3A3F5C`, energía 0.5 (sin contribución del cielo, para no teñir de morado el terreno).
- [ ] **Step 4:** `tema.tres`: aplicar todos los tokens de la tabla de diseño (paneles noche, bordes, bruma, y los acentos vivos de ocre, musgo —con sus variantes hover/presionado/desactivado— y caliza). En `interfaz.gd`, la marca de la cima pasa a `#E3AE48` y el comentario de paleta se actualiza.
- [ ] **Step 5:** Capturas a 1152×648 y 1920×1080 (`--resolution 1920x1080`). Revisar: contraste de la bruma sobre noche (debe leerse), que el terreno no se vea morado y que los paneles no se encimen.
- [ ] **Step 6: Commit** `feat: fondo de espacio latente y paleta noche`

### Task 5: Lanzador del servidor (autoload)

**Files:** Create `servidor_local.gd`, `pruebas/prueba_servidor_local.gd` · Modify `project.godot` (`[autoload] ServidorLocal="*res://servidor_local.gd"`), `interfaz.gd` (usa `ServidorLocal.URL`)

**Interfaces:**
- `const URL := "http://127.0.0.1:8765"`
- `static func buscar_repo(desde: String, niveles := 5) -> String`: sube carpetas desde `desde` hasta encontrar `src/servidor.py`; devuelve la ruta o `""`.
- `static func carpeta_inicio() -> String`: en el editor `ProjectSettings.globalize_path("res://")`; exportado `OS.get_executable_path().get_base_dir()`.
- `func resolver_pythonw() -> String`: `OS.execute("python", ["-c", "import sys; print(sys.executable)"], salida)`; si funciona, `pythonw.exe` en esa carpeta (si existe); si no, `""`. Así el PID es el de Python real, no el del alias de la Store.
- `var pid := -1` (solo se llena si **este** proceso lanzó el servidor).
- `_ready`: `GET /salud` con `HTTPRequest` (timeout 1.5 s). Si responde 200, no hace nada. Si no: repo y pythonw; si ambos existen, `pid = OS.create_process(pythonw, [repo + "/src/servidor.py"])`. Si falta alguno, no hace nada (el visor usa respaldos).
- `_notification(NOTIFICATION_WM_CLOSE_REQUEST)` y `_exit_tree`: si `pid > 0`, `OS.kill(pid)`.

- [ ] **Step 1: Write the failing test** `pruebas/prueba_servidor_local.gd`:
  - Crear en `user://prueba_repo/a/b/` y `user://prueba_repo/src/servidor.py` (vacío); `buscar_repo(<globalize de user://prueba_repo/a/b>)` termina en `prueba_repo`.
  - `buscar_repo` desde una carpeta sin repo en 5 niveles → `""`.
  - Desde la carpeta del proyecto real (`res://` globalizado) encuentra la raíz de `terreno-ai`.
- [ ] **Step 2:** Correr → `FALLO`.
- [ ] **Step 3:** Implementar `servidor_local.gd` según la interfaz. Registrar el autoload. En `interfaz.gd`, cambiar `URL_SERVIDOR` por `ServidorLocal.URL`.
- [ ] **Step 4:** Correr → `OK prueba_servidor_local`.
- [ ] **Step 5: Verificación manual (Review Focus 2 y 4)**, desde el editor con F5:
  - Servidor apagado → a los ~5 s "Generar" va en vivo; al cerrar, `Get-NetTCPConnection -LocalPort 8765` no devuelve nada.
  - Servidor abierto a mano antes → al cerrar el visor sigue vivo.
- [ ] **Step 6: Commit** `feat: el visor enciende y apaga el servidor local`

### Task 6: Título de tierra con pasto

**Files:** Create `fuentes/LilitaOne-Regular.ttf` (+ su `OFL.txt` como `fuentes/OFL-LilitaOne.txt`), `titulo.gdshader`, `titulo.tscn`

**Interfaces:** Produces: escena `titulo.tscn` (raíz `Control`) con `@export var texto := "Gaia-AI"` y `func crecer_pasto(duracion := 0.8)`.

`titulo.tscn`: `SubViewport` transparente (1000×260) con un `Label` (Lilita One, 150 px, blanco) → `TextureRect` con `ViewportTexture` y `titulo.gdshader`.

- [ ] **Step 1: `titulo.gdshader`** (`canvas_item`). `px = TEXTURE_PIXEL_SIZE`. Uniforms: `crecimiento` (0–1), `grosor_pasto = 18.0` (px), `alto_brizna = 10.0` (px), `grosor_contorno = 5.0` (px).
  - `a = alfa(UV)`; `dentro = a > 0.5`.
  - **Pasto encima de la letra:** si no está dentro, pero el pixel `alto_brizna * crecimiento * h(col)` más abajo sí lo está, y el pixel `alto_brizna` más arriba de ese no lo está (es el borde superior), pintar verde `#7BBF3A`. `h(col) = hash(floor(UV.x / px.x / 3.0))` da briznas de 3 px de ancho y alturas distintas.
  - **Contorno:** si no está dentro y hay alfa > 0.5 en un anillo de 8 muestras a `grosor_contorno` px → `#2B1A10`.
  - **Dentro, franja de pasto:** si el pixel `grosor_pasto * (0.7 + 0.3 * h(col))` más arriba está fuera → degradado `#7BBF3A` (arriba) → `#4F8A2B`.
  - **Dentro, tierra:** base `#7A4A2A`; capas `#5E3720` con `step(0.5, fract(UV.y / px.y / 22.0 + ruido * 0.3))`; motas `#A07A55` donde `ruido(UV * 90) > 0.82`; sombreado ×0.85 en la mitad de abajo de cada letra.
- [ ] **Step 2:** Descargar Lilita One de `https://raw.githubusercontent.com/google/fonts/main/ofl/lilitaone/` (`LilitaOne-Regular.ttf`, `OFL.txt`).
- [ ] **Step 3:** `crecer_pasto`: un `Tween` de `crecimiento` 0→1.
- [ ] **Step 4:** Captura del título solo sobre `fondo_2d`. Revisar a 100 % que el pasto se lea como pasto y no como un borde verde; si no, subir `alto_brizna` y la variación de `h`.
- [ ] **Step 5: Commit** `feat: titulo Gaia-AI de tierra con pasto`

### Task 7: Intro, menú y páginas con desplegables

**Files:** Create `intro.tscn`/`intro.gd`, `info.tscn`, `acerca.tscn`, `pagina.gd`, `desplegable.tscn`/`desplegable.gd` · Modify `mundo.tscn`/`interfaz.gd` (botón "Menú" y Esc), `project.godot` (`run/main_scene` = `intro.tscn`)

**Interfaces:**
- `desplegable.gd` (`VBoxContainer`): `@export var titulo: String`, `@export_multiline var texto: String`, `func alternar()`. El encabezado es un `Button` plano "+ titulo" / "– titulo"; el cuerpo es un `Label` con autowrap, oculto al inicio, ancho máximo 620 px (≈ 75 caracteres).
- `pagina.gd`: botón "Volver" y Esc → `get_tree().change_scene_to_file("res://intro.tscn")`.
- `intro.gd`: tres botones → `mundo.tscn`, `info.tscn`, `acerca.tscn`; llama `crecer_pasto()` en `_ready`. Foco inicial en "Explorar terrenos" (Enter la activa).
- Fondo de las 3 páginas: `ColorRect` a pantalla completa con `fondo_2d.gdshader`.

- [ ] **Step 1: Write the failing test** `pruebas/prueba_desplegable.gd`: instanciar `desplegable.tscn`; el cuerpo está oculto y el encabezado empieza con "+"; tras `alternar()`, el cuerpo es visible y empieza con "–"; tras otro `alternar()`, vuelve al inicio.
- [ ] **Step 2:** Correr → `FALLO`. Implementar `desplegable`. Correr → `OK`.
- [ ] **Step 3:** Escenas `intro`, `info`, `acerca` con el texto de abajo (Fernando lo edita a su gusto). En `mundo.tscn`, un botón "Menú" a la izquierda de "Inspeccionar" y Esc → intro.
- [ ] **Step 4:** Capturas de las 3 páginas (con un desplegable abierto) a 1152×648 y 1920×1080; recorrer todo con Tab y Enter sin mouse.
- [ ] **Step 5: Commit** `feat: intro con menu, informacion y acerca de nosotros`

**Texto de `info.tscn`** — título "Cómo funciona Gaia"; desplegables:
- *¿Qué es Gaia-AI?* — Una IA que dibuja terrenos que no existen. Por dentro son dos redes que compiten: una dibuja mapas de altura y la otra trata de adivinar si son reales o inventados. A fuerza de equivocarse, la que dibuja aprende a engañar a la otra.
- *¿De dónde aprendió?* — De 60 recortes de elevación real medida por satélite (SRTM). Cada recorte se reduce a 120 × 120 puntos, unos 90 m por punto, y se le dice qué forma tiene.
- *Las seis formas* — Llanura, lomas, valle, montaña, meseta y volcán. Se eligen por la forma del terreno, no por su altura en metros.
- *Qué hace bien y qué le cuesta* — Volcanes, valles y llanuras le salen claros. Lomas, montañas y mesetas a veces se le confunden. Y sus volcanes no tienen cráter: a esta resolución, la mayoría de los volcanes reales tampoco lo muestran.
- *Cómo usar el visor* — Elige una forma y pulsa "Generar". Gira con W A S D o las flechas, acerca con la rueda o Q y E. "Inspeccionar" muestra la semilla: escríbela para repetir un terreno.

**Texto de `acerca.tscn`** — título "Acerca de nosotros"; desplegables:
- *Quiénes somos* — Somos Luis Fernando Morales Toledo, Sebastian Aguillon Peinado y Cristoff Salvador Garcia Mendoza, de Ingeniería en Sistemas en la FIMAZ-UAS, en Mazatlán. Esto empezó como proyecto de Estructura de Datos y terminó en la expo de IA.
- *Cómo empezó* — Fernando quería mapas para su juego, *A Stupid RPG*. Hacerlos a mano era eterno, así que se nos ocurrió que una IA los inventara.
- *Lo que nos costó* — Entrenamos todo en una laptop sin tarjeta gráfica compatible: 500 rondas de unos 5 segundos cada una. A partir de la ronda 190, más o menos, la red juez le empezó a ganar a la que dibuja, así que nos quedamos con la ronda 150, escogida a ojo comparando mapas.
- *Cómo lo hicimos* — 10 semanas, una meta por semana. Python y PyTorch para la IA, Godot para lo que estás viendo.

### Task 8: Exportar el `.exe`

**Files:** Create `godot/gaia-visor/export_presets.cfg` · Modify `.gitignore` raíz (`dist/`)

- [x] **Step 1:** Plantillas instaladas y verificadas: `%APPDATA%/Godot/export_templates/4.5.1.stable/windows_release_x86_64.exe` existe.
- [ ] **Step 2:** `export_presets.cfg` con un preset `name="Windows Desktop"`, `platform="Windows Desktop"`, `export_filter="all_resources"`, `exclude_filter="pruebas/*"`, `export_path="../../dist/Gaia-AI.exe"`, `binary_format/embed_pck=true`, `application/product_name="Gaia-AI"`.
- [ ] **Step 3:** `"$G" --headless --path godot/gaia-visor --export-release "Windows Desktop" ../../dist/Gaia-AI.exe` → exit 0 y `dist/Gaia-AI.exe` existe.
- [ ] **Step 4: Verificación (Review Focus 2, 3 y 4):**
  - Con el servidor apagado, abrir `dist/Gaia-AI.exe` → aparece la intro; a los ≤10 s el puerto 8765 escucha; "Generar" va en vivo (Origen = "Generado en vivo"); cerrar → el puerto queda libre.
  - Copiar el `.exe` al Escritorio y abrirlo → la intro y el visor funcionan con mapas guardados y no aparece ningún diálogo de error.
- [ ] **Step 5: Commit** `build: preset de exportacion Windows y dist ignorado`

### Task 9: Cierre del Sprint 9

- [ ] **Step 1:** `python scrips/generar_grafo.py`.
- [ ] **Step 2:** `docs/bitacora.md`: decisiones (el `.exe` lanza Python en vez de empaquetarlo; la cámara gira en lugar del bloque; `iniciar_demo.bat` queda reemplazado por el `.exe`; el cambio de paleta a noche). `CLAUDE.md`: estado actualizado.
- [ ] **Step 3:** `python -m pytest test/ -q` y las 4 pruebas de `pruebas/` → todo OK.
- [ ] **Step 4:** Commit `docs: cierre del Sprint 9` y `git tag sprint-09`.

---

## Fuera de alcance

- Girar con el mouse (arrastrar).
- Cualquier cosa no listada aquí: Fernando pidió no hacer nada fuera del plan salvo que sea estrictamente necesario (y en ese caso, reportarlo).

## Supuesto

El `.exe` vive dentro del repo (`dist/`) en la laptop de la expo, con Python y las dependencias instaladas.
