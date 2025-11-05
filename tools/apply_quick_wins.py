from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book" / "1022.2025.newbook.augmented.md"

USAGE_BLOCK = (
    "\n## 如何使用本书\n\n"
    "- 读者对象：具备基础Linux/SQL/脚本能力的测试/数据从业者\n\n"
    "- 推荐阅读路径：入门（第1篇）→ 进阶（第2~4篇）→ 专家与实战（第5~6篇）\n\n"
    "- 动手实践路径：每章“最小实操路径 + 断言 + 验收标准（SLO）”，示例参见附录 D\n\n"
    "- 章节约定：章首“先修/学习目标/核心术语/阅读提示”，章末“小结/课后练习/延伸阅读”\n\n"
)

APPENDICES_BLOCK = (
    "\n\n## 附录 D 代码清单与脚本索引\n\n"
    "> 将正文中的“附：示例与脚本”统一汇总，按“章节索引/目录索引”双视图列出，指向 examples/ 对应路径。\n\n"
    "- 示例：\n"
    "  - 第1篇-第3章 环境搭建：examples/03_environment/\n"
    "  - 第1篇-第4章 数据管理：examples/04_data_management/\n\n"
    "## 附录 E 课后思考/练习题索引\n\n"
    "> 汇总全书练习题，按章节与难度可筛选；与正文各题目互链。\n\n"
    "## 附录 F 图表目录\n\n"
    "> 自动汇总图/表清单，带编号与锚点，便于查阅。\n\n"
    "## 附录 G 参考文献\n\n"
    "> 统一引用格式（标准/论文/文章/官方文档），建议采用：作者. 标题. 年份/版本. 链接。\n\n"
)


def fix_environment_repeats(text: str) -> str:
    # Collapse repeated 'environment' tails like environmentironmentironment...
    text = re.sub(r"(environment)(?:ironment){1,}", r"\\1", text)
    return text


def fix_appendix_example_links(text: str) -> str:
    # Redirect '附录 E/examples/' (and variants like '附录E/examples/') to '附录 D/examples/'
    text = re.sub(r"(附录)\s*E/examples/", r"\1 D/examples/", text)
    # Also handle English 'Appendix E/examples/' variants if present
    text = re.sub(r"(Appendix)\s*E/examples/", r"\1 D/examples/", text)
    return text


def adjust_verified_on_mentions(text: str) -> str:
    # Narrow '附录 B/附录 E 中所有 Verified on 已填实' -> '附录 B 中所有 Verified on 已填实'
    text = text.replace("附录 B/附录 E 中所有 Verified on 已填实", "附录 B 中所有 Verified on 已填实")
    # '（在附录 B/附录 E 使用）' -> '（在附录 B 使用）'
    text = text.replace("（在附录 B/附录 E 使用）", "（在附录 B 使用）")
    return text


def strip_source_suffix_in_headings(text: str) -> str:
    def repl_heading(m: re.Match[str]) -> str:
        line = m.group(0)
        # Remove full-width Chinese parenthetical source markers
        line = re.sub(r"（来自：[^）]+）", "", line)
        # Also remove ASCII version if any
        line = re.sub(r"\s*\(来自：[^)]+\)", "", line)
        return line

    # Apply only on heading lines starting with one or more #'s followed by space
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^#{1,6} ", line):
            lines[i] = repl_heading(re.match(r"^.*$", line))  # type: ignore[arg-type]
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def remove_lower_level_empty_triplets(text: str) -> str:
    # Remove exact empty triplets at lower heading levels (#### or ##### or ######)
    for level_marks in ("######", "#####", "####"):
        pattern = rf"(?:\n)?{level_marks} 学习目标\s*\n\s*{level_marks} 小结\s*\n\s*{level_marks} 练习(?:\s*\n)?"
        text = re.sub(pattern, "\n", text, flags=re.MULTILINE)
    return text


def insert_usage_section(text: str) -> str:
    if "## 如何使用本书" in text:
        return text
    # Insert after the very first H1
    idx = text.find("\n", text.find("\n") + 1)
    # Safer: locate first H1 line start
    m = re.search(r"^# .*$", text, flags=re.MULTILINE)
    if not m:
        return text
    insert_pos = m.end()
    return text[:insert_pos] + USAGE_BLOCK + text[insert_pos:]


def append_missing_appendices(text: str) -> str:
    if "## 附录 D 代码清单与脚本索引" in text:
        return text
    return text + APPENDICES_BLOCK


def main() -> None:
    if not BOOK.exists():
        raise SystemExit(f"Manuscript not found: {BOOK}")
    raw = BOOK.read_text(encoding="utf-8")
    txt = raw
    txt = fix_environment_repeats(txt)
    txt = fix_appendix_example_links(txt)
    txt = adjust_verified_on_mentions(txt)
    txt = strip_source_suffix_in_headings(txt)
    txt = remove_lower_level_empty_triplets(txt)
    txt = insert_usage_section(txt)
    txt = append_missing_appendices(txt)
    if txt != raw:
        BOOK.write_text(txt, encoding="utf-8")
        print(f"[OK] Quick wins applied to {BOOK}")
    else:
        print("[SKIP] No changes detected (already clean)")


if __name__ == "__main__":
    main()
