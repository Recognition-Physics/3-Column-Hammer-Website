# Re-copy Hammer marketing / transcript markdown from the standard Downloads folder
# into this repo's raw bundle (matches existing layout: "Hammer Website" subfolder).
#
# Usage (from repo root):
#   powershell -NoProfile -ExecutionPolicy Bypass -File raw/hammer-data/ingest-from-downloads.ps1
# Optional:
#   .\ingest-from-downloads.ps1 -Source "D:\Other\Hammer Data"

param(
  [string] $Source = "$env:USERPROFILE\Downloads\Hammer Data",
  [string] $DestRoot = $PSScriptRoot
)

$ErrorActionPreference = "Stop"

$website = [System.Collections.Generic.HashSet[string]]::new([string[]]@(
  "Facebook_AIA_Hammer.pdf.md",
  "Hammer_AI_lead_follow-up_for_dealerships.pdf.md",
  "Hammer_AI_lead_follow-up_for_dealerships.pdf_1.md",
  "Hammer_Connect_Hammer.pdf.md",
  "MarketPoster_Hammer.pdf.md"
))

if (-not (Test-Path -LiteralPath $Source)) {
  throw "Source not found: $Source"
}

$Source = [System.IO.Path]::GetFullPath($Source)
$DestRoot = [System.IO.Path]::GetFullPath($DestRoot)

Get-ChildItem -LiteralPath $Source -Recurse -File | ForEach-Object {
  $rel = $_.FullName.Substring($Source.Length).TrimStart('\', '/')
  if ($rel -match '[\\/]') {
    $destPath = Join-Path $DestRoot $rel
  }
  elseif ($website.Contains($_.Name)) {
    $destPath = Join-Path (Join-Path $DestRoot "Hammer Website") $_.Name
  }
  else {
    $destPath = Join-Path $DestRoot $_.Name
  }
  $destDir = Split-Path -Parent $destPath
  New-Item -ItemType Directory -Force -Path $destDir | Out-Null
  Copy-Item -LiteralPath $_.FullName -Destination $destPath -Force
  Write-Host "Copied $($_.Name)"
}

Write-Host "Done -> $DestRoot"
