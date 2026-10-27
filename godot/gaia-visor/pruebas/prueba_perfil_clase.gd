extends SceneTree

const Afirmar := preload("res://pruebas/afirmar.gd")


func _initialize() -> void:
		var terreno: MeshInstance3D = load("res://terreno.gd").new()
		terreno.material_superficie = ShaderMaterial.new()
		terreno.material_paredes = ShaderMaterial.new()

		terreno.aplicar_clase("llanura")
		Afirmar.afirmar(terreno.escala_altura == 4.0, "llanura escala 4")
		terreno.aplicar_clase("volcán")
		Afirmar.afirmar(terreno.escala_altura == 20.0, "volcan escala 20")
		var negro: Color = terreno.material_superficie.get_shader_parameter("color_alto")
		Afirmar.afirmar(negro.is_equal_approx(Color("2A2624")), "volcan cima negra")
		var esc: float = terreno.material_paredes.get_shader_parameter("escala_vertical")
		Afirmar.afirmar(is_equal_approx(esc, 20.0 * terreno.multiplicador_altura), "escala_vertical de paredes")
		terreno.aplicar_clase("montaña")
		var nieve: Color = terreno.material_superficie.get_shader_parameter("color_alto")
		Afirmar.afirmar(nieve.is_equal_approx(Color("D9D9D1")), "montana cima nieve")
		Afirmar.afirmar(terreno.escala_altura == 22.0, "montana escala 22")
		terreno.aplicar_clase("desierto")
		Afirmar.afirmar(terreno.escala_altura == 22.0, "clase desconocida no cambia")

		terreno.free()
		Afirmar.terminar("prueba_perfil_clase")
