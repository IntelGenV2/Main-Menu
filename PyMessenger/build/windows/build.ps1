param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$PyMessengerRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ClientRoot = Join-Path $PyMessengerRoot "app.client"

Write-Host "Installing client dependencies..."
& $Python -m pip install -r (Join-Path $ClientRoot "requirements.txt")

Write-Host "Building messenger client executable..."
Push-Location $ClientRoot
& $Python -m PyInstaller `
    --noconfirm `
    --windowed `
    --name IntelByte256 `
    --paths . `
    messenger_app/main.py
Pop-Location

Write-Host "Build complete. Output is in app.client/dist/IntelByte256/"
