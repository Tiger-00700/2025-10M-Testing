<#!
.SYNOPSIS
  One-click verification for Prometheus and Jaeger using PowerShell.

.DESCRIPTION
  - Detect endpoints (Prometheus, Jaeger)
  - If missing, print startup suggestions (Docker one-liners) and mark as skipped or error
  - Run PromQL assertion and Jaeger assertion using repo scripts
  - Aggregate and report final status with proper exit code

.EXIT CODES
  0: All checks passed (or skipped when -AllowSkip is used)
  2: One or more assertions failed
  3: Environment error (endpoint unreachable and not allowed to skip, script errors)
#>

[CmdletBinding()]
param(
  # Prometheus settings
  [string]$PromUrl = 'http://localhost:9090',
  [string]$PromQuery = 'up',
  [ValidateSet('gt','ge','lt','le','eq','ne')][string]$PromOp = 'gt',
  [double]$PromThreshold = 0,

  # Jaeger settings
  [string]$JaegerBase = 'http://localhost:16686',
  [Parameter(Mandatory=$false)][string]$JaegerService = 'demo',
  [string]$JaegerOperation = '',
  [string]$JaegerLookback = '1h',
  [int]$JaegerMinCount = 1,

  # Behavior
  [switch]$AllowSkip
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-Endpoint {
  param(
    [Parameter(Mandatory=$true)][string]$Url,
    [int]$TimeoutSec = 5
  )
  try {
    $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec
    return $true
  } catch {
    return $false
  }
}

function Write-Header($text) {
  Write-Host "`n=== $text ===" -ForegroundColor Cyan
}

function Resolve-RepoPath([string]$rel) {
  # Ensure resolution from repo root if possible
  $root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)  # tools/pipeline -> tools -> repo root
  $path = Join-Path $root $rel
  return $path
}

Write-Header "Verify Observability (PowerShell)"
Write-Host "Prometheus: $PromUrl | Query: '$PromQuery' $PromOp $PromThreshold"
Write-Host "Jaeger: $JaegerBase | Service: $JaegerService | Op: $JaegerOperation | Lookback: $JaegerLookback | Min: $JaegerMinCount"

$promOk = Test-Endpoint -Url ("{0}/api/v1/status/runtimeinfo" -f $PromUrl.TrimEnd('/'))
if (-not $promOk) {
  Write-Warning "Prometheus endpoint not reachable: $PromUrl"
  Write-Host "Startup suggestion (Docker):" -ForegroundColor Yellow
  Write-Host "  docker run -d --name prometheus -p 9090:9090 prom/prometheus" -ForegroundColor Yellow
}

$jaegerOk = Test-Endpoint -Url ("{0}/api/services" -f $JaegerBase.TrimEnd('/'))
if (-not $jaegerOk) {
  Write-Warning "Jaeger endpoint not reachable: $JaegerBase"
  Write-Host "Startup suggestion (Docker):" -ForegroundColor Yellow
  Write-Host "  docker run -d --name jaeger -p 16686:16686 -p 14268:14268 jaegertracing/all-in-one:1.57" -ForegroundColor Yellow
  Write-Host "If container exists but stopped:  docker start jaeger" -ForegroundColor Yellow
}

$envIssues = @()
if (-not $promOk) { $envIssues += 'prometheus' }
if (-not $jaegerOk) { $envIssues += 'jaeger' }

if ($envIssues.Count -gt 0 -and -not $AllowSkip) {
  Write-Error ("Environment not ready: {0}. Re-run after starting the services or pass -AllowSkip to continue." -f ($envIssues -join ', '))
  exit 3
}

$overall = 0
$results = @()

if ($promOk) {
  Write-Header "Prometheus assertion"
  $promScript = Resolve-RepoPath 'appendix/promql_assert.ps1'
  try {
    & $promScript -PromUrl $PromUrl -Query $PromQuery -Op $PromOp -Threshold $PromThreshold
    $code = $LASTEXITCODE
  } catch { $code = 3 }
  $results += @{ name='prometheus'; code=$code }
  if ($code -eq 2 -and $overall -lt 2) { $overall = 2 }
  elseif ($code -eq 3 -and $overall -lt 3) { $overall = 3 }
} else {
  $results += @{ name='prometheus'; code = 0; skipped = $true }
}

if ($jaegerOk) {
  Write-Header "Jaeger assertion"
  $jaegerScript = Resolve-RepoPath 'examples/13_observability/jaeger_assert.ps1'
  try {
    & $jaegerScript -Base $JaegerBase -Service $JaegerService -Operation $JaegerOperation -Lookback $JaegerLookback -MinCount $JaegerMinCount
    $code = $LASTEXITCODE
  } catch { $code = 3 }
  $results += @{ name='jaeger'; code=$code }
  if ($code -eq 2 -and $overall -lt 2) { $overall = 2 }
  elseif ($code -eq 3 -and $overall -lt 3) { $overall = 3 }
} else {
  $results += @{ name='jaeger'; code = 0; skipped = $true }
}

Write-Header "Summary"
foreach ($r in $results) {
  $status = if ($r.skipped) { 'SKIPPED' } elseif ($r.code -eq 0) { 'PASS' } elseif ($r.code -eq 2) { 'FAIL' } else { 'ERROR' }
  Write-Host ("- {0}: {1} (code={2})" -f $r.name, $status, $r.code)
}

if ($envIssues.Count -gt 0 -and $AllowSkip) {
  Write-Warning ("Skipped due to missing endpoints: {0}" -f ($envIssues -join ', '))
}

if ($overall -eq 0) {
  Write-Host "ALL CHECKS PASSED" -ForegroundColor Green
} elseif ($overall -eq 2) {
  Write-Error "One or more assertions FAILED"
} else {
  Write-Error "Encountered ERROR during verification"
}

exit $overall
