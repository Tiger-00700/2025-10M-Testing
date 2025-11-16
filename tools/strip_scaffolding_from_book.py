import argparse
import re
from pathlib import Path


ANCHOR_LINE_RE = re.compile(r"^\s*<a id=\"[^\"]+\"></a>\s*$")
LABELS = (
    "学习目标",
    "核心术语",
    "阅读提示",
    "章节重点难点总结",
    "课后思考/练习题",
)
LABEL_START_RE = re.compile(r"^\s*>\s*【(?:" + "|".join(map(re.escape, LABELS)) + r")】")
BLOCKQUOTE_RE = re.compile(r"^\s*>")


def strip_scaffolding(text: str) -> str:
    lines = text.splitlines()
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if ANCHOR_LINE_RE.match(line):
            i += 1
            continue
        if LABEL_START_RE.match(line):
            i += 1
            while i < n and BLOCKQUOTE_RE.match(lines[i]):
                i += 1
            # drop trailing blank lines from removed block
            while i < n and lines[i].strip() == "":
                i += 1
            continue
        out.append(line)
        i += 1
    # collapse multiple blank lines to at most one
    cleaned = []
    blank = False
    for l in out:
        if l.strip() == "":
            if not blank:
                cleaned.append("")
            blank = True
        else:
            cleaned.append(l)
            blank = False
    return "\n".join(cleaned) + ("\n" if cleaned and cleaned[-1] != "" else "")


def main():
    ap = argparse.ArgumentParser(description="Strip anchors and scaffold blockquotes from Markdown book")
    ap.add_argument("input", nargs="?", default="book/1022.2025.newbook.cleaned.md")
    ap.add_argument("--output", default=None, help="Optional output path; defaults to in-place overwrite")
    ap.add_argument("--in-place", action="store_true", help="Write changes back to input file")
    args = ap.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        raise SystemExit(f"Input file not found: {inp}")
    text = inp.read_text(encoding="utf-8")
    new_text = strip_scaffolding(text)

    if args.output:
        Path(args.output).write_text(new_text, encoding="utf-8")
        print(f"Wrote cleaned output: {args.output}")
    else:
        # Default to in-place if requested or if no output specified
        if not args.in_place:
            # safety: show a brief summary and require --in-place for overwrite
            removed = len(text) - len(new_text)
            print(f"Dry-run: {removed} bytes would be removed. Use --in-place to overwrite or --output to write elsewhere.")
            return
        inp.write_text(new_text, encoding="utf-8")
        print(f"Updated in-place: {inp}")


if __name__ == "__main__":
    main()
