# STEP 2 (local) — Start the browser UI on http://127.0.0.1:5173
# Requires step 1: .\1-START-LOCAL-API.ps1 running in another terminal.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$web = Join-Path $root "web"
Set-Location $web

Write-Host "=== Hammer website — LOCAL WEB (step 2 of 2) ===" -ForegroundColor Cyan
Write-Host "API must be running: http://127.0.0.1:8780  (from 1-START-LOCAL-API.ps1)" -ForegroundColor DarkGray
Write-Host ""

if (-not (Test-Path "node_modules")) {
  Write-Host "Installing npm packages (first time only)..." -ForegroundColor Yellow
  npm install
}

Write-Host "Website: http://127.0.0.1:5173  (Ctrl+C to stop)" -ForegroundColor Green
npm run dev
