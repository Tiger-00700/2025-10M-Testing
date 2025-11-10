from __future__ import annotations
"""
Apply safe anchor mapping fixes to the cleaned book:
- Reads the latest reports/anchor-mapping-suggestions-cleaned-*.json
- Updates links to ./1022.2025.newbook.cleaned.md#... when a suggestion is 'confident'
  (unique candidate with score=1), replacing the fragment with the suggested anchor.
- Writes in-place and creates a .bak backup.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'
LINK_RE = re.compile(r"\((?:\./)?1022\.2025\.newbook\.cleaned\.md#([^\)\s]+)\)")

def latest_suggestions() -> Path | None:
    files = sorted(REPORTS.glob('anchor-mapping-suggestions-cleaned-*.json'))
    return files[-1] if files else None

def load_lines(p: Path):
    return p.read_text(encoding='utf-8').splitlines()

def save_lines(p: Path, lines):
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')

def main():
    js = latest_suggestions()
    if not js or not js.exists():
        raise SystemExit('No suggestions JSON found in tools/reports')
    sugs = json.loads(js.read_text(encoding='utf-8'))
    # build map: line -> list of replacements (old->new)
    repl: dict[int, list[tuple[str,str]]] = {}
    applied = 0
    for s in sugs:
        if not s.get('confident'): continue
        line_no = s['line']
        target = s['target']
        cand = s['candidates'][0]['anchor'] if s['candidates'] else None
        if not cand: continue
        repl.setdefault(line_no, []).append((target, cand))
    if not repl:
        print('No confident suggestions to apply.')
        return
    # apply in-place by lines
    lines = load_lines(BOOK)
    backup = BOOK.with_suffix('.cleaned.md.bak')
    backup.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    for ln, pairs in repl.items():
        idx = ln - 1
        cur = lines[idx]
        for old, new in pairs:
            cur = re.sub(rf"\((?:\./)?1022\.2025\.newbook\.cleaned\.md#{re.escape(old)}\)", f"(./1022.2025.newbook.cleaned.md#{new})", cur)
        lines[idx] = cur
        applied += len(pairs)
    save_lines(BOOK, lines)
    print(f'Applied {applied} confident anchor fixes. Backup: {backup.name}')

if __name__ == '__main__':
    main()
