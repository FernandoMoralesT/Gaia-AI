extends SceneTree

const Afirmar := preload("res://pruebas/afirmar.gd")

const CARPETA := "user://prueba_exportador"
const INFO := {"clase": "montaña", "semilla": 42, "sigma": 2.0}
const BASE := "montana_42_s2.0"
const ANCHO := 4
const ALTO := 3
const INDICE_MAXIMO := 3
const INDICE_MINIMO := 5
const EXTENSIONES := {"roblox": ".png", "unity": ".raw", "blender": ".obj"}

var terreno: MeshInstance3D


func _initialize() -> void:
		terreno = load("res://terreno.gd").new()
		_probar_exportaciones()
		_probar_caso_plano()
		_probar_carpeta_invalida()
		_limpiar()
		terreno.free()
		await _probar_menu()
		Afirmar.terminar("prueba_exportador")


func _exportadores() -> Dictionary:
		return {
				"roblox": Exportador.exportar_roblox,
				"unity": Exportador.exportar_unity,
				"blender": Exportador.exportar_blender,
		}


# Mapa de 4x3 con valores entre 0.2 y 0.8: obliga a normalizar.
func _datos_con_relieve() -> PackedFloat32Array:
		var datos := _datos_planos()
		datos[INDICE_MAXIMO] = 0.8
		datos[INDICE_MINIMO] = 0.2
		return datos


func _datos_planos() -> PackedFloat32Array:
		var datos := PackedFloat32Array()
		datos.resize(ANCHO * ALTO)
		datos.fill(0.5)
		return datos


func _mapa(datos: PackedFloat32Array) -> Dictionary:
		return {"ancho": ANCHO, "alto": ALTO, "datos": datos}


func _probar_exportaciones() -> void:
		terreno.mapa_actual = _mapa(_datos_con_relieve())
		var exportadores := _exportadores()
		for nombre in exportadores:
				var ruta: String = exportadores[nombre].call(terreno, INFO, CARPETA)
				Afirmar.afirmar(ruta == "%s/%s_%s%s" % [CARPETA, BASE, nombre, EXTENSIONES[nombre]],
						"ruta de " + nombre + ": " + ruta)
				Afirmar.afirmar(FileAccess.file_exists(ruta), "existe el archivo de " + nombre)
				_probar_leeme(nombre)
		_probar_png("%s/%s_roblox.png" % [CARPETA, BASE])
		_probar_raw("%s/%s_unity.raw" % [CARPETA, BASE])
		_probar_obj("%s/%s_blender.obj" % [CARPETA, BASE])


# Los tres formatos escriben el mismo LEEME; se borra para comprobar que cada uno lo deja escrito.
func _probar_leeme(nombre: String) -> void:
		var ruta := "%s/%s_LEEME.txt" % [CARPETA, BASE]
		Afirmar.afirmar(FileAccess.file_exists(ruta), "LEEME tras exportar " + nombre)
		var texto := FileAccess.get_file_as_string(ruta)
		for palabra in ["Roblox", "Unity", "Blender", "montaña", "42", "4 x 3"]:
				Afirmar.afirmar(texto.contains(palabra), "LEEME menciona " + palabra)
		DirAccess.remove_absolute(ruta)


func _probar_png(ruta: String) -> void:
		var imagen := Image.new()
		Afirmar.afirmar(imagen.load(ruta) == OK, "el PNG se abre")
		Afirmar.afirmar(imagen.get_width() == ANCHO and imagen.get_height() == ALTO, "PNG de 4x3")
		Afirmar.afirmar(imagen.get_format() == Image.FORMAT_L8, "PNG en FORMAT_L8")
		Afirmar.afirmar(imagen.get_pixel(3, 0).r8 == 255, "PNG: maximo en 255")
		Afirmar.afirmar(imagen.get_pixel(1, 1).r8 == 0, "PNG: minimo en 0")


func _probar_raw(ruta: String) -> void:
		var bytes := FileAccess.get_file_as_bytes(ruta)
		Afirmar.afirmar(bytes.size() == ANCHO * ALTO * 2, "RAW de 4*3*2 bytes")
		Afirmar.afirmar(bytes.decode_u16(INDICE_MAXIMO * 2) == 65535, "RAW: maximo en 65535")
		Afirmar.afirmar(bytes.decode_u16(INDICE_MINIMO * 2) == 0, "RAW: minimo en 0")


func _probar_obj(ruta: String) -> void:
		var texto := FileAccess.get_file_as_string(ruta)
		var inicio_base := texto.find("o base")
		Afirmar.afirmar(texto.contains("o terreno"), "OBJ con o terreno")
		Afirmar.afirmar(inicio_base > texto.find("o terreno"), "OBJ con o base despues del terreno")
		Afirmar.afirmar(not texto.contains(","), "OBJ sin comas decimales")
		var vertices_terreno := _vertices_en(texto.substr(0, inicio_base))
		Afirmar.afirmar(vertices_terreno == ANCHO * ALTO, "12 vertices en terreno: %d" % vertices_terreno)
		_probar_formato_vertices(texto)
		_probar_indices_de_caras(texto)
		_probar_caras_hacia_afuera(texto)


