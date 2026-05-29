# STEP 1 (local) — Start the Python API on http://127.0.0.1:8780
# Secrets: copy server\.env.example → server\.env first.
# Account creation debug (visible Chromium): .\4-START-ACCOUNT-DEBUG.ps1 — see LOCAL_ACCOUNT_DEBUG.md
# STEP 2: run 2-START-LOCAL-WEB.ps1 in another terminal → http://127.0.0.1:5173

param(
  [switch] $Build
)
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location $root

Write-Host "=== Hammer website — LOCAL API (step 1 of 2) ===" -ForegroundColor Cyan
Write-Host "Next: open a second terminal and run:  .\2-START-LOCAL-WEB.ps1" -ForegroundColor Yellow
Write-Host ""

if ($Build) {
  Set-Location (Join-Path $root "web")
  npm install
  npm run build
  Set-Location $root
}

Set-Location (Join-Path $root "server")
$hammerRepo = (Resolve-Path (Join-Path $root "..\..")).Path
$hammerWiki = Join-Path $hammerRepo "wiki"
if (Test-Path (Join-Path $hammerWiki "demo-public-site-copy.md")) {
  $env:REALTIME_SALES_REPO_ROOT = $hammerRepo
  Remove-Item Env:REALTIME_SALES_WIKI_DIR -ErrorAction SilentlyContinue
  Write-Host "Wiki for /api/site_copy: $hammerWiki" -ForegroundColor DarkGray
} else {
  Write-Host "Using wiki from server/.env or auto-detect (not $hammerWiki)" -ForegroundColor DarkYellow
}
py -3 -m pip install -r requirements.txt -q

$envPath = Join-Path (Get-Location) ".env"
$hasKey = $false
if (Test-Path $envPath) {
  foreach ($line in Get-Content $envPath) {
    if ($line -match '^\s*OPENAI_API_KEY=(.+)$' -and $Matches[1].Trim().Length -gt 10) {
      $hasKey = $true
      break
    }
  }
}
if (-not $hasKey -and -not $env:OPENAI_API_KEY) {
  Write-Host ""
  Write-Host "OPENAI_API_KEY is missing — voice will return HTTP 503." -ForegroundColor Red
  Write-Host "Copy server\.env.example → server\.env and add your key." -ForegroundColor Yellow
  Write-Host ""
}

Write-Host "API: http://127.0.0.1:8780  (Ctrl+C to stop)" -ForegroundColor Green
Write-Host "Voice dashboard: http://127.0.0.1:8780/debug/voice-dashboard" -ForegroundColor DarkCyan
Write-Host "Hammer account debug: http://127.0.0.1:8780/debug/hammer-account" -ForegroundColor DarkGray
py -3 -m uvicorn app:app --host 127.0.0.1 --port 8780 --reload --reload-include .env
