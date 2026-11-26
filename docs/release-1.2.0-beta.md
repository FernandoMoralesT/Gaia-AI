# Gaia-AI 1.2.0-beta: versión para PC con instalador

Primera versión de Gaia-AI que se instala en cualquier Windows de 64 bits y genera terreno en vivo **sin Python y sin clonar el repositorio**.

## Descarga

- **Archivo:** `Gaia-AI-Setup.exe` (159 MB)
- **SHA-256:** `53b223748420fd39473dc0358b8dc28a41a9af597cb7efd5cc2429ea957518e0`

Para comprobar que el archivo no cambió, en PowerShell:

```powershell
Get-FileHash .\Gaia-AI-Setup.exe -Algorithm SHA256
```

El resultado debe coincidir con el de arriba.

## Instalación

1. Ejecuta `Gaia-AI-Setup.exe`. No pide permisos de administrador: se instala en tu usuario (`%LOCALAPPDATA%\Programs\Gaia-AI`).
2. Si Windows muestra **"Windows protegió tu PC"**, haz clic en **Más información** y luego en **Ejecutar de todas formas**. El aviso aparece porque el instalador no tiene firma digital, no porque tenga un problema.
3. Abre Gaia-AI desde el menú Inicio o el acceso directo del escritorio.

El primer terreno tarda unos segundos mientras se carga el modelo; los siguientes son inmediatos.

## Novedades

- Instalador en español con licencia MIT, acceso directo opcional y desinstalador.
- El generador (PyTorch en CPU) viene empaquetado junto al visor; ya no hace falta Python.
- Botón **Exportar** en el visor: PNG de 8 bits para Roblox Studio, RAW de 16 bits para Unity y OBJ para Blender, con un archivo LEEME de importación en `Documentos/Gaia-AI/exportaciones`.
- Ícono propio.

## Notas

- El modelo es el mismo de la v1.0 (época 150) y genera mapas de 120×120 de 6 clases: llanura, lomas, valle, montaña, meseta y volcán.
- La importación de los archivos exportados en Roblox Studio, Unity y Blender todavía no se ha probado.
- Probado en Windows 11 con y sin Python instalado.
