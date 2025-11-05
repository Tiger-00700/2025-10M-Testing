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

## Typesetting bundle (one-click)

You can produce a typesetting-ready bundle (HTML/DOCX/PDF + resources) from the frozen manuscript in one command.

### Prerequisites (best-effort rendering)

- Windows PowerShell 7+ (pwsh)
- Python virtual env is already provided at `.venv/`
- Optional for DOCX/PDF (recommended):
	- pandoc (adds DOCX/PDF generation)
	- One PDF engine:
		- XeLaTeX (TeX Live/MiKTeX) for high-quality PDF, or
		- wkhtmltopdf as a lightweight alternative

If pandoc is missing, the script will fall back to Python markdown to generate HTML only.

Python fallback requires the `markdown` package; in the repo venv:

```powershell
"E:/DONT TOUCH/10M-2025-Testing/.venv/Scripts/python.exe" -m pip install -U markdown
```

### One-click bundle

Run from the repo root (note the quotes for spaces in path):

```powershell
& "tools/pipeline/make_typeset_bundle.ps1"
```

The script pulls from `book/1022.2025.newbook.augmented.frozen.md` and creates a timestamped release under `tools/releases/` with both a folder and a ZIP, for example:

- Folder: `tools/releases/book-YYYYMMDD-HHMMSS/`
- ZIP: `tools/releases/book-YYYYMMDD-HHMMSS.zip`

Contents include:

- `book.md` (copied frozen manuscript)
- `book.html` (always if pandoc or Python fallback is present)
- `book.docx`, `book.pdf` (when pandoc + PDF engine available)
- `appendices/` (all `book/附录-*.md`)
- `examples/99_book_exports/` (exported code blocks)
- `reports/organized-latest.md`, `reports/toc-latest.txt`
- `bundle.json` (manifest summarizing formats generated and any failures)

### Publisher templates integration

Drop your publisher assets under `tools/templates/` and they will be picked up automatically by the one-click script:

- `tools/templates/reference.docx` — DOCX reference template (Pandoc `--reference-doc`), used when generating `.docx`.
- `tools/templates/metadata.yaml` — Pandoc metadata/variables (via `--metadata-file`) applied to all formats (HTML/DOCX/PDF) when Pandoc is available. You can set title, authors, TOC depth, page geometry, fonts, colorlinks, etc.
- `tools/templates/book.css` — HTML/CSS stylesheet. If Pandoc is present, it is passed with `--css` for HTML. If Pandoc is missing, the Python HTML fallback will inline this CSS automatically for visual consistency.

Notes:

- Fonts named in `metadata.yaml` (e.g., Noto Serif CJK SC) must be installed on the machine to take effect in PDF (XeLaTeX) and may affect HTML rendering.
- If you don’t provide a `reference.docx`, Pandoc’s default DOCX theme is used.
- All templates present under `tools/templates/` are copied into each release folder under `templates/` for traceability.

### Customization

- The script already auto-detects `tools/templates/reference.docx`, `tools/templates/metadata.yaml`, and `tools/templates/book.css` and wires them to Pandoc when available (and CSS is also used by the Python fallback). If you need additional flags, edit `tools/pipeline/make_typeset_bundle.ps1`.

### Troubleshooting

- Execution policy: if PowerShell blocks the script, run from a terminal launched as Administrator or use `-ExecutionPolicy Bypass -File`.
- Paths with spaces: always wrap paths in quotes and use the call operator `&`.
- Pandoc not found: install pandoc and ensure it is in PATH, then re-run the command to enable DOCX/PDF.
- PDF engine missing: install XeLaTeX (TeX Live/MiKTeX) or wkhtmltopdf to enable PDF output.
