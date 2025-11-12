#!/usr/bin/env python3
"""Emit per-chapter editorial issue templates from tools/editorial-todo-per-chapter.json

Creates: tools/editorial-issues/<sanitized-title>.md
"""
from pathlib import Path
import json
import re

ROOT = Path('.')
IN_JSON = ROOT / 'tools' / 'editorial-todo-per-chapter.json'
OUT_DIR = ROOT / 'tools' / 'editorial-issues'

def sanitize(name: str) -> str:
    # replace spaces and slashes and other odd chars
    s = re.sub(r"[\s/\\]+", '_', name)
    s = re.sub(r"[^0-9A-Za-z_\-\u4e00-\u9fff\.]+", '', s)
    return s[:120]

def main():
    if not IN_JSON.exists():
        print(f'Missing {IN_JSON}, run generate_content_gaps.py first')
        return
    data = json.loads(IN_JSON.read_text(encoding='utf-8'))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for entry in data.get('files', []):
        title = entry.get('title') or Path(entry.get('path','')).name
        fname = sanitize(title) + '.md'
        outp = OUT_DIR / fname
        with outp.open('w', encoding='utf-8') as fh:
            fh.write(f'# Editorial task: {title}\n\n')
            fh.write(f'Path: `{entry.get("path")}`\n\n')
            fh.write('## Observations\n')
            for k,v in entry.get('counts', {}).items():
                fh.write(f'- {k}: {v}\n')
            if entry.get('found_appendix'):
                fh.write('\n## Appendix files found\n')
                for a in entry.get('found_appendix',[]):
                    fh.write(f'- `{a}`\n')
            if entry.get('missing_appendix'):
                fh.write('\n## Missing appendix references\n')
                for m in entry.get('missing_appendix',[]):
                    fh.write(f'- `{m}` (verify filename or add to `appendix/`)\n')

            fh.write('\n## Suggested editorial TODOs (tick when done)\n')
            if entry.get('suggestions'):
                for s in entry.get('suggestions',[]):
                    fh.write(f'- [ ] {s}\n')
            else:
                fh.write('- [ ] Quick read for style/clarity (no urgent suggestions detected)\n')

            fh.write('\n## Notes for author/editor\n')
            fh.write('- Add concrete examples or exercises where appropriate.\n')
            fh.write('- Add diagrams/images for complex concepts.\n')
            fh.write('- Extract runnable code to `appendix/` and link from chapter where helpful.\n')

    print(f'Wrote issue templates to {OUT_DIR} (count: {len(list(OUT_DIR.glob("*.md")))})')

if __name__ == "__main__":
    main()
