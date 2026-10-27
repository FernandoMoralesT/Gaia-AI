extends Control
# Página con desplegables (info y acerca): "Volver" y Esc regresan a la intro.


func _ready() -> void:
		%Volver.pressed.connect(volver)
		%Volver.grab_focus()


func _unhandled_input(evento: InputEvent) -> void:
		if evento.is_action_pressed("ui_cancel"):
				get_viewport().set_input_as_handled()
				volver()


func volver() -> void:
		get_tree().change_scene_to_file("res://intro.tscn")
