# examples/06_storage — Time-travel diff (minimal)

This example demonstrates a minimal time-travel diff across two CSV snapshots.

## Files

- delta_check.py — Compare two CSV files by key and report added/removed/changed rows. Exits 2 if differences found.
- data/snapshot_v1.csv — Old snapshot
- data/snapshot_v2.csv — New snapshot
- smoke.sh | smoke.ps1 — Lightweight CI stubs (still available)

## Quick start

Python 3.8+ is sufficient; no extra dependencies.

Examples:

- python delta_check.py --old data/snapshot_v1.csv --new data/snapshot_v2.csv --key id
- python delta_check.py --old data/snapshot_v1.csv --new data/snapshot_v2.csv --key id --compare name,amount

Exit codes:
- 0: No differences for the selected dimensions
- 2: Differences detected (added/removed/changed)
- 3: Usage or input error

This script is suitable for CI; for large datasets, adapt it to Parquet/Delta Lake using PySpark or pandas as needed.
