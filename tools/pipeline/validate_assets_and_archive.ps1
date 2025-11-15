$ErrorActionPreference = 'Stop'

# Resolve repo root from this script location
$pipelineDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolsDir = Split-Path -Parent $pipelineDir
$repoRoot = Split-Path -Parent $toolsDir

# Determine Python executable (prefer venv)
$candidateVenvs = @(
	(Join-Path $repoRoot '.venv311/Scripts/python.exe'),
	(Join-Path $repoRoot '.venv/Scripts/python.exe')
)
$pythonExe = $null
foreach ($c in $candidateVenvs) {
	if (Test-Path $c) { $pythonExe = $c; break }
}
if (-not $pythonExe) { $pythonExe = 'python' }

# Ensure reports directory exists
$reports = Join-Path $repoRoot 'tools/reports'
if (-not (Test-Path $reports)) { New-Item -ItemType Directory -Path $reports | Out-Null }

Write-Host "Running validators with: $pythonExe"

# Run asset inventory
$assetsScript = Join-Path $repoRoot 'tools/inventory_referenced_assets.py'
Write-Host "==> inventory_referenced_assets.py"
& $pythonExe $assetsScript
$assetsExit = $LASTEXITCODE

# Run archive status
$archiveScript = Join-Path $repoRoot 'tools/inventory_archive_status.py'
Write-Host "==> inventory_archive_status.py"
& $pythonExe $archiveScript
$archiveExit = $LASTEXITCODE

Write-Host ("ASSETS_EXIT: {0}" -f $assetsExit)
Write-Host ("ARCHIVE_EXIT: {0}" -f $archiveExit)

if ($assetsExit -ne 0 -or $archiveExit -ne 0) {
	exit 1
} else {
	exit 0
}