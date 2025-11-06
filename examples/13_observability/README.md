# examples/13_observability — Minimal Jaeger checks

Small utilities to interact with the Jaeger Query API for test assertions and ad-hoc inspection.

## Files

- jaeger_assert.py — Assert at least N traces exist for a service (and optional operation)
- jaeger_assert.ps1 — PowerShell version of the assertion (Windows-first)
- jaeger_query.ps1 — PowerShell helper to list recent traces with span counts
- smoke.sh | smoke.ps1 — CI stubs (still available)

## Examples

- PowerShell assertion (recommended on Windows):
	- `pwsh -File .\jaeger_assert.ps1 -Base http://localhost:16686 -Service demo -Lookback 1h -MinCount 1`
- Python assertion:
	- `python jaeger_assert.py --base http://localhost:16686 --service demo --lookback 1h --min-count 1`
- PowerShell listing helper:
	- `pwsh -File .\jaeger_query.ps1 -Base http://localhost:16686 -Service demo -Limit 10`

Exit codes: 0 pass, 2 fail, 3 error.
