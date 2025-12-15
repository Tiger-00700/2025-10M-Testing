from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "chapter"
REPORTS = ROOT / "tools" / "reports"

HEADER = "<!-- markdownlint-disable MD025 -->"

def check_file(path: Path):
    text = path.read_text(encoding="utf-8")
    ok_header = text.strip().startswith(HEADER)
    has_archived_block = "archived-content" in text
    return ok_header, has_archived_block

def main():
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = REPORTS / f"archive_status_{ts}.md"
    files = sorted(CHAPTER.glob("*.md"))

    missing_header = []
    missing_block = []
    ok = []
    for f in files:
        h, b = check_file(f)
        if h and b:
            ok.append(f.name)
        else:
            if not h:
                missing_header.append(f.name)
            if not b:
                missing_block.append(f.name)

    lines = []
    lines.append(f"# 归档规范检查 ({ts})")
    lines.append(f"- 文件数: {len(files)}")
    lines.append(f"- 符合规范: {len(ok)}")
    lines.append(f"- 缺少头部: {len(missing_header)}")
    lines.append(f"- 缺少 archived-content: {len(missing_block)}")
    lines.append("")
    lines.append("## 符合规范")
    if ok:
        for n in ok:
            lines.append(f"- {n}")
    else:
        lines.append("- 无")
    lines.append("")
    lines.append("## 缺少头部 (需补 `<!-- markdownlint-disable MD025 -->`)")
    if missing_header:
        for n in missing_header:
            lines.append(f"- {n}")
    else:
        lines.append("- 无")
    lines.append("")
    lines.append("## 缺少 archived-content 区块")
    if missing_block:
        for n in missing_block:
            lines.append(f"- {n}")
    else:
        lines.append("- 无")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote archive status: {out}")

if __name__ == "__main__":
    main()
