param(
  [int]$Keep = 2,
  [switch]$DryRun
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSCommandPath
$releasesDir = Join-Path $root 'releases'
if(-not (Test-Path $releasesDir)){ throw "Releases directory not found: $releasesDir" }
$items = Get-ChildItem -LiteralPath $releasesDir -Directory | Where-Object { $_.Name -like 'book-*' } | Sort-Object Name -Descending
$toKeep = $items | Select-Object -First $Keep
$remove = $items | Select-Object -Skip $Keep
# Also match zip archives
$zips = Get-ChildItem -LiteralPath $releasesDir -File -Filter 'book-*.zip' | Sort-Object Name -Descending
$zipKeep = $zips | Select-Object -First $Keep
$zipRemove = $zips | Select-Object -Skip $Keep
Write-Host "Keeping latest $Keep releases:"; $toKeep | ForEach-Object { Write-Host "  + $_" }
if($zipKeep){ Write-Host "Keeping latest $Keep zip archives:"; $zipKeep | ForEach-Object { Write-Host "  + $_" } }
if($DryRun){ Write-Host "[DryRun] Would remove:"; $remove | ForEach-Object { Write-Host "  - $_" }; $zipRemove | ForEach-Object { Write-Host "  - $_" }; return }
$remove | ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force }
$zipRemove | ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }
Write-Host "Removed $($remove.Count) directories and $($zipRemove.Count) zip archives."