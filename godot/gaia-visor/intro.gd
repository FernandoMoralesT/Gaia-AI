extends Control
# Escena de inicio: título con pasto y tres botones.


func _ready() -> void:
		%Explorar.pressed.connect(func(): get_tree().change_scene_to_file("res://mundo.tscn"))
		%Info.pressed.connect(func(): get_tree().change_scene_to_file("res://info.tscn"))
		%Acerca.pressed.connect(func(): get_tree().change_scene_to_file("res://acerca.tscn"))
		%Titulo.crecer_pasto()
		%Explorar.grab_focus()
