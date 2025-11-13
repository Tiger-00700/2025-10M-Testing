import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Set, Optional

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book" / "1022.2025.newbook.md"
GLOSS = ROOT / "book" / "附录-术语与缩略语表.md"
EXER = ROOT / "book" / "附录-课后思考练习题索引.md"
REPORTS = ROOT / "tools" / "reports"

ANCHOR_RE = re.compile(r'^\s*<a\s+id="([^"]+)"\s*></a>\s*$', re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]*\]\((?:\./)?1022\.2025\.newbook\.md#([^)\s]+)\)")
BASE_RE = re.compile(r"^(.*?)(?:-(\d+))?$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def load_lines(p: Path) -> List[str]:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n")


def gather_anchors(lines: List[str]) -> Tuple[Set[str], Dict[str, List[str]], Dict[str, Tuple[str, ...]]]:
    anchors: Set[str] = set()
    base_map: Dict[str, List[str]] = {}
    anchor_to_path: Dict[str, Tuple[str, ...]] = {}
    path_stack: List[str] = []
    last_anchor: Optional[str] = None
    for i, ln in enumerate(lines):
        am = ANCHOR_RE.match(ln)
        if am:
            aid = am.group(1)
            anchors.add(aid)
            mbase = BASE_RE.match(aid)
            if mbase:
                b = mbase.group(1)
                base_map.setdefault(b, []).append(aid)
            else:
                # unexpected format: fall back to full id
                base_map.setdefault(aid, []).append(aid)
            last_anchor = aid
            continue
        hm = HEADING_RE.match(ln)
        if hm:
            level = len(hm.group(1))
            title = hm.group(2)
            if level == 1:
                path_stack = [title]
            elif level == 2:
                path_stack = [path_stack[0] if path_stack else "", title]
            elif level == 3:
                if len(path_stack) < 1:
                    path_stack = [""]
                if len(path_stack) == 1:
                    path_stack.append(title)
                else:
                    path_stack[1] = title
            elif level == 4:
                if len(path_stack) < 2:
                    while len(path_stack) < 2:
                        path_stack.append("")
                if len(path_stack) == 2:
                    path_stack.append(title)
                else:
                    if len(path_stack) >= 3:
                        path_stack[2] = title
            if last_anchor and level in (3, 4):
                anchor_to_path[last_anchor] = tuple([seg for seg in path_stack if seg])
                last_anchor = None
    # sort candidates
    def sort_key(a: str):
        m = BASE_RE.match(a)
        if m:
            return int(m.group(2)) if m.group(2) else 1
        return 1
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
                path_stack = [path_stack[0] if path_stack else "", title]
            elif level == 3:
                while len(path_stack) < 2:
                    path_stack.append("")
                if len(path_stack) == 2:
                    path_stack.append(title)
                else:
                    path_stack[2] = title
            elif level >= 4:
                if len(path_stack) < 3:
                    while len(path_stack) < 3:
                        path_stack.append("")
                else:
                    path_stack[-1] = title
        ctx[i] = tuple([seg for seg in path_stack if seg])
    return ctx


def parse_exercise_header(line: str) -> Tuple[str, ...]:
    if line.strip().startswith('## '):
        parts = [p.strip() for p in line.strip()[3:].split('>')]
        parts = [p for p in parts if p]
        return tuple(parts)
    return tuple()


def parse_glossary_row(line: str) -> Tuple[str, ...]:
    if '|' in line:
        cols = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cols) >= 3:
            parts = [p.strip() for p in cols[2].split('>') if p.strip()]
            return tuple(parts)
    return tuple()


def suggest_for_file(p: Path, anchors: Set[str], base_map: Dict[str, List[str]], anchor_to_path: Dict[str, Tuple[str, ...]], book_ctx: Optional[List[Tuple[str, ...]]] = None) -> List[Dict[str, object]]:
    lines = load_lines(p)
    suggestions: List[Dict[str, object]] = []
    exer_ctx: Tuple[str, ...] = tuple()
    for i, ln in enumerate(lines):
        if p == EXER:
            h = parse_exercise_header(ln)
            if h:
                exer_ctx = h
        for m in LINK_RE.finditer(ln):
            aid = m.group(1)
            if aid in anchors:
                continue
            mbase = BASE_RE.match(aid)
            base = mbase.group(1) if mbase else aid
            cands = base_map.get(base, [])
            ctx: Tuple[str, ...] = tuple()
            if p == BOOK and book_ctx is not None:
                ctx = book_ctx[i]
            elif p == EXER:
                ctx = exer_ctx
            elif p == GLOSS:
                ctx = parse_glossary_row(ln)
            # rank: exact path match first, then by suffix number asc
            ranked = []
            for c in cands:
                path = anchor_to_path.get(c, tuple())
                score = 1 if path == ctx and ctx else 0
                # lower numeric suffix is preferred (usually first occurrence)
                m2 = BASE_RE.match(c)
                suf = m2.group(2) if m2 else None
                suf_n = int(suf) if suf else 1
                ranked.append((score, -suf_n, c, path))
            ranked.sort(reverse=True)
            top = [(c, path) for (score, _s, c, path) in ranked[:5]]
            suggestions.append({
                "file": str(p.relative_to(ROOT)),
                "line": i+1,
                "source": ln.strip(),
                "target": aid,
                "context": list(ctx),
                "candidates": [{"anchor": c, "path": list(path)} for (c, path) in top]
            })
    return suggestions


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    book_lines = load_lines(BOOK)
    anchors, base_map, anchor_to_path = gather_anchors(book_lines)
    book_ctx = build_book_context(book_lines)

    files = [BOOK]
    if GLOSS.exists():
        files.append(GLOSS)
    if EXER.exists():
        files.append(EXER)

    all_sugs: List[Dict[str, object]] = []
    for f in files:
        all_sugs.extend(suggest_for_file(f, anchors, base_map, anchor_to_path, book_ctx))

    # Filter only entries where we have candidates
    all_sugs = [s for s in all_sugs if s.get("candidates")]

    # Write markdown report
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    md = ["# Anchor Mapping Suggestions", "", f"Total unresolved links with candidates: {len(all_sugs)}", ""]
    for s in all_sugs[:500]:
        md.append(f"## {s['file']}:{s['line']} → {s['target']}")
        md.append("")
        md.append(f"- Context: {' > '.join(s['context']) if s['context'] else '(none)'}")
        md.append(f"- Source: {s['source']}")
        md.append("- Candidates:")
        for c in s['candidates']:
            md.append(f"  - {c['anchor']}  (path: {' > '.join(c['path']) if c['path'] else '(none)'})")
        md.append("")
    (REPORTS / f"anchor-mapping-suggestions-{ts}.md").write_text("\n".join(md), encoding="utf-8")

    # Also write a machine-readable JSON for later apply
    import json
    (REPORTS / f"anchor-mapping-suggestions-{ts}.json").write_text(json.dumps(all_sugs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote anchor mapping suggestions: {ts}")

if __name__ == '__main__':
    main()
