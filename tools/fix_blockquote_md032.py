from __future__ import annotations

from pathlib import Path
import sys


def fix_blockquote_md032(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        # Detect start of a blockquote sequence
        if line.lstrip().startswith("> "):
            start = i
            block: list[str] = []
            while i < n and lines[i].lstrip().startswith("> "):
                block.append(lines[i])
                i += 1

            # Process this blockquote chunk
            fixed_block = _fix_blockquote_block(block)

            # Ensure blank line before blockquote (non-quoted blank)
            if out and out[-1].strip() != "":
                out.append("")

            out.extend(fixed_block)

            # Ensure blank line after blockquote if next line is non-blank and not a blockquote
            if i < n and lines[i].strip() != "" and not lines[i].lstrip().startswith("> "):
                out.append("")
        else:
            out.append(line)
            i += 1

    return "\n".join(out) + "\n"


def _fix_blockquote_block(block: list[str]) -> list[str]:
    """Within a single contiguous blockquote, ensure blank quoted lines
    between label lines (non-list) and list lines, and around lists.
    We keep semantics minimal: only insert lines that are exactly '>'
    (with original indentation preserved for that block).
    """

    if not block:
        return block

    fixed: list[str] = []

    def is_list_item(s: str) -> bool:
        stripped = s.lstrip()
        if not stripped.startswith("> "):
            return False
        content = stripped[2:].lstrip()
        return content.startswith("-") or content[:2].isdigit() and content[2:3] == "."

    for idx, line in enumerate(block):
        prev = block[idx - 1] if idx > 0 else None
        next_line = block[idx + 1] if idx + 1 < len(block) else None

        # If this is the first list item after a non-list within the same block,
        # insert a quoted blank line before it (once).
        if is_list_item(line) and prev is not None and not is_list_item(prev):
            # Use the same leading whitespace and '>' pattern as current line
            prefix = line.split(">", 1)[0]
            quoted_blank = f"{prefix}>"
            if not fixed or fixed[-1].strip() != ">":
                fixed.append(quoted_blank)

        fixed.append(line)

        # If this is the last list item before a non-list within the same block,
        # insert a quoted blank line after it.
        if is_list_item(line) and next_line is not None and not is_list_item(next_line):
            prefix = line.split(">", 1)[0]
            quoted_blank = f"{prefix}>"
            fixed.append(quoted_blank)

    return fixed


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    # Optional path argument; default to 1116 to preserve legacy behavior
    if len(sys.argv) > 1:
        target = (root / sys.argv[1]).resolve() if not Path(sys.argv[1]).is_absolute() else Path(sys.argv[1])
    else:
        target = root / "book" / "1116.2025.newbook.md"
    if not target.exists():
        print(f"Target not found: {target}")
        return
    original = target.read_text(encoding="utf-8")
    fixed = fix_blockquote_md032(original)
    if fixed != original:
        backup = target.with_suffix(".md.bak_md032")
        backup.write_text(original, encoding="utf-8")
        target.write_text(fixed, encoding="utf-8")
        print(f"Updated {target} (backup at {backup})")
    else:
        print("No changes needed; file already MD032-clean for blockquotes.")


if __name__ == "__main__":
    main()
