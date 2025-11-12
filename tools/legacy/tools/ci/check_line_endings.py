import sys
from pathlib import Path

"""
Non-blocking line-endings checker for CI.

Policy:
  - Windows scripts: .ps1, .psm1, .psd1, .bat, .cmd -> CRLF allowed
  - Everything else (common text/code): prefer LF, warn on CRLF lines

This script prints a summary of offending files and exits 0 (never fails CI).
"""

WIN_SCRIPT_EXTS = {".ps1", ".psm1", ".psd1", ".bat", ".cmd"}


def is_binary(p: Path) -> bool:
    try:
        data = p.read_bytes()
    except Exception:
        return False
    return b"\x00" in data[:4096]


def main(root: Path):
    offenders = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        # Skip .git directory and reports/artifacts
        if ".git" in p.parts:
            continue
        if any(part == "__pycache__" for part in p.parts):
            continue
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".zip"}:
            continue
        if is_binary(p):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if p.suffix.lower() in WIN_SCRIPT_EXTS:
            # Skip Windows scripts from CRLF warnings
            continue
        if "\r\n" in text:
            offenders.append(p)

    if offenders:
        print("[line-endings] WARNING: Found CRLF in files expected to use LF:")
        for p in offenders:
            print(f" - {p}")
        print(f"Total: {len(offenders)} file(s)")
    else:
        print("[line-endings] OK: No CRLF offenders found for LF-only policy.")

    # Non-blocking: always exit 0
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(__file__).resolve().parents[2]))
