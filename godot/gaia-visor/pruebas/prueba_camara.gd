extends SceneTree

const Afirmar := preload("res://pruebas/afirmar.gd")


func _initialize() -> void:
		var cam: Node3D = load("res://camara_orbital.gd").new()
		var camara := Camera3D.new()
		camara.name = "Camara"
		cam.add_child(camara)
		var campo := LineEdit.new()
		root.add_child(cam)
		root.add_child(campo)

		await process_frame
		var lim := {"inclinacion_min": 10.0, "inclinacion_max": 80.0, "distancia_min": 70.0, "distancia_max": 260.0}
		Afirmar.afirmar(cam.limitar(95.0, 300.0, lim) == Vector2(80, 260), "limitar maximos")
		Afirmar.afirmar(cam.limitar(0.0, 10.0, lim) == Vector2(10, 70), "limitar minimos")

		Afirmar.afirmar(cam.teclado_libre(), "teclado libre sin foco")
		campo.grab_focus()
		Afirmar.afirmar(not cam.teclado_libre(), "teclado ocupado con LineEdit enfocado")

		var antes: float = cam.giro
		Input.action_press("girar_der")
		cam._process(1.0)
		Afirmar.afirmar(is_equal_approx(cam.giro, antes), "con LineEdit enfocado no gira")
		campo.release_focus()
		cam._process(1.0)
		Afirmar.afirmar(is_equal_approx(cam.giro, antes + 90.0), "girar_der suma 90 grados en 1 s")
		Input.action_release("girar_der")

		Afirmar.terminar("prueba_camara")
