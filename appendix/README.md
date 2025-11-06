# Appendix scripts

This folder contains small, runnable utilities referenced by the book for CI/CD and hands-on labs.

- promql_assert.sh: POSIX shell script to run a PromQL query against a Prometheus HTTP API endpoint and assert numeric results against a threshold.
- promql_assert.ps1: PowerShell version of the same assertion for Windows-first environments.

Both scripts are dependency-light and suitable for use in CI.

## promql_assert.sh

Usage:

- PROM_URL: Base URL of Prometheus, e.g. http://localhost:9090
- QUERY: PromQL expression, e.g. up{job="demo"}
- OP: Comparison operator: gt, ge, lt, le, eq, ne (default: gt)
- THRESHOLD: Numeric threshold to compare against

Exit codes:
- 0: Assertion passed
- 2: Assertion failed
- 3: Script error (usage/network/parse)

Examples:

- PROM_URL=http://localhost:9090 ./promql_assert.sh "up" gt 0
- PROM_URL=http://localhost:9090 ./promql_assert.sh "rate(http_requests_total[5m])" lt 1000

## promql_assert.ps1

Parameters:
- -PromUrl: Base URL of Prometheus, e.g. http://localhost:9090
- -Query: PromQL expression
- -Op: gt|ge|lt|le|eq|ne (default gt)
- -Threshold: [double]

Exit codes are aligned with the shell version.