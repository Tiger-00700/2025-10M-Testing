#!/usr/bin/env python3
"""Generate editorial issue templates for missing appendix references.
Reads: tools/appendix-link-report.json
Writes: tools/editorial-issues/appendix-missing-<NN>.md
"""
import json
from pathlib import Path

ROOT = Path('.')
REPORT = ROOT / 'tools' / 'appendix-link-report.json'
OUT_DIR = ROOT / 'tools' / 'editorial-issues'
OUT_DIR.mkdir(parents=True, exist_ok=True)

if not REPORT.exists():
    print('No report at', REPORT)
    raise SystemExit(1)

data = json.loads(REPORT.read_text(encoding='utf-8'))
missing = [r for r in data.get('references', []) if r.get('exists') is False]

for i, r in enumerate(missing, start=1):
    fname = OUT_DIR / f'appendix-missing-{i:02d}.md'
    title = r.get('matched') or 'MISSING_REF'
    candidates = r.get('candidates') or []
    content = []
    content.append(f"---\ntitle: 'Appendix missing: {title}'\nlabels: editorial,appendix,missing\n---\n")
    content.append(f"## Source\n- file: `{r.get('source_file')}`\n- line: {r.get('line')}\n\n")
    content.append("## Context\n")
    content.append(f"```markdown\n{r.get('raw')}\n```\n\n")
    content.append("## Suggested action checklist\n")
    content.append("- [ ] Confirm whether the referenced appendix file should exist in `appendix/`.\n")
    if candidates:
        content.append("- Candidate(s) discovered in repository (please confirm):\n")
        for c in candidates:
            content.append(f"  - `{c}`\n")
    else:
        content.append("- No candidate files found automatically; please provide the intended target or remove/update reference.\n")
    content.append("\n## Notes for editor\n")
    content.append("- If the intended target exists under a different path, update the markdown to use a relative path from the source file (example: `../appendix/<file>`).\n")
    content.append("- If the file is missing, either add it to `appendix/` or change the reference to a correct location.\n")
    content.append("- If this is a published external URL, consider replacing with the full URL.\n")
    content.append("\n---\n")

    fname.write_text('\n'.join(content), encoding='utf-8')

print('Wrote', len(missing), 'editorial issue templates in', OUT_DIR)
