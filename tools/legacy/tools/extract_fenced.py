#!/usr/bin/env python3
"""
Extract fenced code blocks from markdown files under the chapter directory into
appendix files and replace the blocks with relative links.

Runs in-place and commits changes to the current git branch.
"""
import re
import os
import sys
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / 'chapter'
APPENDIX_DIR = ROOT / 'appendix'

FENCE_RE = re.compile(r"^```\s*([^\n\r]*)?\r?\n(.*?)\r?\n```\s*$", re.MULTILINE | re.DOTALL)

EXT_MAP = {
    'python': 'py', 'py': 'py',
    'bash': 'sh', 'sh': 'sh', 'shell': 'sh',
    'yaml': 'yml', 'yml': 'yml', 'json': 'json',
    'text': 'txt', 'txt': 'txt', 'dockerfile': 'Dockerfile'
}


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or 'file'


def next_filename(base: Path) -> Path:
    if not base.exists():
        return base
    i = 1
    while True:
        candidate = base.with_name(f"{base.stem}-{i}{base.suffix}")
        if not candidate.exists():
            return candidate
        i += 1


def ensure_appendix():
    APPENDIX_DIR.mkdir(parents=True, exist_ok=True)


def extract_from_file(md_path: Path):
    text = md_path.read_text(encoding='utf-8')
    changed = False
    idx = 1
    def make_fname(lang, idx):
        ext = EXT_MAP.get(lang.lower(), None) if lang else None
        if ext is None:
            # fallback to lang name or txt
            if lang and re.match(r'^[a-zA-Z0-9_\-]+$', lang):
                ext = lang
            else:
                ext = 'txt'
        return ext

    def replace_block(match):
        nonlocal idx, changed
        lang = (match.group(1) or '').strip()
        content = match.group(2)
        stem = slugify(md_path.stem)
        ext = make_fname(lang, idx)
        filename = f"{stem}__block{idx}.{ext}"
        target = APPENDIX_DIR / filename
        target = next_filename(target)
        # write file
        target.write_text(content.rstrip() + "\n", encoding='utf-8')
        changed = True
        idx += 1
        # replace with link
        relpath = os.path.relpath(target, md_path.parent)
        # normalize backslashes to forward slashes for Markdown links
        normalized = relpath.replace('\\', '/')
        link = f"[脚本：{filename}]({normalized})"
        return link

    new_text = FENCE_RE.sub(replace_block, text)
    if changed:
        md_path.write_text(new_text, encoding='utf-8')
    return changed


def git_cmd(*args):
    return subprocess.check_output(['git'] + list(args), cwd=ROOT, shell=False).decode('utf-8', errors='ignore')


def main():
    ensure_appendix()
    md_files = sorted(CHAPTER_DIR.glob('*.md'))
    total_changed = 0
    for md in md_files:
        print('Processing', md.name)
        changed = extract_from_file(md)
        if changed:
            print('  -> updated and extracted blocks')
            total_changed += 1
    if total_changed == 0:
        print('No changes detected.')
        return 0
    # git add and commit
    try:
        git_cmd('add', 'appendix')
        git_cmd('add', 'chapter')
        git_cmd('commit', '-m', 'chore(appendix): extract fenced blocks from chapter/*.md into appendix')
        print('Committed changes to git branch.')
    except subprocess.CalledProcessError as e:
        print('Git command failed:', e)
        return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())
