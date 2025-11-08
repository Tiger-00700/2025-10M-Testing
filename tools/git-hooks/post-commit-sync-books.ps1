param()
$ErrorActionPreference = 'Stop'

# Resolve repo root = this script's parent parent
$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = Resolve-Path (Join-Path $scriptDir '../..')
Set-Location $repoRoot

# If either twin book changed in the last commit, sync them
$changed = git --no-pager diff --name-only HEAD~1 HEAD 2>$null
if ($LASTEXITCODE -ne 0) { $changed = git --no-pager show --name-only --pretty="format:" HEAD }

$twinA = 'book/1022.2025.newbook.cleaned.md'
$twinB = 'book/1030.2025.book.md'

if ($changed -match [regex]::Escape($twinA) -or $changed -match [regex]::Escape($twinB)) {
  Write-Host '[post-commit] Twin books changed, syncing...' -ForegroundColor Cyan
  python tools/sync_twin_books.py | Out-Host
} else {
  Write-Host '[post-commit] No twin book changes.' -ForegroundColor DarkGray
}

<#
Install:
  Copy this file to .git/hooks/post-commit and make it executable.
  On Windows:
    Copy-Item tools/git-hooks/post-commit-sync-books.ps1 .git/hooks/post-commit
#>