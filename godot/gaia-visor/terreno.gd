extends MeshInstance3D

@export_file("*.raw") var ruta_raw := "res://mapas/volcan_42_s3.raw"
@export var escala_altura := 20.0
@export var multiplicador_altura := 3.0
@export var tamano_celda := 1.0


func _ready() -> void:
		var mapa := leer_raw(ruta_raw)
		if mapa.is_empty():
				return
		mesh = construir_malla(mapa)


func leer_raw(ruta: String) -> Dictionary:
		var f := FileAccess.open(ruta, FileAccess.READ)
		if f == null:
				push_error("No se pudo abrir %s (error %d)" % [ruta, FileAccess.get_open_error()])
				return {}
		var ancho := f.get_32()
		var alto := f.get_32()
		var esperado := 8 + ancho * alto * 4
		if f.get_length() != esperado:
				push_error("Tamaño incorrecto: %d bytes, se esperaban %d" % [f.get_length(), esperado])
				return {}
		var datos := f.get_buffer(ancho * alto * 4).to_float32_array()
		return {"ancho": ancho, "alto": alto, "datos": datos}


func construir_malla(mapa: Dictionary) -> ArrayMesh:
		var ancho: int = mapa.ancho
		var alto: int = mapa.alto
		var datos: PackedFloat32Array = mapa.datos
		var centro := Vector3((ancho - 1) * tamano_celda / 2.0, 0, (alto - 1) * tamano_celda / 2.0)

		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)

		for fila in alto:
				for col in ancho:
						var v := datos[fila * ancho + col]
						var h := v * escala_altura * multiplicador_altura
						st.set_color(Color(v, v, v))
						st.set_uv(Vector2(float(col) / (ancho - 1), float(fila) / (alto - 1)))
						st.add_vertex(Vector3(col * tamano_celda, h, fila * tamano_celda) - centro)

		for fila in alto - 1:
				for col in ancho - 1:
						var a := fila * ancho + col
						var b := a + 1
						var c := a + ancho
						var d := c + 1
						st.add_index(a); st.add_index(b); st.add_index(c)
						st.add_index(b); st.add_index(d); st.add_index(c)

		st.generate_normals()
		return st.commit()
