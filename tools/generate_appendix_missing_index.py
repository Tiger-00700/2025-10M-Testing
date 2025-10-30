#!/usr/bin/env python3
"""Generate an index file for appendix-missing editorial issue templates.
Writes: tools/editorial-issues/appendix-missing-index.md
"""
from pathlib import Path
import re

ROOT = Path('.')
DIR = ROOT / 'tools' / 'editorial-issues'
OUT = DIR / 'appendix-missing-index.md'

if not DIR.exists():
    print('Editorial issues dir missing:', DIR)
    raise SystemExit(1)

entries = []
for p in sorted(DIR.glob('appendix-missing-*.md')):
    text = p.read_text(encoding='utf-8')
    # extract title from frontmatter or first heading
    m = re.search(r"title:\s*'([^']+)'", text)
    title = m.group(1) if m else p.stem
    # extract source file and line
    m2 = re.search(r"file:\s*`([^`]+)`\n- line:\s*(\d+)", text)
    source = m2.group(1) if m2 else ''
    line = m2.group(2) if m2 else ''
    # extract context code block (first markdown block)
    m3 = re.search(r"```markdown\n([\s\S]*?)\n```", text)
    ctx = m3.group(1).strip() if m3 else ''
    entries.append({'path': p.name, 'title': title, 'source': source, 'line': line, 'context': ctx})

lines = []
lines.append('# Appendix missing references — index')
lines.append('This index lists editorial templates for appendix references that could not be resolved automatically. Each entry links to the template for editorial action.')
lines.append('')
for e in entries:
    lines.append(f"- [{e['title']}](./{e['path']}) — source: `{e['source']}` line {e['line']}")
    if e['context']:
        snippet = e['context']
        if len(snippet) > 160:
            snippet = snippet[:157] + '...'
        lines.append(f"  - Context: `{snippet}`")
    lines.append('')

OUT.write_text('\n'.join(lines), encoding='utf-8')
print('Wrote', OUT)
