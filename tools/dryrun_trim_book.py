import re
import csv
import difflib
import argparse
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


def strip_code_fences(text: str) -> str:
    lines = text.splitlines()
    out = []
    in_fence = False
    fence_pat = re.compile(r"^\s*(```|~~~)")
    for line in lines:
        if fence_pat.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def strip_inline_code(text: str) -> str:
    return re.sub(r"`[^`]*`", "", text)


def normalize_markdown(text: str) -> str:
    s = text
    # Keep link/image text, drop URLs
    s = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"\1", s)
    s = re.sub(r"\[([^\]]*)\]\([^\)]+\)", r"\1", s)
    # Remove emphasis markers
    s = s.replace("**", "").replace("__", "").replace("*", "").replace("_", "")
    # Remove heading markers at start
    s = re.sub(r"^\s*#{1,6}\s*", "", s, flags=re.MULTILINE)
    # Remove blockquote markers at start
    s = re.sub(r"^\s*>\s?", "", s, flags=re.MULTILINE)
    # Remove list markers at start
    s = re.sub(r"^\s*(?:[-+*]|\d+\.)\s+", "", s, flags=re.MULTILINE)
    # Remove HTML tags
    s = re.sub(r"<[^>]+>", "", s)
    # Unescape common entities
    s = s.replace("&nbsp;", " ").replace("&ensp;", " ").replace("&emsp;", " ")
    # Remove backslash escapes
    s = re.sub(r"\\([*_`#>\[\](){}.!+-])", r"\1", s)
    return s


def count_nonspace_chars(text: str) -> int:
    s = strip_code_fences(text)
    s = strip_inline_code(s)
    s = normalize_markdown(s)
    s = re.sub(r"\s+", "", s)
    return len(s)


@dataclass
class Section:
    level: int
    title: str
    start: int  # line index where heading line is
    end: int    # exclusive end line index for this section block


HEADING_RE = re.compile(r"^(\s*)(#{1,6})\s+(.*)$")


def parse_sections(lines: list[str]) -> list[Section]:
    heads: list[Section] = []
    for idx, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if not m:
            continue
        level = len(m.group(2))
        title = m.group(3).strip()
        heads.append(Section(level=level, title=title, start=idx, end=len(lines)))

    # determine end boundaries
    for i, sec in enumerate(heads):
        for j in range(i + 1, len(heads)):
            nxt = heads[j]
            if nxt.level <= sec.level:
                sec.end = nxt.start
                break
    return heads


# Rules
TITLE_RULES = [
    (re.compile(r"(概述|范围说明|本章导言|本章总结|小结|总结|常见问题|常见问题与解答|FAQ|章节结构)"), "compress"),
    (re.compile(r"(工具|测试工具|工具详解|工具选择|工具集成|集成策略)"), "move_to_appendix_or_online"),
]


def classify_action(title: str, content_text: str) -> tuple[str | None, str | None]:
    for rx, action in TITLE_RULES:
        if rx.search(title):
            return action, rx.pattern
    # short section rule (< 200 non-space chars in cleaned content)
    # Only consider if there is content besides the heading
    ns = count_nonspace_chars(content_text)
    if ns > 0 and ns < 200:
        return "merge_up", "short_section_lt200"
    return None, None


def dryrun_trim(src_path: Path) -> dict:
    raw = src_path.read_text(encoding="utf-8", errors="ignore")
    lines = raw.splitlines()
    secs = parse_sections(lines)

    # Build candidate lines
    cand_lines = lines.copy()
    detected: list[dict] = []

    # Walk sections bottom-up to avoid shifting ranges when replacing
    for sec in reversed(secs):
        start_body = sec.start + 1
        end_body = sec.end
        body_text = "\n".join(lines[start_body:end_body]) if start_body < end_body else ""

        action, rule = classify_action(sec.title, body_text)
        if not action:
            continue

        # Count original non-space chars in this block (approximate)
        orig_ns = count_nonspace_chars(body_text)

        # Create placeholder content (keep heading line)
        placeholder = [
            f"> [DRYRUN] 本段建议：{action}（规则：{rule}）。",
            f"> 保留标题，正文建议精简/下沉至附录或在线文档。",
        ]

        # Replace body content with placeholder
        cand_lines[start_body:end_body] = placeholder

        detected.append({
            "level": sec.level,
            "title": sec.title,
            "start": sec.start,
            "end": sec.end,
            "action": action,
            "rule": rule,
            "orig_nonspace": orig_ns,
        })

    cand_text = "\n".join(cand_lines) + ("\n" if not raw.endswith("\n") else "")

    # Stats
    base_ns = count_nonspace_chars(raw)
    cand_ns = count_nonspace_chars(cand_text)
    delta = base_ns - cand_ns

    # Diff
    diff = difflib.unified_diff(
        raw.splitlines(keepends=True),
        cand_text.splitlines(keepends=True),
        fromfile=str(src_path),
        tofile=str(src_path.with_name(src_path.stem + ".DRYRUN.trim.md")),
        n=3,
    )
    diff_text = "".join(diff)

    return {
        "detected": sorted(detected, key=lambda d: (-d["orig_nonspace"], d["title"])),
        "base_nonspace": base_ns,
        "cand_nonspace": cand_ns,
        "delta_nonspace": delta,
        "cand_text": cand_text,
        "diff_text": diff_text,
    }


