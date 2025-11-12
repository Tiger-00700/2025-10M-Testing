# examples/19_ci_and_governance — Minimal CI wiring

Demonstrates how to wire data quality and observability checks into a CI pipeline.

## Files

- pipeline.sample.yml — Example GitHub Actions workflow running three checks
- ci_demo.ps1 — Local demo runner for Windows/pwsh environments
- smoke.sh | smoke.ps1 — CI stubs (still available)

## Checks included

1. CSV time-travel diff: examples/06_storage/delta_check.py
2. Prometheus SLI assertion: appendix/promql_assert.sh or promql_assert.ps1
3. Jaeger trace presence: examples/13_observability/jaeger_assert.py

Note: The sample assumes Prometheus at http://localhost:9090 and Jaeger at http://localhost:16686. Adjust endpoints as needed.

## Appendix scripts moved here

This folder now contains small helper scripts previously stored in `/appendix/`.

- `promql_assert.sh` — POSIX shell script to assert Prometheus query results (see below)
- `promql_assert.ps1` — PowerShell version for Windows/pwsh environments

Usage example (shell):

```bash
PROM_URL=http://localhost:9090 ./promql_assert.sh "up{job=\"demo\"}" gt 0
```

These scripts are dependency-light and suitable for use in CI.

<!-- Placeholder example README. -->