# Por el orden invertido, la normal geometrica de cada cara debe coincidir con su vn.
func _probar_caras_hacia_afuera(texto: String) -> void:
		var vertices: Array[Vector3] = []
		var normales: Array[Vector3] = []
		var caras: PackedStringArray = []
		for linea in texto.split("\n"):
				if linea.begins_with("v "):
						vertices.append(_vector_de(linea))
				elif linea.begins_with("vn "):
						normales.append(_vector_de(linea))
				elif linea.begins_with("f "):
						caras.append(linea)
		Afirmar.afirmar(caras.size() > 0, "el OBJ tiene caras")
		for cara in caras:
				var p := cara.substr(2).split(" ")
				var a := vertices[int(p[0].split("/")[0]) - 1]
				var b := vertices[int(p[1].split("/")[0]) - 1]
				var c := vertices[int(p[2].split("/")[0]) - 1]
				var normal := normales[int(p[0].split("/")[2]) - 1]
				Afirmar.afirmar((b - a).cross(c - a).dot(normal) > 0.0, "cara hacia afuera: " + cara)


func _vector_de(linea: String) -> Vector3:
		var t := linea.split(" ")
		return Vector3(float(t[1]), float(t[2]), float(t[3]))


func _vertices_en(texto: String) -> int:
		var cuenta := 0
		for linea in texto.split("\n"):
				if linea.begins_with("v "):
						cuenta += 1
		return cuenta


func _probar_formato_vertices(texto: String) -> void:
		var patron := RegEx.create_from_string("^v -?\\d+\\.\\d+ -?\\d+\\.\\d+ -?\\d+\\.\\d+$")
		for linea in texto.split("\n"):
				if linea.begins_with("v "):
						Afirmar.afirmar(patron.search(linea) != null, "vertice con punto decimal: " + linea)


# Los indices del OBJ son globales y empiezan en 1.
func _probar_indices_de_caras(texto: String) -> void:
		var total := _vertices_en(texto)
		for linea in texto.split("\n"):
				if linea.begins_with("f "):
						_probar_cara(linea, total)


func _probar_cara(linea: String, total: int) -> void:
		for elemento in linea.substr(2).split(" "):
				var indice := int(elemento.split("/")[0])
				Afirmar.afirmar(indice >= 1 and indice <= total, "indice de cara en rango: " + linea)


func _probar_caso_plano() -> void:
		terreno.mapa_actual = _mapa(_datos_planos())
		var imagen := Image.new()
		imagen.load(Exportador.exportar_roblox(terreno, INFO, CARPETA))
		for y in ALTO:
				for x in ANCHO:
						Afirmar.afirmar(imagen.get_pixel(x, y).r8 == 0, "PNG plano en 0")
		var bytes := FileAccess.get_file_as_bytes(Exportador.exportar_unity(terreno, INFO, CARPETA))
		for i in ANCHO * ALTO:
				Afirmar.afirmar(bytes.decode_u16(i * 2) == 0, "RAW plano en 0")


func _probar_carpeta_invalida() -> void:
		var archivo := FileAccess.open(CARPETA + "/archivo.txt", FileAccess.WRITE)
		archivo.close()
		var carpeta := CARPETA + "/archivo.txt/sub"
		var exportadores := _exportadores()
		for nombre in exportadores:
				Afirmar.afirmar(exportadores[nombre].call(terreno, INFO, carpeta) == "",
						"carpeta invalida en " + nombre)


func _probar_menu() -> void:
		var mundo: Node = load("res://mundo.tscn").instantiate()
		root.add_child(mundo)
		current_scene = mundo
		await process_frame
		var interfaz: Node = mundo.get_node("Interfaz")
		var menu := interfaz.get_node_or_null("%Exportar") as MenuButton
		Afirmar.afirmar(menu != null, "Exportar existe y es un MenuButton")
		if menu == null:
				return
		var popup := menu.get_popup()
		var textos := ["PNG 8 bits (Roblox)", "RAW 16 bits (Unity)", "OBJ (Blender)"]
		Afirmar.afirmar(popup.item_count == textos.size(), "el menu tiene 3 elementos")
		for i in textos.size():
				Afirmar.afirmar(popup.get_item_text(i) == textos[i], "texto del elemento %d" % i)
		Afirmar.afirmar(menu.focus_mode == Control.FOCUS_NONE, "Exportar no toma foco")
		Afirmar.afirmar(popup.id_pressed.get_connections().size() > 0, "el menu esta conectado")
		Afirmar.afirmar(popup.get_theme_color("font_color").to_html(false) == "f4f0e6", "el menu usa caliza del tema")
		Afirmar.afirmar(not menu.disabled, "Exportar empieza habilitado")
		# Con el servidor "activo" la petición queda en curso y el botón debe seguir deshabilitado.
		interfaz.servidor_activo = true
		interfaz.generar()
		Afirmar.afirmar(menu.disabled, "Exportar deshabilitado mientras se genera")


func _limpiar() -> void:
		var carpeta := DirAccess.open(CARPETA)
		if carpeta == null:
				return
		for nombre in carpeta.get_files():
				carpeta.remove(nombre)
		DirAccess.remove_absolute(CARPETA)
