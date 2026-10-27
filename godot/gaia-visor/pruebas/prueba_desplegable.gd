extends SceneTree

const Afirmar := preload("res://pruebas/afirmar.gd")


func _initialize() -> void:
		var d: Node = load("res://desplegable.tscn").instantiate()
		d.titulo = "Pregunta"
		d.texto = "Respuesta"
		root.add_child(d)
		await process_frame

		var encabezado: Button = d.get_node("Encabezado")
		var cuerpo: Label = d.get_node("Cuerpo")
		Afirmar.afirmar(not cuerpo.visible, "el cuerpo empieza oculto")
		Afirmar.afirmar(encabezado.text.begins_with("+"), "el encabezado empieza con +: " + encabezado.text)
		Afirmar.afirmar(cuerpo.text == "Respuesta", "el cuerpo muestra el texto")

		d.alternar()
		Afirmar.afirmar(cuerpo.visible, "tras alternar el cuerpo se ve")
		Afirmar.afirmar(encabezado.text.begins_with("–"), "tras alternar empieza con guion largo: " + encabezado.text)

		d.alternar()
		Afirmar.afirmar(not cuerpo.visible, "tras otro alternar vuelve a ocultarse")
		Afirmar.afirmar(encabezado.text.begins_with("+"), "vuelve a +")

		encabezado.pressed.emit()
		Afirmar.afirmar(cuerpo.visible, "pulsar el encabezado alterna")
		Afirmar.terminar("prueba_desplegable")
