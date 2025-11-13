"""
Generate fuzzy anchor mapping suggestions for unresolved internal links in
the cleaned book.

Strategy:
- Collect existing anchors and heading titles (produce slug bases).
- Identify broken link targets (targets without existing anchor).
- For each broken target, compare its base (strip numeric suffix) with
    available anchor bases and heading slug bases using difflib
    SequenceMatcher ratio.
- Produce candidates with ratio >= MIN_RATIO (default 0.78).
- Mark 'confident' if exactly one candidate with ratio >= CONF_RATIO
    (default 0.90).

Output: tools/reports/fuzzy-anchor-suggestions-cleaned-<ts>.json & .md
"""
from __future__ import annotations
import re, json
from pathlib import Path
from datetime import datetime, timezone
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

link_pattern = (
    r"\[[^\]]*\]\((?:\./)?"
    r"1022\.2025\.newbook\.cleaned\.md#([^\)\s]+)\)"
)
LINK_RE = re.compile(link_pattern)
ANCHOR_RE = re.compile(r'^\s*<a\s+id="([^"/]+)"\s*></a>\s*$', re.IGNORECASE)
HEAD_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
PUNCT_RE = re.compile(r"[!\"#$%&'()*+,\./:;<=>?@\[\\\]^_`{|}~，。、《》？；：‘’“”（）【】·—…]+")

MIN_RATIO = 0.78
CONF_RATIO = 0.90
MAX_CANDIDATES = 5

def load_lines(p: Path) -> list[str]:
    text = p.read_text(encoding='utf-8')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text.split('\n')

def slug_base(title: str) -> str:
    t = title.strip().lower()
    t = PUNCT_RE.sub('', t)
    t = re.sub(r"\s+", '-', t)
    t = re.sub(r"-{2,}", '-', t)
    return t

def strip_suffix(aid: str) -> str:
    m = re.match(r"^(.*?)(?:-(\d+))?$", aid)
    return m.group(1) if m else aid

def collect(lines: list[str]):
    anchors = set()
    for ln in lines:
        am = ANCHOR_RE.match(ln.strip())
        if am:
            anchors.add(am.group(1))
    anchor_bases = {strip_suffix(a) for a in anchors}
    heading_bases = set()
    for ln in lines:
        hm = HEAD_RE.match(ln)
        if hm:
            heading_bases.add(slug_base(hm.group(2)))
    return anchors, anchor_bases, heading_bases

def broken_targets(lines: list[str], anchors: set[str]):
    broken = set()
    for ln in lines:
        for m in LINK_RE.finditer(ln):
            target = m.group(1)
            if target not in anchors:
                broken.add(target)
    return broken

def ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def main():
    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    lines = load_lines(BOOK)
    anchors, anchor_bases, heading_bases = collect(lines)
    broken = broken_targets(lines, anchors)
    candidates_space = list(anchor_bases | heading_bases)
    suggestions = []
    for tgt in sorted(broken):
        base = strip_suffix(tgt)
        scored = []
        for cand in candidates_space:
            r = ratio(base, cand)
            if r >= MIN_RATIO:
                scored.append((r, cand))
        scored.sort(reverse=True)
        top = scored[:MAX_CANDIDATES]
        if not top:
            continue
        confident = False
        high = [c for c in top if c[0] >= CONF_RATIO]
        if len(high) == 1:
            confident = True
        cand_list: list[dict[str, object]] = []
        for r_val, cand_val in top:
            cand_list.append({'anchor_base': cand_val, 'ratio': round(r_val, 3)})
        suggestions.append({
            'target': tgt,
            'base': base,
            'candidates': cand_list,
            'confident': confident,
        })
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    (REPORTS / f'fuzzy-anchor-suggestions-cleaned-{ts}.json').write_text(
        json.dumps(suggestions, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    md_lines = [
        f"# Fuzzy Anchor Suggestions CLEANED ({ts})",
        "",
        "Broken targets: " + str(len(broken)),
        "Suggestions generated: " + str(len(suggestions)),
        "",
    ]
    for s in suggestions[:400]:
        title = "## " + s['target'] + " → candidates"
        if s.get('confident'):
            title += " (CONFIDENT)"
        md_lines.append(title)
        for c in s['candidates']:
            md_lines.append(f"- {c['anchor_base']} (ratio={c['ratio']})")
        md_lines.append('')
    (REPORTS / f'fuzzy-anchor-suggestions-cleaned-{ts}.md').write_text('\n'.join(md_lines), encoding='utf-8')
    confident_cnt = sum(1 for s in suggestions if s.get('confident'))
    print(f"Suggestions={len(suggestions)} confident={confident_cnt} broken={len(broken)}")

if __name__ == '__main__':
    main()
