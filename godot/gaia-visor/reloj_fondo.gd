extends Node
# Autoload: reloj del fondo de curvas de nivel. TIME de Godot vuelve a 0 cada
# hora y las curvas saltaban; este reloj sube una hora y luego baja otra, así
# el recorrido se invierte en lugar de reiniciarse.

const PERIODO := 3600.0

var segundos := 0.0


static func ida_y_vuelta(t: float, periodo: float) -> float:
		var m := fposmod(t, 2.0 * periodo)
		return m if m <= periodo else 2.0 * periodo - m


func _process(delta: float) -> void:
		segundos += delta
		RenderingServer.global_shader_parameter_set("tiempo_fondo", ida_y_vuelta(segundos, PERIODO))
