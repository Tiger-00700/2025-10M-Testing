"""Inject HTML anchors for H3/H4 headings in cleaned book.

This mirrors tools/inject_html_anchors.py but targets 1022.2025.newbook.cleaned.md
and is idempotent.
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import List, Tuple, Dict

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'

heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
code_fence_re = re.compile(r"^\s*(```|~~~)")
anchor_re = re.compile(r'^\s*<a\s+id="([^"]+)"\s*></a>\s*$', re.IGNORECASE)
punct_re = re.compile(r"[!\"#$%&'()*+,\./:;<=>?@\[\\\]^_`{|}~，。、《》？；：‘’“”（）【】·—…]+")

def load_lines(p: Path) -> List[str]:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n")

def save_lines(p: Path, lines: List[str]):
    p.write_text("\n".join(lines)+"\n", encoding="utf-8")

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
                if level in (2, 3, 4):
                    # look back 1 blank line tolerance
                    prev_idx = len(out) - 1
                    prev_line = out[prev_idx] if prev_idx >= 0 else ""
                    prev_prev = out[prev_idx - 1] if prev_idx - 1 >= 0 else None
                    anchor_id = None
                    m_prev = anchor_re.match(prev_line or "")
                    if m_prev:
                        anchor_id = m_prev.group(1)
                    else:
                        if (prev_line.strip() == "" and prev_prev is not None):
                            m_prev_prev = anchor_re.match(prev_prev)
                            if m_prev_prev:
                                anchor_id = m_prev_prev.group(1)
                    base = slugify(title)
                    if anchor_id:
                        # sync counter
                        m2 = re.match(r"^(.*?)(?:-(\d+))?$", anchor_id)
                        if m2:
                            b = m2.group(1)
                            k = m2.group(2)
                            counts[b] = max(counts.get(b, 0), int(k) if k else 1)
                        out.append(line)
                        i += 1
                        continue
                    if len(out) > 0 and out[-1].strip() != "":
                        out.append("")
                    new_id = next_id(base)
                    out.append(f"<a id=\"{new_id}\"></a>")
                    injected += 1
                out.append(line)
                i += 1
                continue
        out.append(line)
        i += 1
    return out, injected

def main():
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    lines = load_lines(BOOK)
    new_lines, injected = inject_anchors(lines)
    if injected:
        save_lines(BOOK, new_lines)
    print(f"Injected {injected} anchors into H3/H4 headings in {BOOK.name}")

if __name__ == "__main__":
    main()
