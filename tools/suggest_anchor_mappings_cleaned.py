from __future__ import annotations
"""
Suggest mappings for unresolved internal links in cleaned book
([text](./1022.2025.newbook.cleaned.md#...)).

Approach:
- Gather anchors (<a id="..."></a>) and map each to its section path (H1/H2/H3/H4 context).
- For each unresolved link target, use base-id (strip numeric suffix like -2) to
  find candidate anchors; rank by (1) exact path match score, then (2) smaller suffix.
- Emit Markdown and JSON reports; include a 'confident' flag when a unique candidate
  has score=1.
"""
import re, json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Set, Optional

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

ANCHOR_RE = re.compile(r'^\s*<a\s+id="([^"/]+)"\s*></a>\s*$', re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]*\]\((?:\./)?1022\.2025\.newbook\.cleaned\.md#([^\)\s]+)\)")
BASE_RE = re.compile(r"^(.*?)(?:-(\d+))?$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

def load_lines(p: Path) -> List[str]:
    return p.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n').split('\n')

def gather_anchors(lines: List[str]) -> Tuple[Set[str], Dict[str, List[str]], Dict[str, Tuple[str, ...]]]:
    anchors: Set[str] = set()
    base_map: Dict[str, List[str]] = {}
    anchor_to_path: Dict[str, Tuple[str, ...]] = {}
    path_stack: List[str] = []
    last_anchor: Optional[str] = None
    for i, ln in enumerate(lines):
        am = ANCHOR_RE.match(ln.strip())
        if am:
            aid = am.group(1)
            anchors.add(aid)
            b = BASE_RE.match(aid).group(1)
            base_map.setdefault(b, []).append(aid)
            last_anchor = aid
            continue
        hm = HEADING_RE.match(ln)
        if hm:
            level = len(hm.group(1))
            title = hm.group(2)
            if level == 1:
                path_stack = [title]
            elif level == 2:
                path_stack = [path_stack[0] if path_stack else '', title]
            elif level == 3:
                while len(path_stack) < 2:
                    path_stack.append('')
                if len(path_stack) == 2:
                    path_stack.append(title)
                else:
                    path_stack[2] = title
            elif level >= 4:
                if len(path_stack) < 3:
                    while len(path_stack) < 3:
                        path_stack.append('')
                else:
                    path_stack[-1] = title
            if last_anchor and level in (3,4):
                anchor_to_path[last_anchor] = tuple([seg for seg in path_stack if seg])
                last_anchor = None
    # order base_map by numeric suffix
    def sort_key(a: str):
        m = BASE_RE.match(a)
        return int(m.group(2)) if m and m.group(2) else 1
    for k in base_map:
        base_map[k].sort(key=sort_key)
    return anchors, base_map, anchor_to_path

def build_book_context(lines: List[str]) -> List[Tuple[str, ...]]:
    ctx: List[Tuple[str, ...]] = [tuple() for _ in lines]
    path_stack: List[str] = []
    for i, ln in enumerate(lines):
        hm = HEADING_RE.match(ln)
        if hm:
            level = len(hm.group(1))
            title = hm.group(2)
            if level == 1:
                path_stack = [title]
            elif level == 2:
                path_stack = [path_stack[0] if path_stack else '', title]
            elif level == 3:
                while len(path_stack) < 2:
                    path_stack.append('')
                if len(path_stack) == 2:
                    path_stack.append(title)
                else:
                    path_stack[2] = title
            elif level >= 4:
                if len(path_stack) < 3:
                    while len(path_stack) < 3:
                        path_stack.append('')
                else:
                    path_stack[-1] = title
        ctx[i] = tuple([seg for seg in path_stack if seg])
    return ctx

def suggest(lines: List[str], anchors: Set[str], base_map: Dict[str, List[str]], anchor_to_path: Dict[str, Tuple[str, ...]], ctx: List[Tuple[str, ...]]):
    suggestions = []
    for i, ln in enumerate(lines):
        for m in LINK_RE.finditer(ln):
            aid = m.group(1)
            if aid in anchors:
                continue
            base = BASE_RE.match(aid).group(1)
            cands = base_map.get(base, [])
            ranked = []
            for c in cands:
                path = anchor_to_path.get(c, tuple())
                score = 1 if (path and path == ctx[i]) else 0
                suf = BASE_RE.match(c).group(2)
                suf_n = int(suf) if suf else 1
                ranked.append((score, -suf_n, c, path))
            ranked.sort(reverse=True)
            top = [(c, path, sc) for (sc, _s, c, path) in ranked[:5]]
            confident = True if (top and top[0][2] == 1 and len([t for t in top if t[2] == 1]) == 1) else False
            suggestions.append({
                'line': i+1,
                'source': ln.strip(),
                'target': aid,
                'context': list(ctx[i]),
                'candidates': [{'anchor': c, 'path': list(p), 'score': sc} for (c, p, sc) in top],
                'confident': confident,
            })
    return suggestions

def main():
    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    lines = load_lines(BOOK)
    anchors, base_map, anchor_to_path = gather_anchors(lines)
    ctx = build_book_context(lines)
    sugs = [s for s in suggest(lines, anchors, base_map, anchor_to_path, ctx) if s.get('candidates')]
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    md = [f'# Anchor Mapping Suggestions for CLEANED ({ts})','',f'Candidates for unresolved links: {len(sugs)}','']
    for s in sugs[:500]:
        md.append(f"## Line {s['line']} → {s['target']} {'(CONFIDENT)' if s['confident'] else ''}")
        md.append('')
        md.append(f"- Context: {' > '.join(s['context']) if s['context'] else '(none)'}")
        md.append(f"- Source: {s['source']}")
        md.append('- Candidates:')
        for c in s['candidates']:
            md.append(f"  - {c['anchor']} (score={c['score']}) path: {' > '.join(c['path']) if c['path'] else '(none)'}")
        md.append('')
    (REPORTS / f'anchor-mapping-suggestions-cleaned-{ts}.md').write_text('\n'.join(md), encoding='utf-8')
    (REPORTS / f'anchor-mapping-suggestions-cleaned-{ts}.json').write_text(json.dumps(sugs, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Suggestions written: {ts} (total={len(sugs)})')

if __name__ == '__main__':
    main()
