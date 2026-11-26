class_name Exportador
extends RefCounted
# Guarda el terreno actual para Roblox, Unity y Blender.
# Cada exportar_* devuelve la ruta escrita, o "" si algo falla.

const STUDS_POR_PIXEL := 4
const MAXIMO_8_BITS := 255
const MAXIMO_16_BITS := 65535
const OBJETOS_OBJ := ["terreno", "base"]
# Godot tiene el frente en sentido horario y el OBJ en antihorario: se invierte cada triángulo.
const ORDEN_INVERTIDO := [0, 2, 1]
const ACENTOS := {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}

const LEEME_DATOS := """Gaia-AI: terreno exportado
Clase: %s
Semilla: %d
Suavizado (sigma): %.1f
Mapa: %d x %d
Las alturas son relativas (de 0 a 1), no son metros.
"""
const LEEME_ROBLOX := """
Roblox Studio (archivo _roblox.png, 8 bits en escala de grises)
1. En el Terrain Editor abre la pestaña Import y elige el PNG como mapa de alturas.
2. En el importador un píxel equivale a 4 studs.
3. Tamaño: X = Z = %d studs, Y = %.1f studs (conserva la proporción del visor).
"""
const LEEME_UNITY := """
Unity (archivo _unity.raw, 16 bits sin encabezado)
1. Crea un Terrain y abre Terrain Settings -> Import Raw.
2. Depth: 16 bit. Byte Order: Windows. Width = %d, Height = %d.
3. Flip Vertically: actívalo o no según veas el relieve.
4. Tamaño del terreno: X = Z = %d, Y = %.1f (misma proporción que el visor).
Si Unity exige una resolución 2^n + 1, usa 129 o 257 y deja que remuestree.
"""
const LEEME_BLENDER := """
Blender (archivo _blender.obj, con los objetos terreno y base)
1. File -> Import -> Wavefront (.obj).
2. Deja Forward -Z y Up Y (los valores por defecto). No rotes el modelo.
"""


static func exportar_roblox(terreno: MeshInstance3D, info: Dictionary, carpeta: String) -> String:
		var base := _preparar(terreno, info, carpeta)
		if base.is_empty():
				return ""
		var mapa: Dictionary = terreno.mapa_actual
		var imagen := Image.create_from_data(mapa.ancho, mapa.alto, false, Image.FORMAT_L8,
				_alturas_en_bytes(normalizar_alturas(mapa.datos)))
		var ruta := base + "_roblox.png"
		return ruta if imagen.save_png(ruta) == OK else ""


static func exportar_unity(terreno: MeshInstance3D, info: Dictionary, carpeta: String) -> String:
		var base := _preparar(terreno, info, carpeta)
		if base.is_empty():
				return ""
		var ruta := base + "_unity.raw"
		var archivo := FileAccess.open(ruta, FileAccess.WRITE)
		if archivo == null:
				return ""
		for valor in normalizar_alturas(terreno.mapa_actual.datos):
				archivo.store_16(roundi(valor * MAXIMO_16_BITS))
		archivo.close()
		return ruta


static func exportar_blender(terreno: MeshInstance3D, info: Dictionary, carpeta: String) -> String:
		var base := _preparar(terreno, info, carpeta)
		if base.is_empty():
				return ""
		var ruta := base + "_blender.obj"
		var archivo := FileAccess.open(ruta, FileAccess.WRITE)
		if archivo == null:
				return ""
		var mapa: Dictionary = terreno.mapa_actual
		var malla: ArrayMesh = terreno.construir_bloque(
				{"ancho": mapa.ancho, "alto": mapa.alto, "datos": normalizar_alturas(mapa.datos)})
		# Los índices del OBJ son globales: cada objeto sigue la cuenta del anterior.
		var desplazamiento := {"v": 0, "vt": 0}
		for i in OBJETOS_OBJ.size():
				_escribir_objeto(archivo, OBJETOS_OBJ[i], malla.surface_get_arrays(i), desplazamiento)
		archivo.close()
		return ruta


# Min-max a 0..1; si todos los valores son iguales, todo en 0.
static func normalizar_alturas(datos: PackedFloat32Array) -> PackedFloat32Array:
		var minimo := INF
		var maximo := -INF
		for valor in datos:
				minimo = minf(minimo, valor)
				maximo = maxf(maximo, valor)
		var normalizados := PackedFloat32Array()
		normalizados.resize(datos.size())
		var rango := maximo - minimo
		if rango <= 0.0:
				return normalizados
		for i in datos.size():
				normalizados[i] = (datos[i] - minimo) / rango
		return normalizados


