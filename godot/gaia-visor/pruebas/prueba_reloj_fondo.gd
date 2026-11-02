extends SceneTree

const Afirmar := preload("res://pruebas/afirmar.gd")


func _initialize() -> void:
		var reloj: GDScript = load("res://reloj_fondo.gd")
		# Sube de 0 a 3600 s y luego baja: al pasar una hora el fondo se recorre al revés.
		Afirmar.afirmar(is_equal_approx(reloj.ida_y_vuelta(0.0, 3600.0), 0.0), "empieza en 0")
		Afirmar.afirmar(is_equal_approx(reloj.ida_y_vuelta(1800.0, 3600.0), 1800.0), "a media hora va de ida")
		Afirmar.afirmar(is_equal_approx(reloj.ida_y_vuelta(3600.0, 3600.0), 3600.0), "a la hora llega al tope")
		Afirmar.afirmar(is_equal_approx(reloj.ida_y_vuelta(3700.0, 3600.0), 3500.0), "pasada la hora regresa")
		Afirmar.afirmar(is_equal_approx(reloj.ida_y_vuelta(7200.0, 3600.0), 0.0), "a las dos horas vuelve a 0")
		Afirmar.afirmar(is_equal_approx(reloj.ida_y_vuelta(7300.0, 3600.0), 100.0), "y empieza otra ida")

		Afirmar.afirmar(ProjectSettings.get_setting("autoload/RelojFondo", "") == "*res://reloj_fondo.gd",
				"RelojFondo es autoload")
		Afirmar.afirmar(ProjectSettings.has_setting("shader_globals/tiempo_fondo"), "existe el global tiempo_fondo")
		Afirmar.terminar("prueba_reloj_fondo")
