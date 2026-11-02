extends SceneTree

const Afirmar := preload("res://pruebas/afirmar.gd")


func _initialize() -> void:
		# Solo se instancia, sin agregarla al árbol: no corre _ready ni pide terreno.
		var mundo: Node = load("res://mundo.tscn").instantiate()
		var sol := mundo.get_node("Sol") as DirectionalLight3D
		var relleno := mundo.get_node("Relleno") as DirectionalLight3D

		Afirmar.afirmar(sol.shadow_enabled, "el sol proyecta sombra")
		Afirmar.afirmar(not relleno.shadow_enabled, "el relleno no proyecta sombra")
		# Distancia máxima de cámara (260) + diagonal del bloque (~170).
		Afirmar.afirmar(sol.directional_shadow_max_distance >= 400.0,
				"la sombra cubre la camara a distancia maxima")

		mundo.free()
		Afirmar.terminar("prueba_sombras")
