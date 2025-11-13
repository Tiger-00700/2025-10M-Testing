import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set

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


def save_lines(p: Path, lines: List[str]):
    p.write_text("\n".join(lines), encoding="utf-8")


def gather_anchors(lines: List[str]) -> Tuple[Set[str], Dict[str, List[str]], Dict[str, Tuple[str, ...]]]:
    anchors: Set[str] = set()
    base_map: Dict[str, List[str]] = {}
    anchor_to_path: Dict[str, Tuple[str, ...]] = {}
    # Build mapping by pairing anchor lines with subsequent H3/H4 headings and tracking path
    path_stack: List[str] = []
    last_anchor: Optional[str] = None
    for i, ln in enumerate(lines):
        am = ANCHOR_RE.match(ln)
        if n:
            BOOK_LINKS.write_text(new_text, encoding='utf-8')
            msg = (
                f"Removed {n} invalid appendix links from {BOOK_LINKS.relative_to(ROOT)} "
                f"(backslash:{n1}, slash:{n2})"
            )
            print(msg)
        else:
            print("No invalid appendix links found.")
                b = mbase.group(1)
                base_map.setdefault(b, []).append(aid)
            else:
                # unexpected format; skip
                continue
            last_anchor = aid
            continue
        hm = HEADING_RE.match(ln)
        if hm:
            level = len(hm.group(1))
            title = hm.group(2)
            # update path stack for H1..H4 (deeper levels keep last)
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
            # if a heading arrived right after an anchor, pair it
            if last_anchor and level in (3, 4):
                key = tuple([seg for seg in path_stack if seg])
                anchor_to_path[last_anchor] = key
                last_anchor = None
    # sort each base list by numeric suffix (None or ascending)
    def sort_key(a: str):
        m = BASE_RE.match(a)
        if m:
            return int(m.group(2)) if m.group(2) else 1
        return 1
    for k in base_map:
        base_map[k].sort(key=sort_key)
    return anchors, base_map, anchor_to_path


def build_context_paths_for_book(lines: List[str]) -> List[Tuple[str, ...]]:
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
                # keep last 3 levels only
                if len(path_stack) < 3:
                    while len(path_stack) < 3:
                        path_stack.append("")
                else:
                    path_stack[-1] = title
        ctx[i] = tuple([seg for seg in path_stack if seg])
    return ctx


def parse_exercise_heading_to_path(line: str) -> Tuple[str, ...]:
    # Expect "## A > B > C" pattern
    if line.strip().startswith("## "):
        hdr = line.strip()[3:].strip()
        parts = [p.strip() for p in hdr.split('>')]
        parts = [p for p in parts if p]
        return tuple(parts)
    return tuple()


def parse_glossary_row_path(line: str) -> Tuple[str, ...]:
    # Table row like "| term | zh | A > B > C | [link](...) | brief |"
    if '|' in line:
        cols = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cols) >= 3:
            path = cols[2]
            if path:
                parts = [p.strip() for p in path.split('>')]
                parts = [p for p in parts if p]
                return tuple(parts)
    return tuple()


def fix_file(p: Path, anchors: Set[str], base_map: Dict[str, List[str]], anchor_to_path: Dict[str, Tuple[str, ...]]) -> Tuple[int, List[Tuple[int, str, str]]]:
    lines = load_lines(p)
    changes: List[Tuple[int, str, str]] = []
    fixed = 0
    # Build context by file type
    book_ctx: Optional[List[Tuple[str, ...]]] = None
    current_exer_path: Tuple[str, ...] = tuple()

    def replace_in_line(i: int, line: str) -> str:
        # 'fixed' is modified in the inner repl(); keep nonlocal there.
        # current_exer_path is read by repl() but not assigned here, so
        # no nonlocal declaration is required at this level.
        def repl(m):
            nonlocal fixed
            target = m.group(1)
            if target in anchors:
                return m.group(0)
            b = BASE_RE.match(target).group(1)
            cands = base_map.get(b, [])
            # Try disambiguation by context path when multiple candidates
            if len(cands) > 1:
                context: Tuple[str, ...] = tuple()
                if p == BOOK:
                    nonlocal book_ctx
                    if book_ctx is None:
                        book_ctx = build_context_paths_for_book(lines)
                    context = book_ctx[i] if i < len(book_ctx) else tuple()
                elif p == EXER:
                    context = current_exer_path
                elif p == GLOSS:
                    context = parse_glossary_row_path(line)
                if context:
                    # filter candidates by matching path
                    filt = [aid for aid in cands if anchor_to_path.get(aid, tuple()) == context]
                    if len(filt) == 1:
                        new_id = filt[0]
                        old = m.group(0)
                        new = old.replace('#'+target, '#'+new_id)
                        changes.append((i+1, old.strip(), new.strip()))
                        fixed += 1
                        return new
            if len(cands) == 1:
                new_id = cands[0]
                old = m.group(0)
                new = old.replace('#'+target, '#'+new_id)
                changes.append((i+1, old.strip(), new.strip()))
                fixed += 1
                return new
            return m.group(0)
        return LINK_RE.sub(repl, line)

    for i in range(len(lines)):
        # track exercise appendix context
        if p == EXER:
            ph = parse_exercise_heading_to_path(lines[i])
            if ph:
                current_exer_path = ph
        new_line = replace_in_line(i, lines[i])
        if new_line != lines[i]:
            lines[i] = new_line
    if fixed:
        save_lines(p, lines)
    return fixed, changes


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    book_lines = load_lines(BOOK)
    anchors, base_map, anchor_to_path = gather_anchors(book_lines)

    total_fixed = 0
    all_changes: List[Tuple[str, int, List[Tuple[int, str, str]]]] = []
    for src in (BOOK, GLOSS, EXER):
        if not src.exists():
            continue
        n, ch = fix_file(src, anchors, base_map, anchor_to_path)
        total_fixed += n
        all_changes.append((str(src.relative_to(ROOT)), n, ch))

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    report = REPORTS / f"fixed-links-{ts}.md"
    out = ["# Fixed Links Report", "", f"Total links fixed: {total_fixed}", ""]
    for f, n, ch in all_changes:
        out.append(f"## {f} — fixed: {n}")
        out.append("")
        if ch:
            out.append("| Line | Before | After |")
            out.append("|---|---|---|")
            for (ln, before, after) in ch[:300]:
                safe_before = before.replace('|', '\\|')
                safe_after = after.replace('|', '\\|')
                out.append(f"| {ln} | {safe_before} | {safe_after} |")
            out.append("")
    report.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote fixed links report to {report}")

if __name__ == "__main__":
    main()
