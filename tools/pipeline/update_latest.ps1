Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$reportDir = Join-Path -Path 'tools' -ChildPath 'reports'
if (-not (Test-Path $reportDir)) { throw "Reports directory not found: $reportDir" }

# Find newest timestamp by filename pattern yyyyMMdd-HHmmss
$organized = Get-ChildItem -Path $reportDir -Filter 'organized-*.md' -File |
  Where-Object { $_.Name -notmatch '-latest' } |
  Sort-Object Name | Select-Object -Last 1
$log = Get-ChildItem -Path $reportDir -Filter 'organize-log-*.md' -File |
  Where-Object { $_.Name -notmatch '-latest' } |
  Sort-Object Name | Select-Object -Last 1
$toc = Get-ChildItem -Path $reportDir -Filter 'toc-*.txt' -File |
  Where-Object { $_.Name -notmatch '-latest' } |
  Sort-Object Name | Select-Object -Last 1

if (-not $organized -or -not $log -or -not $toc) {
  throw 'Required report files not found to create latest pointers.'
}

Copy-Item -LiteralPath $organized.FullName -Destination (Join-Path $reportDir 'organized-latest.md') -Force
Copy-Item -LiteralPath $log.FullName -Destination (Join-Path $reportDir 'organize-log-latest.md') -Force
Copy-Item -LiteralPath $toc.FullName -Destination (Join-Path $reportDir 'toc-latest.txt') -Force

Write-Host "Latest pointers updated:" 
Write-Host " - organized-latest.md -> $($organized.Name)"
Write-Host " - organize-log-latest.md -> $($log.Name)"
Write-Host " - toc-latest.txt -> $($toc.Name)"