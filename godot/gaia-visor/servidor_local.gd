extends Node
# Autoload: enciende el servidor de Python si no está vivo y lo apaga al salir.
# Solo apaga el servidor que este proceso lanzó (pid > 0).

const URL := "http://127.0.0.1:8765"

var pid := -1


# Sube carpetas desde `desde` hasta encontrar src/servidor.py. Devuelve la ruta o "".
static func buscar_repo(desde: String, niveles := 5) -> String:
		var carpeta := desde.replace("\\", "/").rstrip("/")
		for i in range(niveles + 1):
				if FileAccess.file_exists(carpeta + "/src/servidor.py"):
						return carpeta
				var padre := carpeta.get_base_dir()
				if padre == carpeta or padre == "":
						break
				carpeta = padre
		return ""


static func carpeta_inicio() -> String:
		if OS.has_feature("editor"):
				return ProjectSettings.globalize_path("res://")
		return OS.get_executable_path().get_base_dir()


# pythonw.exe junto al Python real (no el alias de la Store), para que el PID sea el correcto.
func resolver_pythonw() -> String:
		var salida := []
		var codigo := OS.execute("python", ["-c", "import sys; print(sys.executable)"], salida)
		if codigo != 0 or salida.is_empty():
				return ""
		var exe := String(salida[0]).strip_edges().replace("\\", "/")
		if exe == "":
				return ""
		var pythonw := exe.get_base_dir() + "/pythonw.exe"
		return pythonw if FileAccess.file_exists(pythonw) else ""


func _ready() -> void:
		if DisplayServer.get_name() == "headless":
				return
		var http := HTTPRequest.new()
		http.timeout = 1.5
		add_child(http)
		http.request_completed.connect(_al_responder_salud.bind(http))
		if http.request(URL + "/salud") != OK:
				_lanzar()


func _al_responder_salud(resultado: int, codigo: int, _cab: PackedStringArray, _cuerpo: PackedByteArray, http: HTTPRequest) -> void:
		http.queue_free()
		if resultado == HTTPRequest.RESULT_SUCCESS and codigo == 200:
				return
		_lanzar()


func _lanzar() -> void:
		var repo := buscar_repo(carpeta_inicio())
		if repo == "":
				return
		var pythonw := resolver_pythonw()
		if pythonw == "":
				return
		pid = OS.create_process(pythonw, [repo + "/src/servidor.py"])


func _apagar() -> void:
		if pid > 0:
				OS.kill(pid)
				pid = -1


func _notification(que: int) -> void:
		if que == NOTIFICATION_WM_CLOSE_REQUEST:
				_apagar()


func _exit_tree() -> void:
		_apagar()
