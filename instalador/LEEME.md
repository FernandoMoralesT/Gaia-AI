# Recursos del ícono

- `logo.svg`: logo de la página (rama `gh-pages`, `img/logo.svg`), líneas blancas sin fondo.
- `icono_chico.svg`: favicon de la página (`img/favicon.svg`), fondo `#2C5F6F`. Se usa para 16, 32 y 48 px.
- `icono_grande.svg`: el mismo diseño con líneas más delgadas para que la malla se vea a 256 px.

`godot/gaia-visor/icono.ico` junta seis tamaños, los que pide Godot (16, 32 y 48 desde `icono_chico.svg`;
64 con líneas intermedias; 128 y 256 desde `icono_grande.svg`). Lo usan el .exe del visor (`export_presets.cfg`) y el instalador.

# Construir el instalador (Gaia-AI-Setup.exe)

Desde la raíz del repo, en este orden:

1. `powershell -ExecutionPolicy Bypass -File scrips/construir_servidor.ps1` → `dist\gaia-servidor\`
2. Exportar el visor con Godot (`--export-release "Windows Desktop" ../../dist/Gaia-AI.exe`) → `dist\Gaia-AI.exe`
3. Compilar `instalador\gaia-ai.iss` con Inno Setup 7 (`& "C:\Program Files\Inno Setup 7\ISCC.exe" instalador\gaia-ai.iss`, unos 3 min) → `dist\instalador\Gaia-AI-Setup.exe`

La versión se cambia en `#define AppVersion` dentro de `gaia-ai.iss`. El `AppId` no se cambia nunca.
