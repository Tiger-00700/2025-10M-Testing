Param()
Write-Host "Running Windows smoke tests for example directories..."

$root = Resolve-Path -Relative (Join-Path $PSScriptRoot "..\..")

$dirs = @(
  'examples/advanced_methods',
  'examples/01_ecosystem',
  'examples/07_batch',
  'examples/08_analysis',
  'examples/10_tdms',
  'examples/11_automation',
  'examples/17_practices',
  'examples/18_performance',
  'examples/20_trends',
  'examples/21_career_paths'
)

$failed = $false
foreach ($d in $dirs) {
    Write-Host "`n=== Smoke: $d ==="
    $path = Join-Path $root $d
    if (-not (Test-Path $path)) {
        Write-Host "  SKIP: directory not found"
        continue
    }
    # prefer PowerShell script
    $ps1 = Join-Path $path 'ci_demo.ps1'
    if (Test-Path $ps1) {
        Write-Host "  Running $ps1"
        try {
            & pwsh -NoProfile -File $ps1
        } catch {
            Write-Host "  ERROR: $($_.Exception.Message)"
            $failed = $true
        }
        continue
    }
    # Special-case: prefer eda_pandas.py for the analysis example
    if ($d -like '*08_analysis*') {
        $eda = Join-Path $path 'eda_pandas.py'
        if (Test-Path $eda) {
            Write-Host "  Running python eda_pandas.py"
            try {
                python $eda
            } catch {
                Write-Host "  ERROR: $($_.Exception.Message)"
                $failed = $true
            }
            continue
        }
    }
    # run python if present
    $py = Get-ChildItem -Path $path -Filter '*.py' -File -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($py) {
        Write-Host "  Running python $($py.Name)"
        try {
            python $py.FullName
        } catch {
            Write-Host "  ERROR: $($_.Exception.Message)"
            $failed = $true
        }
        continue
    }
    if (Test-Path (Join-Path $path 'README.md')) {
        Write-Host "  INFO: Only README present for $d"
        continue
    }
    Write-Host "  WARN: No runnable example found for $d"
}

if ($failed) { Write-Error "One or more smoke tests failed"; exit 1 }
Write-Host "All smoke tests completed."; exit 0
