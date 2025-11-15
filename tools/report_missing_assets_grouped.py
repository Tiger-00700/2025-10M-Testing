"""
Scan Markdown sources for local links, list missing files, and output a grouped
report by asset type: images, attachments, scripts, other.

Types mapping (by file extension, case-insensitive):
- images: .png .jpg .jpeg .gif .svg .webp .bmp
- attachments: .pdf .doc .docx .xls .xlsx .csv .zip .tar .gz .json .yaml .yml .txt .md
- scripts/code: .py .sh .ps1 .bat .sql .java .scala .js .ts .go .rb .rs .c .cpp .h .cs .kt .psm1 .tf
- other: anything else or no extension

Usage:
  python tools/report_missing_assets_grouped.py
  python tools/report_missing_assets_grouped.py --sources book/*.md chapter/*.md
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


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
    s = url.strip()
    if not s:
        return s
    if s.startswith("<") and s.endswith(">"):
        return s[1:-1].strip()
    if s.startswith("\"") or s.startswith("'"):
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


def _gather_markdown_files(patterns: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for pat in patterns:
        files.extend(sorted(ROOT.glob(pat)))
    seen = set()
    result: List[Path] = []
    for p in files:
        if p.is_file() and p not in seen:
            seen.add(p)
            result.append(p)
    return result


def _resolve_ref(base: Path, ref: str) -> Path:
    return (base.parent / ref).resolve()


IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"}
ATT_EXT = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".zip", ".tar", ".gz", ".json", ".yaml", ".yml", ".txt", ".md"}
CODE_EXT = {".py", ".sh", ".ps1", ".bat", ".sql", ".java", ".scala", ".js", ".ts", ".go", ".rb", ".rs", ".c", ".cpp", ".h", ".cs", ".kt", ".psm1", ".tf"}


def _type_of(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMG_EXT:
        return "images"
    if ext in ATT_EXT:
        return "attachments"
    if ext in CODE_EXT:
        return "scripts"
    return "other"


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="*", default=["book/*.md", "chapter/*.md"], help="Glob patterns (relative to repo root)")
    args = ap.parse_args(argv)

    sources = _gather_markdown_files(args.sources)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    report = REPORTS / f"missing_assets_grouped_{ts}.txt"

    missing_by_type: Dict[str, List[Tuple[Path, str, Path]]] = defaultdict(list)
    checked = 0

    for md in sources:
        text = md.read_text(encoding="utf-8", errors="ignore")
        for m in LINK_RE.finditer(text):
            raw = m.group(1) if m.group(1) is not None else m.group(2)
            if raw is None:
                continue
            url = _strip_title(raw)
            if _is_external(url):
                continue
            url2 = _strip_anchor(url)
            if not url2 or url2.startswith('#'):
                continue
            resolved = _resolve_ref(md, url2)
            checked += 1
            if not resolved.exists():
                t = _type_of(resolved)
                missing_by_type[t].append((md, url2, resolved))

    with report.open("w", encoding="utf-8") as rep:
        total_missing = sum(len(v) for v in missing_by_type.values())
        rep.write(f"Missing assets grouped report @ {ts}\n")
        rep.write(f"Sources: {len(sources)} files\n")
        rep.write(f"Checked refs: {checked}\n")
        rep.write(f"Total missing: {total_missing}\n\n")
        for t in ("images", "attachments", "scripts", "other"):
            items = missing_by_type.get(t, [])
            rep.write(f"[{t}] count={len(items)}\n")
            for md, url, resolved in items[:200]:
                rep.write(f"  - {md.relative_to(ROOT)} :: {url} -> {resolved}\n")
            if len(items) > 200:
                rep.write(f"  ... ({len(items)-200} more)\n")
            rep.write("\n")

    print(f"REPORT: {report}")
    print("COUNTS: " + ", ".join(f"{k}={len(v)}" for k, v in missing_by_type.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
