# Instalador do PrintQuote by BMR.
# Instala por usuário (sem precisar de administrador), cria atalhos no
# Menu Iniciar e na Área de Trabalho, e registra o app em
# "Aplicativos instalados" do Windows (com desinstalador).
#
# Uso: rode este script a partir da pasta que contém installer/ e dist/
#   powershell -ExecutionPolicy Bypass -File installer\install.ps1

$ErrorActionPreference = "Stop"

$AppName = "PrintQuote by BMR"
$Publisher = "BMR"
$AppVersion = "1.0.0"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$SourceDir = Join-Path $RepoRoot "dist\$AppName"
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\$AppName"
$ExePath = Join-Path $InstallDir "$AppName.exe"
$IconPath = Join-Path $InstallDir "calc3d\ui\assets\icon.ico"

if (-not (Test-Path $SourceDir)) {
    Write-Error "Build não encontrado em '$SourceDir'. Rode primeiro: pyinstaller ... (veja BUILD.md)"
    exit 1
}

Write-Host "Instalando $AppName em $InstallDir ..."

if (Test-Path $InstallDir) {
    Remove-Item -Recurse -Force $InstallDir
}
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item -Recurse -Force "$SourceDir\*" $InstallDir

# Copia o desinstalador para dentro da instalação
Copy-Item -Force (Join-Path $PSScriptRoot "uninstall.ps1") (Join-Path $InstallDir "uninstall.ps1")

# --- Atalhos ---
$WshShell = New-Object -ComObject WScript.Shell

$StartMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$StartMenuShortcut = $WshShell.CreateShortcut((Join-Path $StartMenuDir "$AppName.lnk"))
$StartMenuShortcut.TargetPath = $ExePath
$StartMenuShortcut.WorkingDirectory = $InstallDir
$StartMenuShortcut.IconLocation = $IconPath
$StartMenuShortcut.Save()

$DesktopShortcut = $WshShell.CreateShortcut((Join-Path ([Environment]::GetFolderPath("Desktop")) "$AppName.lnk"))
$DesktopShortcut.TargetPath = $ExePath
$DesktopShortcut.WorkingDirectory = $InstallDir
$DesktopShortcut.IconLocation = $IconPath
$DesktopShortcut.Save()

# --- Registro em "Aplicativos instalados" (por usuário, sem admin) ---
$UninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\PrintQuoteByBMR"
New-Item -Path $UninstallKey -Force | Out-Null
Set-ItemProperty -Path $UninstallKey -Name "DisplayName" -Value $AppName
Set-ItemProperty -Path $UninstallKey -Name "DisplayVersion" -Value $AppVersion
Set-ItemProperty -Path $UninstallKey -Name "Publisher" -Value $Publisher
Set-ItemProperty -Path $UninstallKey -Name "DisplayIcon" -Value $ExePath
Set-ItemProperty -Path $UninstallKey -Name "InstallLocation" -Value $InstallDir
Set-ItemProperty -Path $UninstallKey -Name "UninstallString" -Value "powershell -ExecutionPolicy Bypass -File `"$InstallDir\uninstall.ps1`""
Set-ItemProperty -Path $UninstallKey -Name "NoModify" -Value 1 -Type DWord
Set-ItemProperty -Path $UninstallKey -Name "NoRepair" -Value 1 -Type DWord

Write-Host ""
Write-Host "$AppName instalado com sucesso." -ForegroundColor Green
Write-Host "Atalhos criados no Menu Iniciar e na Área de Trabalho."
Write-Host "Para desinstalar: Configurações > Aplicativos, ou rode uninstall.ps1 dentro da pasta de instalação."
