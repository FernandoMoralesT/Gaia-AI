extends Node3D
# Cámara orbital: este nodo (Pivote) está en el origen y gira; la hija "Camara"
# se aleja `distancia` sobre su eje Z. El sol no se mueve.

@export var velocidad_giro := 90.0
@export var inclinacion := 30.0
@export var inclinacion_min := 10.0
@export var inclinacion_max := 80.0
@export var distancia := 170.0
@export var distancia_min := 70.0
@export var distancia_max := 260.0
@export var paso_rueda := 12.0

var giro := 0.0


static func limitar(incl: float, dist: float, lim: Dictionary) -> Vector2:
		return Vector2(
				clampf(incl, lim["inclinacion_min"], lim["inclinacion_max"]),
				clampf(dist, lim["distancia_min"], lim["distancia_max"]))


func teclado_libre() -> bool:
		return not (get_viewport().gui_get_focus_owner() is LineEdit)


func _limites() -> Dictionary:
		return {
				"inclinacion_min": inclinacion_min, "inclinacion_max": inclinacion_max,
				"distancia_min": distancia_min, "distancia_max": distancia_max}


func _ready() -> void:
		_colocar()


func _process(delta: float) -> void:
		if teclado_libre():
				giro += Input.get_axis("girar_izq", "girar_der") * velocidad_giro * delta
				inclinacion += Input.get_axis("bajar", "subir") * velocidad_giro * delta
				distancia -= Input.get_axis("alejar", "acercar") * paso_rueda * 4.0 * delta
		_colocar()


func _unhandled_input(evento: InputEvent) -> void:
		if evento is InputEventMouseButton and evento.pressed:
				if evento.button_index == MOUSE_BUTTON_WHEEL_UP:
						distancia -= paso_rueda
				elif evento.button_index == MOUSE_BUTTON_WHEEL_DOWN:
						distancia += paso_rueda
				_colocar()


func _colocar() -> void:
		var v := limitar(inclinacion, distancia, _limites())
		inclinacion = v.x
		distancia = v.y
		giro = fposmod(giro, 360.0) if absf(giro) >= 360.0 else giro
		rotation_degrees = Vector3(-inclinacion, giro, 0.0)
		var camara := get_node_or_null("Camara") as Node3D
		if camara != null:
				camara.position = Vector3(0, 0, distancia)
