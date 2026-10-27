extends MeshInstance3D

@export_file("*.raw") var ruta_raw := "res://mapas/respaldo_volcan.raw"
@export var escala_altura := 20.0
@export var multiplicador_altura := 3.0
@export var tamano_celda := 1.0

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
		mesh = construir_malla(mapa_actual)
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
