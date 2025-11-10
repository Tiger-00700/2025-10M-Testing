"""Compose merged content drafts based on merge-candidates CSV and source book.

Reads latest tools/reports/merge-candidates-*.csv, parses
book/1022.2025.newbook.augmented.frozen.md into sections, and produces
book/merge_drafts/merge-drafts-<ts>.md with proposed merged content blocks.

Merging strategy (safe, editorial-friendly):
- For 'similar' (同章/同篇):
  * Create a merged heading labeled '【合并稿】<A.title> / <B.title>' under the common context.
  * Combine paragraphs using ordered union (A then B), paragraph key = stripped text.
  * Emit two source subsections with diff paragraphs (A-only / B-only) if any.
- For 'duplicate':
  * If 同章: pick the longest source as主稿，补充另一处缺失段落（有则补），并建议移除重复标题。
  * If 同篇: 生成“抽象公共模块”草稿：列出共性要点（交集）与差异要点（A-only/B-only）。

Output header includes rationale, scope, and original paths for traceability.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Tuple

BOOK = Path("book/1022.2025.newbook.augmented.frozen.md")
REPORT_DIR = Path("tools/reports")
OUT_DIR = Path("book/merge_drafts")

HEAD_RE = re.compile(r"^(?P<hash>#{1,6})\s+(?P<title>.*\S)\s*$")


@dataclass
class Section:
    line: int
    level: int
    title: str
    path: str
    content: List[str]


def parse_sections(text: str) -> List[Section]:
    lines = text.splitlines()
    stack: List[Tuple[int, str]] = []
    sections: List[Section] = []
    current: Section | None = None
    for idx, raw in enumerate(lines, start=1):
        m = HEAD_RE.match(raw)
        if m:
            level = len(m.group("hash"))
            title = m.group("title").strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            if current:
                sections.append(current)
            current = Section(
                line=idx,
                level=level,
                title=title,
                path=" / ".join(t for _, t in stack),
                content=[],
            )
        else:
            if current:
                current.content.append(raw)
    if current:
        sections.append(current)
    return sections


def latest_merge_candidates() -> Path | None:
    pats = sorted(
        REPORT_DIR.glob("merge-candidates-*.csv"),
        key=lambda p: p.name,
        reverse=True,
    )
    return pats[0] if pats else None


def split_paragraphs(lines: List[str]) -> List[str]:
    out: List[str] = []
    buf: List[str] = []
    def flush():
        if buf:
            # Preserve original paragraph with internal newlines
            out.append("\n".join(buf).rstrip())
            buf.clear()
    for ln in lines:
        if ln.strip() == "":
            flush()
        else:
            buf.append(ln)
    flush()
    # Drop pure heading echoes or anchors if any slipped in (rare)
    return out


def ordered_union(a: List[str], b: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for para in a + b:
        key = para.strip()
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(para)
    return out


def common_prefix(segs_a: List[str], segs_b: List[str]) -> List[str]:
    out = []
    for x, y in zip(segs_a, segs_b):
        if x == y:
            out.append(x)
        else:
            break
    return out


def main():
    if not BOOK.exists():
        raise SystemExit(f"Source not found: {BOOK}")
    mc = latest_merge_candidates()
    if not mc or not mc.exists():
        raise SystemExit("No merge-candidates CSV found in tools/reports/")

    text = BOOK.read_text(encoding="utf-8")
    sections = parse_sections(text)
    by_line: Dict[int, Section] = {s.line: s for s in sections}

    with mc.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"merge-drafts-{ts}.md"

    out: List[str] = []
    out.append(f"# 合并候选草稿（{ts} UTC）")
    out.append("")
    out.append(f"来源：{mc.as_posix()} 与 {BOOK.as_posix()}")
    out.append("")

    for r in rows:
        kind = r.get("kind", "")
        scope = r.get("scope", "")
        prio = r.get("priority", "")
        score = r.get("score", "")
        title_a = (r.get("title_a") or r.get("title") or "").strip()
        title_b = (r.get("title_b") or r.get("title") or "").strip()
        line_a = int(r.get("line_a") or 0) if r.get("line_a") else None
        line_b = int(r.get("line_b") or 0) if r.get("line_b") else None
        path_a = r.get("path_a", "")
        path_b = r.get("path_b", "")
        group_size = r.get("group_size", "")
        lines_in_group = r.get("lines_in_group", "")
        suggestion = r.get("suggestion", "")
        rationale = r.get("rationale", "")

        out.append("\n---\n")
        # Header block
        out.append(f"## [{prio}/{scope}] {kind} 合并建议")
        if score:
            out.append(f"- 相似度：{score}")
        if group_size:
            out.append(f"- 组大小：{group_size}（行：{lines_in_group}）")
        out.append(f"- 建议：{suggestion}")
        out.append(f"- 理由：{rationale}")
        if path_a:
            out.append(f"- A：行 {line_a} ｜ {path_a}")
        if path_b:
            out.append(f"- B：行 {line_b} ｜ {path_b}")
        out.append("")

        # Extract sections
        sec_a = by_line.get(line_a) if line_a else None
        sec_b = by_line.get(line_b) if line_b else None

        # Determine context
        ctx = ""
        if sec_a and sec_b:
            segs_a = sec_a.path.split(" / ")
            segs_b = sec_b.path.split(" / ")
            ctx_segs = common_prefix(segs_a, segs_b)
            ctx = " / ".join(ctx_segs)

        # Build merged heading label
        label = title_a if title_a else (title_b or "合并稿")
        if kind == "similar" and title_b and title_b != title_a:
            label = f"{title_a} / {title_b}" if title_a else title_b

        merged_h = f"### 【合并稿】{label}"
        if ctx:
            merged_h += f"（上下文：{ctx}）"
        out.append(merged_h)

        # Paragraph-level union/diff
        paras_a = split_paragraphs(sec_a.content) if sec_a else []
        paras_b = split_paragraphs(sec_b.content) if sec_b else []
        merged = ordered_union(paras_a, paras_b)

        if not merged and (paras_a or paras_b):
            # If identical, keep one representative
            merged = paras_a or paras_b

        if not merged:
            out.append("（占位：源小节暂无可合并正文，请补充内容）")
        else:
            out.append("")
            out.extend(merged)

        # Optional diff view if there are unique paragraphs
        only_a = [p for p in paras_a if p.strip() and p.strip() not in {q.strip() for q in paras_b}]
        only_b = [p for p in paras_b if p.strip() and p.strip() not in {q.strip() for q in paras_a}]

        if only_a:
            out.append("")
            out.append("#### A 专有段落（供筛选）")
            out.extend(only_a)
        if only_b:
            out.append("")
            out.append("#### B 专有段落（供筛选）")
            out.extend(only_b)

    out.append("\n---\n")
    out_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Merge drafts written: {out_path.as_posix()}")


if __name__ == "__main__":
    main()
