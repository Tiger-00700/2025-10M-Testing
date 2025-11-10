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

LINK_RE = re.compile(r"\[[^\]]*\]\((?:\./)?1022\.2025\.newbook\.cleaned\.md#([^)#\s]+)\)")
ANCHOR_RE = re.compile(r'^\s*<a\s+id="([^"/]+)"\s*></a>\s*$', re.IGNORECASE)

def load_lines(p: Path) -> list[str]:
    return p.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n').split('\n')

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
            links.append((i, lm.group(1), ln.strip()))
    broken = [(ln, aid, src) for (ln, aid, src) in links if aid not in anchors]
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    rep = REPORTS / f'internal-anchors-cleaned-{ts}.md'
    out = [f'# Internal Anchors Check ({ts})','',f'Anchors declared: {len(anchors)}',f'Links: {len(links)}',f'Broken: {len(broken)}','']
    if broken:
        out += ['## Broken examples','', '| Line | Anchor | Excerpt |', '|---|---|---|']
        for ln, aid, src in broken[:300]:
            out.append(f'| {ln} | {aid} | {src.replace("|","\\|")[:120]} |')
        if len(broken) > 300:
            out.append(f'... and {len(broken)-300} more')
        out.append('')
    rep.write_text('\n'.join(out), encoding='utf-8')
    print(f'Anchors={len(anchors)} links={len(links)} broken={len(broken)} report={rep.name}')

if __name__ == '__main__':
    main()
