extends CanvasLayer

# Paleta noche (ver tema.tres): abismo #0A1235, índigo #33196B, noche #141B3D,
# borde #34408A, bruma #A9B6E0, ocre #E3AE48, musgo #4A8225, caliza #F4F0E6.

# Mismo orden que CLASES en src/dataset/dem_dataset.py.
const CLASES := ["llanura", "lomas", "valle", "montaña", "meseta", "volcán"]
const SEMILLA_MAX := 2147483647
# Los respaldos se generan con scrips/generar_respaldos.py.
const SEMILLA_RESPALDO := 42
const SIGMA_RESPALDO := 2.0
const LADO_MINIMAPA := 240
const NIVELES_CURVAS := 10

@export var terreno: MeshInstance3D

var clase := "volcán"
# Clase con la que se envió la petición en curso.
var clase_pedida := "volcán"
var ocupado := false
var inicio_ms := 0
var info := {}
# Se averigua con /salud; si está apagado, el respaldo sale sin esperar.
var servidor_activo := false
var comprobando := false


func _ready() -> void:
		var grupo := ButtonGroup.new()
		for nombre in CLASES:
				var boton := Button.new()
				boton.text = nombre.capitalize()
				boton.theme_type_variation = &"BotonClase"
				boton.toggle_mode = true
				boton.focus_mode = Control.FOCUS_NONE
				boton.button_group = grupo
				boton.button_pressed = nombre == clase
				boton.pressed.connect(func(): clase = nombre)
				%Clases.add_child(boton)

		# Solo la semilla toma foco; así las flechas mueven únicamente la cámara.
		for c in [%Sigma, %Menu, %Inspeccionar, %Generar]:
				c.focus_mode = Control.FOCUS_NONE
		%Sigma.value_changed.connect(func(v): %ValorSigma.text = "%.1f" % v)
		%Semilla.text_changed.connect(_al_cambiar_semilla)
		%Semilla.text_submitted.connect(func(_t): generar())
		%Generar.pressed.connect(generar)
		%Menu.pressed.connect(volver_al_menu)
		%Inspeccionar.toggled.connect(func(activo): %Inspeccion.visible = activo)
		%Peticion.request_completed.connect(_al_recibir)
		%Salud.request_completed.connect(_al_responder_salud)

		# Mientras el servidor no responda, se vuelve a preguntar cada 3 s.
		var reloj := Timer.new()
		reloj.wait_time = 3.0
		reloj.timeout.connect(_al_vencer_reloj)
		add_child(reloj)
		reloj.start()
		_comprobar_servidor()

		# El terreno ya cargó su mapa inicial (respaldo de volcán) en su _ready.
		info = {"clase": clase, "semilla": SEMILLA_RESPALDO, "sigma": SIGMA_RESPALDO,
				"en_vivo": false, "ms": -1}
		actualizar_inspeccion()


func _input(evento: InputEvent) -> void:
		if evento.is_action_pressed("ui_cancel"):
				get_viewport().set_input_as_handled()
				# Mientras se escribe, Esc solo suelta el campo; el segundo Esc sale.
				var foco := get_viewport().gui_get_focus_owner()
				if foco is LineEdit:
						foco.release_focus()
				else:
						volver_al_menu()


func volver_al_menu() -> void:
		get_tree().change_scene_to_file("res://intro.tscn")


func generar() -> void:
		if ocupado:
				return
		ocupado = true
		%Generar.disabled = true
		%Generar.text = "Generando…"
		inicio_ms = Time.get_ticks_msec()

		if not servidor_activo:
				_usar_respaldo()
				_terminar()
				return
		clase_pedida = clase
		var consulta := "clase=%s&sigma=%s" % [clase.uri_encode(), str(%Sigma.value)]
		if not %Semilla.text.is_empty():
				consulta += "&semilla=" + %Semilla.text
		if %Peticion.request(ServidorLocal.URL + "/terreno?" + consulta) != OK:
				_usar_respaldo()
				_terminar()


func _al_recibir(resultado: int, codigo: int, encabezados: PackedStringArray, cuerpo: PackedByteArray) -> void:
		if resultado == HTTPRequest.RESULT_SUCCESS and codigo == 200 and _cargar_en_vivo(cuerpo):
				var enc := _leer_encabezados(encabezados)
				info = {
						"clase": enc.get("x-clase", clase_pedida.uri_encode()).uri_decode(),
						"semilla": int(enc.get("x-semilla", "0")),
						"sigma": float(enc.get("x-sigma", str(%Sigma.value))),
						"en_vivo": true,
						"ms": Time.get_ticks_msec() - inicio_ms,
				}
				%Nota.visible = false
		else:
				servidor_activo = false
				_usar_respaldo()
		_terminar()


func _cargar_en_vivo(cuerpo: PackedByteArray) -> bool:
		terreno.aplicar_clase(clase_pedida)
		return terreno.cargar_bytes(cuerpo)


func _al_vencer_reloj() -> void:
		if not servidor_activo:
				_comprobar_servidor()


func _comprobar_servidor() -> void:
		if comprobando:
				return
		comprobando = true
		if %Salud.request(ServidorLocal.URL + "/salud") != OK:
				comprobando = false


func _al_responder_salud(resultado: int, codigo: int, _encabezados: PackedStringArray, _cuerpo: PackedByteArray) -> void:
		comprobando = false
		servidor_activo = resultado == HTTPRequest.RESULT_SUCCESS and codigo == 200
		if servidor_activo:
				%Nota.visible = false


