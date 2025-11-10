"""Validate example links in cleaned book and produce an integrity report.

Also inventories exercise blocks ("> 【课后思考/练习题】") and emits stats used by downstream
quality dashboard.

Patterns validated:
  - Markdown links to examples: [text](../examples/...) or (./examples/...) or (examples/...) relative forms
  - Inline code/path references: `examples/dir/script.py` (best-effort)

Output:
  tools/reports/example-links-exercises-<ts>.md
Exit code 0 unless --fail-on-broken passed and broken links found.

Idempotent: read-only for book; does not modify content.
"""
from __future__ import annotations
import re
from pathlib import Path
from datetime import datetime, timezone
import argparse

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
EXAMPLES_DIR = ROOT / 'examples'
REPORTS = ROOT / 'tools' / 'reports'

MD_LINK_RE = re.compile(r"\[[^\]]*\]\((?:\./|\.\./|)examples/[^)#\s]+\)")
LINK_TARGET_RE = re.compile(r"\[[^\]]*\]\(((?:\./|\.\./|)examples/[^)#\s]+)\)")
INLINE_CODE_RE = re.compile(r"`(examples/[^`\s]+)`")
EXERCISE_BLOCK_RE = re.compile(r"^>\s*【课后思考/练习题】")
QUESTION_LINE_RE = re.compile(r"^(?:\d+\.\s+|[-*]\s+).+")

def load_lines(p: Path) -> list[str]:
    return p.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n').split('\n')

def normalize_target(t: str) -> Path:
    # strip leading ./ or ../
    while t.startswith('./'):
        t = t[2:]
    if t.startswith('../'):
        # allow one level up but we expect examples/ so collapse
        t = t[3:]
    return (ROOT / t).resolve()

def collect_example_links(lines: list[str]):
    links = []  # (line_no, raw_line, target)
    broken = []
    for i, ln in enumerate(lines, start=1):
        for m in LINK_TARGET_RE.finditer(ln):
            tgt = m.group(1)
            p = normalize_target(tgt)
            links.append((i, ln.strip(), tgt, p))
            if not p.exists():
                broken.append((i, ln.strip(), tgt))
        for im in INLINE_CODE_RE.finditer(ln):
            tgt = im.group(1)
            if tgt.endswith('/'):
                p = normalize_target(tgt.rstrip('/'))
            else:
                p = normalize_target(tgt)
            links.append((i, ln.strip(), tgt, p))
            if not p.exists():
                broken.append((i, ln.strip(), tgt))
    return links, broken

def collect_exercises(lines: list[str]):
    exercises = []  # list of (start_line, question_lines)
    i = 0
    while i < len(lines):
        ln = lines[i]
        if EXERCISE_BLOCK_RE.match(ln.strip()):
            q_lines = []
            j = i + 1
            while j < len(lines):
                s = lines[j].strip()
                if s == '':
                    # allow single blank but break on double
                    if j + 1 < len(lines) and lines[j+1].strip() == '':
                        break
                    j += 1
                    continue
                if EXERCISE_BLOCK_RE.match(s):
                    break
                if QUESTION_LINE_RE.match(s):
                    q_lines.append(lines[j])
                    j += 1
                    continue
                # stop on next heading
                if s.startswith('#'):
                    break
                j += 1
            exercises.append((i+1, q_lines))
            i = j
            continue
        i += 1
    return exercises

def render_report(links, broken, exercises):
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = [f"# Example Links & Exercises Report ({ts})", "", f"Total example link refs: {len(links)}", f"Broken example links: {len(broken)}", "", f"Exercise blocks: {len(exercises)}"]
    total_questions = sum(len(qs) for _, qs in exercises)
    out.append(f"Total exercise questions: {total_questions}")
    out.append("")
    if broken:
        out.append("## Broken Links")
        out.append("")
        out.append("| Line | Target | Excerpt |")
        out.append("|------|--------|---------|")
        for ln, raw, tgt in broken[:300]:
            out.append(f"| {ln} | {tgt} | {raw.replace('|','\\|')[:120]} |")
        if len(broken) > 300:
            out.append(f"... and {len(broken)-300} more")
        out.append("")
    # exercise stats
    if exercises:
        out.append("## Exercise Blocks Summary")
        out.append("")
        out.append("| Start Line | Questions |")
        out.append("|------------|-----------|")
        for ln, qs in exercises[:200]:
            out.append(f"| {ln} | {len(qs)} |")
        if len(exercises) > 200:
            out.append(f"... and {len(exercises)-200} more")
        out.append("")
    return "\n".join(out) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fail-on-broken', action='store_true', help='Exit non-zero if broken example links found.')
    args = ap.parse_args()
    if not BOOK.exists():
        raise SystemExit(f'Cleaned book not found: {BOOK}')
    if not EXAMPLES_DIR.exists():
        raise SystemExit(f'Examples dir not found: {EXAMPLES_DIR}')
    lines = load_lines(BOOK)
    links, broken = collect_example_links(lines)
    exercises = collect_exercises(lines)
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    rep = REPORTS / f'example-links-exercises-{ts}.md'
    rep.write_text(render_report(links, broken, exercises), encoding='utf-8')
    print(f'Example link refs={len(links)} broken={len(broken)} exercise_blocks={len(exercises)} report={rep.name}')
    if args.fail_on_broken and broken:
        raise SystemExit(2)

if __name__ == '__main__':
    main()
