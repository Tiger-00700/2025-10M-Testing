#!/usr/bin/env python3
"""检查 book 和 chapter 下对 appendix (附录) 的引用，并验证目标文件存在。
输出:
 - tools/appendix-link-report.json
 - tools/appendix-link-report.txt
"""
import re, os, json
from pathlib import Path

ROOT = Path('.')
BOOK = ROOT / 'book' / '1022.2025.book.md'
CHAPTER_DIR = ROOT / 'chapter'
APPENDIX_DIR = ROOT / 'appendix'
OUT_JSON = ROOT / 'tools' / 'appendix-link-report.json'
OUT_TXT = ROOT / 'tools' / 'appendix-link-report.txt'

# patterns to capture links and bare filenames
link_re = re.compile(r"\[.*?\]\(([^)]+)\)")
paren_re = re.compile(r"\(([^)]+appendix[^)]*)\)", re.IGNORECASE)
# capture backtick or bare filenames with common extensions
file_re = re.compile(r"[`\(]?([A-Za-z0-9_\-./\\]+\.(sh|py|java|sql|json|yml|yaml|properties))[`\)]?", re.IGNORECASE)

files_to_scan = [BOOK] + sorted(CHAPTER_DIR.glob('*.md')) if CHAPTER_DIR.exists() else [BOOK]

report = {'summary':{}, 'references': []}
seen = 0
missing = 0

# helper: fuzzy candidates in appendix
def candidates(name):
    name_low = name.lower()
    cands = []
    if APPENDIX_DIR.exists():
        for p in APPENDIX_DIR.rglob('*'):
            if p.is_file() and name_low in p.name.lower():
                cands.append(str(p))
    return cands

for f in files_to_scan:
    try:
        lines = f.read_text(encoding='utf-8').splitlines()
    except Exception:
        continue
    for i,line in enumerate(lines, start=1):
        # check explicit markdown links
        for m in link_re.finditer(line):
            tgt = m.group(1).strip()
            if 'appendix' in tgt.lower() or '附录' in tgt:
                # resolve relative
                ref = tgt
                # remove anchors and query
                ref_norm = ref.split('#')[0].split('?')[0]
                # possible relative paths
                resolved = None
                if ref_norm.startswith('http'):
                    resolved = ref_norm
                    exists = None
                else:
                    # try resolve relative to current file
                    base = f.parent
                    cand = (base / ref_norm).resolve()
                    if cand.exists():
                        resolved = str(cand)
                        exists = True
                    else:
                        # try workspace relative
                        cand2 = (ROOT / ref_norm).resolve()
                        if cand2.exists():
                            resolved = str(cand2)
                            exists = True
                        else:
                            # try appendix dir
                            append_cand = (APPENDIX_DIR / Path(ref_norm).name).resolve()
                            if append_cand.exists():
                                resolved = str(append_cand)
                                exists = True
                            else:
                                resolved = str(append_cand)
                                exists = False
                ent = {'source_file': str(f), 'line': i, 'raw': line.strip(), 'matched': tgt, 'resolved': resolved, 'exists': exists}
                if exists is False:
                    ent['candidates'] = candidates(Path(tgt).name)
                    missing += 1
                report['references'].append(ent)
                seen += 1
        # paren_re for parenthesized appendix mentions
        for m in paren_re.finditer(line):
            tgt = m.group(1).strip()
            # similar handling
            ref_norm = tgt.split('#')[0].split('?')[0]
            resolved = None
            exists = None
            if ref_norm.startswith('http'):
                resolved = ref_norm; exists = None
            else:
                base = f.parent
                cand = (base / ref_norm).resolve()
                if cand.exists():
                    resolved = str(cand); exists = True
                else:
                    cand2 = (ROOT / ref_norm).resolve()
                    if cand2.exists():
                        resolved = str(cand2); exists = True
                    else:
                        append_cand = (APPENDIX_DIR / Path(ref_norm).name).resolve()
                        if append_cand.exists():
                            resolved = str(append_cand); exists = True
                        else:
                            resolved = str(append_cand); exists = False
            ent = {'source_file': str(f), 'line': i, 'raw': line.strip(), 'matched': tgt, 'resolved': resolved, 'exists': exists}
            if exists is False:
                ent['candidates'] = candidates(Path(tgt).name)
                missing += 1
            report['references'].append(ent)
            seen += 1
        # file names in text (bare references)
        for m in file_re.finditer(line):
            name = m.group(1).strip()
            # if name located in appendix
            candidate = (APPENDIX_DIR / Path(name)).resolve()
            exists = candidate.exists() if APPENDIX_DIR.exists() else False
            resolved = str(candidate)
            # Only add if appendix dir has candidate or if line mentions '附录' nearby
            if '附录' in line or 'appendix' in line.lower() or APPENDIX_DIR.exists() and candidate.exists():
                ent = {'source_file': str(f), 'line': i, 'raw': line.strip(), 'matched': name, 'resolved': resolved, 'exists': exists}
                if exists is False:
                    ent['candidates'] = candidates(Path(name).name)
                    missing += 1
                report['references'].append(ent)
                seen += 1

report['summary'] = {'references_found': seen, 'missing_targets': missing}

OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

with OUT_TXT.open('w', encoding='utf-8') as fh:
    fh.write(f"Appendix link report\nReferences found: {seen}\nMissing targets: {missing}\n\n")
    for r in report['references']:
        fh.write(f"Source: {r['source_file']} (line {r['line']})\n")
        fh.write(f"  -> matched: {r['matched']}\n")
        fh.write(f"  -> resolved: {r['resolved']}\n")
        fh.write(f"  -> exists: {r['exists']}\n")
        if not r['exists']:
            fh.write(f"  -> candidates: {r.get('candidates', [])}\n")
        fh.write('\n')

print('Wrote', OUT_JSON, 'and', OUT_TXT)
