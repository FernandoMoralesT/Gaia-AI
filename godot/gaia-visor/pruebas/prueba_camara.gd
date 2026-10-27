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
		var lim: Dictionary = cam._limites()
		Afirmar.afirmar(cam.limitar(95.0, 300.0, lim) == Vector2(80, 260), "limitar maximos")
		Afirmar.afirmar(cam.limitar(0.0, 10.0, lim) == Vector2(10, 110), "limitar minimos")

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

		# A distancia minima la camara nunca queda dentro del bloque (119x119, altura max 66)
		cam.giro = 45.0
		for incl in [10.0, 38.0, 80.0]:
				cam.inclinacion = incl
				cam.distancia = 0.0
				cam._colocar()
				var p: Vector3 = cam.get_node("Camara").global_position
				var dentro := absf(p.x) <= 59.5 and absf(p.z) <= 59.5 and p.y <= 66.0
				Afirmar.afirmar(not dentro, "camara fuera del bloque a inclinacion %s (pos %s)" % [incl, p])

		Afirmar.terminar("prueba_camara")
