extends SceneTree

const Afirmar := preload("res://pruebas/afirmar.gd")


func _tecla_esc() -> void:
		for p in [true, false]:
				var e := InputEventKey.new()
				e.keycode = KEY_ESCAPE
				e.physical_keycode = KEY_ESCAPE
				e.pressed = p
				root.push_input(e)
		await process_frame
		await process_frame


func _initialize() -> void:
		var mundo: Node = load("res://mundo.tscn").instantiate()
		root.add_child(mundo)
		current_scene = mundo
		await process_frame
		await process_frame

		var semilla: LineEdit = mundo.get_node("Interfaz").get_node("%Semilla")
		semilla.grab_focus()
		Afirmar.afirmar(root.gui_get_focus_owner() == semilla, "la semilla tiene foco")

		await _tecla_esc()
		Afirmar.afirmar(current_scene == mundo and mundo.is_inside_tree(), "primer Esc no cambia de escena")
		Afirmar.afirmar(root.gui_get_focus_owner() != semilla, "primer Esc suelta el foco")

		await _tecla_esc()
		await process_frame
		Afirmar.afirmar(current_scene != null and current_scene.name == "Intro", "segundo Esc vuelve a la intro")
		Afirmar.terminar("prueba_esc_semilla")
