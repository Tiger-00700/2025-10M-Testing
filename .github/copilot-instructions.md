# Copilot Instructions for 2025-10M-Testing

## Project Overview
- **Canonical source**: All book content is maintained in `book/1022.2025.newbook.augmented.md`.
- **Generated outputs**: Build scripts produce various exports (links-only, appendices, code blocks) under `book/` and `examples/99_book_exports/`.
- **Appendix and examples**: All referenced scripts and data are under `appendix/` and `examples/`.

## Architecture & Data Flow
- **Book build pipeline**: Orchestrated by PowerShell scripts in `tools/pipeline/`.
  - `build_all.ps1` runs the full pipeline: organize → augment → appendices → QA → export.
  - Outputs and logs are timestamped in `tools/reports/`.
- **CI/CD**: Validates asset references and archive compliance using Python scripts in `tools/`.
  - `inventory_referenced_assets.py` ensures all referenced files exist.
  - `inventory_archive_status.py` enforces archive patterns in `chapter/`.
- **Archive pattern**: All `chapter/*.md` files must start with `<!-- markdownlint-disable MD025 -->` and wrap legacy content in a single `archived-content` block.

## Developer Workflows
- **Full build (Windows PowerShell):**
  ```powershell
  pwsh -NoLogo -NoProfile -File tools/pipeline/build_all.ps1
  ```
- **Quick validation (Python):**
  ```powershell
  python tools/inventory_referenced_assets.py
  python tools/inventory_archive_status.py
  ```
- **Manual pipeline steps:**
  - Organize: `tools/pipeline/organize_by_outline.ps1`
  - Augment: `tools/pipeline/augment_book.ps1`
  - Appendices: `tools/pipeline/generate_appendices.ps1`
  - QA: `tools/pipeline/check_markdown.ps1`

## Project Conventions
- **Line endings**: LF for code/text, CRLF for Windows scripts. CI checks but does not block on violations.
- **Appendix scripts**: Must be dependency-light and runnable in CI (see `appendix/README.md`).
- **Links**: All links to `examples/` are validated and can be auto-fixed with `tools/update_links_from_examples.py`.
- **Reports**: All validation and build scripts write timestamped reports to `tools/reports/`.

## Key Files & Directories
- `book/` — Canonical and generated manuscripts
- `chapter/` — Archived legacy chapters (must follow archive pattern)
- `examples/`, `appendix/` — Referenced scripts, data, and code exports
- `tools/` — Build, validation, and CI scripts
- `tools/pipeline/` — Orchestrator and pipeline scripts
- `tools/reports/` — All build/validation logs and reports

## Examples
- To export code blocks and run smoke tests:
  ```powershell
  python tools/export_code_blocks.py
  python tools/run_exports_smoke.py
  ```
- To check/fix links in the links-only book:
  ```powershell
  python tools/update_links_from_examples.py --dry-run --fail-on-ambiguous
  ```

## Troubleshooting
- See `tools/README.md` and `tools/pipeline/README.md` for script usage and troubleshooting tips.
- All build/validation failures are logged in `tools/reports/` with timestamps for traceability.

---

For any unclear or missing conventions, review the root `README.md` and `tools/README.md` for up-to-date workflow and policy details.
