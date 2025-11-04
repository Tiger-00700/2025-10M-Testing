# 2025-10M-Testing

## Canonical manuscript and generated outputs

- Canonical source (single source of truth): `book/1022.2025.newbook.augmented.md`
- Generated during local build:
	- Links-only book (inline code → links): `book/1022.2025.newbook.links.md`
	- Base book: `book/1022.2025.newbook.md`
	- Appendices: `book/附录-图表目录.md`, `book/附录-代码清单.md`, `book/附录-脚本索引.md`, `book/附录-课后思考练习题索引.md`
	- Exported scripts from book: `examples/99_book_exports/newbook__blockNN.*`

All build logs and QA reports are timestamped under `tools/reports/`.

## Archive pattern for legacy chapter files

All files under `chapter/` follow a minimal, standardized archive pattern:

1) Place `<!-- markdownlint-disable MD025 -->` at the very top (suppresses “multiple top-level headings”).
2) Keep a short navigation stub that points readers to the canonical book above.
3) Wrap the legacy content in a single block (e.g., `<!-- archived-content:begin --> … <!-- archived-content:end -->`).

Our CI verifies this; non-compliance will fail the build (see “CI validations” below).

## CI validations (enforced on PRs/branches)

Two fast checks run in CI and can be executed locally:

- Referenced assets inventory: `tools/inventory_referenced_assets.py`
	- Reads `book/1022.2025.newbook.md` and verifies that all referenced items under `examples/` and `appendix/` exist.
	- Fails the build if any referenced asset is missing.
	- Writes a report under `tools/reports/inventory-assets-*.md`.

- Archive compliance scan: `tools/inventory_archive_status.py`
	- Ensures each `chapter/*.md` has the MD025 suppression at file top and exactly one archived-content block.
	- Fails the build if any file is non-compliant.
	- Writes a report under `tools/reports/archive-status-*.md`.

Both scripts exit non-zero on failure so CI can gate merges. Unused assets are reported but do not fail the build.

## Local build and tooling

- Build orchestrator (PowerShell): `tools/pipeline/build_all.ps1`
	- Produces the augmented book, appendices, quality report, and runs markdown checks.
	- Also exports fenced code blocks from the canonical book into `examples/99_book_exports/` and generates the links-only variant.

### Quick run (Windows PowerShell)

```powershell
# End-to-end build (organize → augment → QA → export)
pwsh -NoLogo -NoProfile -File tools/pipeline/build_all.ps1

# Minimal export & QA sequence (if you only want code exports and tests)
python tools/export_code_blocks.py
python tools/run_exports_smoke.py
python tools/run_pytest_coverage.py
python tools/lint_script_exports.py
python tools/report_min_environment.py
python tools/report_export_warnings.py
```

- Validator scripts and how-to: see `tools/README.md` for quick local run snippets on Windows PowerShell.

## More details

See `tools/pipeline/README.md` for organizer details and `tools/README.md` for validation scripts and troubleshooting.

## CI line-endings check (non-blocking)

CI runs a non-blocking check to report line-ending deviations against our policy (LF for code/text; CRLF for Windows scripts like .ps1/.psm1/.psd1/.bat/.cmd). The job logs warnings but does not fail the build. See `.github/workflows/line-endings.yml`.
