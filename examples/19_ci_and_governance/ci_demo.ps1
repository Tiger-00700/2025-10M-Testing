Write-Host "[CI-DEMO] CSV delta check"
python ../06_storage/delta_check.py --old ../06_storage/data/snapshot_v1.csv --new ../06_storage/data/snapshot_v2.csv --key id
if ($LASTEXITCODE -ne 0) { exit 2 }

Write-Host "[CI-DEMO] Prometheus assertion (up>0)"
$env:PROM_URL = 'http://localhost:9090'
powershell -ExecutionPolicy Bypass -File ../../appendix/promql_assert.ps1 -PromUrl $env:PROM_URL -Query 'up' -Op 'gt' -Threshold 0
if ($LASTEXITCODE -ne 0) { exit 2 }

Write-Host "[CI-DEMO] Jaeger traces exist"
python ../13_observability/jaeger_assert.py --base http://localhost:16686 --service demo --min-count 1
if ($LASTEXITCODE -ne 0) { exit 2 }

Write-Host "[CI-DEMO] All checks passed"
exit 0
