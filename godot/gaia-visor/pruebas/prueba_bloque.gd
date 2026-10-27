extends SceneTree

const Afirmar := preload("res://pruebas/afirmar.gd")


func _initialize() -> void:
		var terreno: MeshInstance3D = load("res://terreno.gd").new()
		# Mapa 4x3; el 1.0 está en un borde (col 3, fila 0) y el 0.0 en el interior.
		var datos := PackedFloat32Array([
				0.5, 0.5, 0.5, 1.0,
				0.5, 0.0, 0.5, 0.5,
				0.5, 0.5, 0.5, 0.5])
		var malla: ArrayMesh = terreno.construir_bloque({"ancho": 4, "alto": 3, "datos": datos})

		Afirmar.afirmar(malla.get_surface_count() == 2, "dos superficies")
		var sup: Array = malla.surface_get_arrays(0)
		Afirmar.afirmar(sup[Mesh.ARRAY_VERTEX].size() == 12, "superficie 0 con 12 vertices")

		var pared: Array = malla.surface_get_arrays(1)
		var verts: PackedVector3Array = pared[Mesh.ARRAY_VERTEX]
		var normales: PackedVector3Array = pared[Mesh.ARRAY_NORMAL]
		var min_y := INF
		var max_y := -INF
		for v in verts:
				min_y = minf(min_y, v.y)
				max_y = maxf(max_y, v.y)
		Afirmar.afirmar(is_equal_approx(min_y, -terreno.profundidad_base), "min y = -profundidad_base")
		var tope: float = 1.0 * terreno.escala_altura * terreno.multiplicador_altura
		Afirmar.afirmar(is_equal_approx(max_y, tope), "max y = altura maxima")

		var dirs := {"+x": false, "-x": false, "+z": false, "-z": false, "-y": false}
		for n in normales:
				if n.dot(Vector3.RIGHT) > 0.999: dirs["+x"] = true
				if n.dot(Vector3.LEFT) > 0.999: dirs["-x"] = true
				if n.dot(Vector3.BACK) > 0.999: dirs["+z"] = true
				if n.dot(Vector3.FORWARD) > 0.999: dirs["-z"] = true
				if n.dot(Vector3.DOWN) > 0.999: dirs["-y"] = true
		for k in dirs:
				Afirmar.afirmar(dirs[k], "hay normal " + k)

		terreno.free()
		Afirmar.terminar("prueba_bloque")
