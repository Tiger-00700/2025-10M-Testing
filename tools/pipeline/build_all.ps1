<#
.SYNOPSIS
  One-shot orchestrator to build the manuscript and QA artifacts.

.DESCRIPTION
  Runs organize → augment → QA, then post-QA exporters.
  All steps are optional via switches.

.EXAMPLE
  pwsh -NoLogo -NoProfile -File tools/pipeline/build_all.ps1
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
  Write-Host ('==> ' + $Name) -ForegroundColor Cyan
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  & $Action
  $sw.Stop()
  Write-Host ('[OK] ' + $Name + ' in ' + $sw.Elapsed.ToString()) -ForegroundColor Green
}

# Resolve repo root from this script's location (tools/pipeline)
$scriptDir = Split-Path -Parent $PSCommandPath
$repoRoot = Resolve-Path (Join-Path $scriptDir '../..')
Set-Location $repoRoot
Write-Host ('Repo root: ' + $repoRoot) -ForegroundColor DarkGray

function Resolve-PwshExe {
  $cmd = Get-Command pwsh -ErrorAction SilentlyContinue
  if ($null -ne $cmd) { return $cmd.Source }
  # Fallback to current host
  return (Get-Process -Id $PID).Path
}

$pwshExe = Resolve-PwshExe

function Resolve-PythonExe {
  $venvPy = Join-Path $repoRoot '.venv311/Scripts/python.exe'
  if (Test-Path -LiteralPath $venvPy) { return $venvPy }
  return 'python'
}

$pythonExe = Resolve-PythonExe

