"""
Asset inventory (scoped) for 1116/1130 manuscripts and related appendices.

- Scans `book/1116.2025.newbook.md` and `book/1130.2025.newbook.md`
- Optionally includes other `book/*.md` appendices except legacy 1022 references
- Excludes links to `book/1022.*` and `book-old/1022.*`
- Resolves local links/images and reports missing assets
- Writes timestamped report to `tools/reports/`

Usage:
  python tools/asset_all.py [--include-appendices]
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path
from typing import Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "tools" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

LINK_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)|\[[^\]]*\]\(([^)]+)\)")

EXCLUDE_PREFIXES = (
    "book/1022.",
    "book-old/1022.",
)


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
    s = url.strip()
    if not s:
        return s
    if s.startswith("<") and s.endswith(">"):
        return s[1:-1].strip()
    if s.startswith('"') or s.startswith("'"):
        m = re.match(r"^([\"\'])(.*?)(\1)", s)
        if m:
            return m.group(2)
    return s.split()[0]


def _strip_anchor(url: str) -> str:
    if url.startswith('#'):
        return url
    if '#' in url:
        return url.split('#', 1)[0]
    return url


def _gather_files(include_appendices: bool) -> List[Path]:
    files: List[Path] = []
    base = [ROOT / "book" / "1116.2025.newbook.md", ROOT / "book" / "1130.2025.newbook.md"]
    files.extend([p for p in base if p.is_file()])
    if include_appendices:
        for p in sorted((ROOT / "book").glob("*.md")):
            # Skip the two already added and any legacy 1022 files
            name = p.name
            if name in {"1116.2025.newbook.md", "1130.2025.newbook.md"}:
                continue
            if name.startswith("1022."):
                continue
            files.append(p)
    return files


def _resolve_ref(base: Path, ref: str) -> Path:
    return (base.parent / ref).resolve()


def _is_excluded(url: str) -> bool:
    for prefix in EXCLUDE_PREFIXES:
        if url.startswith(prefix):
            return True
    return False


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-appendices", action="store_true", help="Also scan other book/*.md excluding legacy 1022.*")
    args = ap.parse_args(argv)

    sources = _gather_files(args.include_appendices)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS / f"assets_inventory_scoped_{ts}.txt"

    missing: List[Tuple[Path, str, Path]] = []
    checked = 0

    with report_path.open("w", encoding="utf-8") as rep:
        rep.write(f"Scoped assets inventory report @ {ts}\n")
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
                if _is_excluded(url_no_anchor):
                    continue
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
    import sys
    raise SystemExit(main(sys.argv[1:]))
