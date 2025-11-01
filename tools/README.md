# Tooling quick guide

This folder contains local build utilities and CI validators. The canonical manuscript is `book/1022.2025.newbook.md`.

## Build orchestrator (PowerShell)

- Script: `tools/pipeline/build_all.ps1`
- Produces:
  - `book/1022.2025.newbook.augmented.md`
  - `book/附录-图表目录.md`, `book/附录-代码清单.md`, `book/附录-脚本索引.md`
  - Quality and lint reports under `tools/reports/`
- Optional flag: `-SkipOrganize` to speed up local checks when you don’t need to re-organize sources.

## CI validators (run locally the same way)

Both validators write timestamped reports to `tools/reports/` and return a non‑zero exit code on failure.

### 1) Referenced assets inventory

- Script: `tools/inventory_referenced_assets.py`
- Purpose: Parse references in the canonical book to `examples/` and `appendix/` files.
- Fails when: Any referenced asset is missing.
- Does not fail for: "Unused" assets (reported for awareness only).
- Output: `tools/reports/inventory-assets-YYYYMMDD-HHMMSS.md`

Run on Windows PowerShell:

- `pwsh`: `python tools/inventory_referenced_assets.py`

### 2) Archive compliance scan

- Script: `tools/inventory_archive_status.py`
- Purpose: Ensure each `chapter/*.md` conforms to the archive pattern:
  1. The very first line disables MD025 (`<!-- markdownlint-disable MD025 -->`).
  2. Exactly one archived-content block wrapping legacy content.
- Fails when: Any chapter is missing the MD025 suppression or the archive block.
- Output: `tools/reports/archive-status-YYYYMMDD-HHMMSS.md`

Run on Windows PowerShell:

- `pwsh`: `python tools/inventory_archive_status.py`

## Archive pattern (reference)

For any file under `chapter/`:

1. Add `<!-- markdownlint-disable MD025 -->` at the top.
2. Keep a minimal navigation stub pointing to `book/1022.2025.newbook.md`.
3. Wrap the legacy content between markers. Example markers:

```text
<!-- archived-content:begin -->
... legacy content ...
<!-- archived-content:end -->
```

## Troubleshooting

- Python not found: Install Python 3.9+ and ensure `python` is on PATH.
- Reports not updating: Delete old files under `tools/reports/` if needed and re-run.
- CI failures: Open the corresponding report in `tools/reports/` and fix the specific file(s) or missing asset(s). Commit and push; CI should turn green.
