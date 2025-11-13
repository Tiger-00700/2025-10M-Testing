#!/usr/bin/env python
"""Replace old book title variants with the new canonical title across markdown files.
Idempotent: running multiple times produces same result.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_VARIANTS = [
    "大数据测试全栈指南：从入门到实战精通",
    "大数据测试全栈指南",
]
NEW_TITLE = "大数据全栈测试：从理论到实战"

MD_GLOB = "**/*.md"

def replace_in_text(text: str) -> str:
    # Simple global replacement of any variant
    for old in OLD_VARIANTS:
        text = text.replace(old, NEW_TITLE)
    return text

def main():
    changed = []
    for md in ROOT.glob(MD_GLOB):
        try:
            original = md.read_text(encoding="utf-8")
        except Exception:
            continue
        updated = replace_in_text(original)
        if updated != original:
            md.write_text(updated, encoding="utf-8")
            changed.append(md)
    print(f"Updated title in {len(changed)} markdown files.")
    for c in changed[:20]:
        print(" -", ROOT.relative_to(ROOT).joinpath(c))
    if len(changed) > 20:
        print(" ... (truncated list) ...")

if __name__ == "__main__":
    main()
