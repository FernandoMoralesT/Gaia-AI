# Empaqueta src/servidor.py como dist/gaia-servidor/gaia-servidor.exe (PyInstaller --onedir).
# Uso, desde la raiz del repo:
#   powershell -ExecutionPolicy Bypass -File scrips/construir_servidor.ps1
# La primera vez crea .venv-build con requirements-build.txt (torch solo CPU).
# Al final enciende el .exe, pide /salud y un terreno, y lo apaga.
param(
    [switch]$SinPrueba  # omite la prueba de humo del final
)
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

$venv = Join-Path $raiz ".venv-build"
$python = Join-Path $venv "Scripts\python.exe"

# Lanzador py (Python de python.org) si existe; si no, python (Microsoft Store)
function Crear-Venv {
    $lanzador = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }
    $opcion = if ($lanzador -eq "py") { @("-3.13") } else { @() }
    $version = & $lanzador @opcion -c "import sys; print('%d.%d' % sys.version_info[:2])"
    if ($version -ne "3.13") { throw "Se necesita Python 3.13 y se encontro $version" }
    Write-Host "Creando .venv-build con Python $version ($lanzador)..."
    & $lanzador @opcion -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear .venv-build" }
}

function Preparar-Venv {
    if (-not (Test-Path $python)) { Crear-Venv }
    & $python -m pip install --upgrade pip
    & $python -m pip install -r requirements-build.txt
}

function Empaquetar {
    # --onedir: un solo proceso y arranque rapido (onefile se descomprime cada vez)
    # --noupx: UPX provoca falsos positivos de antivirus
    # --paths src: encuentra inferencia, model y dataset como en desarrollo
    & $python -m PyInstaller src/servidor.py `
        --name gaia-servidor --onedir --noconsole --noupx --clean -y `
        --paths src `
        --add-data "modelos/generador_epoca150.pt;modelos" `
        --distpath dist --workpath build --specpath build
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller fallo (codigo $LASTEXITCODE)" }
}

function Esperar-Salud($url, $segundos) {
    for ($i = 0; $i -lt $segundos; $i++) {
        try {
            $r = Invoke-WebRequest "$url/salud" -UseBasicParsing -TimeoutSec 1
            if ($r.StatusCode -eq 200) { return $true }
        } catch { Start-Sleep -Seconds 1 }
    }
    return $false
}

function Probar-Exe {
    $exe = Join-Path $raiz "dist\gaia-servidor\gaia-servidor.exe"
    $url = "http://127.0.0.1:8765"
    $proceso = Start-Process $exe -PassThru
    try {
        if (-not (Esperar-Salud $url 60)) { throw "El servidor no respondio /salud en 60 s" }
        $r = Invoke-WebRequest "$url/terreno?clase=llanura&semilla=42&sigma=2" -UseBasicParsing
        # 8 bytes de encabezado + 120 x 120 x 4
        if ($r.RawContentLength -ne 57608) { throw "Terreno con tamano inesperado: $($r.RawContentLength)" }
        Write-Host "Prueba OK: /salud y /terreno responden (57608 bytes)." -ForegroundColor Green
    } finally {
        Stop-Process -Id $proceso.Id -ErrorAction SilentlyContinue
    }
}

Preparar-Venv
Empaquetar
$tamano = (Get-ChildItem dist\gaia-servidor -Recurse | Measure-Object Length -Sum).Sum / 1MB
Write-Host ("dist\gaia-servidor listo: {0:N0} MB" -f $tamano)
if (-not $SinPrueba) { Probar-Exe }
