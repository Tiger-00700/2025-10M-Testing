import re
from pathlib import Path
from datetime import datetime
from typing import List

BOOK = Path(__file__).resolve().parents[1] / "book" / "1022.2025.newbook.md"
REPORTS = Path(__file__).resolve().parents[1] / "tools" / "reports"
CIT_NUM_RE = re.compile(r"\[(\d+)\]")
CIT_AUTHYEAR_RE = re.compile(r"\b([A-Z][a-zA-Z]+)\s*,\s*(19|20)\d{2}\b")


def load_lines(p: Path) -> List[str]:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n")


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    lines = load_lines(BOOK)

    num_hits = []
    auth_hits = []

    for i, ln in enumerate(lines):
        for m in CIT_NUM_RE.finditer(ln):
            num_hits.append((i + 1, ln.strip(), m.group(1)))
        for m in CIT_AUTHYEAR_RE.finditer(ln):
            auth_hits.append((i + 1, ln.strip(), f"{m.group(1)}, {m.group(2)}xx"))

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = [
        "# Citations Scan Report",
        "",
        f"Numeric citations: {len(num_hits)}",
        f"Author-year style: {len(auth_hits)}",
        "",
        "## Samples",
        "",
    ]
    for group, title in ((num_hits, "Numeric"), (auth_hits, "Author-year")):
        out.append(f"### {title}")
        out.append("")
        for (ln, src, mark) in group[:50]:
            out.append(f"- L{ln}: {src[:140]}")
        out.append("")

    report = REPORTS / f"citations-{ts}.md"
    report.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote citations report to {report}")

if __name__ == "__main__":
    main()
