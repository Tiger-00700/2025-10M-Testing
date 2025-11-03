#!/usr/bin/env python3
"""
Enforce placeholder policy across examples/ to keep the repo consistent.

Rules:
- For small text files (<= max-bytes, default 2048) under examples/, ensure they contain a
  standard placeholder marker if they look like placeholders.
- Marker substring accepted (any of):
  - "Placeholder example file."
  - "Placeholder example README."
- Only checks text-like extensions: .py, .sh, .md, .txt, .yaml, .yml
- Skips files inside version control/CI folders (none expected under examples/).

Exit codes:
- 0: OK
- 1: Violations found

You can override threshold by: --max-bytes 4096
You can run in list-only mode by: --list-only (won't fail, just prints)
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
    ap.add_argument("--max-bytes", type=int, default=2048, help="Max size to consider a file a placeholder candidate")
    ap.add_argument("--list-only", action="store_true", help="List violations but do not fail")
    ap.add_argument("--allow-file", action="append", default=[], help="Path to a file with allow patterns (glob) relative to repo root")
    ap.add_argument("--allow-path", action="append", default=[], help="Inline allow pattern (glob) relative to repo root")
    args = ap.parse_args(argv)

    if not EXAMPLES.exists():
        print("examples/ folder not found; skipping")
        return 0

    # Build allowlist patterns (glob against posix-style relative path)
    allow_files = [Path(s) if s else None for s in args.allow_file]
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
            violations.append(f"{rel} (size={p.stat().st_size} bytes) missing placeholder marker")

    if violations:
        print("[PLACEHOLDER POLICY] Violations:")
        for v in violations:
            print(" -", v)
        if args.list_only:
            return 0
        return 1

    print("[PLACEHOLDER POLICY] OK: All small text files under examples/ carry placeholder markers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
