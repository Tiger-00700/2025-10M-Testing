<#
Summarize latest organize logs: Missing counts and top 10 misses.
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$logs = Get-ChildItem 'tools/reports/organize-log-*.md' -ErrorAction Stop | Sort-Object LastWriteTime -Descending
if (-not $logs -or $logs.Count -eq 0) {
  Write-Host 'No organize logs found under tools/reports'
  exit 0
}

function Get-MissingCount([string]$path) {
  $first = Get-Content -Path $path -TotalCount 1
  if ($first -match 'Missing=([0-9]+)') { return [int]$Matches[1] } else { return -1 }
}

$latest = $logs[0]
$latestCount = Get-MissingCount $latest.FullName
Write-Host ("Latest: {0}  Missing={1}" -f $latest.Name, $latestCount)

if ($logs.Count -ge 2) {
  $prev = $logs[1]
  $prevCount = Get-MissingCount $prev.FullName
  $delta = $latestCount - $prevCount
  Write-Host ("Previous: {0}  Missing={1}  (Δ={2})" -f $prev.Name, $prevCount, $delta)
}

Write-Host ''
Write-Host 'Top 10 MISS in latest:'
Get-Content -Path $latest.FullName |
  Where-Object { $_ -like 'MISS*' } |
  Select-Object -First 10 |
  ForEach-Object { $_ }
