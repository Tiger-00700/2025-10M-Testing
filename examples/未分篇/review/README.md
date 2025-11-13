<!-- markdownlint-disable MD046 -->
# 2025-10M-Testing

## 大数据全栈测试：从理论到实战

Big Data Full-Stack Testing: From Theory to Practice

## Canonical manuscript and generated outputs

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

- Referenced assets inventory: `python tools/inventory_referenced_assets.py`
  - Reads `book/1022.2025.newbook.md` and verifies that all referenced items under `examples/` and `appendix/` exist.
  - Fails the build if any referenced asset is missing.
  - Writes a report under `tools/reports/inventory-assets-*.md`.

- Archive compliance scan: `python tools/inventory_archive_status.py`
  - Ensures each `chapter/*.md` has the MD025 suppression at file top and exactly one archived-content block.
  - Fails the build if any file is non-compliant.
  - Writes a report under `tools/reports/archive-status-*.md`.

Both scripts exit non-zero on failure so CI can gate merges. Unused assets are reported but do not fail the build.

## Local build and tooling

- Build orchestrator (PowerShell): `tools/pipeline/build_all.ps1`
  - Produces the augmented book, appendices, quality report, and runs markdown checks.
  - Exports fenced code blocks from the canonical book into `examples/99_book_exports/` and generates the links-only variant.

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


## More details

See `tools/pipeline/README.md` for organizer details and `tools/README.md` for validation scripts and troubleshooting.

## CI line-endings check (non-blocking)

CI runs a non-blocking check to report line-ending deviations against our policy (LF for code/text; CRLF for Windows scripts like .ps1/.psm1/.psd1/.bat/.cmd). The job logs warnings but does not fail the build. See `.github/workflows/line-endings.yml`.

## Typesetting bundle (one-click)

You can produce a typesetting-ready bundle (HTML/DOCX/PDF + resources) from the frozen manuscript in one command.

### Prerequisites (best-effort rendering)

-- PowerShell 7+ (pwsh)
-- Python 3.10+ (repo venv: `.venv311311/`)
- pandoc (adds DOCX/PDF generation)
- One PDF engine:
  - XeLaTeX (TeX Live/MiKTeX) for high-quality PDF, or
  - wkhtmltopdf as a lightweight alternative

If pandoc is missing, the script will fall back to Python markdown to generate HTML only.

Python fallback requires the `markdown` package; in the repo venv:

```powershell
"E:/DONT TOUCH/10M-2025-Testing/.venv311311/Scripts/python.exe" -m pip install -U markdown
```

### One-click bundle

Run from the repo root (note the quotes for spaces in path):

```powershell
& "tools/pipeline/make_typeset_bundle.ps1"
```

The script pulls from `book/1022.2025.newbook.augmented.frozen.md` and creates a timestamped release under `tools/releases/` with both a folder and a ZIP, for example:


Contents include:


### Publisher templates integration

Drop your publisher assets under `tools/templates/` and they will be picked up automatically by the one-click script:


Notes:


### Customization


### Troubleshooting


