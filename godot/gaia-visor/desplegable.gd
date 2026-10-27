extends VBoxContainer
# Sección que se abre y se cierra: encabezado plano "+ título" / "– título"
# y un cuerpo de texto de hasta 620 px de ancho (unos 75 caracteres).

@export var titulo := "":
		set(valor):
				titulo = valor
				if is_node_ready():
						_actualizar()

@export_multiline var texto := "":
		set(valor):
				texto = valor
				if is_node_ready():
						_actualizar()

@onready var _encabezado: Button = $Encabezado
@onready var _cuerpo: Label = $Cuerpo


func _ready() -> void:
		_encabezado.pressed.connect(alternar)
		_actualizar()


func alternar() -> void:
		_cuerpo.visible = not _cuerpo.visible
		_actualizar()


func _actualizar() -> void:
		_encabezado.text = ("– " if _cuerpo.visible else "+ ") + titulo
		_cuerpo.text = texto
