#!/usr/bin/env python3
"""Generate per-chapter editorial TODOs by scanning markdown files.

Heuristics used:
- Examples: look for headings or inline keywords like 示例、例子、Example, `示例` blocks, or code fences with explanatory text
- Exercises: headings or keywords 练习、习题、Exercise、练习题
- Diagrams/figures: presence of image links ![ or figures keyword
- References: presence of 参考, 参考文献, 引用, bibliography, or a 'References' section
- Glossary/terms: presence of 术语, 术语表, glossary, or Appendix A references
- Appendix links: detect references to ../appendix/ or [脚本：...] and verify target file exists under appendix/
- Inline fenced code: presence of fenced blocks (``` ) suggesting possible extraction to appendix

Outputs:
- tools/editorial-todo-per-chapter.md  (human readable)
- tools/editorial-todo-per-chapter.json (machine readable)

Run: python tools/generate_content_gaps.py
"""
from pathlib import Path
import re
import json

ROOT = Path('.')
TARGET_DIRS = ['book', 'chapter']
OUT_MD = Path('tools/editorial-todo-per-chapter.md')
OUT_JSON = Path('tools/editorial-todo-per-chapter.json')

img_re = re.compile(r'!\[.*?\]\(.*?\)')
fence_re = re.compile(r'^\s{0,3}```')
appendix_link_re = re.compile(r'\[脚本：([^\]]+)\]|\]\(\.\./appendix/([^\)]+)\)')
example_kw = ['示例', '例子', 'Example', '示范']
exercise_kw = ['练习', '习题', 'Exercise', '练习题']
reference_kw = ['参考', '参考文献', '引用', 'References', 'Bibliography']
glossary_kw = ['术语', '术语表', 'Glossary']


def list_md_files():
    files = []
    for d in TARGET_DIRS:
        p = ROOT / d
        if not p.exists():
            continue
        for f in p.rglob('*.md'):
            files.append(f)
    return sorted(files)


def scan_file(path: Path):
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    title = None
    first_h1 = None
    for ln in lines[:50]:
        m = re.match(r'^\s{0,3}#\s+(.*)', ln)
        if m:
            first_h1 = m.group(1).strip()
            break
    title = first_h1 or path.name

    has_images = bool(img_re.search(text))
    fenced = any(fence_re.match(ln) for ln in lines)
    examples = 0
    exercises = 0
    references = 0
    glossary = 0
    appendix_links = []

    for ln in lines:
        for kw in example_kw:
            if kw in ln:
                examples += 1
                break
        for kw in exercise_kw:
            if kw in ln:
                exercises += 1
                break
        for kw in reference_kw:
            if kw in ln:
                references += 1
                break
        for kw in glossary_kw:
            if kw in ln:
                glossary += 1
                break
        for m in appendix_link_re.finditer(ln):
            target = m.group(1) or m.group(2)
            if target:
                appendix_links.append(target)

    # normalize appendix link targets and check existence
    appendix_dir = ROOT / 'appendix'
    missing_appendix = []
    found_appendix = []
    for t in appendix_links:
        # sometimes it's like '..\appendix\2-4__block8.sh' or path only name
        name = Path(t).name
        cand = appendix_dir / name
        if cand.exists():
            found_appendix.append(str(cand.as_posix()))
        else:
            missing_appendix.append(name)

    suggestions = []
    if examples == 0:
        suggestions.append('Consider adding at least one concrete example or runnable snippet for reader practice.')
    if exercises == 0:
        suggestions.append('Consider adding exercises or practice questions to reinforce learning (label as 练习/Exercise).')
    if not has_images:
        suggestions.append('Consider adding at least one diagram/figure where concepts are complex (use images/figures).')
    if references == 0:
        suggestions.append('Add a references/进一步阅读 section or citations if this chapter references external materials.')
    if glossary == 0:
        suggestions.append('If chapter introduces many domain terms, suggest pointing to the glossary/Appendix A or add short definitions.')
    if fenced and not appendix_links:
        suggestions.append('This chapter contains fenced code blocks; consider extracting runnable code to `appendix/` and linking to them consistently.')
    if missing_appendix:
        suggestions.append(f'Missing appendix files referenced: {missing_appendix} — verify filenames or add the files to `appendix/`.')

    return {
        'path': str(path.as_posix()),
        'title': title,
        'counts': {
            'images': int(has_images),
            'fenced_code_blocks': int(fenced),
            'example_kw_matches': examples,
            'exercise_kw_matches': exercises,
            'reference_kw_matches': references,
            'glossary_kw_matches': glossary,
            'appendix_links_found': len(found_appendix),
            'appendix_links_missing': len(missing_appendix),
        },
        'found_appendix': found_appendix,
        'missing_appendix': missing_appendix,
        'suggestions': suggestions,
    }


def main():
    files = list_md_files()
    report = {'files': [], 'summary': {}}
    total_missing_appendix = 0
    for f in files:
        r = scan_file(f)
        total_missing_appendix += len(r['missing_appendix'])
        report['files'].append(r)

    report['summary']['total_files'] = len(report['files'])
    report['summary']['total_missing_appendix'] = total_missing_appendix

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    # write human readable
    with OUT_MD.open('w', encoding='utf-8') as fh:
        fh.write('# Editorial TODO per chapter\n\n')
        fh.write(f'Total scanned files: {report["summary"]["total_files"]}\n')
        fh.write(f'Total missing appendix refs: {report["summary"]["total_missing_appendix"]}\n\n')
        for f in report['files']:
            fh.write(f'## {f["title"]}\n')
            fh.write(f'* Path: `{f["path"]}`\n')
            fh.write('* Counts:\n')
            for k,v in f['counts'].items():
                fh.write(f'  * {k}: {v}\n')
            if f['found_appendix']:
                fh.write(f'* Appendix files found: {len(f["found_appendix"])}\n')
            if f['missing_appendix']:
                fh.write(f'* Missing appendix references: {f["missing_appendix"]}\n')
            if f['suggestions']:
                fh.write('* Suggestions:\n')
                for s in f['suggestions']:
                    fh.write(f'  * {s}\n')
            fh.write('\n')

    print(f'Wrote {OUT_JSON} and {OUT_MD}')


if __name__ == '__main__':
    main()
