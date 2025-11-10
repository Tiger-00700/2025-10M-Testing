"""Generate simple 'See Also' related links blocks for sections in cleaned book.

Method:
  - Parse H3/H4 sections (title + content until next heading of same or higher level).
  - Tokenize (CJK chars contiguous, alnum words) removing stop words & short tokens.
  - Compute tf-idf vectors (in-memory) and cosine similarity.
  - For each section above MIN_TOKENS, choose top N related sections (excluding itself) with similarity >= MIN_SIM.
  - Append a block: > 【See Also】 本节相关：[Title A](#anchorA) · [Title B](#anchorB) · [Title C](#anchorC)
    placed after the section content but before the next heading.
  - Idempotent: skip if a See Also block already present directly following section.

Anchors: rely on existing <a id="..."></a> lines preceding headings (if not, slugify title for local link).

Outputs a report with counts and modifies book in-place if any blocks added.
"""
from __future__ import annotations
import re
from pathlib import Path
from collections import Counter, defaultdict
from math import sqrt
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

HEAD_RE = re.compile(r'^(#{1,6})\s+(.*\S)\s*$')
ANCHOR_RE = re.compile(r'^<a\s+id="([^"]+)"\s*></a>\s*$')
SEE_ALSO_RE = re.compile(r'^>\s*【See Also】')
META_RE = re.compile(r'<!--\s*see-also:\s*([^>]+)\s*-->')
TOKEN_RE = re.compile(r'[A-Za-z0-9_]+|[\u4e00-\u9fa5]{2,}')
STOP = {"the","and","of","to","in","a","for","is","on","with","by","an","or","be","as","at","that","this","it","本节","以及","进行","实现","数据","测试"}
MIN_TOKENS = 30
TOP_N = 2
MIN_SIM = 0.32

def load_lines(p: Path) -> list[str]:
    return p.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n').split('\n')

def slugify(title: str) -> str:
    t = title.strip().lower()
    t = re.sub(r"[!\"#$%&'()*+,./:;<=>?@\[\\\]^_`{|}~，。、《》？；：‘’“”（）【】·—…]+", '', t)
    t = re.sub(r"\s+", '-', t)
    t = re.sub(r"-{2,}", '-', t)
    return t

def parse_sections(lines: list[str]):
    sections = []
    anchors = {}  # line index -> anchor id
    for i, ln in enumerate(lines):
        am = ANCHOR_RE.match(ln.strip())
        if am:
            anchors[i] = am.group(1)
    current = None
    for i, ln in enumerate(lines):
        m = HEAD_RE.match(ln)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            if current:
                current['end'] = i
                sections.append(current)
            # find anchor above within previous 3 lines
            aid = None
            for back in range(i-1, max(-1, i-4), -1):
                if back in anchors:
                    aid = anchors[back]
                    break
            if not aid:
                aid = slugify(title)
            current = {'level': level, 'title': title, 'start': i, 'end': len(lines), 'anchor': aid, 'content': [], 'meta': {}}
        else:
            if current:
                current['content'].append(ln)
    if current:
        sections.append(current)
    # parse metadata from the first few lines of each section content
    for s in sections:
        meta = {}
        for ln in s['content'][:8]:
            mm = META_RE.search(ln)
            if not mm:
                continue
            cfg = mm.group(1)
            parts = [p.strip() for p in cfg.split(';') if p.strip()]
            for p in parts:
                if p.lower() in ('off', 'off=true', 'off=1'):
                    meta['off'] = True
                elif p.lower().startswith('min_sim='):
                    try:
                        meta['min_sim'] = float(p.split('=',1)[1])
                    except:
                        pass
                elif p.lower().startswith('top_n='):
                    try:
                        meta['top_n'] = int(p.split('=',1)[1])
                    except:
                        pass
        s['meta'] = meta
    # propagate H2 chapter-level meta to subsections if not overridden
    current_chapter_meta = {}
    for s in sections:
        if s['level'] == 2:
            current_chapter_meta = s.get('meta') or {}
        else:
            if current_chapter_meta:
                m = s.get('meta') or {}
                eff = dict(m)
                # inherit keys if not present locally
                for k in ('off','min_sim','top_n'):
                    if k not in eff and k in current_chapter_meta:
                        eff[k] = current_chapter_meta[k]
                s['meta'] = eff
    return sections

