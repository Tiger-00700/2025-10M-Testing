"""Apply fuzzy anchor mappings (base-level) to update broken link fragments.

Logic:
  - Read latest fuzzy-anchor-suggestions-cleaned-*.json.
  - For each confident suggestion: if there exists an actual anchor beginning with that base (exact or with -N suffix), pick the first (lowest suffix) and replace link fragment.
  - Skip if no realized anchor matches candidate base.
  - Create a backup of the book before modifying.
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'
LINK_TARGET_RE = re.compile(r"(\((?:\./)?1022\.2025\.newbook\.cleaned\.md#)([^)\s]+)(\))")
ANCHOR_RE = re.compile(r'^\s*<a\s+id="([^"/]+)"\s*></a>\s*$', re.IGNORECASE)

def latest_json(prefix: str) -> Path | None:
    files = sorted(REPORTS.glob(prefix + '-*.json'))
    return files[-1] if files else None

def load_lines(p: Path):
    return p.read_text(encoding='utf-8').splitlines()

def save_lines(p: Path, lines):
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')

def collect_anchors(lines):
    anchors = []
    for ln in lines:
        m = ANCHOR_RE.match(ln.strip())
        if m:
            anchors.append(m.group(1))
    return anchors

def choose_anchor_for_base(bases: list[str], base: str) -> str | None:
    # exact match first; then base-N (lowest N)
    candidates = []
    for a in bases:
        if a == base:
            candidates.append((0,a))
        elif a.startswith(base + '-'):
            suf = a[len(base)+1:]
            if suf.isdigit():
                candidates.append((int(suf), a))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]

def main():
    js = latest_json('fuzzy-anchor-suggestions-cleaned')
    if not js:
        raise SystemExit('No fuzzy suggestions JSON found.')
    suggestions = json.loads(js.read_text(encoding='utf-8'))
    lines = load_lines(BOOK)
    anchors = collect_anchors(lines)
    applied = 0
    backup = BOOK.with_suffix('.cleaned.md.fuzzy.bak')
    backup.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    # construct line updates
    for i, line in enumerate(lines):
        def replace_func(m):
            prefix, frag, suffix = m.groups()
            # find confident suggestion for this frag
            for s in suggestions:
                if s.get('confident') and s['target'] == frag:
                    base = s['candidates'][0]['anchor_base']  # top candidate
                    chosen = choose_anchor_for_base(anchors, base)
                    if chosen:
                        nonlocal applied
                        applied += 1
                        return f"{prefix}{chosen}{suffix}"
            return m.group(0)
        new_line = LINK_TARGET_RE.sub(replace_func, line)
        lines[i] = new_line
    if applied:
        save_lines(BOOK, lines)
    print(f'Applied fuzzy anchor replacements: {applied}. Backup: {backup.name}')

if __name__ == '__main__':
    main()
