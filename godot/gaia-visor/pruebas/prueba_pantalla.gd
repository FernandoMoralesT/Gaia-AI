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

		var intro: Node = load("res://intro.tscn").instantiate()
		Afirmar.afirmar(intro.get_node_or_null("%Salir") is Button, "la intro tiene boton Salir")
		intro.free()

		Afirmar.terminar("prueba_pantalla")
