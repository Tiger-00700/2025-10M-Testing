# Tooling quick guide

This folder contains local build utilities and CI validators. The canonical manuscript is `book/1022.2025.newbook.md`.

## Build orchestrator (PowerShell)

- Script: `tools/pipeline/build_all.ps1`
- Produces:
  - `book/1022.2025.newbook.links.md` (code blocks replaced with links)
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

### 2) Links updater (examples/)

- Script: `tools/update_links_from_examples.py`
- Purpose: Check and (optionally) fix Markdown links in `book/1022.2025.newbook.links.md` that point to `examples/` files.
- Strategy:
  - If a link already points to an existing file, keep as-is.
  - If a link is broken but the visible text contains a `__blockNNN.ext` basename, it finds candidate files under `examples/` and picks the best match using URL directory context and token overlap scoring.
  - If multiple candidates tie, the link is left unchanged and recorded as ambiguous.
- Useful options:
  - `--dry-run` — do not write changes; still produces reports.
  - `--fail-on-ambiguous` — exit non-zero when ambiguous matches exist (useful for CI).
  - `--report-json <path>` and `--report-md <path>` — write detailed reports.
- Examples (PowerShell):
  - Dry run with CI-like reporting:
    - `python tools/update_links_from_examples.py --dry-run --fail-on-ambiguous --report-json tools/reports/links-ci.json --report-md tools/reports/links-ci.md`
  - Apply fixes in place:
    - `python tools/update_links_from_examples.py`

### 3) CI integration

- Workflow: `.github/workflows/links-and-inventory.yml`
- Runs on pull requests:
  - Links updater (dry-run, fail on ambiguous) — emits JSON/Markdown report artifacts.
  - Assets inventory — fails when any referenced asset is missing.

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

## Code export from book → examples

- Script: `tools/export_book_code_to_examples.py`
- Purpose: Extract fenced code blocks from `book/1022.2025.newbook.md` into
  `examples/99_book_exports/` and generate `book/1022.2025.newbook.links.md`
  where inline code is replaced by links to those files.
- Integration: Automatically invoked by `build_all.ps1` before augmentation.
- Notes:
  - File names are stable: `newbook__blockNN.<ext>` based on traversal order.
  - Exported脚本按章节自动分层：`examples/99_book_exports/<H2>/<H3>/<H4>/newbook__blockNN.ext`。
    - 目录段采用“数字前缀 + 标题 slug”，例如：`14-02-功能测试案例设计/.../14-02-01-数据采集测试用例/...`。
    - 无对应层级时自动跳过该层级（不会产生空段）。
  - Language-to-extension mapping covers common types (python, bash, ps1, yaml, sql, json, ...).
