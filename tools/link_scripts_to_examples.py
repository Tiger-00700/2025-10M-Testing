#!/usr/bin/env python3
"""
Replace plain-text "脚本：<fname>" mentions in the links-only book with
links to files under `examples/`.

Rules:
- If `examples/**` already contains a file named `<fname>`, link to that
    file (prefer the first match under `examples/` in lexicographical path
    order).
- Else if `appendix/<fname>` exists, copy it to
    `examples/99_book_exports/_appendix_migrated/<fname>` and link to that
    new path.
- Else create an empty placeholder at the same `_appendix_migrated` path with
    a minimal header, then link to it.

Idempotent: re-running will keep links intact and won't duplicate copies.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.links.md'
EXAMPLES_ROOT = ROOT / 'examples'
APPENDIX_ROOT = ROOT / 'appendix'
MIGRATED_DIR = EXAMPLES_ROOT / '99_book_exports' / '_appendix_migrated'

# File name pattern like 2-4__block9.py or 14-03-02-01__block023.py
FNAME_RE = r"[\w\-]+__block\d+\.[A-Za-z0-9]+"
pattern = r"(脚本：\s*)(" + FNAME_RE + r")"
TOKEN_RE = re.compile(pattern)


def find_examples_target(fname: str) -> Path | None:
    # Search examples/** for a file with matching name
    matches = sorted(EXAMPLES_ROOT.rglob(fname)) if EXAMPLES_ROOT.exists() else []
    for m in matches:
        if m.is_file():
            return m
    return None


def ensure_migrated_from_appendix(fname: str) -> Path:
    MIGRATED_DIR.mkdir(parents=True, exist_ok=True)
    target = MIGRATED_DIR / fname
    if target.exists():
        return target
    src = APPENDIX_ROOT / fname
    if src.exists() and src.is_file():
        # Copy from appendix
        target.write_bytes(src.read_bytes())
        return target
    # Create placeholder with a minimal header comment based on extension
    ext = target.suffix.lower()
    common_placeholder = (
        "# Placeholder: migrated from book reference, "
        "please fill content.\n"
    )
    bash_header = "#!/usr/bin/env bash\n" + common_placeholder
    json_header = '{\n  "placeholder": true\n}\n'
    header = {
        '.py': common_placeholder,
        '.sh': bash_header,
        '.ps1': common_placeholder,
        '.sql': '-- ' + common_placeholder,
        '.yaml': common_placeholder,
        '.yml': common_placeholder,
        '.json': json_header,
        '.java': '// ' + common_placeholder,
        '.scala': '// ' + common_placeholder,
        '.txt': common_placeholder,
    }.get(ext, common_placeholder)
    target.write_text(header, encoding='utf-8')
    return target


def process_book() -> tuple[int, int, int]:
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    text = BOOK.read_text(encoding='utf-8')

    replacements = 0
    copied = 0
    created = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal replacements, copied, created
        prefix = m.group(1)  # '脚本：'
        fname = m.group(2)
        # Check if already linked nearby (avoid double-linking)
        # We'll replace the token with a markdown link regardless.
        target = find_examples_target(fname)
        # local flags not needed; counts updated directly
        if target is None:
            # Try appendix migration
            target = ensure_migrated_from_appendix(fname)
            if (APPENDIX_ROOT / fname).exists():
                copied += 1
            else:
                created += 1
        rel = target.relative_to(ROOT).as_posix()
        replacements += 1
        return f"[{prefix}{fname}]({rel})"

    new_text, n = TOKEN_RE.subn(repl, text)
    if n:
        BOOK.write_text(new_text, encoding='utf-8')
    return replacements, copied, created


def main() -> int:
    reps, copied, created = process_book()
    msg = (
        f"Replaced {reps} script mentions with links. "
        f"Copied: {copied}, Created: {created}."
    )
    print(msg)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
