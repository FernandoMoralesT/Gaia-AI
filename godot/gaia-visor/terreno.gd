extends MeshInstance3D

@export_file("*.raw") var ruta_raw := "res://mapas/respaldo_volcan.raw"
@export var escala_altura := 20.0
@export var multiplicador_altura := 3.0
@export var tamano_celda := 1.0
@export var profundidad_base := 14.0
@export var material_superficie: ShaderMaterial
@export var material_paredes: ShaderMaterial

var mapa_actual := {}


func _ready() -> void:
		cargar_archivo(ruta_raw)


func cargar_archivo(ruta: String) -> bool:
		if not FileAccess.file_exists(ruta):
				return false
		return cargar_bytes(FileAccess.get_file_as_bytes(ruta))


# Formato .raw: encabezado <u4 (ancho, alto) y datos <f4 fila por fila.
func cargar_bytes(bytes: PackedByteArray) -> bool:
		if bytes.size() < 8:
				return false
		var ancho := bytes.decode_u32(0)
		var alto := bytes.decode_u32(4)
		if ancho < 2 or alto < 2 or bytes.size() != 8 + ancho * alto * 4:
				return false
		var datos := bytes.slice(8).to_float32_array()
		mapa_actual = {"ancho": ancho, "alto": alto, "datos": datos}
		mesh = construir_bloque(mapa_actual)
		return true


# Datos relativos (0 = punto más bajo, 1 = más alto); no son metros.
func estadisticas() -> Dictionary:
		if mapa_actual.is_empty():
				return {}
		var datos: PackedFloat32Array = mapa_actual.datos
		var ancho: int = mapa_actual.ancho
		var n := datos.size()
		var suma := 0.0
		var altos := 0
		var i_cima := 0
		for i in n:
				suma += datos[i]
				if datos[i] > 0.75:
						altos += 1
				if datos[i] > datos[i_cima]:
						i_cima = i
		var media := suma / n
		var varianza := 0.0
		for v in datos:
				varianza += (v - media) * (v - media)
		return {
				"ancho": ancho,
				"alto": mapa_actual.alto,
				"media": media,
				"rugosidad": sqrt(varianza / n),
				"zona_alta": float(altos) / n,
				"cima": Vector2i(i_cima % ancho, i_cima / ancho),
		}


func construir_bloque(mapa: Dictionary) -> ArrayMesh:
		var ancho: int = mapa.ancho
		var alto: int = mapa.alto
		var datos: PackedFloat32Array = mapa.datos
		var centro := Vector3((ancho - 1) * tamano_celda / 2.0, 0, (alto - 1) * tamano_celda / 2.0)
		var escala := escala_altura * multiplicador_altura
		var malla := ArrayMesh.new()

		# Superficie 0: el terreno.
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)

		for fila in alto:
				for col in ancho:
						var v := datos[fila * ancho + col]
						var h := v * escala
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
		st.commit(malla)

		# Superficie 1: cuatro paredes y el fondo. Cada cara usa vértices propios
		# y grupo de suavizado -1 para que las normales queden planas.
		var pared := SurfaceTool.new()
		pared.begin(Mesh.PRIMITIVE_TRIANGLES)
		var fondo_y := -profundidad_base
		var bordes := [
				{"salida": Vector3.FORWARD, "n": ancho, "pos": func(i): return Vector2i(i, 0)},
				{"salida": Vector3.BACK, "n": ancho, "pos": func(i): return Vector2i(i, alto - 1)},
				{"salida": Vector3.LEFT, "n": alto, "pos": func(i): return Vector2i(0, i)},
				{"salida": Vector3.RIGHT, "n": alto, "pos": func(i): return Vector2i(ancho - 1, i)},
		]
		for borde in bordes:
				for i in borde.n - 1:
						var pa: Vector2i = borde.pos.call(i)
						var pb: Vector2i = borde.pos.call(i + 1)
						var va := datos[pa.y * ancho + pa.x]
						var vb := datos[pb.y * ancho + pb.x]
						var a_arriba := Vector3(pa.x * tamano_celda, va * escala, pa.y * tamano_celda) - centro
						var b_arriba := Vector3(pb.x * tamano_celda, vb * escala, pb.y * tamano_celda) - centro
						var a_abajo := Vector3(a_arriba.x, fondo_y, a_arriba.z)
						var b_abajo := Vector3(b_arriba.x, fondo_y, b_arriba.z)
						_agregar_cuadro(pared, [a_arriba, b_arriba, a_abajo, b_abajo],
								[Color(va, va, va), Color(vb, vb, vb), Color(va, va, va), Color(vb, vb, vb)],
								borde.salida)

		var esq_a := Vector3(0, fondo_y, 0) - centro
		var esq_b := Vector3((ancho - 1) * tamano_celda, fondo_y, 0) - centro
		var esq_c := Vector3(0, fondo_y, (alto - 1) * tamano_celda) - centro
		var esq_d := Vector3((ancho - 1) * tamano_celda, fondo_y, (alto - 1) * tamano_celda) - centro
		var negro := Color(0, 0, 0)
		_agregar_cuadro(pared, [esq_a, esq_b, esq_c, esq_d], [negro, negro, negro, negro], Vector3.DOWN)

		pared.generate_normals()
		pared.commit(malla)

		malla.surface_set_material(0, material_superficie)
		malla.surface_set_material(1, material_paredes)
		if material_paredes != null:
				material_paredes.set_shader_parameter("escala_vertical", escala)
		return malla


# Dos triángulos con p = [esquina 0, 1, 2, 3] (disposición en Z); se ordenan para que la cara mire hacia "salida".
func _agregar_cuadro(st: SurfaceTool, p: Array, colores: Array, salida: Vector3) -> void:
		# En Godot el frente es el sentido horario: la normal frontal es (p2 - p0) x (p1 - p0).
		var orden := [0, 1, 2, 1, 3, 2]
		if (p[2] - p[0]).cross(p[1] - p[0]).dot(salida) < 0.0:
				orden = [0, 2, 1, 1, 2, 3]
		for k in orden:
				st.set_smooth_group(-1)
				st.set_color(colores[k])
				st.add_vertex(p[k])
