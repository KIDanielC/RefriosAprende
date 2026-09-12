; Script de Inno Setup para "Refrios Aprende".
;
; Requisitos previos:
;   1. Compilar primero con PyInstaller (desde la raiz del proyecto):
;        py -m PyInstaller packaging/refrios_aprende.spec
;      Esto debe dejar la carpeta dist/RefriosAprende/RefriosAprende.exe lista.
;   2. Tener instalado Inno Setup (https://jrsoftware.org/isinfo.php, gratuito).
;
; Para compilar el instalador (con Inno Setup instalado y en PATH como "iscc"):
;        iscc packaging/instalador.iss
;   El instalador resultante queda en packaging/salida/RefriosAprende-Setup-<version>.exe
;
; Ver documentation/EMPAQUETADO.md para el procedimiento completo.

#define MyAppName "Refrios Aprende"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Refrios"
#define MyAppExeName "RefriosAprende.exe"
#define MyDistDir "..\dist\RefriosAprende"

[Setup]
AppId={{9C6C6E3E-6E2A-4B0B-9C2E-6B1A5B7E7B10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Instala en Program Files; los datos de usuario (BD, contenidos subidos) NO viven aqui,
; sino en %LOCALAPPDATA%\RefriosAprende (ver config/settings.py) para no requerir permisos
; de administrador en cada arranque.
PrivilegesRequired=lowest
OutputDir=salida
OutputBaseFilename=RefriosAprende-Setup-{#MyAppVersion}
SetupIconFile=..\resources\icons\app.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el Escritorio"; GroupDescription: "Accesos directos adicionales:"; Flags: unchecked

[Files]
Source: "{#MyDistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; El instalador solo borra lo que instaló en Program Files. Los datos del usuario en
; %LOCALAPPDATA%\RefriosAprende (base de datos, contenidos subidos) se conservan a
; propósito tras desinstalar, por si el usuario vuelve a instalar la aplicación después.
