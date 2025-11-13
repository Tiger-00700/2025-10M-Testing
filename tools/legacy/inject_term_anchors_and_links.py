"""Inject term anchors and first-use links based on glossary.

Workflow:
  1. Parse glossary table in 附录-术语与缩略语表.md extracting terms.
  2. For each term, find first occurrence in cleaned book outside code fences and headings.
  3. Insert an HTML anchor <a id="term-<slug>"></a> one line before the first occurrence (if not already anchored) and
     wrap the first occurrence with a link to glossary entry: [Term](./附录-术语与缩略语表.md#<slug>)
  4. Idempotent: skips if link already present or anchor id already inserted.

Glossary slug: lowercase, strip punctuation, spaces -> '-'.
Outputs report with counts.
"""
from __future__ import annotations
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
GLOSS = ROOT / 'book' / '附录-术语与缩略语表.md'
REPORTS = ROOT / 'tools' / 'reports'

PUNCT_RE = re.compile(r"[!""#$%&'()*+,./:;<=>?@\[\\\]^_`{|}~，。、《》？；：‘’“”（）【】·—…]+")
CODE_FENCE_RE = re.compile(r"^\s*(```|~~~)")
ANCHOR_LINE_RE = re.compile(r'^\s*<a\s+id="term-([^"/]+)"\s*></a>\s*$', re.IGNORECASE)

def slugify(term: str) -> str:
    t = term.strip().lower()
    t = PUNCT_RE.sub('', t)
    t = re.sub(r"\s+", '-', t)
    t = re.sub(r'-{2,}', '-', t)
    return t

def parse_glossary_terms(text: str) -> list[str]:
    lines = text.splitlines()
    header_idx = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith('| 术语 |'):
            header_idx = i
            break
    if header_idx is None:
        return []
    terms = []
    for ln in lines[header_idx+2:]:
        if not ln.strip().startswith('|'):
            break
        cols = [c.strip() for c in ln.strip().strip('|').split('|')]
        if cols:
            terms.append(cols[0])
    return terms

def load_text(p: Path) -> str:
    return p.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n')

def inject(lines: list[str], terms: list[str]):
    anchors_added = 0
    links_added = 0
    inside_code = False
    existing_anchors = set()
    for ln in lines:
        m = ANCHOR_LINE_RE.match(ln.strip())
        if m:
            existing_anchors.add(m.group(1))
    # map term->first index
    first_occurrence: dict[str,int] = {}
    for idx, ln in enumerate(lines):
        stripped = ln.strip()
        if CODE_FENCE_RE.match(stripped):
            inside_code = not inside_code
            continue
        if inside_code:
            continue
        # skip headings
        if stripped.startswith('#'):
            continue
        for term in terms:
            if term in first_occurrence:
                continue
            # simple raw substring search; ensure not already linked
            if f']({GLOSS.name}#' in ln:
                continue
            if term in ln:
                first_occurrence[term] = idx
    # apply injections from bottom to top to keep indices stable
    for term, idx in sorted(first_occurrence.items(), key=lambda x: x[1], reverse=True):
        slug = slugify(term)
        if slug in existing_anchors:
            # anchor already exists, but ensure first link (wrap term once)
            line = lines[idx]
            if f']({GLOSS.name}#' in line:
                continue
            # replace first occurrence of term with link
            new_line = line.replace(term, f'[{term}]({GLOSS.name}#{slug})', 1)
            lines[idx] = new_line
            links_added += 1
            continue
        # Insert anchor above if previous line not blank, add blank for readability
        if idx > 0 and lines[idx-1].strip() != '':
            lines.insert(idx, '')
            idx += 1
        lines.insert(idx, f'<a id="term-{slug}"></a>')
        anchors_added += 1
        existing_anchors.add(slug)
        # link term in line below
        line = lines[idx+1]
        if f']({GLOSS.name}#' not in line:
            lines[idx+1] = line.replace(term, f'[{term}]({GLOSS.name}#{slug})', 1)
            links_added += 1
    return lines, anchors_added, links_added, len(first_occurrence)

def main():
    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    if not GLOSS.exists():
        raise SystemExit(f'Glossary not found: {GLOSS}')
    book_lines = load_text(BOOK).split('\n')
    terms = parse_glossary_terms(load_text(GLOSS))
    new_lines, anchors_added, links_added, found_terms = inject(book_lines, terms)
    if anchors_added or links_added:
        BOOK.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    rep = REPORTS / f'term-anchors-links-{ts}.md'
    rep.write_text('\n'.join([
        f'# Term Anchors & Links Report ({ts})',
        '',
        f'Terms scanned: {len(terms)}',
        f'Terms first occurrences found: {found_terms}',
        f'Anchors added: {anchors_added}',
        f'First-use links added: {links_added}',
        ''
    ]), encoding='utf-8')
    print(f'Terms={len(terms)} found_first={found_terms} anchors_added={anchors_added} links_added={links_added} report={rep.name}')

if __name__ == '__main__':
    main()
