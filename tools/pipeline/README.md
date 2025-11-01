# Organizer pipeline

This folder contains the canonical PowerShell script for assembling the manuscript by the outline, with exact/alias/fuzzy matching, plus utilities for augmentation and QA. A local one-shot orchestrator is provided for convenience.

## Files

- `organize_by_outline.ps1` (canonical)
  - Reads outline: `book/篇章结构.md`
  - Base manuscript: `book/1022.2025.newbook.md`
  - Source manuscript: `book/1022.2025.book.md`
  - Outputs into `tools/reports/`:
    - `organized-<ts>.md` — assembled manuscript
    - `organize-log-<ts>.md` — run log with Missing count and matching details
    - `toc-<ts>.txt` — table of contents of the outline
- `update_latest.ps1`
  - Copies newest run artifacts to stable aliases: `organized-latest.md`, `organize-log-latest.md`, `toc-latest.txt`.
- `augment_book.ps1`
  - Inserts per-chapter skeletons (学习目标/小结/练习) and embeds content from `examples/` & `appendix/` with language labels. Marks generated blocks with `<!-- augment:code -->`.
- `generate_appendices.ps1`
  - Generates `book/附录-图表目录.md`, `book/附录-代码清单.md`, `book/附录-脚本索引.md` from the latest organized output and repository file trees.
- `fix_links_in_reports.ps1`
  - Normalizes appendix links in `tools/reports/organized-latest.md` to CI-friendly relative paths.
- `check_markdown.ps1`
  - QA checks: ensures language labels for generated code fences and validates links/images in `organized-latest.md`.
- `build_all.ps1`
  - One-shot local orchestrator: organize ➜ update_latest ➜ augment ➜ appendices ➜ link-fix ➜ quality report ➜ markdown checks.
- `../tmp/report_missing.ps1`
  - Summarizes the latest Missing count, compares with the previous run, and prints the Top 10 MISS entries.
- `organize_by_outline.fixed.ps1` (deprecated)
  - Kept for reference only. Use `organize_by_outline.ps1` instead.

## Quickstart (Windows PowerShell)

Run everything locally (recommended):

```powershell
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "tools/pipeline/build_all.ps1"
```

Optional switches:

- `-SkipOrganize` — reuse last organized output (faster while iterating on augmentation/QA)
- `-SkipAugment` — skip augmentation & appendices generation
- `-SkipQA` — skip quality report & markdown checks

## Manual run (advanced)

1. Assemble by outline

```powershell
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "tools/pipeline/organize_by_outline.ps1"
```

2. Summarize Missing and delta

```powershell
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "tools/tmp/report_missing.ps1"
```

Outputs are timestamped in `tools/reports/`.

## Post-run utilities

3. Update stable "latest" links

Use this after a successful run to refresh stable pointers used by the root README:

```powershell
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "tools/pipeline/update_latest.ps1"
```

This writes/refreshes:

- `tools/reports/organized-latest.md`
- `tools/reports/organize-log-latest.md`
- `tools/reports/toc-latest.txt`

4. Generate a quality summary

Produces a compact distribution of match modes and heading levels for the most recent run:

```powershell
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "tools/tmp/report_quality.ps1"
```

The report is saved as `tools/reports/quality-<ts>.md`. In CI, the newest file may also be copied to `tools/reports/quality-latest.md` for convenience.

5. Run link fixer and markdown checks

```powershell
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "tools/pipeline/fix_links_in_reports.ps1"
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "tools/pipeline/check_markdown.ps1"
```

## Matching strategy

- Normalization:
  - Remove invisible chars, unify punctuation, convert Chinese numerals
  - Drop bracketed segments and section numbering for fuzzy
  - Synonym unification: 特征→特点, 海量数据→大数据, 比较→对比, 等
- Aliases:
  - Exact alias, alias-any fallback, and numeric-prefix-insensitive + prefix matches
  - Targeted alias map for hotspot sections (11.x/15.x/16.x/17.x/19.x/21.x, etc.)
- Fuzzy:
  - Bigram Dice with containment bonus
  - Proximity boosts: same-part (+0.10), same-level (+0.03)
  - Thresholds: H1–H2=0.62, H3=0.66, H4=0.70, H5+=0.68

## Tips

- To fine-tune matches, update `Get-AliasKeys` inside `organize_by_outline.ps1`.
- For deeper generic subheads (H5/H6) that are phrased like “定义与价值/必要性/分类/挑战”, map them to their logical parent section via aliases.
- If you adjust thresholds, re-run the organizer and the report script to validate Missing remains stable.

## Troubleshooting

- If push fails due to network, retry later:

```powershell
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "git push"
```

- If PSScriptAnalyzer warns about unapproved verbs, note that the canonical script uses an approved verb (Invoke). The deprecated `*.fixed.ps1` may still trigger warnings and is safe to ignore.

## CI overview

The workflow `.github/workflows/organizer.yml` runs on push and includes:

1. Organizer ➜ updates stable `*-latest` pointers
2. Augmentation (`augment_book.ps1`) and appendices generation
3. Link normalization in `organized-latest.md`
4. Quality report generation + copy to `quality-latest.md`
5. Markdown checks (generated code fence language labels, links/images)

The build fails if Missing > 0 or markdown checks fail. Artifacts (organized outputs, logs, TOC, quality report, appendices, augmented book) are uploaded for inspection.