static func _alturas_en_bytes(alturas: PackedFloat32Array) -> PackedByteArray:
		var bytes := PackedByteArray()
		bytes.resize(alturas.size())
		for i in alturas.size():
				bytes[i] = roundi(alturas[i] * MAXIMO_8_BITS)
		return bytes


static func _nombre_base(info: Dictionary) -> String:
		var clase: String = info.clase
		for acento in ACENTOS:
				clase = clase.replace(acento, ACENTOS[acento])
		return "%s_%d_s%.1f" % [clase, info.semilla, info.sigma]


# Crea la carpeta y escribe el LEEME. Devuelve la ruta sin extensión, o "" si falla.
static func _preparar(terreno: MeshInstance3D, info: Dictionary, carpeta: String) -> String:
		var existe := DirAccess.dir_exists_absolute(carpeta)
		if not existe and DirAccess.make_dir_recursive_absolute(carpeta) != OK:
				return ""
		var base := carpeta + "/" + _nombre_base(info)
		if not _escribir_leeme(base + "_LEEME.txt", terreno, info):
				return ""
		return base


static func _escribir_leeme(ruta: String, terreno: MeshInstance3D, info: Dictionary) -> bool:
		var archivo := FileAccess.open(ruta, FileAccess.WRITE)
		if archivo == null:
				return false
		archivo.store_string(_texto_leeme(terreno, info))
		archivo.close()
		return true


static func _texto_leeme(terreno: MeshInstance3D, info: Dictionary) -> String:
		var ancho: int = terreno.mapa_actual.ancho
		var alto: int = terreno.mapa_actual.alto
		var altura: float = terreno.escala_altura * terreno.multiplicador_altura
		return LEEME_DATOS % [info.clase, info.semilla, info.sigma, ancho, alto] \
				+ LEEME_ROBLOX % [ancho * STUDS_POR_PIXEL, altura * STUDS_POR_PIXEL] \
				+ LEEME_UNITY % [ancho, alto, ancho, altura] \
				+ LEEME_BLENDER


static func _escribir_objeto(archivo: FileAccess, nombre: String, arrays: Array, desplazamiento: Dictionary) -> void:
		var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var normales: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
		var uvs := PackedVector2Array()
		if arrays[Mesh.ARRAY_TEX_UV] != null:
				uvs = arrays[Mesh.ARRAY_TEX_UV]
		archivo.store_line("o " + nombre)
		for v in vertices:
				archivo.store_line("v %.5f %.5f %.5f" % [v.x, v.y, v.z])
		for uv in uvs:
				archivo.store_line("vt %.5f %.5f" % [uv.x, uv.y])
		for n in normales:
				archivo.store_line("vn %.5f %.5f %.5f" % [n.x, n.y, n.z])
		_escribir_caras(archivo, _indices_de(arrays, vertices.size()), desplazamiento, not uvs.is_empty())
		desplazamiento.v += vertices.size()
		desplazamiento.vt += uvs.size()


# Una superficie sin índices (las paredes) se lee de tres en tres vértices.
static func _indices_de(arrays: Array, cantidad_vertices: int) -> PackedInt32Array:
		if arrays[Mesh.ARRAY_INDEX] != null:
				return arrays[Mesh.ARRAY_INDEX]
		var secuencia := PackedInt32Array()
		for i in cantidad_vertices:
				secuencia.append(i)
		return secuencia


static func _escribir_caras(archivo: FileAccess, indices: PackedInt32Array, desplazamiento: Dictionary, con_uv: bool) -> void:
		for inicio in range(0, indices.size(), 3):
				var cara := PackedStringArray()
				for k in ORDEN_INVERTIDO:
						cara.append(_referencia_de_cara(indices[inicio + k], desplazamiento, con_uv))
				archivo.store_line("f " + " ".join(cara))


# Índices de 1 en adelante: v/vt/vn con UV, v//vn sin UV.
static func _referencia_de_cara(indice: int, desplazamiento: Dictionary, con_uv: bool) -> String:
		var vertice: int = indice + 1 + desplazamiento.v
		if con_uv:
				return "%d/%d/%d" % [vertice, indice + 1 + desplazamiento.vt, vertice]
		return "%d//%d" % [vertice, vertice]
