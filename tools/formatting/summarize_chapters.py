#!/usr/bin/env python3
"""
简单的章节摘要生成器：
- 将 `book/1022.2025.newbook.cleaned.md` 按章节（以 '## ' 标题）拆分
- 为每章生成最多 3 条要点（基于章节开头的句子摘取）
- 输出到 `tools/optimization/phase2_patches/<slug>.md`

用法:
  python tools/formatting/summarize_chapters.py --input book/1022.2025.newbook.cleaned.md --outdir tools/optimization/phase2_patches
"""
import argparse
import os
import re
import io


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")[:120]


def split_sentences(text: str):
    # Split on Chinese and ASCII sentence punctuation
    parts = re.split(r'(?<=[。！？.!?])\s+', text.replace('\n', ' '))
    parts = [p.strip() for p in parts if p.strip()]
    return parts


def parse_markdown_by_chapter(path: str):
    chapters = []
    cur_title = None
    cur_lines = []
    with io.open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('## '):
                if cur_title:
                    chapters.append((cur_title, ''.join(cur_lines).strip()))
                cur_title = line.strip('# \n')
                cur_lines = []
            else:
                if cur_title is not None:
                    cur_lines.append(line)
    if cur_title:
        chapters.append((cur_title, ''.join(cur_lines).strip()))
    return chapters


def generate_summary_for_text(text: str, max_points=3):
    sents = split_sentences(text)
    if len(sents) >= max_points:
        points = sents[:max_points]
    else:
        # fallback: take first few non-empty lines
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        points = lines[:max_points]
    # normalize to single-line bullets
    bullets = []
    for p in points:
        p = re.sub(r'\s+', ' ', p)
        bullets.append(p.strip())
    return bullets


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--outdir', required=True)
    args = p.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    chapters = parse_markdown_by_chapter(args.input)
    if not chapters:
        print('未找到任何以 "## " 开头的章节，请检查输入文件。')
        return
    for title, body in chapters:
        slug = slugify(title)
        fname = os.path.join(args.outdir, f"{slug}.md")
        bullets = generate_summary_for_text(body, max_points=3)
        with io.open(fname, 'w', encoding='utf-8') as fo:
            fo.write(f"# {title}\n\n")
            fo.write("## 3 条要点草稿\n\n")
            for b in bullets:
                fo.write(f"- {b}\n")
            fo.write("\n---\n\n")
            fo.write("建议：对本章进行语言精简、添加 3 条要点小结与易错点说明。\n")
    print(f'已为 {len(chapters)} 个章节生成要点草稿，输出目录：{args.outdir}')


if __name__ == '__main__':
    main()
