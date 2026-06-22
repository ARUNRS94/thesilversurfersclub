param(
    [string]$OutputDir = "dist\SeniorConnect-Windows"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is required to build the Windows installer package."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "Node.js/npm is required to build the frontend."
}

python -m pip install -r backend\requirements.txt
python -m pip install pyinstaller
Push-Location frontend
npm install
npm run build
Pop-Location

python -m PyInstaller --clean --onefile --name SeniorConnectServer --paths backend --collect-submodules app --hidden-import app.main --hidden-import app.seed backend\start_server.py

$Package = Join-Path $Root $OutputDir
Remove-Item $Package -Recurse -Force -ErrorAction SilentlyContinue
New-Item $Package -ItemType Directory | Out-Null
New-Item (Join-Path $Package "frontend") -ItemType Directory | Out-Null
Copy-Item dist\SeniorConnectServer.exe $Package
Copy-Item frontend\dist (Join-Path $Package "frontend\dist") -Recurse
Copy-Item installer\windows\Start-SeniorConnect.bat $Package
Copy-Item installer\windows\README-Windows.txt $Package

Write-Host "Built one-click Windows package at $Package"
