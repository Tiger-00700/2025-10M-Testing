# Requires -Version 5.1
# Minimal build pipeline for two books only:
# - book/1116.2025.newbook.md
# - book/1130.2025.newbook.md
# Orchestrates available Python validators and format fixers, writes timestamped reports.

param(
    [string]$PythonExe = ".venv311/Scripts/python.exe"
)

$ErrorActionPreference = "Stop"

function Resolve-RepoPath([string]$rel) {
    return Join-Path -Path (Get-Location) -ChildPath $rel
}

function Ensure-ReportsDir {
    $reports = Resolve-RepoPath "tools/reports"
    if (-not (Test-Path $reports)) {
        New-Item -ItemType Directory -Path $reports | Out-Null
    }
    return $reports
}

function Get-Timestamp {
    return (Get-Date).ToString("yyyyMMdd_HHmmss")
}

function Invoke-Python([string]$script, [string[]]$pyArgs) {
    $py = Resolve-RepoPath $PythonExe
    $full = Resolve-RepoPath $script
    if (-not (Test-Path $py)) { throw "Python executable not found: $py" }
    if (-not (Test-Path $full)) { throw "Script not found: $full" }
    & $py $full @pyArgs
}

function Validate-Books {
    param([string[]]$books)
    foreach ($b in $books) {
        $path = Resolve-RepoPath $b
        if (-not (Test-Path $path)) {
            Write-Warning "Missing book: $b"
        } else {
            Write-Host "Found book: $b"
        }
    }
}

function Run-FormatFixers {
    param([string[]]$books)
    Write-Host "Running format fixers on target books (non-destructive for 1116)"
    foreach ($b in $books) {
        $inPath = Resolve-RepoPath $b
        if (-not (Test-Path $inPath)) { continue }
        # Only apply aggressive fixes to 1130; keep 1116 content intact
        $is1130 = $b -like "book/1130*.md"
        if ($is1130) {
            $tmpOut = [System.IO.Path]::ChangeExtension($inPath, ".formatted.tmp.md")
            Write-Host "Fix lists/blanklines: $b"
            try { Invoke-Python "tools/fix_lists_and_blanklines.py" @($b, $tmpOut) } catch { Write-Warning $_.Exception.Message }
            if (Test-Path (Resolve-RepoPath $tmpOut)) {
                Copy-Item -Force (Resolve-RepoPath $tmpOut) $inPath
                Remove-Item (Resolve-RepoPath $tmpOut) -ErrorAction SilentlyContinue
            }
            Write-Host "Wrap long lines: $b"
            try { Invoke-Python "tools/wrap_long_lines.py" @($b) } catch { Write-Warning $_.Exception.Message }
            Write-Host "Fix blockquotes MD032: $b"
            try { Invoke-Python "tools/fix_blockquote_md032.py" @($b) } catch { Write-Warning "No changes needed or script requires different usage." }
        } else {
            Write-Host "Skipping aggressive format for $b to preserve content"
        }
    }
}

function Run-AssetsInventory {
    $reports = Ensure-ReportsDir
    $ts = Get-Timestamp
    Write-Host "Running assets inventory"
    try {
        Invoke-Python "tools/asset_all.py" @("--include-appendices")
        Write-Host "Assets inventory (scoped) completed"
    } catch {
        Write-Warning $_.Exception.Message
    }
}

function Run-ArchiveStatus {
    $reports = Ensure-ReportsDir
    $ts = Get-Timestamp
    Write-Host "Running archive status inventory"
    try {
        Invoke-Python "tools/inventory_archive_status.py" @()
        Write-Host "Archive status inventory completed"
    } catch {
        Write-Warning $_.Exception.Message
    }
}

function Run-MissingAssetsGrouped {
    Write-Host "Generating grouped missing assets report"
    try {
        Invoke-Python "tools/report_missing_assets_grouped.py" @()
        Write-Host "Grouped missing assets report generated"
    } catch {
        Write-Warning $_.Exception.Message
    }
}

function Run-NumberingQA {
    Write-Host "Running numbering consistency QA (read-only)"
    try {
        Invoke-Python "tools/check_subsection_numbering.py" @()
        Write-Host "Numbering consistency QA completed"
    } catch {
        Write-Warning $_.Exception.Message
    }
}

# Entry
$books = @(
    "book/1116.2025.newbook.md",
    "book/1130.2025.newbook.md"
)

Write-Host "==== Build (two books) started ===="
Validate-Books -books $books
Run-FormatFixers -books $books
Run-AssetsInventory
Run-ArchiveStatus
Run-MissingAssetsGrouped
Run-NumberingQA
Write-Host "==== Build (two books) completed ===="
