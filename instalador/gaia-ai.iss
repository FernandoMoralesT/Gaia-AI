; Instalador de Gaia-AI para Windows (Inno Setup 7).
; Antes de compilar deben existir, desde la raiz del repo:
;   dist\Gaia-AI.exe          (exportacion de Godot con Embed PCK)
;   dist\gaia-servidor\       (scrips\construir_servidor.ps1)
; Compilar:  & "C:\Program Files\Inno Setup 7\ISCC.exe" instalador\gaia-ai.iss
; Resultado: dist\instalador\Gaia-AI-Setup.exe

#define AppVersion "1.2.0-beta"

[Setup]
; AppId identifica la app para actualizar y desinstalar: no cambiarlo nunca
AppId={{7BD57662-81E6-43B5-BAC2-16BB64DE18F8}
AppName=Gaia-AI
AppVersion={#AppVersion}
AppPublisher=Luis Fernando Morales Toledo
AppPublisherURL=https://fernandomoralest.github.io/Gaia-AI/
AppSupportURL=https://github.com/FernandoMoralesT/Gaia-AI
; Carpeta del usuario: no pide permisos de administrador
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\Gaia-AI
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
SetupIconFile=..\godot\gaia-visor\icono.ico
UninstallDisplayIcon={app}\Gaia-AI.exe
UninstallDisplayName=Gaia-AI
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist\instalador
OutputBaseFilename=Gaia-AI-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "escritorio"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\Gaia-AI.exe"; DestDir: "{app}"; Flags: ignoreversion
; Misma estructura que dist\: ServidorLocal busca gaia-servidor\gaia-servidor.exe junto al visor
Source: "..\dist\gaia-servidor\*"; DestDir: "{app}\gaia-servidor"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Gaia-AI"; Filename: "{app}\Gaia-AI.exe"
Name: "{autodesktop}\Gaia-AI"; Filename: "{app}\Gaia-AI.exe"; Tasks: escritorio

[Run]
Filename: "{app}\Gaia-AI.exe"; Description: "{cm:LaunchProgram,Gaia-AI}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Si el servidor quedo vivo, sus archivos estan en uso y no se podrian borrar
Filename: "{sys}\taskkill.exe"; Parameters: "/f /im gaia-servidor.exe"; Flags: runhidden; RunOnceId: "CerrarServidor"
