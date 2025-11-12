# PowerShell script: archive candidates to tools/legacy and run checks
# Usage: run from repo root

$ErrorActionPreference = 'Stop'

$manifestPath = 'tools/reports/tools_candidates_for_pruning.json'
if (-not (Test-Path $manifestPath)) {
    Write-Error "找不到 manifest: $manifestPath"
    exit 1
}

$raw = Get-Content $manifestPath -Raw -Encoding UTF8
$manifest = $raw | ConvertFrom-Json
$candidates = $manifest.candidates

if (-not $candidates -or $candidates.Count -eq 0) {
    Write-Output "清单中无候选项，退出。"
    exit 0
}

$destRoot = Join-Path (Get-Location) 'tools/legacy'
if (-not (Test-Path $destRoot)) { New-Item -ItemType Directory -Path $destRoot -Force | Out-Null }

$moved = @()
$missing = @()
$failed = @()

foreach ($rel in $candidates) {
    $relTrim = $rel.Trim()
    if ([string]::IsNullOrWhiteSpace($relTrim)) { continue }

    $src = Join-Path (Get-Location) $relTrim
    if (-not (Test-Path $src)) {
        $missing += $relTrim
        continue
    }

    $dstFull = Join-Path $destRoot $relTrim
    $dstDir = Split-Path $dstFull -Parent
    if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }

    $isTracked = $false
    try {
        git ls-files --error-unmatch $relTrim 2>$null
        if ($LASTEXITCODE -eq 0) { $isTracked = $true }
    } catch {
        $isTracked = $false
    }

    if ($isTracked) {
        try {
            # Use git mv (escape path)
            git mv --force -- "$relTrim" "$dstFull"
            $moved += $relTrim
            continue
        } catch {
            Write-Warning "git mv 失败，对 $relTrim 使用本地移动：$($_.Exception.Message)"
        }
    }

    # Fallback: Move-Item and git add
    try {
        Move-Item -Path $src -Destination $dstFull -Force
        try { git add "$dstFull" 2>$null } catch {}
        $moved += $relTrim
    } catch {
        Write-Warning "移动失败: $relTrim -> $dstFull; 错误: $($_.Exception.Message)"
        $failed += $relTrim
    }
}

$summary = @{ moved = $moved; missing = $missing; failed = $failed; dest = 'tools/legacy' }
$summaryPath = 'tools/reports/archive_candidates_summary.json'
$summaryJson = $summary | ConvertTo-Json -Depth 10
Set-Content -Path $summaryPath -Value $summaryJson -Encoding UTF8
Write-Output "Wrote summary to $summaryPath"

# Commit changes if any
try {
    # Only commit when there are staged changes
    $status = git status --porcelain
    if ($status) {
        git commit -m "chore(restructure): archive candidate tools into tools/legacy/" -a
        Write-Output "Committed archive changes."
    } else {
        Write-Output "没有变更需要提交。"
    }
} catch {
    Write-Warning "git commit 失败：$($_.Exception.Message)"
}

# Run placeholder check and tests using .venv311 if present
$py = Join-Path (Get-Location) '.venv311/Scripts/python.exe'
if (Test-Path $py) {
    Write-Output "Running placeholder check with $py"
    & $py tools/check_placeholders.py --max-bytes 2048 --allow-file tools/placeholder_whitelist.txt
    Write-Output "Running pytest with $py"
    & $py -m pytest -q
} else {
    Write-Warning ".venv311 中未找到 Python: $py。请在有 Python 的环境中手动运行占位符检查和测试。"
}

Write-Output "Done." 