function Invoke-PwshFile {
  param([Parameter(Mandatory)] [string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    Write-Host ('Skip (missing): ' + $Path) -ForegroundColor Yellow
    return
  }
  & $pwshExe -NoLogo -NoProfile -File $Path
}

function Invoke-PythonIfExists {
  param([Parameter(Mandatory)] [string]$RelPath)
  if (-not (Test-Path -LiteralPath $RelPath)) {
    Write-Host ('Skip (missing): ' + $RelPath) -ForegroundColor Yellow
    return
  }
  & $pythonExe $RelPath
}

if (-not $SkipOrganize) {
  Invoke-Step -Name 'Organize by outline' -Action {
    Invoke-PwshFile -Path (Join-Path $repoRoot 'tools/pipeline/organize_by_outline.ps1')
  }
  Invoke-Step -Name 'Update latest pointers' -Action {
    Invoke-PwshFile -Path (Join-Path $repoRoot 'tools/pipeline/update_latest.ps1')
  }
} else {
  Write-Host 'Skipping organize step by request' -ForegroundColor Yellow
}

if (-not $SkipAugment) {
  Invoke-Step -Name 'Export book code to examples & links variant' -Action {
    Invoke-PythonIfExists -RelPath 'tools/export_book_code_to_examples.py'
  }
  Invoke-Step -Name 'Fix invalid appendix links in links book' -Action {
    Invoke-PythonIfExists -RelPath 'tools/fix_invalid_links_in_links_book.py'
  }
  Invoke-Step -Name 'Link script mentions to examples' -Action {
    Invoke-PythonIfExists -RelPath 'tools/link_scripts_to_examples.py'
  }
  Invoke-Step -Name 'Migrate placeholders to semantic examples' -Action {
    Invoke-PythonIfExists -RelPath 'tools/migrate_migrated_placeholders_to_semantic.py'
  }
  Invoke-Step -Name 'Organize examples into part directories' -Action {
    Invoke-PythonIfExists -RelPath 'tools/migrate_examples_to_part_dirs.py'
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
  }
} else {
  Write-Host 'Skipping augmentation steps by request' -ForegroundColor Yellow
}

if (-not $SkipQA) {
  if ($SkipOrganize) { $env:CHECK_INCLUDE_ORGANIZED = '0' }
  Invoke-Step -Name 'Generate quality report' -Action {
    Invoke-PwshFile -Path (Join-Path $repoRoot 'tools/tmp/report_quality.ps1')
  }
  Invoke-Step -Name 'Markdown checks' -Action {
    Invoke-PwshFile -Path (Join-Path $repoRoot 'tools/pipeline/check_markdown.ps1')
  }
} else {
  Write-Host 'Skipping QA steps by request' -ForegroundColor Yellow
}

# Post-QA exporters (always)
Invoke-Step -Name 'Export fenced code blocks from book' -Action {
  Invoke-PythonIfExists -RelPath 'tools/export_code_blocks.py'
}
Invoke-Step -Name 'Run exports smoke checks' -Action {
  Invoke-PythonIfExists -RelPath 'tools/run_exports_smoke.py'
}
Invoke-Step -Name 'Run pytest coverage for exports' -Action {
  Invoke-PythonIfExists -RelPath 'tools/run_pytest_coverage.py'
}
Invoke-Step -Name 'Lint script exports' -Action {
  Invoke-PythonIfExists -RelPath 'tools/lint_script_exports.py'
}
Invoke-Step -Name 'Report minimal environment requirements' -Action {
  Invoke-PythonIfExists -RelPath 'tools/report_min_environment.py'
}
Invoke-Step -Name 'Export warnings report' -Action {
  Invoke-PythonIfExists -RelPath 'tools/report_export_warnings.py'
}

# 自动合并候选，生成 merged 版本
Invoke-Step -Name 'Apply merge candidates to book (merged version)' -Action {
  Invoke-PythonIfExists -RelPath 'tools/apply_merge_candidates_to_book.py'
}

Invoke-Step -Name 'Cleanup merged book (规范化收尾)' -Action {
  Invoke-PythonIfExists -RelPath 'tools/cleanup_merged_book.py'
}

Invoke-Step -Name 'Diff frozen vs cleaned (占位符/结构对比)' -Action {
  $a = 'book/1022.2025.newbook.augmented.frozen.md'
  $b = 'book/1022.2025.newbook.cleaned.md'
  $out = 'tools/reports/book-diff-frozen-vs-cleaned.md'
  if ((Test-Path $a) -and (Test-Path $b)) {
    & $pythonExe 'tools/diff_books.py' $a $b | Out-File -Encoding utf8 $out
  } else {
    Write-Host "Skip diff: missing $a or $b" -ForegroundColor Yellow
  }
}

Invoke-Step -Name 'Sync twin books (cleaned ↔ 1030)' -Action {
  Invoke-PythonIfExists -RelPath 'tools/sync_twin_books.py'
}

Invoke-Step -Name 'Prune intermediate book files' -Action {
  Invoke-PythonIfExists -RelPath 'tools/prune_book_intermediates.py'
}
Invoke-Step -Name 'Prune unreferenced book files (frozen-driven)' -Action {
  Invoke-PythonIfExists -RelPath 'tools/prune_unreferenced_book_files.py'
}
Invoke-Step -Name 'Generate book reference topology' -Action {
  Invoke-PythonIfExists -RelPath 'tools/book_reference_topology.py'
}

Invoke-Step -Name 'Fill learning blocks (学习目标/小结/练习)' -Action {
  $argsList = @()
  if ($env:LEARNING_BLOCK_STYLE) { $argsList += '--style'; $argsList += $env:LEARNING_BLOCK_STYLE }
  if ($env:LEARNING_BLOCK_REWRITE -eq '1') { $argsList += '--rewrite' }
  if ($env:LEARNING_BLOCK_INPUT) {
    $argsList += '--input'; $argsList += $env:LEARNING_BLOCK_INPUT
  } else {
    # Prefer cleaned book if present; else fallback to frozen (script default)
    $cleaned = 'book/1022.2025.newbook.cleaned.md'
    if (Test-Path -LiteralPath $cleaned) { $argsList += '--input'; $argsList += $cleaned }
  }
  if ($env:LEARNING_BLOCK_OUTPUT) { $argsList += '--output'; $argsList += $env:LEARNING_BLOCK_OUTPUT }
  & $pythonExe 'tools/fill_learning_blocks.py' @argsList
}

Invoke-Step -Name 'Verify book topology (CI checks: cycles/unreferenced)' -Action {
  $argsList = @()
  if ($env:BOOK_CI_FAIL_ON_CYCLES -eq '1') { $argsList += '--fail-on-cycles' }
  if ($env:BOOK_CI_FAIL_ON_UNREF -eq '1') { $argsList += '--fail-on-unreferenced' }
  & $pythonExe 'tools/check_book_topology.py' @argsList
}

Invoke-Step -Name 'Check example links & exercise inventory' -Action {
  $argsList = @()
  if ($env:QUALITY_FAIL_ON_BROKEN_EXAMPLE_LINKS -eq '1') { $argsList += '--fail-on-broken' }
  & $pythonExe 'tools/check_example_links_and_exercises.py' @argsList
}

Invoke-Step -Name 'Annotate exercise difficulty gradient' -Action {
  $argsList = @()
  if ($env:EXERCISE_DIFFICULTY_DRY_RUN -eq '1') { $argsList += '--dry-run' }
  & $pythonExe 'tools/annotate_exercise_difficulty.py' @argsList
}

Invoke-Step -Name 'Inject term anchors & first-use links' -Action {
  & $pythonExe 'tools/inject_term_anchors_and_links.py'
}

Invoke-Step -Name 'Generate related links (See Also blocks)' -Action {
  & $pythonExe 'tools/generate_related_links.py'
}

Invoke-Step -Name 'Aggregate quality dashboard (CI thresholds)' -Action {
  # Optionally enforce internal link cleanliness via QUALITY_MAX_BROKEN_INTERNAL_LINKS=0
  & $pythonExe 'tools/aggregate_quality_dashboard.py'
}

Write-Host 'All steps completed successfully.' -ForegroundColor Green
