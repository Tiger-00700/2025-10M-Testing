import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book" / "1022.2025.newbook.augmented.md"
ORG = ROOT / "tools" / "reports" / "organized-latest.md"
REPORTS = ROOT / "tools" / "reports"

# Extract mapping from augmented book: [脚本：X](examples/...) -> X -> examples/...
SCRIPT_LINK_RE = re.compile(r"\[脚本：\s*([^\]]+?)\s*\]\((examples/[^)]+)\)")
# Organized-latest broken appendix links pattern
APPX_LINK_RE = re.compile(r"\[脚本：\s*([^\]]+?)\s*\]\(((?:\.\./)+|(?:\.\.[\\/])+)?appendix[\\/][^)]+\)")


def build_mapping_from_book(text: str):
    mapping = {}
    for m in SCRIPT_LINK_RE.finditer(text):
        key = m.group(1).strip()
        val = m.group(2).strip()
        mapping[key] = val
    return mapping


def rewrite_organized(text: str, mapping: dict):
    changes = []

    def repl(m: re.Match):
        label = m.group(1).strip()
        old = m.group(0)
        if label in mapping:
            new = f"[脚本：{label}]({mapping[label]})"
            if new != old:
                changes.append((label, old, new))
            return new
        return old

    new_text = APPX_LINK_RE.sub(repl, text)
    return new_text, changes


def main():
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    if not ORG.exists():
        raise SystemExit(f"Organized latest not found: {ORG}")

    book = BOOK.read_text(encoding="utf-8", errors="ignore")
    mapping = build_mapping_from_book(book)

    org = ORG.read_text(encoding="utf-8", errors="ignore")
    new_org, changes = rewrite_organized(org, mapping)

    if changes:
        ORG.write_text(new_org, encoding="utf-8")
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    rep = REPORTS / f"organized-appendix-links-fix-{ts}.md"
    lines = [
        "# organized-latest appendix links fix",
        "",
        f"total changed: {len(changes)}",
        "",
    ]
    if changes:
        lines.append("| Label | Before | After |")
        lines.append("|---|---|---|")
        for label, before, after in changes[:300]:
            lines.append(f"| {label} | {before.replace('|','\\|')} | {after.replace('|','\\|')} |")
        lines.append("")
    rep.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] Rewrote organized-latest appendix links. Changed: {len(changes)}")


if __name__ == "__main__":
    main()
