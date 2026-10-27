extends SceneTree

const Afirmar := preload("res://pruebas/afirmar.gd")


func _initialize() -> void:
		var Lanzador = load("res://servidor_local.gd")
		var base := ProjectSettings.globalize_path("user://prueba_repo")
		DirAccess.make_dir_recursive_absolute(base + "/a/b")
		DirAccess.make_dir_recursive_absolute(base + "/src")
		var f := FileAccess.open(base + "/src/servidor.py", FileAccess.WRITE)
		f.close()

		var hallado: String = Lanzador.buscar_repo(base + "/a/b")
		Afirmar.afirmar(hallado.ends_with("prueba_repo"), "encuentra repo subiendo carpetas: " + hallado)

		DirAccess.make_dir_recursive_absolute(base + "/v/1/2/3/4/5/6")
		DirAccess.make_dir_recursive_absolute(base + "/v/1/2/3/4/5/6/7")
		var vacio: String = Lanzador.buscar_repo(base + "/v/1/2/3/4/5/6/7", 5)
		Afirmar.afirmar(vacio == "", "sin repo en 5 niveles devuelve vacio: " + vacio)

		var real: String = Lanzador.buscar_repo(ProjectSettings.globalize_path("res://"))
		Afirmar.afirmar(FileAccess.file_exists(real + "/src/servidor.py") and real != "", "encuentra la raiz real")

		# Limpieza
		for ruta in ["/v/1/2/3/4/5/6/7", "/v/1/2/3/4/5/6", "/v/1/2/3/4/5", "/v/1/2/3/4", "/v/1/2/3", "/v/1/2", "/v/1", "/v", "/a/b", "/a", "/src/servidor.py", "/src", ""]:
				DirAccess.remove_absolute(base + ruta)
		Afirmar.terminar("prueba_servidor_local")
