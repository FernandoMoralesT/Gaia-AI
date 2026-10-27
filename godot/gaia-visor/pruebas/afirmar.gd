extends RefCounted
# Ayudante común de las pruebas headless.

static var fallos := 0


static func afirmar(cond: bool, msg: String) -> void:
		if not cond:
				fallos += 1
				print("FALLO: ", msg)


# Imprime OK si nada falló y termina el proceso con el código adecuado.
static func terminar(nombre: String) -> void:
		if fallos == 0:
				print("OK ", nombre)
		Engine.get_main_loop().quit(0 if fallos == 0 else 1)
