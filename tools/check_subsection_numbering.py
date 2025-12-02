from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "tools" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

CHAPTER_RE = re.compile(r"^###\s+第(\d+)章\s")
NUM_HDR_RE = re.compile(r"^(#{2,6})\s+(\d+(?:\.\d+)*)([ .、])\s*(.*)$")


def _scan_book(md: Path) -> List[str]:
    warnings: List[str] = []
    lines = md.read_text(encoding="utf-8", errors="ignore").splitlines()

    chapter_no: int | None = None
    # For N.x (depth=2) track last x
    last_x: int | None = None
    # For N.x.y (depth=3) track per-parent x the last y
    last_y_for_x: Dict[int, int] = {}
    # For deeper depths N.x.y.z ... we track per parent tuple
    last_for_parent: Dict[Tuple[int, ...], int] = {}
    in_code = False

    for idx, raw in enumerate(lines, start=1):
        l = raw
        ls = l.lstrip()
        if ls.startswith("```") or ls.startswith("~~~"):
            in_code = not in_code
            continue
        if in_code:
            continue

        mchap = CHAPTER_RE.match(l)
        if mchap:
            # Reset chapter state
            chapter_no = int(mchap.group(1))
            last_x = None
            last_y_for_x.clear()
            last_for_parent.clear()
            continue

        mh = NUM_HDR_RE.match(l)
        if not mh or chapter_no is None:
            continue
        numseq = mh.group(2)
        parts = [int(p) for p in numseq.split('.') if p.isdigit()]
        if not parts:
            continue
        # First segment should equal chapter number; if not, warn
        if parts[0] != chapter_no:
            warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: PREFIX_MISMATCH -> {numseq}")
            # continue checks using found parts anyway

        depth = len(parts)

        if depth == 2:
            x = parts[1]
            if last_x is None:
                if x != 1:
                    warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: START_NOT_1 -> {numseq}")
                last_x = x
            else:
                if x == last_x:
                    warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: DUP -> {numseq}")
                elif x == last_x + 1:
                    last_x = x
                elif x < last_x:
                    warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: BACKWARD {last_x} -> {x} ({numseq})")
                    last_x = x
                else:
                    warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: JUMP {last_x}+1 -> {x} ({numseq})")
                    last_x = x
            # reset deeper level tracker when x changes
            last_y_for_x.pop(x, None)
        elif depth == 3:
            x, y = parts[1], parts[2]
            # if parent changes relative to last seen x, expect y to start at 1
            last_y = last_y_for_x.get(x)
            if last_y is None:
                if y != 1:
                    warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: START_NOT_1 for {chapter_no}.{x}.y -> {numseq}")
                last_y_for_x[x] = y
            else:
                if y == last_y:
                    warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: DUP -> {numseq}")
                elif y == last_y + 1:
                    last_y_for_x[x] = y
                elif y < last_y:
                    warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: BACKWARD {last_y} -> {y} ({numseq})")
                    last_y_for_x[x] = y
                else:
                    warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: JUMP {last_y}+1 -> {y} ({numseq})")
                    last_y_for_x[x] = y
        else:
            # Depth >=4: general rule per parent tuple
            parent = tuple(parts[:-1])
            cur = parts[-1]
            last = last_for_parent.get(parent)
            if last is None:
                if cur != 1:
                    warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: START_NOT_1 for {'.'.join(map(str,parent))}.k -> {numseq}")
                last_for_parent[parent] = cur
            else:
                if cur == last:
                    warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: DUP -> {numseq}")
                elif cur == last + 1:
                    last_for_parent[parent] = cur
                elif cur < last:
                    warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: BACKWARD {last} -> {cur} ({numseq})")
                    last_for_parent[parent] = cur
                else:
                    warnings.append(f"{md.relative_to(ROOT)}:{idx}: CH{chapter_no}: JUMP {last}+1 -> {cur} ({numseq})")
                    last_for_parent[parent] = cur

    return warnings


def main() -> int:
    sources = [ROOT / "book" / "1130.2025.newbook.md"]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = REPORTS / f"numbering_consistency_{ts}.txt"

    all_warnings: List[str] = []
    for md in sources:
        if md.exists():
            all_warnings.extend(_scan_book(md))

    with report.open("w", encoding="utf-8") as rep:
        rep.write(f"Numbering consistency QA @ {ts}\n")
        rep.write(f"Sources: {len(sources)} files\n")
        rep.write(f"Warnings: {len(all_warnings)}\n\n")
        for w in all_warnings:
            rep.write(w + "\n")

    print(f"REPORT: {report}")
    print(f"WARNINGS: {len(all_warnings)}")
    # Read-only QA: always return success
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
