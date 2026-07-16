# Desinstalador do PrintQuote by BMR.
# Remove os arquivos instalados, atalhos e a entrada em "Aplicativos
# instalados". NÃO apaga seus dados (materiais, impressoras, histórico) —
# eles ficam em %LOCALAPPDATA%\BMR\PrintQuote by BMR\printquote.db.
# Para apagar os dados também, rode com -PurgeData.

param(
    [switch]$PurgeData
)

$ErrorActionPreference = "SilentlyContinue"

$AppName = "PrintQuote by BMR"
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\$AppName"

Write-Host "Desinstalando $AppName ..."

Remove-Item -Force (Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\$AppName.lnk")
Remove-Item -Force (Join-Path ([Environment]::GetFolderPath("Desktop")) "$AppName.lnk")
Remove-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\PrintQuoteByBMR" -Recurse -Force

if ($PurgeData) {
    Remove-Item -Recurse -Force (Join-Path $env:LOCALAPPDATA "BMR\$AppName")
    Write-Host "Dados do usuário (materiais, impressoras, histórico) também foram apagados."
}

# Remove a pasta de instalação por último (este próprio script está dentro
# dela) — agenda a remoção via cmd para rodar depois que este processo sair.
Start-Process -WindowStyle Hidden cmd.exe -ArgumentList "/c timeout /t 2 & rmdir /s /q `"$InstallDir`""

Write-Host "$AppName desinstalado." -ForegroundColor Green
