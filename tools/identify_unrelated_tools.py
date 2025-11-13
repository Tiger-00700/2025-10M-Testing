"""Identify tools that don't reference the canonical book or examples and list them for review.
Usage: python tools/identify_unrelated_tools.py
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
KEYWORDS = ['1022.2025.newbook', 'newbook', 'book/', 'examples/', 'check_placeholders', 'placeholder']

candidates = []
related = []
for p in sorted(TOOLS.rglob('*')):
    if p.is_dir():
        continue
    # skip reports
    if 'reports' in p.parts:
        continue
    try:
        s = p.read_text(encoding='utf-8')
    except Exception:
        try:
            s = p.read_text(errors='ignore')
        except Exception:
            s = ''
    if any(k in s for k in KEYWORDS):
        related.append(str(p.relative_to(ROOT)))
    else:
        candidates.append(str(p.relative_to(ROOT)))

out = {
    'related_count': len(related),
    'candidates_count': len(candidates),
    'related': related[:200],
    'candidates': candidates[:200]
}
import json
print(json.dumps(out, ensure_ascii=False, indent=2))
