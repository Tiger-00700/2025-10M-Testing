param(
  [switch]$DeleteCandidates,
  [switch]$NoBackup
)

$ErrorActionPreference = 'Stop'

# Resolve repo root from this script location
$pipelineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolsDir = Split-Path -Parent $pipelineDir
$repoRoot = Split-Path -Parent $toolsDir

$chapterDir = Join-Path $repoRoot 'chapter'

if (-not (Test-Path $chapterDir)) {
  Write-Error "Chapter directory not found: $chapterDir"
}

$candidates = Get-ChildItem -Path $chapterDir -Filter '*.archivefix.candidate.md' -File | Sort-Object Name
if ($candidates.Count -eq 0) {
  Write-Host 'No candidate files found.'
  exit 0
}

Write-Host ("Found {0} candidate files" -f $candidates.Count)

$promoted = 0
foreach ($cand in $candidates) {
  $orig = Join-Path $cand.DirectoryName (($cand.BaseName -replace '\.archivefix\.candidate$', '') + '.md')
  if (-not (Test-Path $orig)) {
    Write-Warning ("Original not found for candidate: {0}" -f $cand.FullName)
    continue
  }
  if (-not $NoBackup) {
    $bak = $orig + '.pre-archivefix.bak'
    Copy-Item -Path $orig -Destination $bak -Force
  }
  Copy-Item -Path $cand.FullName -Destination $orig -Force
  if ($DeleteCandidates) {
    Remove-Item -Path $cand.FullName -Force
  }
  $promoted++
  Write-Host ("Promoted: {0}" -f $orig)
}

Write-Host ("PROMOTED: {0}" -f $promoted)
exit 0
