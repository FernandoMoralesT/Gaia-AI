# Recursos del ícono

- `logo.svg`: logo de la página (rama `gh-pages`, `img/logo.svg`), líneas blancas sin fondo.
- `icono_chico.svg`: favicon de la página (`img/favicon.svg`), fondo `#2C5F6F`. Se usa para 16, 32 y 48 px.
- `icono_grande.svg`: el mismo diseño con líneas más delgadas para que la malla se vea a 256 px.

`godot/gaia-visor/icono.ico` junta seis tamaños, los que pide Godot (16, 32 y 48 desde `icono_chico.svg`;
64 con líneas intermedias; 128 y 256 desde `icono_grande.svg`). Lo usan el .exe del visor (`export_presets.cfg`) y el instalador.