def write_reports(src_path: Path, result: dict, mode: str = "dryrun") -> dict:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = Path("tools/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Candidate manuscript
    suffix = ".DRYRUN.trim.md" if mode == "dryrun" else ".trim.round1.md"
    cand_path = src_path.with_name(src_path.stem + suffix)
    cand_path.write_text(result["cand_text"], encoding="utf-8")

    # Diff
    diff_prefix = f"trim_{mode}_diff_{ts}.patch"
    diff_path = reports_dir / diff_prefix
    diff_path.write_text(result["diff_text"], encoding="utf-8")

    # Summary report
    rep_prefix = f"trim_{mode}_report_{ts}.md"
    rep_path = reports_dir / rep_prefix
    lines: list[str] = []
    title = "# 干跑（Dry-Run）版精简报告" if mode == "dryrun" else "# Round1 应用版精简报告"
    lines.append(title)
    lines.append("")
    lines.append(f"- 基准总字数：{result['base_nonspace']}")
    lines.append(f"- 候选总字数：{result['cand_nonspace']}")
    lines.append(f"- 预估可压缩：{result['delta_nonspace']}（约 {result['delta_nonspace']/1000:.1f} 千字）")
    lines.append("")
    lines.append("**命中段落（按原字数降序）**")
    lines.append("")
    lines.append("| 等级 | 标题 | 动作 | 规则 | 原字数 | 位置(行) |")
    lines.append("|---:|---|---|---|---:|---|")
    for d in result["detected"]:
        lines.append(
            f"| H{d['level']} | {d['title']} | {d['action']} | {d['rule']} | {d['orig_nonspace']} | {d['start']+1}-{d['end']} |"
        )
    lines.append("")
    rep_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # CSV report of actions
    csv_path = reports_dir / f"trim_{mode}_actions_{ts}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["level", "title", "action", "rule", "orig_nonspace", "start_line", "end_line"])
        for d in result["detected"]:
            writer.writerow([d["level"], d["title"], d["action"], d["rule"], d["orig_nonspace"], d["start"] + 1, d["end"]])

    return {
        "candidate": cand_path,
        "report": rep_path,
        "diff": diff_path,
        "csv": csv_path,
    }


def apply_trim(src_path: Path) -> dict:
    # Reuse dryrun detection, but write different placeholders for apply mode
    raw = src_path.read_text(encoding="utf-8", errors="ignore")
    lines = raw.splitlines()
    secs = parse_sections(lines)

    cand_lines = lines.copy()
    detected: list[dict] = []

    for sec in reversed(secs):
        start_body = sec.start + 1
        end_body = sec.end
        body_text = "\n".join(lines[start_body:end_body]) if start_body < end_body else ""
        action, rule = classify_action(sec.title, body_text)
        if not action:
            continue
        orig_ns = count_nonspace_chars(body_text)

        if action == "compress":
            replacement = [
                "> [APPLY] 本段已压缩为精要（待人工完善）。",
                "> 建议保留2-4句要点与实践建议。",
            ]
        elif action == "move_to_appendix_or_online":
            replacement = [
                "> [APPLY] 本段详细工具清单已迁移至附录/在线文档。",
                "> 参考：附录《工具清单索引》（占位链接，待补充）。",
            ]
        elif action == "merge_up":
            replacement = [
                "> [APPLY] 本段内容较短，已合并至上级段落（待人工确认）。",
            ]
        else:
            replacement = [
                f"> [APPLY] 建议：{action}（规则：{rule}）",
            ]

        cand_lines[start_body:end_body] = replacement
        detected.append({
            "level": sec.level,
            "title": sec.title,
            "start": sec.start,
            "end": sec.end,
            "action": action,
            "rule": rule,
            "orig_nonspace": orig_ns,
        })

    cand_text = "\n".join(cand_lines) + ("\n" if not raw.endswith("\n") else "")

    base_ns = count_nonspace_chars(raw)
    cand_ns = count_nonspace_chars(cand_text)
    delta = base_ns - cand_ns

    diff = difflib.unified_diff(
        raw.splitlines(keepends=True),
        cand_text.splitlines(keepends=True),
        fromfile=str(src_path),
        tofile=str(src_path.with_name(src_path.stem + ".trim.round1.md")),
        n=3,
    )
    diff_text = "".join(diff)

    return {
        "detected": sorted(detected, key=lambda d: (-d["orig_nonspace"], d["title"])) ,
        "base_nonspace": base_ns,
        "cand_nonspace": cand_ns,
        "delta_nonspace": delta,
        "cand_text": cand_text,
        "diff_text": diff_text,
    }


def main():
    parser = argparse.ArgumentParser(description="Trim book (dryrun/apply)")
    parser.add_argument("--apply", action="store_true", help="Apply actions instead of DRYRUN placeholders")
    parser.add_argument("--output", type=str, default=None, help="Output file path for candidate manuscript")
    parser.add_argument("--source", type=str, default="book/1022.2025.newbook.cleaned.md", help="Source book path")
    args = parser.parse_args()

    src = Path(args.source)
    if not src.exists():
        raise SystemExit(f"Not found: {src}")

    if args.apply:
        result = apply_trim(src)
        outs = write_reports(src, result, mode="apply")
    else:
        result = dryrun_trim(src)
        outs = write_reports(src, result, mode="dryrun")

    # Override candidate output path if provided
    if args.output:
        Path(args.output).write_text(result["cand_text"], encoding="utf-8")
        print(args.output)
    else:
        print(str(outs["candidate"]))
    print(str(outs["report"]))
    print(str(outs["diff"]))
    if "csv" in outs:
        print(str(outs["csv"]))


if __name__ == "__main__":
    main()
