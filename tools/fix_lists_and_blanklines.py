import argparse
from pathlib import Path


def is_fence_start(line: str) -> bool:
    l = line.lstrip()
    return l.startswith("```") or l.startswith("~~~")


def is_heading(line: str) -> bool:
    l = line.lstrip()
    return l.startswith("#") and not l.startswith("#######!")


def is_list_item(line: str) -> bool:
    l = line.lstrip()
    if not l:
        return False
    # unordered
    if l.startswith(('- ', '* ', '+ ')):
        return True
    # ordered: digits + . or ) then space
    i = 0
    while i < len(l) and l[i].isdigit():
        i += 1
    if i > 0 and i < len(l) and l[i] in ".)" and i + 1 < len(l) and l[i + 1] == ' ':
        return True
    return False


def is_blockquote(line: str) -> bool:
    l = line.lstrip()
    return l.startswith('>')


def normalize_ordered_marker(line: str) -> str:
    # Convert leading ordered list marker to "1. " while preserving indent
    s = line
    indent_len = len(s) - len(s.lstrip(' '))
    indent = ' ' * indent_len
    l = s.lstrip(' ')
    # digits+.) pattern
    i = 0
    while i < len(l) and l[i].isdigit():
        i += 1
    if i > 0 and i < len(l) and l[i] in ".)":
        # skip the . or ) and one following space if present
        j = i + 1
        if j < len(l) and l[j] == ' ':
            j += 1
        return f"{indent}1. {l[j:]}".rstrip('\n') + ('\n' if line.endswith('\n') else '')
    return line


def process(lines: list[str]) -> list[str]:
    out: list[str] = []
    in_fence = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Track code fences (do not modify inside)
        if is_fence_start(line):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue

        if in_fence:
            out.append(line)
            i += 1
            continue

        # Remove multiple blank lines -> keep max 1
        if line.strip() == "":
            if out and out[-1].strip() == "":
                i += 1
                continue
            # For blockquotes: avoid blank line inside consecutive blockquotes
            prev_is_bq = len(out) > 0 and is_blockquote(out[-1])
            next_is_bq = False
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines):
                next_is_bq = is_blockquote(lines[j])
            if prev_is_bq and next_is_bq:
                i += 1
                continue
            out.append(line)
            i += 1
            continue

        # Normalize ordered list markers to 1. (conservative, outside code fence)
        if is_list_item(line):
            l = line.lstrip()
            if l and l[0].isdigit():
                line = normalize_ordered_marker(line)

        out.append(line)
        i += 1

    # Second pass: ensure blank lines around lists and headings (MD032/MD022)
    final: list[str] = []
    in_fence = False
    for idx, line in enumerate(out):
        if is_fence_start(line):
            in_fence = not in_fence
            final.append(line)
            continue

        if in_fence:
            final.append(line)
            continue

        # Heading: ensure blank before and after
        if is_heading(line):
            if final and final[-1].strip() != "":
                final.append("\n")
            final.append(line)
            nxt = out[idx + 1] if idx + 1 < len(out) else None
            if nxt is not None and nxt.strip() != "":
                final.append("\n")
            continue

        # List block boundaries: ensure blank before/after a list block
        if is_list_item(line):
            # ensure blank before
            k = len(final) - 1
            while k >= 0 and final[k].strip() == "":
                k -= 1
            prev_line = final[k] if k >= 0 else None
            if prev_line is not None and prev_line.strip() != "" and not is_list_item(prev_line) and not is_heading(prev_line) and not is_blockquote(prev_line):
                # only append a blank if we don't already end with a blank
                if not (len(final) > 0 and final[-1].strip() == ""):
                    final.append("\n")

            final.append(line)

            # ensure blank after list block when next non-empty is not list/blockquote
            j = idx + 1
            while j < len(out) and out[j].strip() == "":
                j += 1
            if j < len(out):
                nxt = out[j]
                if not is_list_item(nxt) and not is_blockquote(nxt):
                    if idx + 1 < len(out) and out[idx + 1].strip() != "":
                        final.append("\n")
            continue

        final.append(line)

    return final


def main():
    ap = argparse.ArgumentParser(description="Fix common list and blank line markdown issues conservatively.")
    ap.add_argument("input", help="Input markdown file")
    ap.add_argument("output", help="Output file (candidate)")
    args = ap.parse_args()

    inp = Path(args.input)
    outp = Path(args.output)
    outp.parent.mkdir(parents=True, exist_ok=True)

    data = inp.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    fixed = process(data)
    outp.write_text(''.join(fixed), encoding="utf-8")


if __name__ == "__main__":
    main()
