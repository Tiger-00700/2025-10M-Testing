"""Aggregate quality metrics and optionally fail CI based on thresholds.

Metrics computed directly from cleaned book:
    placeholders_type_a, placeholders_type_b
    example_links_total, example_links_broken
    exercise_blocks, exercise_questions, exercise_tagged_questions
    term_anchors_added (approx = count of <a id="term-..."> lines)
    see_also_blocks (lines starting with > 【See Also】)
    internal_links_total, internal_links_broken (links pointing to ./1022.2025.newbook.cleaned.md#...)

Threshold env vars (numeric):
  QUALITY_MAX_BROKEN_EXAMPLE_LINKS
  QUALITY_MIN_EXERCISE_TAGGED_RATIO (0-1)
  QUALITY_MIN_SEE_ALSO_BLOCKS
    QUALITY_MAX_SEE_ALSO_BLOCKS
  QUALITY_MAX_PLACEHOLDERS_A
  QUALITY_MAX_PLACEHOLDERS_B
    QUALITY_MAX_BROKEN_INTERNAL_LINKS

Outputs JSON and Markdown summary in tools/reports.
Exit non-zero if any threshold violated.
"""
from __future__ import annotations
import re, json, os, math
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

PLACEHOLDER_KEY = 'Placeholder: migrated from book reference, please fill content.'
MIGRATED_NOTICE = 'Placeholder: migrated to part dir.'
HEAD_RE = re.compile(r'^(#{1,6})\s+(.*\S)\s*$')
EXAMPLE_LINK_TARGET_RE = re.compile(r'\[[^\]]*\]\(((?:\./|\.\./|)examples/[^)#\s]+)\)')
INLINE_EXAMPLE_CODE_RE = re.compile(r'`(examples/[^`\s]+)`')
EXERCISE_BLOCK_RE = re.compile(r'^>\s*【课后思考/练习题】')
QUESTION_TAGGED_RE = re.compile(r'^(?:\d+\.\s+|[-*]\s+)【(?:入门|进阶|专家)】')
TERM_ANCHOR_RE = re.compile(r'^<a\s+id="term-[^"/]+"\s*></a>')
SEE_ALSO_RE = re.compile(r'^>\s*【See Also】')
INTERNAL_LINK_RE = re.compile(r'\[[^\]]*\]\((?:\./)?1022\.2025\.newbook\.cleaned\.md#([^)\s]+)\)')
ANCHOR_LINE_RE = re.compile(r'^<a\s+id="([^"/]+)"\s*></a>\s*$', re.IGNORECASE)
H2_RE = re.compile(r'^##\s+(.*\S)\s*$')

def load_lines(p: Path) -> list[str]:
    return p.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n').split('\n')

def classify_placeholders(lines: list[str]):
    A=B=0
    for ln in lines:
        m = HEAD_RE.match(ln)
        if m and m.group(2).strip() == PLACEHOLDER_KEY:
            A += 1
        else:
            s = ln.strip()
            if PLACEHOLDER_KEY in s and s != MIGRATED_NOTICE:
                B += 1
    return A,B

def example_links(lines: list[str]):
    refs=0; broken=0
    for ln in lines:
        for m in EXAMPLE_LINK_TARGET_RE.finditer(ln):
            refs += 1
            target = m.group(1)
            # coarse existence check: path relative to root
            t = target
            while t.startswith('./'): t = t[2:]
            if t.startswith('../'): t = t[3:]
            p = (ROOT / t).resolve()
            if not p.exists():
                broken += 1
        for m in INLINE_EXAMPLE_CODE_RE.finditer(ln):
            refs += 1
            t = m.group(1)
            if t.endswith('/'): t = t.rstrip('/')
            p = (ROOT / t.lstrip('./')).resolve()
            if not p.exists():
                broken += 1
    return refs, broken

def exercises(lines: list[str]):
    blocks=0; questions=0; tagged=0
    i=0
    while i < len(lines):
        ln = lines[i]
        if EXERCISE_BLOCK_RE.match(ln.strip()):
            blocks += 1
            j=i+1
            while j < len(lines):
                s = lines[j].strip()
                if s=='':
                    if j+1 < len(lines) and lines[j+1].strip()=='' :
                        break
                    j+=1; continue
                if EXERCISE_BLOCK_RE.match(s) or s.startswith('#'): break
                if re.match(r'^(?:\d+\.\s+|[-*]\s+).+', s):
                    questions += 1
                    if QUESTION_TAGGED_RE.match(lines[j]): tagged += 1
                j+=1
            i=j; continue
        i+=1
    return blocks, questions, tagged

def count_term_anchors(lines: list[str]):
    return sum(1 for ln in lines if TERM_ANCHOR_RE.match(ln.strip()))

def count_see_also(lines: list[str]):
    return sum(1 for ln in lines if SEE_ALSO_RE.match(ln.strip()))

def chapter_see_also_counts(lines: list[str]):
    chapters = []
    current = None
    for i, ln in enumerate(lines):
        m = H2_RE.match(ln)
        if m:
            if current:
                chapters.append(current)
            current = {'title': m.group(1).strip(), 'start': i, 'end': len(lines), 'count': 0}
        else:
            if current and SEE_ALSO_RE.match(ln.strip()):
                current['count'] += 1
    if current:
        chapters.append(current)
    return chapters

def internal_links_status(lines: list[str]):
    anchors = set()
    for ln in lines:
        m = ANCHOR_LINE_RE.match(ln.strip())
        if m:
            anchors.add(m.group(1))
    total = 0
    broken = 0
    for ln in lines:
        for m in INTERNAL_LINK_RE.finditer(ln):
            total += 1
            target = m.group(1)
            if target not in anchors:
                broken += 1
    return total, broken