func _usar_respaldo() -> void:
		var archivo := clase.replace("á", "a").replace("ñ", "n")
		terreno.aplicar_clase(clase)
		terreno.cargar_archivo("res://mapas/respaldo_%s.raw" % archivo)
		info = {"clase": clase, "semilla": SEMILLA_RESPALDO, "sigma": SIGMA_RESPALDO,
				"en_vivo": false, "ms": -1}
		%Nota.text = "El generador no está activo. Se muestra un mapa guardado de %s." % clase
		%Nota.visible = true


func _terminar() -> void:
		ocupado = false
		%Generar.disabled = false
		%Generar.text = "Generar"
		actualizar_inspeccion()


func _leer_encabezados(encabezados: PackedStringArray) -> Dictionary:
		var resultado := {}
		for linea in encabezados:
				var partes := linea.split(":", true, 1)
				if partes.size() == 2:
						resultado[partes[0].strip_edges().to_lower()] = partes[1].strip_edges()
		return resultado


# Solo dígitos y sin pasar del máximo que acepta el servidor.
func _al_cambiar_semilla(texto: String) -> void:
		var limpio := ""
		for c in texto:
				if c >= "0" and c <= "9":
						limpio += c
		if not limpio.is_empty() and int(limpio) > SEMILLA_MAX:
				limpio = str(SEMILLA_MAX)
		if limpio != texto:
				%Semilla.text = limpio
				%Semilla.caret_column = limpio.length()


# --- Panel de inspección -----------------------------------------------------

func actualizar_inspeccion() -> void:
		var est: Dictionary = terreno.estadisticas()
		if est.is_empty():
				return
		%TituloClase.text = String(info.clase).capitalize()
		%Mapa.texture = ImageTexture.create_from_image(dibujar_minimapa(est.cima))

		for hijo in %Datos.get_children():
				hijo.queue_free()
		_fila("Semilla", str(info.semilla))
		_fila("Suavizado", "%.1f" % info.sigma)
		_fila("Altura media", "%d %%" % roundi(est.media * 100))
		_fila("Rugosidad", "%.3f" % est.rugosidad)
		_fila("Zona alta", "%d %% del área" % roundi(est.zona_alta * 100))
		_fila("Cima", "columna %d, fila %d" % [est.cima.x, est.cima.y])
		_fila("Origen", "Generado en vivo" if info.en_vivo else "Mapa guardado")
		if info.ms >= 0:
				_fila("Tiempo", "%d ms" % info.ms)


func _fila(etiqueta: String, valor: String) -> void:
		var e := Label.new()
		e.text = etiqueta
		e.theme_type_variation = &"Etiqueta"
		var v := Label.new()
		v.text = valor
		v.theme_type_variation = &"Valor"
		%Datos.add_child(e)
		%Datos.add_child(v)


# Mapa topográfico: color por altura y curvas de nivel cada 1/NIVELES_CURVAS.
func dibujar_minimapa(cima: Vector2i) -> Image:
		var mapa: Dictionary = terreno.mapa_actual
		var ancho: int = mapa.ancho
		var alto: int = mapa.alto
		var datos: PackedFloat32Array = mapa.datos
		var material: ShaderMaterial = terreno.material_superficie
		var bajo: Color = material.get_shader_parameter("color_bajo")
		var medio: Color = material.get_shader_parameter("color_medio")
		var cumbre: Color = material.get_shader_parameter("color_alto")
		var tinta := Color("2B2622")
		var marca := Color("E3AE48")

		var n := LADO_MINIMAPA
		var alturas := PackedFloat32Array()
		alturas.resize(n * n)
		for y in n:
				for x in n:
						alturas[y * n + x] = _muestra(datos, ancho, alto,
								float(x) / (n - 1) * (ancho - 1), float(y) / (n - 1) * (alto - 1))

		var img := Image.create(n, n, false, Image.FORMAT_RGB8)
		for y in n:
				for x in n:
						var h := alturas[y * n + x]
						var c := bajo.lerp(medio, smoothstep(0.27, 0.43, h))
						c = c.lerp(cumbre, smoothstep(0.67, 0.83, h))
						var nivel := floori(h * NIVELES_CURVAS)
						var es_curva := (x + 1 < n and floori(alturas[y * n + x + 1] * NIVELES_CURVAS) != nivel) \
								or (y + 1 < n and floori(alturas[(y + 1) * n + x] * NIVELES_CURVAS) != nivel)
						if es_curva:
								c = c.lerp(tinta, 0.7)
						img.set_pixel(x, y, c)

		# Marca de la cima: un punto ocre con borde oscuro.
		var cx := roundi(float(cima.x) / (ancho - 1) * (n - 1))
		var cy := roundi(float(cima.y) / (alto - 1) * (n - 1))
		for dy in range(-4, 5):
				for dx in range(-4, 5):
						var d := dx * dx + dy * dy
						var px := cx + dx
						var py := cy + dy
						if d <= 16 and px >= 0 and px < n and py >= 0 and py < n:
								img.set_pixel(px, py, marca if d <= 6 else tinta)
		return img


# Interpolación bilineal entre los cuatro píxeles vecinos.
func _muestra(datos: PackedFloat32Array, ancho: int, alto: int, fx: float, fy: float) -> float:
		var x0 := mini(floori(fx), ancho - 2)
		var y0 := mini(floori(fy), alto - 2)
		var tx := fx - x0
		var ty := fy - y0
		var arriba := lerpf(datos[y0 * ancho + x0], datos[y0 * ancho + x0 + 1], tx)
		var abajo := lerpf(datos[(y0 + 1) * ancho + x0], datos[(y0 + 1) * ancho + x0 + 1], tx)
		return lerpf(arriba, abajo, ty)
