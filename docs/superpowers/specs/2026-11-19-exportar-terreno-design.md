# Exportar el terreno desde el visor (diseño breve)

## Intención
Que Fernando (y quien pruebe el visor) se lleve el terreno actual a Roblox, Unity o Blender con un botón.

## Metas
- Botón "Exportar" en `FilaAjustes` (entre Inspeccionar y Generar) que despliega un menú; cada opción exporta solo ese formato.
- Opciones del menú, con formato y uso: "PNG 8 bits (Roblox)", "RAW 16 bits (Unity)", "OBJ (Blender)".
- Cada exportación escribe también `<base>_LEEME.txt` con los pasos de los tres programas.

## No metas
- Metros reales, STL, GLB, opción "Todos", botón "abrir carpeta" (v1.6.0 del roadmap cubre lo demás).

## Decisiones
- `exportador.gd` (`class_name Exportador`, `RefCounted`, funciones `static`): `exportar_roblox/unity/blender(terreno, info, carpeta)`; devuelven la ruta o "".
- `info = {clase, semilla, sigma}`. Nombre base `<clase sin acentos>_<semilla>_s<sigma %.1f>`.
- Normalización min-max única; el OBJ se construye con `terreno.construir_bloque` sobre el mapa normalizado y con triángulos invertidos (Godot: frente horario; OBJ: antihorario).
- `interfaz.gd` solo conecta el menú, llama al exportador y muestra el resultado en `%Nota`; deshabilita Exportar mientras `ocupado`.
- Carpeta: Documentos del usuario + `/Gaia-AI/exportaciones`.
- `tema.tres`: bloque `PopupMenu` reutilizando StyleBox, colores y fuentes existentes (sin colores ni fuentes nuevas).
- Estilo del repo: 2 tabuladores por nivel.

## Enfoques considerados
1. `MenuButton` nativo con tema `PopupMenu` (elegido): mínimo código, hereda el estilo de Button.
2. Botón + panel propio desplegable: más control visual, mucho más código y foco/clics a mano.
3. Tres botones sueltos: no cumple "un botón con menú".

## Lo que queda al implementador
Textos exactos del LEEME y detalle de estilos del `PopupMenu`.