def main():
    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    lines = load_lines(BOOK)
    A,B = classify_placeholders(lines)
    ex_refs, ex_broken = example_links(lines)
    ex_blocks, ex_questions, ex_tagged = exercises(lines)
    term_anchors = count_term_anchors(lines)
    see_also = count_see_also(lines)
    # chapter-level stats for See Also
    ch = chapter_see_also_counts(lines)
    ch_counts = [c['count'] for c in ch]
    def median(vals):
        if not vals: return 0.0
        s = sorted(vals)
        n = len(s); m = n//2
        return float(s[m]) if n%2==1 else (s[m-1]+s[m])/2.0
    def percentile(vals, p):
        if not vals: return 0.0
        s = sorted(vals)
        k = (len(s)-1)*p
        f = math.floor(k); c = math.ceil(k)
        if f==c: return float(s[int(k)])
        d0 = s[f]*(c-k); d1 = s[c]*(k-f)
        return float(d0+d1)
    def stdev(vals):
        if not vals: return 0.0
        mu = sum(vals)/len(vals)
        var = sum((x-mu)*(x-mu) for x in vals)/len(vals)
        return math.sqrt(var)
    def gini(vals):
        n = len(vals)
        if n==0: return 0.0
        s = sorted(vals)
        total = sum(s)
        if total == 0: return 0.0
        num = 0
        for i, x in enumerate(s, start=1):
            num += (2*i - n - 1) * x
        return float(num)/(n*total)
    ch_mean = (sum(ch_counts)/len(ch_counts)) if ch_counts else 0.0
    ch_median = median(ch_counts)
    ch_p90 = percentile(ch_counts, 0.90)
    ch_std = stdev(ch_counts)
    ch_gini = gini(ch_counts)
    internal_total, internal_broken = internal_links_status(lines)
    tagged_ratio = (ex_tagged / ex_questions) if ex_questions else 0.0
    metrics = {
        'placeholders_type_a': A,
        'placeholders_type_b': B,
        'example_links_total': ex_refs,
        'example_links_broken': ex_broken,
        'exercise_blocks': ex_blocks,
        'exercise_questions': ex_questions,
        'exercise_tagged_questions': ex_tagged,
        'exercise_tagged_ratio': round(tagged_ratio,4),
        'term_anchors': term_anchors,
        'see_also_blocks': see_also,
        'see_also_chapter_mean': round(ch_mean,2),
        'see_also_chapter_median': round(ch_median,2),
        'see_also_chapter_p90': round(ch_p90,2),
        'see_also_chapter_std': round(ch_std,2),
        'see_also_chapter_gini': round(ch_gini,3),
        'internal_links_total': internal_total,
        'internal_links_broken': internal_broken,
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    json_path = REPORTS / f'quality-dashboard-{ts}.json'
    json_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding='utf-8')
    md_path = REPORTS / f'quality-dashboard-{ts}.md'
    md_lines = [f'# Quality Dashboard ({ts})','']
    for k,v in metrics.items():
        md_lines.append(f'- {k}: {v}')
    md_path.write_text('\n'.join(md_lines)+'\n', encoding='utf-8')
    print(f'Metrics written: {json_path.name} {md_path.name}')
    # thresholds
    violations = []
    def env_int(name, default=None):
        val = os.getenv(name)
        if val is None: return default
        try: return int(val)
        except: return default
    def env_float(name, default=None):
        val = os.getenv(name)
        if val is None: return default
        try: return float(val)
        except: return default
    if (mx := env_int('QUALITY_MAX_BROKEN_EXAMPLE_LINKS')) is not None and ex_broken > mx:
        violations.append(f'Broken example links {ex_broken} > {mx}')
    if (mn := env_float('QUALITY_MIN_EXERCISE_TAGGED_RATIO')) is not None and tagged_ratio < mn:
        violations.append(f'Exercise tagged ratio {tagged_ratio:.2f} < {mn}')
    if (mn := env_int('QUALITY_MIN_SEE_ALSO_BLOCKS')) is not None and see_also < mn:
        violations.append(f'See Also blocks {see_also} < {mn}')
    if (mx := env_int('QUALITY_MAX_SEE_ALSO_BLOCKS')) is not None and see_also > mx:
        violations.append(f'See Also blocks {see_also} > {mx}')
    if (mx := env_int('QUALITY_MAX_PLACEHOLDERS_A')) is not None and A > mx:
        violations.append(f'Placeholders A {A} > {mx}')
    if (mx := env_int('QUALITY_MAX_PLACEHOLDERS_B')) is not None and B > mx:
        violations.append(f'Placeholders B {B} > {mx}')
    if (mx := env_int('QUALITY_MAX_BROKEN_INTERNAL_LINKS')) is not None and internal_broken > mx:
        violations.append(f'Broken internal links {internal_broken} > {mx}')
    # advanced see-also distribution thresholds
    def env_float(name, default=None):
        val = os.getenv(name)
        if val is None: return default
        try: return float(val)
        except: return default
    if (mxg := env_float('QUALITY_MAX_SEE_ALSO_GINI')) is not None and ch_gini > mxg:
        violations.append(f'See Also chapter Gini {ch_gini:.3f} > {mxg}')
    if (tmean := env_float('QUALITY_TARGET_SEE_ALSO_MEAN')) is not None and ch_mean > tmean:
        violations.append(f'See Also chapter mean {ch_mean:.2f} > {tmean}')
    if violations:
        print('Threshold violations:\n - ' + '\n - '.join(violations))
        raise SystemExit(3)

if __name__ == '__main__':
    main()
