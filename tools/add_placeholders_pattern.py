#!/usr/bin/env python3
"""Insert placeholder markers into small example files matching a filename pattern.

Usage:
    python tools/add_placeholders_pattern.py \
        --target examples/99_book_exports \
        --pattern "newbook__block*" \
        --max-bytes 2048 \
        --max-files 500

This is a targeted helper for files that the generic inserter missed due to
path/name patterns. It behaves like tools/add_placeholders.py but filters
files by a shell-style pattern on the filename.
"""
from pathlib import Path
import argparse
import fnmatch

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = ROOT / "examples"
TEXT_EXTS = {".py", ".sh", ".md", ".txt", ".yaml", ".yml"}
COMMENT_FOR = {
    ".py": "# Placeholder example file.",
    ".sh": "# Placeholder example file.",
    ".md": "<!-- Placeholder example README. -->",
    ".txt": "Placeholder example file.",
    ".yaml": "# Placeholder example file.",
    ".yml": "# Placeholder example file.",
}


def has_marker_text(p: Path) -> bool:
    markers = ("Placeholder example file.", "Placeholder example README.")
    try:
        s = p.read_text(encoding='utf-8')
    except Exception:
        try:
            s = p.read_text(errors='ignore')
        except Exception:
            return False
    return any(m in s for m in markers)


def looks_small(p: Path, max_bytes: int) -> bool:
    try:
        return p.stat().st_size <= max_bytes
    except Exception:
        return False


def make_bak_and_prepend(p: Path, marker: str) -> bool:
    bak = p.with_suffix(p.suffix + ".bak")
    if not bak.exists():
        try:
            p.replace(bak)
        except Exception:
            try:
                bak.write_bytes(p.read_bytes())
            except Exception:
                return False
    try:
        content = bak.read_text(encoding='utf-8')
    except Exception:
        content = bak.read_text(errors='ignore')
    new = marker + "\n" + content
    try:
        p.write_text(new, encoding='utf-8')
    except Exception:
        return False
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default=str(DEFAULT_TARGET))
    pattern_help = (
        'Shell-style pattern to match filenames '
        '(e.g. "newbook__block*")'
    )
    ap.add_argument("--pattern", required=True, help=pattern_help)
    ap.add_argument("--max-bytes", type=int, default=2048)
    ap.add_argument("--max-files", type=int, default=500)
    args = ap.parse_args(argv)

    target = Path(args.target)
    if not target.exists():
        print(f"Target {target} not found; nothing to do")
        return 0

    modified = []
    count = 0
    for p in sorted(target.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in TEXT_EXTS:
            continue
        if not fnmatch.fnmatch(p.name, args.pattern):
            continue
        if has_marker_text(p):
            continue
        if not looks_small(p, args.max_bytes):
            continue
        marker = COMMENT_FOR.get(p.suffix.lower(), "Placeholder example file.")
        ok = make_bak_and_prepend(p, marker)
        if ok:
            try:
                rel = p.relative_to(ROOT).as_posix()
            except Exception:
                # fallback to a portable relative path string
                import os

                rel = os.path.relpath(str(p), str(ROOT)).replace('\\', '/')
            modified.append(rel)
            count += 1
            if count >= args.max_files:
                break

    if modified:
        msg = f"Inserted placeholders into {len(modified)} files"
        msg += f" (pattern={args.pattern}):"
        print(msg)
        for m in modified:
            print(" -", m)
    else:
        print("No files matched the pattern/criteria or all already had markers.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
