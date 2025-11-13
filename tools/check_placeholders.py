#!/usr/bin/env python3
"""
Enforce placeholder policy across `examples/` to keep the repo consistent.

Checks small text files (default <= 2048 bytes) and ensures they contain a
standard placeholder marker when they appear to be placeholders. Only a few
text extensions are checked (.py, .sh, .md, .txt, .yaml, .yml).

Usage notes:
    --max-bytes 4096     # override size threshold
    --list-only          # print violations but don't fail (exit 0)

Exit codes:
    0 = OK, 1 = violations found
"""
from __future__ import annotations
import argparse
from pathlib import Path
from fnmatch import fnmatch

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
DEFAULT_ALLOW_FILE = ROOT / "tools" / "placeholder_whitelist.txt"
TEXT_EXTS = {".py", ".sh", ".md", ".txt", ".yaml", ".yml"}
MARKERS = ("Placeholder example file.", "Placeholder example README.")


def is_text_like(p: Path) -> bool:
    return p.suffix.lower() in TEXT_EXTS


def looks_small(p: Path, max_bytes: int) -> bool:
    try:
        return p.stat().st_size <= max_bytes
    except FileNotFoundError:
        return False


def has_marker(p: Path) -> bool:
    try:
        content = p.read_text(encoding="utf-8")
    except Exception:
        try:
            content = p.read_text(errors="ignore")
        except Exception:
            return False
    return any(m in content for m in MARKERS)


def load_allowlist(files: list[Path], inline: list[str]) -> list[str]:
    patterns: list[str] = []
    for f in files:
        if not f or not f.exists():
            continue
        try:
            for line in f.read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                patterns.append(s)
        except Exception:
            try:
                for line in f.read_text(errors="ignore").splitlines():
                    s = line.strip()
                    if not s or s.startswith("#"):
                        continue
                    patterns.append(s)
            except Exception:
                pass
    patterns.extend([p for p in inline if p])
    return patterns


def is_allowed(rel_posix: str, allow_patterns: list[str]) -> bool:
    return any(fnmatch(rel_posix, pat) for pat in allow_patterns)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check placeholder policy for examples/")
    ap.add_argument(
        "--max-bytes",
        type=int,
        default=2048,
        help="Max size to consider a file a placeholder candidate",
    )
    ap.add_argument(
        "--list-only",
        action="store_true",
        help="List violations but do not fail",
    )
    ap.add_argument(
        "--allow-file",
        action="append",
        default=[],
        help=(
            "Path to a file with allow patterns (glob) relative to repo root"
        ),
    )
    ap.add_argument(
        "--allow-path",
        action="append",
        default=[],
        help=(
            "Inline allow pattern (glob) relative to repo root"
        ),
    )
    args = ap.parse_args(argv)

    if not EXAMPLES.exists():
        print("examples/ folder not found; skipping")
        return 0

    # Build allowlist patterns (glob against posix-style relative path)
    allow_files = [Path(s) for s in args.allow_file if s]
    if DEFAULT_ALLOW_FILE.exists():
        allow_files.append(DEFAULT_ALLOW_FILE)
    allow_patterns = load_allowlist(allow_files, args.allow_path)

    violations: list[str] = []
    for p in EXAMPLES.rglob("*"):
        if not p.is_file():
            continue
        if not is_text_like(p):
            continue
        rel = p.relative_to(ROOT).as_posix()
        if is_allowed(rel, allow_patterns):
            continue
        if looks_small(p, args.max_bytes) and not has_marker(p):
            # Likely a tiny placeholder but without marker
            size = p.stat().st_size
            msg = "{} (size={} bytes) missing placeholder marker".format(rel, size)
            violations.append(msg)

    if violations:
        print("[PLACEHOLDER POLICY] Violations:")
        for v in violations:
            print(" -", v)
        if args.list_only:
            return 0
        return 1

    ok_msg = (
        "[PLACEHOLDER POLICY] OK: All small text files under examples/ "
        "carry placeholder markers."
    )
    print(ok_msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
