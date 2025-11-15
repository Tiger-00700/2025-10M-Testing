"""
Inventory and validate referenced assets in Markdown files.

Scans book/ and chapter/ Markdown files for local links and images, then
verifies that referenced paths exist within the repository. Writes a
timestamped report under tools/reports/ and exits non-zero if any
missing assets are detected.

Usage (default sources):
  python tools/inventory_referenced_assets.py

Optional:
  python tools/inventory_referenced_assets.py --sources book/*.md chapter/*.md
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "tools" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)


LINK_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)|\[[^\]]*\]\(([^)]+)\)")


def _is_external(url: str) -> bool:
    u = url.strip()
    if not u:
        return True
    u_lower = u.lower()
    return (
        u_lower.startswith("http://")
        or u_lower.startswith("https://")
        or u_lower.startswith("mailto:")
        or u_lower.startswith("javascript:")
        or u_lower.startswith("#")
    )


def _strip_title(url: str) -> str:
    # Markdown allows "url title" inside (), optionally quoted title.
    # We keep only the URL part up to first whitespace, unless the URL is quoted.
    s = url.strip()
    if not s:
        return s
    if s.startswith("<") and s.endswith(">"):
        return s[1:-1].strip()
    if s.startswith("\"") or s.startswith("\'"):
        # Rare: "url with spaces" "title" — keep first quoted blob
        m = re.match(r"^([\"\'])(.*?)(\1)", s)
        if m:
            return m.group(2)
    # Default: split at first whitespace
    return s.split()[0]


def _strip_anchor(url: str) -> str:
    # Remove fragment part after #, but keep urls that are only '#...'
    if url.startswith('#'):
        return url
    if '#' in url:
        return url.split('#', 1)[0]
    return url


def _gather_markdown_files(patterns: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for pat in patterns:
        files.extend(sorted(ROOT.glob(pat)))
    # unique and only files
    seen = set()
    result: List[Path] = []
    for p in files:
        if p.is_file() and p not in seen:
            seen.add(p)
            result.append(p)
    return result


def _resolve_ref(base: Path, ref: str) -> Path:
    # Resolve relative to the file's directory; normalize .. and . segments
    return (base.parent / ref).resolve()


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--sources",
        nargs="*",
        default=["book/*.md", "chapter/*.md"],
        help="Glob patterns (relative to repo root) for Markdown sources",
    )
    args = ap.parse_args(argv)

    sources = _gather_markdown_files(args.sources)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS / f"assets_inventory_{ts}.txt"

    missing: List[Tuple[Path, str, Path]] = []
    checked = 0

    with report_path.open("w", encoding="utf-8") as rep:
        rep.write(f"Inventory referenced assets report @ {ts}\n")
        rep.write(f"Sources: {len(sources)} files\n\n")

        for md in sources:
            text = md.read_text(encoding="utf-8", errors="ignore")
            for m in LINK_RE.finditer(text):
                raw = m.group(1) if m.group(1) is not None else m.group(2)
                if raw is None:
                    continue
                url = _strip_title(raw)
                if _is_external(url):
                    continue
                url_no_anchor = _strip_anchor(url)
                if not url_no_anchor or url_no_anchor.startswith('#'):
                    continue
                # Skip pure anchors or in-doc references
                resolved = _resolve_ref(md, url_no_anchor)
                checked += 1
                status = "OK" if resolved.exists() else "MISSING"
                rep.write(f"{md.relative_to(ROOT)} :: {url_no_anchor} -> {resolved} [{status}]\n")
                if status == "MISSING":
                    missing.append((md, url_no_anchor, resolved))

        rep.write("\nSummary:\n")
        rep.write(f"  Checked refs: {checked}\n")
        rep.write(f"  Missing: {len(missing)}\n")
        if missing:
            rep.write("\nMissing details:\n")
            for md, url, resolved in missing:
                rep.write(f"  - {md.relative_to(ROOT)} :: {url} -> {resolved}\n")

    print(f"REPORT: {report_path}")
    print(f"CHECKED: {checked}")
    print(f"MISSING: {len(missing)}")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
