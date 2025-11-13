"""
Generate merge candidates by crossing filtered duplicate headings and
high-similarity section pairs.

Inputs (auto-detected under tools/reports/):
- heading-duplicates-filtered-<ts>.csv  (from tools/heading_duplicates_filtered_report.py)
- similar-sections-<ts>.csv            (from tools/find_similar_sections.py)
- book/1022.2025.newbook.augmented.frozen.md (to resolve chapter/part)

Output: tools/reports/merge-candidates-<ts>.csv

Heuristics:
- Keep similar pairs with score >= 0.92 when they are in 同章 or 同篇.
    同章优先，建议同章合并/去重；同篇抽象为公共模块或模板。
- For duplicates: group by章节名, emit a candidate when a group has >1
    occurrences (include group size and line numbers).

CSV Columns:
kind,priority,scope,score,title_a,line_a,chapter_a,path_a,title_b,line_b,chapter_b,path_b,group_size,lines_in_group,suggestion,rationale
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import datetime, timezone
# combinations import removed (unused) to satisfy flake8 F401
from pathlib import Path

REPORT_DIR = Path("tools/reports")
BOOK = Path("book/1022.2025.newbook.augmented.frozen.md")

MIN_SIM_SCORE = 0.92


def latest_file(prefix: str, suffix: str) -> Path | None:
    patt = re.compile(re.escape(prefix) + r"-(\d{8}T\d{6}Z)" + re.escape(suffix) + r"$")
    candidates = []
    if not REPORT_DIR.exists():
        return None
    for p in REPORT_DIR.iterdir():
        if p.is_file():
            m = patt.match(p.name)
            if m:
                candidates.append((m.group(1), p))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


HEAD_RE = re.compile(r"^(?P<hash>#{1,6})\s+(?P<title>.*\S)\s*$")


@dataclass
class Heading:
    line: int
    level: int
    title: str
    path: str
    chapter: str | None
    part: str | None


def extract_part_and_chapter(segments: list[str]) -> tuple[str | None, str | None]:
    part = None
    chapter = None
    for seg in segments:
        s = seg.strip()
        if part is None and re.match(r"^第[一二三四五六七八九十百千0-9]+篇", s):
            part = s
        if chapter is None and re.match(r"^第[一二三四五六七八九十百千0-9]+章", s):
            chapter = s
    return part, chapter


def parse_book_headings(book_path: Path) -> dict[int, Heading]:
    lines = book_path.read_text(encoding="utf-8").splitlines()
    stack: list[tuple[int,str]] = []
    map_by_line: dict[int, Heading] = {}
    for i, raw in enumerate(lines, start=1):
        m = HEAD_RE.match(raw)
        if not m:
            continue
        level = len(m.group("hash"))
        title = m.group("title").strip()
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        segs = [t for _, t in stack]
        path = " / ".join(segs)
        part, chapter = extract_part_and_chapter(segs)
        map_by_line[i] = Heading(i, level, title, path, chapter, part)
    return map_by_line


def read_duplicates_csv(path: Path):
    rows = []
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return rows


def read_similar_csv(path: Path):
    rows = []
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            # Normalize numeric types
            try:
                r["score"] = float(r["score"]) if r.get("score") else None
                r["hamming"] = int(r["hamming"]) if r.get("hamming") else None
                r["a_line"] = int(r["a_line"]) if r.get("a_line") else None
                r["b_line"] = int(r["b_line"]) if r.get("b_line") else None
            except Exception:
                pass
            rows.append(r)
    return rows


def scope_and_priority(a: Heading, b: Heading):
    if a.chapter and b.chapter and a.chapter == b.chapter:
        return "同章", "P1"
    if a.part and b.part and a.part == b.part:
        return "同篇", "P2"
    return "跨篇", "P3"


def suggestion_for(kind: str, scope: str) -> tuple[str, str]:
    if kind == "similar":
        if scope == "同章":
            return "合并/去重", "内容高度相似且处于同章，合并可减少重复，保留差异要点。"
        if scope == "同篇":
            return "抽象公共模块", "同篇内多处相似，建议沉淀方法/模板并在各章引用。"
        return "抽象公共模块或保留", "跨篇相似度高，考虑提炼通用方法并引用，或保留差异语境。"
    else:  # duplicate
        if scope == "同章":
            return "合并/改名", "同章内标题重复，建议合并或加限定词以区分语义。"
        if scope == "同篇":
            return "抽象公共模块/改名", "同篇内多处同名，建议抽象公共模块并加上下文限定。"
        return "评估是否抽象或保留", "跨篇同名可能为全书性概念，评估是否抽象为统一章节或保留各自语境。"


def main():
    dup_csv = latest_file("heading-duplicates-filtered", ".csv")
    sim_csv = latest_file("similar-sections", ".csv")
    if not dup_csv or not sim_csv:
        msg = (
            "Missing required input reports. Ensure filtered duplicates and "
            "similar sections CSVs exist in tools/reports/."
        )
        raise SystemExit(msg)
    if not BOOK.exists():
        raise SystemExit(f"Missing source book: {BOOK}")

    line_map = parse_book_headings(BOOK)
    dup_rows = read_duplicates_csv(dup_csv)
    sim_rows = read_similar_csv(sim_csv)

    out_rows = []

    # Process similar pairs
    for r in sim_rows:
        score = r.get("score") or 0.0
        if score < MIN_SIM_SCORE:
            continue
        a_line = r.get("a_line")
        b_line = r.get("b_line")
        if not a_line or not b_line:
            continue
        A = line_map.get(int(a_line))
        B = line_map.get(int(b_line))
        if not A or not B:
            continue
        scope, prio = scope_and_priority(A, B)
        if scope not in ("同章", "同篇"):
            continue  # 优先同章/同篇
        sug, why = suggestion_for("similar", scope)
        out_rows.append({
            "kind": "similar",
            "priority": prio,
            "scope": scope,
            "score": f"{score:.3f}",
            "title_a": A.title,
            "line_a": A.line,
            "chapter_a": A.chapter or "",
            "path_a": A.path,
            "title_b": B.title,
            "line_b": B.line,
            "chapter_b": B.chapter or "",
            "path_b": B.path,
            "group_size": "",
            "lines_in_group": "",
            "suggestion": sug,
            "rationale": why,
        })

    # Process duplicates by grouping occurrences per chapter
    for r in dup_rows:
        title = r.get("title", "").strip()
        raw_lines = r.get("all_lines", "")
        all_lines = [int(x) for x in raw_lines.split(",") if x.strip().isdigit()]
        # Build groups per chapter
        chapter_groups: dict[str, list[int]] = {}
        part_groups: dict[str, list[int]] = {}
        cross_lines: list[int] = []
        for ln in all_lines:
            h = line_map.get(ln)
            if not h:
                continue
            if h.chapter:
                chapter_groups.setdefault(h.chapter, []).append(ln)
            elif h.part:
                part_groups.setdefault(h.part, []).append(ln)
            else:
                cross_lines.append(ln)

        # Same-chapter candidates
        for chap, lns in chapter_groups.items():
            if len(lns) < 2:
                continue
            A = line_map.get(lns[0])
            B = line_map.get(lns[1])
            if not A or not B:
                continue
            sug, why = suggestion_for("duplicate", "同章")
            out_rows.append({
                "kind": "duplicate",
                "priority": "P1",
                "scope": "同章",
                "score": "",
                "title_a": title,
                "line_a": A.line,
                "chapter_a": chap,
                "path_a": A.path,
                "title_b": title,
                "line_b": B.line,
                "chapter_b": chap,
                "path_b": B.path,
                "group_size": len(lns),
                "lines_in_group": ",".join(str(x) for x in lns),
                "suggestion": sug,
                "rationale": why,
            })

        # Same-part candidates (exclude those already handled by same-chapter)
        for part, lns in part_groups.items():
            # Filter out lines that already appear in any chapter group with size>1
            covered = set()
            for grp in chapter_groups.values():
                if len(grp) > 1:
                    covered.update(grp)
            lns2 = [ln for ln in lns if ln not in covered]
            if len(lns2) < 2:
                continue
            A = line_map.get(lns2[0])
            B = line_map.get(lns2[1])
            if not A or not B:
                continue
            sug, why = suggestion_for("duplicate", "同篇")
            out_rows.append({
                "kind": "duplicate",
                "priority": "P2",
                "scope": "同篇",
                "score": "",
                "title_a": title,
                "line_a": A.line,
                "chapter_a": A.chapter or "",
                "path_a": A.path,
                "title_b": title,
                "line_b": B.line,
                "chapter_b": B.chapter or "",
                "path_b": B.path,
                "group_size": len(lns2),
                "lines_in_group": ",".join(str(x) for x in lns2),
                "suggestion": sug,
                "rationale": why,
            })

    # Sort by priority then score desc (similar first within same priority)
    def sort_key(r):
        prio_order = {"P1": 0, "P2": 1, "P3": 2}
        kind_rank = 0 if r["kind"] == "similar" else 1
        score = float(r["score"]) if r["score"] else 0.0
        return (prio_order.get(r["priority"], 9), kind_rank, -score)

    out_rows.sort(key=sort_key)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = REPORT_DIR / f"merge-candidates-{ts}.csv"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "kind","priority","scope","score",
                "title_a","line_a","chapter_a","path_a",
                "title_b","line_b","chapter_b","path_b",
                "group_size","lines_in_group","suggestion","rationale",
            ],
        )
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"Merge candidates written: {out_path.as_posix()} (rows={len(out_rows)})")


if __name__ == "__main__":
    main()
