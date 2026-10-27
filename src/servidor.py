import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import json
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
from inferencia import generar_terreno, raw_a_bytes
from dataset.dem_dataset import CLASES

HOST = "127.0.0.1"  # solo esta máquina; nadie en la red puede conectarse
PUERTO = 8765
SIGMA_MAX = 10.0
SEMILLA_MAX = 2**31 - 1

class ErrorPeticion(Exception):
    """Parámetros inválidos: se responde 400 con el mensaje."""

def leer_parametros(consulta):
    # parse_qs decodifica %C3%A1 -> á, así "volcán" llega bien desde Godot
    params = parse_qs(consulta)

    clase = params.get("clase", [None])[0]
    if clase is None:
        raise ErrorPeticion(f"Falta el parámetro clase. Válidas: {CLASES}")
    if clase not in CLASES:
        raise ErrorPeticion(f"Clase desconocida: {clase!r}. Válidas: {CLASES}")

    texto_semilla = params.get("semilla", [None])[0]
    if texto_semilla is None:
        semilla = random.randint(0, SEMILLA_MAX)
    else:
        try:
            semilla = int(texto_semilla)
        except ValueError:
            raise ErrorPeticion(f"semilla debe ser un entero, llegó {texto_semilla!r}")
        if not 0 <= semilla <= SEMILLA_MAX:
            raise ErrorPeticion(f"semilla debe estar entre 0 y {SEMILLA_MAX}")

    texto_sigma = params.get("sigma", ["2"])[0]
    try:
        sigma = float(texto_sigma)
    except ValueError:
        raise ErrorPeticion(f"sigma debe ser un número, llegó {texto_sigma!r}")
    if not 0 <= sigma <= SIGMA_MAX:
        raise ErrorPeticion(f"sigma debe estar entre 0 y {SIGMA_MAX}")

    return clase, semilla, sigma

class ManejadorGaia(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/salud":
            self._responder_json(200, {"estado": "ok"})
        elif url.path == "/terreno":
            self._terreno(url.query)
        else:
            self._responder_json(404, {"error": f"Ruta desconocida: {url.path}"})

    def _terreno(self, consulta):
        try:
            clase, semilla, sigma = leer_parametros(consulta)
        except ErrorPeticion as e:
            self._responder_json(400, {"error": str(e)})
            return
        try:
            # el modelo se carga aquí la primera vez (caché en inferencia.py)
            datos = raw_a_bytes(generar_terreno(clase, semilla, sigma))
        except Exception as e:
            self._responder_json(500, {"error": f"Falló la generación: {e}"})
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(datos)))
        # los encabezados HTTP solo aceptan ASCII: la clase va codificada
        self.send_header("X-Clase", quote(clase))
        self.send_header("X-Semilla", str(semilla))
        self.send_header("X-Sigma", str(sigma))
        self.end_headers()
        self.wfile.write(datos)

    def _responder_json(self, codigo, cuerpo):
        datos = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

def crear_servidor(puerto=PUERTO):
    # puerto=0 deja que el sistema elija uno libre (útil en los tests)
    return HTTPServer((HOST, puerto), ManejadorGaia)

if __name__ == "__main__":
    servidor = crear_servidor()
    print(f"Gaia-AI escuchando en http://{HOST}:{servidor.server_port}  (Ctrl+C para salir)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()
