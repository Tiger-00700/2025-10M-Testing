import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book" / "1208.2025.newbook.md"
EXAMPLES = ROOT / "examples"
REPORTS = ROOT / "tools" / "reports"

def main():
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = REPORTS / f"asset_inventory_{ts}.md"
    text = BOOK.read_text(encoding="utf-8")
    # Match backticked paths like `examples/...` and `tools/reports/...`
    paths = re.findall(r"`(examples/[\w_\-/\.]+|tools/reports/[\w_\-/\.]+)`", text)

    missing = []
    present = []
    for p in paths:
        target = ROOT / p.replace("/", "\\" if "\\" in str(ROOT) else "/")
        if target.exists():
            present.append(p)
        else:
            missing.append(p)

    lines = []
    lines.append(f"# 资产引用清单 ({ts})")
    lines.append(f"- 总引用数: {len(paths)}")
    lines.append(f"- 存在: {len(present)}")
    lines.append(f"- 缺失: {len(missing)}")
    lines.append("")
    lines.append("## 存在的引用")
    for p in sorted(set(present)):
        lines.append(f"- {p}")
    lines.append("")
    lines.append("## 缺失的引用")
    if missing:
        for p in sorted(set(missing)):
            lines.append(f"- {p}")
    else:
        lines.append("- 无")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote asset inventory: {out}")

if __name__ == "__main__":
    main()
