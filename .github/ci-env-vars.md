# CI Environment Variables

This document lists environment variables recognized by the build/QA pipeline and tooling. Set them in your CI system (e.g., GitHub Actions `env:` or repository/organization secrets) or locally when running `pwsh`.

## Core pipeline

- BOOK_CI_FAIL_ON_CYCLES: `1` to fail when reference topology has cycles. Default: unset (warn-only).
- BOOK_CI_FAIL_ON_UNREFERENCED: `1` to fail when unreferenced files are detected. Default: unset (warn-only).

## Learning blocks (学习目标/小结/练习)

- LEARNING_BLOCK_STYLE: `balanced` | `academic` | `industry`. Default: `balanced`.
- LEARNING_BLOCK_REWRITE: `1` to force rewrite even if present. Default: unset (idempotent append).
- LEARNING_BLOCK_INPUT: Path to input book. Default: prefers `book/1022.2025.newbook.cleaned.md` if exists, else script defaults.
- LEARNING_BLOCK_OUTPUT: Path to output book. Default: script default.

## Links and examples

- QUALITY_FAIL_ON_BROKEN_EXAMPLE_LINKS: `1` to fail if any example link is broken. Default: unset.

## Internal links (cleaned book)

- QUALITY_MAX_BROKEN_INTERNAL_LINKS: Maximum allowed broken internal links (links to `./1022.2025.newbook.cleaned.md#...`).
  - Recommended: `0` in protected branches.

## Exercise difficulty

- EXERCISE_DIFFICULTY_DRY_RUN: `1` to only report without modifying the book. Default: unset (apply in-place).

## Quality thresholds (dashboard)

- QUALITY_MAX_BROKEN_EXAMPLE_LINKS: integer max allowed broken example links. Default: unset.
- QUALITY_MIN_EXERCISE_TAGGED_RATIO: float [0,1], min required ratio of tagged exercises. Default: unset.
- QUALITY_MIN_SEE_ALSO_BLOCKS: integer min required See Also blocks (optional). Default: unset.
- QUALITY_MAX_SEE_ALSO_BLOCKS: integer max allowed See Also blocks (optional cap). Default: unset.
- QUALITY_MAX_PLACEHOLDERS_A: integer max allowed Type-A (heading) placeholders. Default: unset.
- QUALITY_MAX_PLACEHOLDERS_B: integer max allowed Type-B (inline) placeholders. Default: unset.

## See Also generation

- No env toggles currently. Adjust in `tools/generate_related_links.py`:
  - MIN_SIM (default 0.30), TOP_N (default 2), and dedupe logic.

## PowerShell examples

```powershell
# Fail on topology cycles/unreferenced
$env:BOOK_CI_FAIL_ON_CYCLES = '1'
$env:BOOK_CI_FAIL_ON_UNREFERENCED = '1'

# Enforce link quality
$env:QUALITY_FAIL_ON_BROKEN_EXAMPLE_LINKS = '1'
$env:QUALITY_MAX_BROKEN_INTERNAL_LINKS = '0'

# Learning blocks style
$env:LEARNING_BLOCK_STYLE = 'balanced'
$env:LEARNING_BLOCK_REWRITE = '1'
```

## GitHub Actions example (snippet)

```yaml
env:
  BOOK_CI_FAIL_ON_CYCLES: '1'
  BOOK_CI_FAIL_ON_UNREFERENCED: '1'
  QUALITY_FAIL_ON_BROKEN_EXAMPLE_LINKS: '1'
  QUALITY_MAX_BROKEN_INTERNAL_LINKS: '0'
  LEARNING_BLOCK_STYLE: balanced
  LEARNING_BLOCK_REWRITE: '1'
```

Notes:

- Thresholds are enforced by `tools/aggregate_quality_dashboard.py` after book processing steps.
- Internal link metrics are computed against `book/1022.2025.newbook.cleaned.md`.
- Reports are written under `tools/reports/` with timestamps for traceability.
