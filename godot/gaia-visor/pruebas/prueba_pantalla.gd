extends SceneTree

const Afirmar := preload("res://pruebas/afirmar.gd")


func _initialize() -> void:
		var pantalla: GDScript = load("res://pantalla.gd")
		var ventana := DisplayServer.WINDOW_MODE_WINDOWED
		var completa := DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN
		Afirmar.afirmar(pantalla.modo_siguiente(ventana) == completa, "ventana pasa a pantalla completa")
		Afirmar.afirmar(pantalla.modo_siguiente(completa) == ventana, "pantalla completa exclusiva vuelve a ventana")
		Afirmar.afirmar(pantalla.modo_siguiente(DisplayServer.WINDOW_MODE_FULLSCREEN) == ventana,
				"pantalla completa vuelve a ventana")
		Afirmar.afirmar(pantalla.modo_siguiente(DisplayServer.WINDOW_MODE_MAXIMIZED) == completa,
				"maximizada pasa a pantalla completa")

		# La acción y el autoload viven en el proyecto, así F11 sirve en todas las escenas.
		Afirmar.afirmar(ProjectSettings.has_setting("input/pantalla_completa"), "existe la accion pantalla_completa")
		Afirmar.afirmar(ProjectSettings.get_setting("autoload/Pantalla", "") == "*res://pantalla.gd",
				"Pantalla es autoload")

		# La intro en un viewport del tamaño base del proyecto (1152x648).
		var vista := SubViewport.new()
		vista.size = Vector2i(1152, 648)
		root.add_child(vista)
		var intro: Control = load("res://intro.tscn").instantiate()
		vista.add_child(intro)
		Afirmar.afirmar(intro.get_node_or_null("%Salir") is Button, "la intro tiene boton Salir")
		await process_frame
		await process_frame
		for nombre in ["Explorar", "Info", "Acerca", "Salir"]:
				var boton: Control = intro.get_node("%" + nombre)
				var centro := boton.get_global_rect().get_center().x
				Afirmar.afirmar(absf(centro - 576.0) <= 2.0, "%s centrado (centro x %s)" % [nombre, centro])
		var titulo: Control = intro.get_node("%Titulo")
		Afirmar.afirmar(absf(titulo.get_global_rect().get_center().x - 576.0) <= 2.0, "titulo centrado")
		# El texto se dibuja en un SubViewport del ancho de la caja; debe ir centrado dentro.
		var texto: Label = titulo.get_node("SubViewport/Texto")
		Afirmar.afirmar(texto.horizontal_alignment == HORIZONTAL_ALIGNMENT_CENTER, "letras del titulo centradas")
		vista.free()

		Afirmar.terminar("prueba_pantalla")
