extends SceneTree

const Afirmar := preload("res://pruebas/afirmar.gd")


func _initialize() -> void:
		var mundo: Node = load("res://mundo.tscn").instantiate()
		root.add_child(mundo)
		current_scene = mundo
		await process_frame
		await process_frame

		var ui: Node = mundo.get_node("Interfaz")
		for nombre in ["Sigma", "Inspeccionar", "Generar", "Menu"]:
				var c: Control = ui.get_node("%" + nombre)
				Afirmar.afirmar(c.focus_mode == Control.FOCUS_NONE, "%s no toma foco" % nombre)
		for boton in ui.get_node("%Clases").get_children():
				Afirmar.afirmar(boton.focus_mode == Control.FOCUS_NONE, "boton de clase no toma foco")
		Afirmar.afirmar(ui.get_node("%Semilla").focus_mode == Control.FOCUS_ALL, "la semilla si toma foco")

		# Con el deslizador arrastrado, las flechas no deben cambiarlo.
		var sigma: HSlider = ui.get_node("%Sigma")
		sigma.grab_focus()
		var antes := sigma.value
		var e := InputEventKey.new()
		e.keycode = KEY_RIGHT
		e.physical_keycode = KEY_RIGHT
		e.pressed = true
		root.push_input(e)
		await process_frame
		Afirmar.afirmar(is_equal_approx(sigma.value, antes), "flecha derecha no cambia sigma")
		Afirmar.terminar("prueba_foco_visor")
