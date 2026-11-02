extends Node
# Autoload: F11 alterna pantalla completa en cualquier escena.


static func modo_siguiente(modo: DisplayServer.WindowMode) -> DisplayServer.WindowMode:
		if modo == DisplayServer.WINDOW_MODE_FULLSCREEN or modo == DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN:
				return DisplayServer.WINDOW_MODE_WINDOWED
		return DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN


func alternar() -> void:
		DisplayServer.window_set_mode(modo_siguiente(DisplayServer.window_get_mode()))


func _unhandled_input(evento: InputEvent) -> void:
		if evento.is_action_pressed("pantalla_completa"):
				get_viewport().set_input_as_handled()
				alternar()
