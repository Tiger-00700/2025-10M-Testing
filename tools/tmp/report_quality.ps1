Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Get-LatestLogFile {
  $dir = 'tools/reports'
  if (-not (Test-Path $dir)) { throw "Reports dir not found: $dir" }
  $log = Get-ChildItem -Path $dir -Filter 'organize-log-*.md' -File | Sort-Object Name | Select-Object -Last 1
  if (-not $log) { throw 'No organize-log-*.md found' }
  return $log.FullName
}

$logPath = Get-LatestLogFile
$lines = [IO.File]::ReadAllLines($logPath, [Text.Encoding]::UTF8)

$modeCounts = @{}
$levelCounts = @{}
$missing = 0

foreach ($ln in $lines) {
  if ($ln -match '^Missing=(\d+)') { $missing = [int]$Matches[1]; continue }
  if ($ln -match '^(OK|MISS)') {
    # Example OK line: OK    [fuzzy:0.712]  3    Title -> Match
    # Example MISS line: MISS  -       4    Title
    if ($ln.StartsWith('OK')) {
      $mode = ($ln -replace '^OK\s*\[(.*?)\].*$', '$1')
      if ($mode -match '^(?<m>[^:]+)') { $m = $Matches['m'] } else { $m = 'unknown' }
      $modeCounts[$m] = 1 + ($modeCounts[$m] | ForEach-Object { $_ })
    } elseif ($ln.StartsWith('MISS')) {
      $modeCounts['MISS'] = 1 + ($modeCounts['MISS'] | ForEach-Object { $_ })
    }
    if ($ln -match '^\S+\s+\S+\s+(\d+)\s+') {
      $lvl = [int]$Matches[1]
      $levelCounts[$lvl] = 1 + ($levelCounts[$lvl] | ForEach-Object { $_ })
    }
  }
}

# Build report
$ts = (Get-Date).ToString('yyyyMMdd-HHmmss')
$outDir = 'tools/reports'
$outPath = Join-Path $outDir ("quality-" + $ts + ".md")

$sb = New-Object System.Text.StringBuilder
$null = $sb.AppendLine("# Organizer Quality Report ($ts)")
$null = $sb.AppendLine("")
$null = $sb.AppendLine(("Source log: {0}" -f $logPath))
$null = $sb.AppendLine(("Missing: {0}" -f $missing))
$null = $sb.AppendLine("")
$null = $sb.AppendLine("## Match mode distribution")
$null = $sb.AppendLine("")
foreach ($k in ($modeCounts.Keys | Sort-Object)) {
  $null = $sb.AppendLine(("{0}: {1}" -f $k, $modeCounts[$k]))
}
$null = $sb.AppendLine("")
$null = $sb.AppendLine("## Level distribution")
$null = $sb.AppendLine("")
foreach ($k in ($levelCounts.Keys | Sort-Object)) {
  $null = $sb.AppendLine(("H{0}: {1}" -f $k, $levelCounts[$k]))
}

[IO.File]::WriteAllText($outPath, $sb.ToString(), [Text.Encoding]::UTF8)

Write-Host "Quality report written: $outPath"