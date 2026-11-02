# Gaia-AI v1.0

Gaia-AI es una IA local que genera terreno nuevo (mapas de altura) a partir de seis formas de relieve: llanura, lomas, valle, montaña, meseta y volcán. Es una GAN condicional entrenada con elevación real (SRTM) que funciona en CPU, sin servicios externos, y se explora en 3D con un visor hecho en Godot.

## Novedades de la versión
- Visor 3D con generación en vivo: eliges la forma, la semilla y el suavizado, y el terreno se genera al momento.
- Sombras del sol sobre el relieve.
- Cámara orbital con W A S D, flechas o arrastrando el mouse; zoom con la rueda o Q y E.
- Pantalla completa con F11 y botón Salir en el menú (al salir se apaga el servidor de Python).
- Intro centrada con un fondo de curvas de nivel animadas.
- Comparación contra el generador clásico de ruido Simplex ([`docs/comparacion_simplex.md`](comparacion_simplex.md)).

## Requisitos
- Windows con Python 3.13.
- Unos 3 GB libres para PyTorch y las demás dependencias.
- Godot 4.5.1, para abrir el visor.

## Instalación
```powershell
git clone https://github.com/FernandoMoralesT/Gaia-AI.git
cd Gaia-AI
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

El modelo de la demo (`modelos/generador_epoca150.pt`) ya viene en el repositorio. No hace falta clave de OpenTopography, salvo para descargar tiles nuevos.

## Uso
1. Abre `godot/gaia-visor/project.godot` con Godot 4.5.1 y pulsa F5.
2. El visor enciende solo el servidor local de Python (`127.0.0.1:8765`) y lo apaga al cerrar. Si no encuentra Python, muestra mapas guardados.
3. Si prefieres arrancar el servidor a mano: `python src/servidor.py`.

Esta versión no incluye un `.exe` descargable. El ejecutable necesita estar dentro de la carpeta del repositorio y con Python instalado, así que suelto no funcionaría. Si quieres generarlo, sigue la sección *Demo (.exe)* del README, que lo exporta a `dist/Gaia-AI.exe` con el preset de Windows.

## Limitaciones conocidas
- Las alturas son relativas, no metros: cada mapa se normaliza por separado y la escala vertical depende de la clase.
- Los volcanes salen como conos sin cráter: a 90 m por píxel la mayoría de los cráteres reales no se distinguen, y hay muy pocos ejemplos en los datos.
- Las clases lomas, montaña y meseta se parecen entre sí.
- Solo CPU; el entrenamiento se hizo sin GPU.

## Equipo
- Luis Fernando Morales Toledo: desarrollador principal.
- Cristoff Salvador Garcia Mendoza: documentación y recabación de datos.
- Sebastian Aguillon Peinado: frontend.

Licencia MIT. Los créditos de fuentes, datos y bibliotecas están en el README.
