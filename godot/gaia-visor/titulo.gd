extends Control
# Título de tierra con pasto: el texto se dibuja en un SubViewport y
# titulo.gdshader lo convierte en tierra con pasto encima.

@export var texto := "Gaia-AI":
		set(valor):
				texto = valor
				if is_node_ready():
						_aplicar_texto()

@onready var _etiqueta: Label = $SubViewport/Texto
@onready var _vista: SubViewport = $SubViewport
@onready var _imagen: TextureRect = $Imagen


func _ready() -> void:
		# El shader lee el alfa del texto desde su propio uniform (ver titulo.gdshader).
		(_imagen.material as ShaderMaterial).set_shader_parameter("textura", _vista.get_texture())
		_aplicar_texto()


# Hace crecer las briznas de pasto una sola vez (uniform crecimiento 0 a 1).
func crecer_pasto(duracion := 0.8) -> void:
		var material := _imagen.material as ShaderMaterial
		material.set_shader_parameter("crecimiento", 0.0)
		var tween := create_tween()
		tween.tween_method(
				func(v: float) -> void: material.set_shader_parameter("crecimiento", v),
				0.0, 1.0, duracion
		).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)


func _aplicar_texto() -> void:
		_etiqueta.text = texto
		_vista.render_target_update_mode = SubViewport.UPDATE_ONCE
