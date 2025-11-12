#!/usr/bin/env python3
"""Generate a conservative fix plan for appendix link mismatches.
Only include fixes where the report lists exactly 1 candidate.
Writes: tools/appendix-fix-plan.json
"""
import json
from pathlib import Path
import os

ROOT = Path('.')
REPORT = ROOT / 'tools' / 'appendix-link-report.json'
OUT = ROOT / 'tools' / 'appendix-fix-plan.json'

if not REPORT.exists():
    print('Report not found:', REPORT)
    raise SystemExit(1)

data = json.loads(REPORT.read_text(encoding='utf-8'))
plan = []
for r in data.get('references', []):
    if r.get('exists') is False:
        cands = r.get('candidates') or []
        if len(cands) == 1:
            # candidate is like 'appendix\\file' or 'appendix\x'
            cand = cands[0]
            # candidate is relative to repo root; make absolute path
            cand_path = (ROOT / cand).resolve()
            src = Path(r['source_file'])
            src_path = (ROOT / src).resolve()
            # compute relative path from source file parent
            try:
                rel = os.path.relpath(cand_path, start=src_path.parent)
            except Exception:
                rel = str(cand_path)
            # normalize to forward slashes for markdown
            rel = rel.replace('\\', '/')
            old = r['matched']
            # build new matched string: if old looks like a path, replace basename with rel
            new = rel
            # get context lines
            try:
                lines = src_path.read_text(encoding='utf-8').splitlines()
                idx = r['line'] - 1
                pre = lines[max(0, idx-3):idx]
                old_line = lines[idx]
                post = lines[idx+1:idx+4]
            except Exception:
                pre = []
                old_line = r.get('raw','')
                post = []
            # craft new_line by replacing the first occurrence of old in old_line with new
            if old in old_line:
                new_line = old_line.replace(old, new, 1)
            else:
                # fallback: attempt to replace basename
                import os as _os
                new_line = old_line.replace(_os.path.basename(old), Path(rel).name, 1)
            plan.append({
                'source_file': str(src),
                'line': r['line'],
                'old': old,
                'old_line': old_line,
                'new_line': new_line,
                'pre_context': pre,
                'post_context': post,
                'candidate': str(cand_path),
                'relpath': rel
            })

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
print('Wrote', OUT, 'with', len(plan), 'planned fixes')
