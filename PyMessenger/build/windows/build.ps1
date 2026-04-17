param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

Write-Host "Installing dependencies..."
& $Python -m pip install -r (Join-Path $ProjectRoot "requirements.txt")

Write-Host "Building messenger client executable..."
Push-Location $ProjectRoot
& $Python -m PyInstaller `
    --noconfirm `
    --windowed `
    --name IntelByte256 `
    --paths . `
    messenger_app/main.py
Pop-Location

Write-Host "Build complete. Output is in dist/IntelByte256/"
