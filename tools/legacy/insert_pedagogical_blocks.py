import re
from pathlib import Path

TARGET = Path(__file__).resolve().parents[1] / "book" / "1022.2025.newbook.md"

def load_lines(path: Path):
    text = path.read_text(encoding="utf-8")
    # Normalize line endings to \n for processing
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.split("\n")

def save_lines(path: Path, lines):
    text = "\n".join(lines)
    path.write_text(text, encoding="utf-8")

heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

class Node:
    def __init__(self, level: int, idx: int, title: str):
        self.level = level
        self.idx = idx
        self.title = title
        self.end = None  # exclusive


def parse_nodes(lines):
    nodes = []
    for i, line in enumerate(lines):
        m = heading_re.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2)
            nodes.append(Node(level, i, title))
    # compute end indices
    n = len(nodes)
    for i in range(n):
        end = len(lines)
        for j in range(i+1, n):
            if nodes[j].level <= nodes[i].level:
                end = nodes[j].idx
                break
        nodes[i].end = end
    return nodes


def section_has(lines, start, end, marker: str) -> bool:
    for i in range(start+1, min(start+10, end)):
        if i < len(lines) and marker in lines[i]:
            return True
    # broader search inside section if not found near top
    for i in range(start+1, end):
        if marker in lines[i]:
            return True
    return False


def ensure_blank_before(lines, pos):
    # Ensure at least one blank line before position pos (insert if not present and not at top)
    if pos <= 0:
        return pos
    if lines[pos-1].strip() != "":
        lines.insert(pos, "")
        return pos + 1
    return pos


def ensure_blank_after(lines, pos):
    # Ensure at least one blank line after position pos (insert if needed)
    insert_pos = pos + 1
    if insert_pos >= len(lines):
        lines.append("")
        return
    if lines[insert_pos].strip() != "":
        lines.insert(insert_pos, "")


def build_reading_tip(level: int, title: str):
    if level == 1:
        scope = "本篇"
    elif level == 2:
        scope = "本章"
    else:
        scope = "本节"
    text = f"> 【阅读提示】{scope}聚焦：{title}。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。"
    return [text, ""]


def build_summary_and_exercises():
    block = []
    block.append("> 【章节重点难点总结】")
    block.append("")
    block.append("- 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准")
    block.append("- 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡")
    block.append("")
    block.append("> 【课后思考/练习题】")
    block.append("")
    block.append("1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。")
    block.append("2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。")
    block.append("")
    return block


def apply_inserts(lines):
    nodes = parse_nodes(lines)
    # We'll collect (position, content_lines) and then apply in reverse order
    inserts = []
    for nd in nodes:
        if nd.level not in (1, 2, 3):
            continue
        # Insert reading tip below heading if absent
        if not section_has(lines, nd.idx, nd.end, "【阅读提示】"):
            # insert at nd.idx+1, but ensure one blank line after heading
            inserts.append((nd.idx+1, build_reading_tip(nd.level, nd.title)))
        # For level-3 sections, add summary/exercises near the end if absent
        if nd.level == 3:
            need_summary = not section_has(lines, nd.idx, nd.end, "【章节重点难点总结】")
            need_ex = not section_has(lines, nd.idx, nd.end, "【课后思考/练习题】")
            if need_summary or need_ex:
                content = []
                if need_summary or need_ex:
                    content.extend(build_summary_and_exercises())
                # insert just before nd.end, but ensure a blank line before
                inserts.append((nd.end, content))
    # Apply inserts in reverse order
    inserts.sort(key=lambda x: x[0], reverse=True)
    for pos, content in inserts:
        # Ensure blank line before insertion point (avoid breaking lists/paragraphs)
        pos = ensure_blank_before(lines, pos)
        lines[pos:pos] = content
    return lines, len(inserts)


def main():
    if not TARGET.exists():
        raise SystemExit(f"Target not found: {TARGET}")
    lines = load_lines(TARGET)
    new_lines, count = apply_inserts(lines)
    if count > 0:
        save_lines(TARGET, new_lines)
        print(f"Applied {count} inserts to {TARGET}")
    else:
        print("No inserts needed (already up to date)")

if __name__ == "__main__":
    main()
