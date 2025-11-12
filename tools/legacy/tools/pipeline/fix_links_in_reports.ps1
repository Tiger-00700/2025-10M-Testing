Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
$orgLatest = Join-Path $repoRoot 'tools/reports/organized-latest.md'
if(-not (Test-Path $orgLatest)) { Write-Host 'No organized-latest.md to fix.'; exit 0 }

$content = Get-Content -LiteralPath $orgLatest -Raw
# Normalize appendix links to repo-root relative from tools/reports
# Replace any sequence of ../ or ..\ preceding 'appendix/' or 'appendix\' with '../../appendix/'
$pattern = '((\.\./|\.\.[\\/])+)(appendix[\\/])'
$content = [regex]::Replace($content, $pattern, '../../appendix/')
Set-Content -LiteralPath $orgLatest -Value $content -Encoding UTF8
Write-Host 'Rewrote appendix links in organized-latest.md to repo-root relative.'
