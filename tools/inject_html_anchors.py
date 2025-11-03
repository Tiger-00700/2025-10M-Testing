import re
from pathlib import Path
from typing import List, Tuple, Dict

BOOK = Path(__file__).resolve().parents[1] / "book" / "1022.2025.newbook.md"

heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
code_fence_re = re.compile(r"^\s*(```|~~~)")
anchor_re = re.compile(r'^\s*<a\s+id="([^"]+)"\s*></a>\s*$', re.IGNORECASE)
punct_re = re.compile(r"[!\"#$%&'()*+,\./:;<=>?@\[\\\]^_`{|}~，。、《》？；：‘’“”（）【】·—…]+")


def load_lines(p: Path) -> List[str]:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n")


def save_lines(p: Path, lines: List[str]):
    p.write_text("\n".join(lines), encoding="utf-8")


def slugify(text: str) -> str:
    t = text.strip().lower()
    t = punct_re.sub("", t)
    t = re.sub(r"\s+", "-", t)
    t = re.sub(r"-{2,}", "-", t)
    return t


def inject_anchors(lines: List[str]) -> Tuple[List[str], int]:
    out: List[str] = []
    inside_code = False
    counts: Dict[str, int] = {}
    injected = 0

    def next_id(base: str) -> str:
        n = counts.get(base, 0)
        if n == 0:
            counts[base] = 1
            return base
        else:
            n += 1
            counts[base] = n
            return f"{base}-{n}"

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if code_fence_re.match(stripped):
            inside_code = not inside_code
            out.append(line)
            i += 1
            continue

        if not inside_code:
            m = heading_re.match(line)
            if m:
                level = len(m.group(1))
                title = m.group(2)
                if level in (3, 4):
                    # Check if previous non-empty line is an anchor
                    prev_idx = len(out) - 1
                    # allow one blank before anchor
                    prev_line = out[prev_idx] if prev_idx >= 0 else ""
                    if prev_line.strip() == "" and prev_idx - 1 >= 0:
                        prev_line2 = out[prev_idx - 1]
                        prev_idx2 = prev_idx - 1
                    else:
                        prev_line2 = None
                        prev_idx2 = None

                    anchor_line_idx = None
                    anchor_id = None

                    # direct previous line
                    am = anchor_re.match(prev_line)
                    if am:
                        anchor_line_idx = prev_idx
                        anchor_id = am.group(1)
                    # or one line above if blank line between
                    elif prev_line.strip() == "" and prev_line2 is not None:
                        am2 = anchor_re.match(prev_line2)
                        if am2:
                            anchor_line_idx = prev_idx2
                            anchor_id = am2.group(1)

                    base = slugify(title)
                    if anchor_id:
                        # update counts to account for existing id
                        m2 = re.match(r"^(.*?)(?:-(\d+))?$", anchor_id)
                        if m2:
                            b = m2.group(1)
                            k = m2.group(2)
                            if k is None:
                                counts[b] = max(counts.get(b, 0), 1)
                            else:
                                counts[b] = max(counts.get(b, 0), int(k))
                        out.append(line)
                        i += 1
                        continue
                    # ensure a blank line before anchor for readability
                    if len(out) > 0 and out[-1].strip() != "":
                        out.append("")
                    new_id = next_id(base)
                    out.append(f"<a id=\"{new_id}\"></a>")
                    injected += 1
                # append the heading line regardless
                out.append(line)
                i += 1
                continue
        # default path
        out.append(line)
        i += 1

    return out, injected


def main():
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    lines = load_lines(BOOK)
    new_lines, injected = inject_anchors(lines)
    save_lines(BOOK, new_lines)
    print(f"Injected {injected} anchors into H3/H4 headings in {BOOK}")


if __name__ == "__main__":
    main()
