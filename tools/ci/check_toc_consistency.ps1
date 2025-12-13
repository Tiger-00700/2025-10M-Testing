# Ensures README and manuscript TOC are aligned enough for CI
# Criteria: Parts match = True, no missing chapters in either side.

param(
    [string]$PythonCmd = "python"
)

$ErrorActionPreference = "Stop"

# Run the checker
& $PythonCmd "tools/check_toc_consistency.py" | Out-Host

# Find the latest report
$reportsDir = Join-Path (Split-Path $PSScriptRoot -Parent) "reports"
$latest = Get-ChildItem -Path $reportsDir -Filter "toc_consistency_*.txt" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $latest) {
    Write-Error "No TOC consistency report found in $reportsDir"
}

$content = Get-Content -Path $latest.FullName -Raw

# Basic checks
$partsMatch = $content -match "Parts match: True"
$missingMd   = $content -match "Missing in manuscript: \[\]"
$missingRead = $content -match "Missing in README: \[\]"
$titlesOk    = $content -match "Title mismatches: None"

if ($partsMatch -and $missingMd -and $missingRead -and $titlesOk) {
    Write-Host "TOC CI Check: PASS ($($latest.Name))"
    exit 0
} else {
    Write-Host "TOC CI Check: FAIL ($($latest.Name))"
    # Print summary context
    $lines = $content -split "`n"
    $lines | Where-Object { $_ -match "^(Parts match|Missing in manuscript|Missing in README|Title mismatches)" } | Out-Host
    exit 1
}
