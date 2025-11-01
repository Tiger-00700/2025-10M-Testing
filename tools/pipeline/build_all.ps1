<#
 .SYNOPSIS
   One-shot local orchestrator to build the manuscript and QA artifacts.

 .DESCRIPTION
   Runs the full pipeline locally in this order:
     1) organize_by_outline.ps1
     2) update_latest.ps1
     3) augment_book.ps1
     4) generate_appendices.ps1
     5) fix_links_in_reports.ps1
     6) report_quality.ps1
     7) check_markdown.ps1

   Exits non-zero if any step fails. All scripts are invoked with pwsh.

 .PARAMETER SkipOrganize
   Skip the organize step (useful when only regenerating QA artifacts).
   When set, this also skips updating organized "latest" pointers and
   fixing links in organized-latest, and excludes organized reports from
   markdown checks (env CHECK_INCLUDE_ORGANIZED=0).

 .PARAMETER SkipAugment
   Skip the augmentation step.

 .PARAMETER SkipQA
   Skip the QA steps (quality report + markdown checks).

 .EXAMPLE
   pwsh -NoLogo -NoProfile -File tools/pipeline/build_all.ps1

 .EXAMPLE
   pwsh -NoLogo -NoProfile -File tools/pipeline/build_all.ps1 -SkipOrganize
#>
[CmdletBinding()]
param(
  [switch]$SkipOrganize,
  [switch]$SkipAugment,
  [switch]$SkipQA
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Step {
  param(
    [Parameter(Mandatory)] [string]$Name,
    [Parameter(Mandatory)] [scriptblock]$Action
  )
  Write-Host "==> $Name" -ForegroundColor Cyan
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  & $Action
  $sw.Stop()
  Write-Host "✔ $Name completed in $($sw.Elapsed.ToString())" -ForegroundColor Green
}

# Resolve repo root from this script's location (tools/pipeline)
$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = Resolve-Path (Join-Path $scriptDir '../..')
Set-Location $repoRoot
Write-Host "Repo root: $repoRoot" -ForegroundColor DarkGray

$pwsh = (Get-Process -Id $PID).Path

function Invoke-PwshFile {
  param([Parameter(Mandatory)] [string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Script not found: $Path"
  }
  & $pwsh -NoLogo -NoProfile -File $Path
}

if (-not $SkipOrganize) {
  Invoke-Step -Name 'Organize by outline' -Action {
    Invoke-PwshFile -Path (Join-Path $repoRoot 'tools/pipeline/organize_by_outline.ps1')
  }
} else {
  Write-Host 'Skipping organize step by request' -ForegroundColor Yellow
}

if (-not $SkipOrganize) {
  Invoke-Step -Name 'Update latest pointers' -Action {
    Invoke-PwshFile -Path (Join-Path $repoRoot 'tools/pipeline/update_latest.ps1')
  }
} else {
  Write-Host 'Skipping update of organized latest pointers (SkipOrganize)' -ForegroundColor Yellow
}

if (-not $SkipAugment) {
  Invoke-Step -Name 'Export book code to examples & links variant' -Action {
    & python "tools/export_book_code_to_examples.py"
  }

  # Post-process the links-only book to clean invalid appendix links and
  # convert plain-text script mentions into valid examples/ links
  Invoke-Step -Name 'Fix invalid appendix links in links book' -Action {
    & python "tools/fix_invalid_links_in_links_book.py"
  }

  Invoke-Step -Name 'Link script mentions to examples' -Action {
    & python "tools/link_scripts_to_examples.py"
  }

  Invoke-Step -Name 'Migrate placeholders to semantic examples' -Action {
    & python "tools/migrate_migrated_placeholders_to_semantic.py"
  }

  Invoke-Step -Name 'Organize examples into part directories' -Action {
    & python "tools/migrate_examples_to_part_dirs.py"
  }

  Invoke-Step -Name 'Augment newbook' -Action {
    Invoke-PwshFile -Path (Join-Path $repoRoot 'tools/pipeline/augment_book.ps1')
  }

  Invoke-Step -Name 'Generate appendices' -Action {
    Invoke-PwshFile -Path (Join-Path $repoRoot 'tools/pipeline/generate_appendices.ps1')
  }

  if (-not $SkipOrganize) {
    Invoke-Step -Name 'Fix links in organized-latest' -Action {
      Invoke-PwshFile -Path (Join-Path $repoRoot 'tools/pipeline/fix_links_in_reports.ps1')
    }
  } else {
    Write-Host 'Skipping fix-links for organized-latest (SkipOrganize)' -ForegroundColor Yellow
  }
} else {
  Write-Host 'Skipping augmentation steps by request' -ForegroundColor Yellow
}

if (-not $SkipQA) {
  if ($SkipOrganize) {
    # Exclude organized reports from markdown checks when organizing is skipped
    $env:CHECK_INCLUDE_ORGANIZED = '0'
  }
  Invoke-Step -Name 'Generate quality report' -Action {
    Invoke-PwshFile -Path (Join-Path $repoRoot 'tools/tmp/report_quality.ps1')
  }

  Invoke-Step -Name 'Markdown checks' -Action {
    Invoke-PwshFile -Path (Join-Path $repoRoot 'tools/pipeline/check_markdown.ps1')
  }
} else {
  Write-Host 'Skipping QA steps by request' -ForegroundColor Yellow
}

Write-Host "All steps completed successfully." -ForegroundColor Green