def tokenize(txt: str):
    for tok in TOKEN_RE.findall(txt):
        if tok.lower() in STOP or len(tok) < 2:
            continue
        yield tok.lower()

def build_vectors(sections):
    docs = []
    df = Counter()
    for s in sections:
        text = '\n'.join(s['content'])
        toks = list(tokenize(text))
        if len(toks) < MIN_TOKENS:
            s['skip'] = True
            docs.append(Counter())
            continue
        c = Counter(toks)
        for k in c:
            df[k] += 1
        docs.append(c)
    # compute idf
    N = len(sections)
    idf = {t: (1 + N)/(1 + df[t]) for t in df}
    vectors = []
    norms = []
    for s, c in zip(sections, docs):
        vec = {t: (c[t] * idf.get(t, 1.0)) for t in c}
        vectors.append(vec)
        norms.append(sqrt(sum(v*v for v in vec.values())) or 1.0)
    return vectors, norms

def cosine(a, b, norm_a, norm_b):
    common = set(a.keys()) & set(b.keys())
    if not common:
        return 0.0
    dot = sum(a[t]*b[t] for t in common)
    return dot/(norm_a*norm_b)

def main():
    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    lines = load_lines(BOOK)
    sections = parse_sections(lines)
    vectors, norms = build_vectors(sections)
    added = 0
    # iterate sections and decide See Also insertion point (end-1 before next heading)
    prev_block = None
    for idx, s in enumerate(sections):
        if s.get('skip'):
            continue
        # section-level override or disable
        meta = s.get('meta') or {}
        if meta.get('off'):
            continue
        local_min_sim = meta.get('min_sim', MIN_SIM)
        local_top_n = meta.get('top_n', TOP_N)
        # check if block already present in its trailing content
        tail_lines = s['content'][-6:]
        if any(SEE_ALSO_RE.match(t.strip()) for t in tail_lines):
            continue
        sims = []
        for j, other in enumerate(sections):
            if j == idx or other.get('skip'):
                continue
            sim = cosine(vectors[idx], vectors[j], norms[idx], norms[j])
            if sim >= local_min_sim:
                sims.append((sim, other))
        sims.sort(reverse=True, key=lambda x: x[0])
        # pick top then dedupe anchors within same block to avoid duplicates
        top = sims[:max(0, int(local_top_n))]
        seen_anchors = set()
        dedup_top = []
        for sim, o in top:
            a = o["anchor"]
            if a in seen_anchors:
                continue
            seen_anchors.add(a)
            dedup_top.append((sim, o))
        top = dedup_top
        if not top:
            continue
        # build block text
        links = []
        for sim, o in top:
            links.append(f'[{o["title"]}](./1022.2025.newbook.cleaned.md#{o["anchor"]})')
        block = f'> 【See Also】 本节相关：' + ' · '.join(links)
        # dedupe: skip if identical to previous block to avoid back-to-back duplicates
        if block == prev_block:
            continue
        # insert before next heading (i.e., just before s['end']) but after trimming trailing blanks
        insert_at = s['end'] - 1
        # move up over trailing blanks
        while insert_at > s['start'] and lines[insert_at].strip() == '' and not HEAD_RE.match(lines[insert_at]):
            insert_at -= 1
        # add a blank then block then blank
        lines.insert(insert_at + 1, '')
        lines.insert(insert_at + 2, block)
        lines.insert(insert_at + 3, '')
        added += 1
        prev_block = block
        # adjust subsequent section indices
        delta = 3
        for k in range(idx+1, len(sections)):
            sections[k]['start'] += delta
            sections[k]['end'] += delta
    if added:
        BOOK.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    rep = REPORTS / f'related-links-{ts}.md'
    rep.write_text('\n'.join([
        f'# Related Links Report ({ts})',
        '',
        f'Sections parsed: {len(sections)}',
        f'See Also blocks added: {added}',
        f'MIN_SIM={MIN_SIM} TOP_N={TOP_N} MIN_TOKENS={MIN_TOKENS}',
        ''
    ]), encoding='utf-8')
    print(f'Sections={len(sections)} blocks_added={added} report={rep.name}')

if __name__ == '__main__':
    main()
