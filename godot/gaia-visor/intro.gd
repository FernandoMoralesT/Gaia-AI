extends Control
# Escena de inicio: título con pasto y cuatro botones.


func _ready() -> void:
		%Explorar.pressed.connect(func(): get_tree().change_scene_to_file("res://mundo.tscn"))
		%Info.pressed.connect(func(): get_tree().change_scene_to_file("res://info.tscn"))
		%Acerca.pressed.connect(func(): get_tree().change_scene_to_file("res://acerca.tscn"))
		# Al cerrar, el autoload ServidorLocal apaga pythonw en su _exit_tree.
		%Salir.pressed.connect(func(): get_tree().quit())
		%Titulo.crecer_pasto()
		%Explorar.grab_focus()
