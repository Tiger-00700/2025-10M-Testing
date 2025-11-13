import re
from pathlib import Path
from typing import List, Tuple, Dict

BOOK = Path(__file__).resolve().parents[1] / "book" / "1022.2025.newbook.cleaned.md"
OUT = Path(__file__).resolve().parents[1] / "book" / "附录-课后思考练习题索引.md"

heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
punct_re = re.compile(r"[!\"#$%&'()*+,\./:;<=>?@\[\\\]^_`{|}~，。、《》？；：‘’“”（）【】·—…]+")

class Node:
    def __init__(self, level: int, idx: int, title: str):
        self.level = level
        self.idx = idx
        self.title = title
        self.end: int | None = None


def load_lines(p: Path) -> List[str]:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n")


def parse_nodes(lines: List[str]) -> List[Node]:
    nodes: List[Node] = []
    for i, line in enumerate(lines):
        m = heading_re.match(line)
        if m:
            nodes.append(Node(len(m.group(1)), i, m.group(2)))
    for i in range(len(nodes)):
        end = len(lines)
        for j in range(i + 1, len(nodes)):
            if nodes[j].level <= nodes[i].level:
                end = nodes[j].idx
                break
        nodes[i].end = end
    return nodes


def collect_exercises(lines: List[str]) -> List[Tuple[List[str], List[str], str]]:
    nodes = parse_nodes(lines)
    path_stack: List[str] = []
    results: List[Tuple[List[str], List[str], str]] = []

    # map node idx->title for quick lookup and maintain path by scanning
    node_iter = iter(nodes)
    current = next(node_iter, None)

    def update_stack(title: str, level: int):
        nonlocal path_stack
        if level == 1:
            path_stack = [title]
        elif level == 2:
            if len(path_stack) >= 1:
                path_stack = [path_stack[0], title]
            else:
                path_stack = ["", title]
        elif level == 3:
            while len(path_stack) < 2:
                path_stack.append("")
            if len(path_stack) == 2:
                path_stack.append(title)
            else:
                path_stack[2] = title
        else:
            # deeper levels: append/replace last
            if len(path_stack) == 0:
                path_stack = [title]
            elif len(path_stack) == 1:
                path_stack.append(title)
            elif len(path_stack) == 2:
                path_stack.append(title)
            else:
                path_stack[-1] = title

    for i, line in enumerate(lines):
        # advance node pointer and update stack
        while current is not None and i == current.idx:
            update_stack(current.title, current.level)
            current = next(node_iter, None)
        # find exercise block
        if line.strip().startswith("> 【课后思考/练习题】"):
            # collect numbered list until blank line or next heading/marker
            questions: List[str] = []
            j = i + 1
            while j < len(lines):
                s = lines[j].strip()
                if s == "":
                    # allow one blank line inside block, but stop on double blank
                    if j + 1 < len(lines) and lines[j + 1].strip() == "":
                        break
                    j += 1
                    continue
                if heading_re.match(lines[j]) or s.startswith("> 【"):
                    break
                if re.match(r"^\d+\.\s+", s) or s.startswith("-") or s.startswith("*"):
                    questions.append(lines[j])
                j += 1
            if questions:
                # choose anchor title: prefer the deepest non-empty title in path
                anchor_title = next((seg for seg in reversed(path_stack) if seg), path_stack[-1] if path_stack else "")
                results.append((path_stack.copy(), questions, anchor_title))
    return results


def slugify(text: str) -> str:
    t = text.strip().lower()
    # remove ascii and common CJK punctuation
    t = punct_re.sub("", t)
    # collapse whitespace to single hyphens
    t = re.sub(r"\s+", "-", t)
    t = re.sub(r"-{2,}", "-", t)
    return t


def build_anchor_map(lines: List[str]) -> Dict[Tuple[str, ...], str]:
    nodes = parse_nodes(lines)
    path_stack: List[str] = []
    counts: Dict[str, int] = {}

    def update_stack(title: str, level: int):
        nonlocal path_stack
        if level == 1:
            path_stack = [title]
        elif level == 2:
            if len(path_stack) >= 1:
                path_stack = [path_stack[0], title]
            else:
                path_stack = ["", title]
        elif level == 3:
            while len(path_stack) < 2:
                path_stack.append("")
            if len(path_stack) == 2:
                path_stack.append(title)
            else:
                path_stack[2] = title
        else:
            if len(path_stack) == 0:
                path_stack = [title]
            elif len(path_stack) == 1:
                path_stack.append(title)
            elif len(path_stack) == 2:
                path_stack.append(title)
            else:
                path_stack[-1] = title

    def next_id(base: str) -> str:
        n = counts.get(base, 0)
        if n == 0:
            counts[base] = 1
            return base
        else:
            n += 1
            counts[base] = n
            return f"{base}-{n}"

    anchors: Dict[Tuple[str, ...], str] = {}
    for nd in nodes:
        update_stack(nd.title, nd.level)
        if nd.level in (3, 4):
            base = slugify(nd.title)
            aid = next_id(base)
            key = tuple([seg for seg in path_stack if seg])
            anchors[key] = aid
    return anchors


def render_index(entries: List[Tuple[List[str], List[str], str]], anchors: Dict[Tuple[str, ...], str]) -> List[str]:
    out: List[str] = []
    out.append("# 附录 课后思考与练习题索引")
    out.append("")
    out.append("> 说明：本索引自动汇总全书各节的【课后思考/练习题】，按篇/章/节归档，便于教学与查阅。")
    out.append("")
    for path, questions, anchor_title in entries:
        # path like [part, chapter, section, ...]
        key_tuple = tuple([seg for seg in path if seg])
        p = " > ".join(list(key_tuple))
        out.append(f"## {p}")
        out.append("")
        if anchor_title:
            aid = anchors.get(key_tuple)
            if not aid:
                # fallback to slug of title
                aid = slugify(anchor_title)
            out.append(f"[跳转到本节](./1022.2025.newbook.cleaned.md#{aid})")
            out.append("")
        for q in questions:
            out.append(q)
        out.append("")
    return out


def main():
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    lines = load_lines(BOOK)
    entries = collect_exercises(lines)
    anchors = build_anchor_map(lines)
    rendered = render_index(entries, anchors)
    OUT.write_text("\n".join(rendered), encoding="utf-8")
    print(f"Wrote exercise index with {len(entries)} sections to {OUT}")

if __name__ == "__main__":
    main()
