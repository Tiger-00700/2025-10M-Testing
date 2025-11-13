"""Check internal anchor links in cleaned book and report broken ones.

Scans links of the form [text](./1022.2025.newbook.cleaned.md#anchor) and collects
declared anchors as <a id="..."></a>. Reports counts and examples.
"""
from __future__ import annotations
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

LINK_RE_PAT = (
    r"\[[^\]]*\]\((?:\./)?1022\.2025\.newbook\.cleaned\.md#"
    r"([^)#\s]+)\)"
)
LINK_RE = re.compile(LINK_RE_PAT)
ANCHOR_RE = re.compile(
    r'^\s*<a\s+id="([^"/]+)"\s*></a>\s*$',
    re.IGNORECASE,
)

def load_lines(p: Path) -> list[str]:
    txt = p.read_text(encoding='utf-8')
    txt = txt.replace('\r\n', '\n')
    txt = txt.replace('\r', '\n')
    return txt.split('\n')

def main():
    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    lines = load_lines(BOOK)
    anchors = set()
    links = []
    for i, ln in enumerate(lines, start=1):
        m = ANCHOR_RE.match(ln.strip())
        if m: anchors.add(m.group(1))
        for lm in LINK_RE.finditer(ln):
            aid = lm.group(1)
            links.append((i, aid, ln.strip()))
    broken = [(ln, aid, src) for (ln, aid, src) in links if aid not in anchors]
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    rep = REPORTS / f'internal-anchors-cleaned-{ts}.md'
    out = []
    out.append(f'# Internal Anchors Check ({ts})')
    out.append('')
    out.append(f'Anchors declared: {len(anchors)}')
    out.append(f'Links: {len(links)}')
    out.append(f'Broken: {len(broken)}')
    out.append('')
    if broken:
        out.append('## Broken examples')
        out.append('')
        out.append('| Line | Anchor | Excerpt |')
        out.append('|---|---|---|')
        for ln, aid, src in broken[:300]:
            safe_excerpt = src.replace("|", "\\|")[:120]
            row = '| {} | {} | {} |'.format(ln, aid, safe_excerpt)
            out.append(row)
        if len(broken) > 300:
            n_more = len(broken) - 300
            out.append('... and {} more'.format(n_more))
        out.append('')
    rep.write_text('\n'.join(out) + '\n', encoding='utf-8')
    msg = (
        'Anchors=' + str(len(anchors))
        + ' links=' + str(len(links))
        + ' broken=' + str(len(broken))
        + ' report=' + rep.name
    )
    print(msg)

if __name__ == '__main__':
    main()
