#!/usr/bin/env python3
"""
Inventory script for the chapter workspace.
Scans markdown files under the chapter workspace for:
- image references (![](...), <img src=...>)
- fenced code blocks (language and content)
- local file links (relative links to scripts/assets)
- headings and duplicate headings across files
- reports missing referenced local files

Writes report to tools/inventory_report.json and a human summary to tools/inventory_summary.txt
"""
import re
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MD_GLOB = ['*.md']

img_md_re = re.compile(r'!\[[^\]]*\]\(([^)]+)\)')
img_html_re = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')
link_re = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
heading_re = re.compile(r'^(#{1,6})\s*(.+)$', re.MULTILINE)
fence_re = re.compile(r'^```\s*([^\n\r]*)?\r?\n(.*?)\r?\n```', re.MULTILINE | re.DOTALL)

report: dict[str, Any] = {
    'files_scanned': [],
    'images': [],
    'images_missing': [],
    'local_links': [],
    'local_links_missing': [],
    'fenced_blocks': [],
    'headings': {},
}


def is_local_link(href):
    if href.startswith('http://') or href.startswith('https://') or href.startswith('#'):
        return False
    # data: or mailto:
    if re.match(r'^[a-z]+:', href):
        return False
    return True


def scan_file(path: Path):
    text = path.read_text(encoding='utf-8')
    report['files_scanned'].append(str(path.relative_to(ROOT)))
    # fenced blocks (capture first so we can ignore code when scanning for links/images/headings)
    for i, m in enumerate(fence_re.finditer(text), start=1):
        lang = (m.group(1) or '').strip()
        content = m.group(2).strip()
        report['fenced_blocks'].append({'file': str(path.relative_to(ROOT)), 'index': i, 'lang': lang, 'preview': content[:200]})

    # remove fenced code blocks from text for the remaining scans to avoid false positives
    text_no_code = fence_re.sub('\n', text)

    # images markdown
    for m in img_md_re.finditer(text_no_code):
        href = m.group(1).strip()
        report['images'].append({'file': str(path.relative_to(ROOT)), 'href': href})
        if is_local_link(href):
            target = (path.parent / href).resolve()
            if not target.exists():
                report['images_missing'].append({'file': str(path.relative_to(ROOT)), 'href': href, 'resolved': str(target)})
    # images html
    for m in img_html_re.finditer(text_no_code):
        href = m.group(1).strip()
        report['images'].append({'file': str(path.relative_to(ROOT)), 'href': href})
        if is_local_link(href):
            target = (path.parent / href).resolve()
            if not target.exists():
                report['images_missing'].append({'file': str(path.relative_to(ROOT)), 'href': href, 'resolved': str(target)})
    # links
    for m in link_re.finditer(text_no_code):
        href = m.group(1).strip()
        if is_local_link(href):
            report['local_links'].append({'file': str(path.relative_to(ROOT)), 'href': href})
            target = (path.parent / href).resolve()
            if not target.exists():
                report['local_links_missing'].append({'file': str(path.relative_to(ROOT)), 'href': href, 'resolved': str(target)})
    # headings
    for m in heading_re.finditer(text_no_code):
        level = len(m.group(1))
        title = m.group(2).strip()
        key = title
        report['headings'].setdefault(key, []).append({'file': str(path.relative_to(ROOT)), 'level': level})


def scan():
    md_files = list((ROOT).rglob('*.md'))
    # prefer book file first
    md_files = sorted(md_files)
    for md in md_files:
        scan_file(md)

    # dedupe headings
    report['duplicate_headings'] = {k: v for k, v in report['headings'].items() if len(v) > 1}

    # simple summary
    summary = []
    summary.append(f"Files scanned: {len(report['files_scanned'])}")
    summary.append(f"Fenced code blocks found: {len(report['fenced_blocks'])}")
    summary.append(f"Image references found: {len(report['images'])}, missing: {len(report['images_missing'])}")
    summary.append(f"Local links found: {len(report['local_links'])}, missing: {len(report['local_links_missing'])}")
    summary.append(f"Duplicate headings detected: {len(report['duplicate_headings'])}")

    # write outputs
    tools = ROOT / 'tools'
    tools.mkdir(exist_ok=True)
    (tools / 'inventory_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    (tools / 'inventory_summary.txt').write_text('\n'.join(summary) + '\n', encoding='utf-8')
    print('\n'.join(summary))

if __name__ == '__main__':
    scan()
