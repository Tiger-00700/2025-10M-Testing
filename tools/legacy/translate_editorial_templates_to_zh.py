#!/usr/bin/env python3
"""Translate editorial templates (appendix-missing) and index into Chinese (zh).
Reads: tools/editorial-issues/appendix-missing-*.md and appendix-missing-index.md
Writes: same dirname with .zh.md appended: appendix-missing-01.zh.md, appendix-missing-index.zh.md
This is a conservative, rule-based translator (no external service).
"""
from pathlib import Path
import re

DIR = Path('tools') / 'editorial-issues'
if not DIR.exists():
    print('editorial-issues dir not found:', DIR)
    raise SystemExit(1)

files = sorted(DIR.glob('appendix-missing-*.md'))
# include index
index = DIR / 'appendix-missing-index.md'
if index.exists():
    files.insert(0, index)

replacements = [
    (r"title:\s*'Appendix missing:\s*(.+)'", r"title: '附录缺失：\1'"),
    (r"## Source", "## 来源"),
    (r"## Context", "## 上下文"),
    (r"## Suggested action checklist", "## 建议操作清单"),
    (r"- \[ \] Confirm whether the referenced appendix file should exist in `appendix/`\.", "- [ ] 确认引用的附录文件是否应存在于 `appendix/`。"),
    (r"- Candidate\(s\) discovered in repository \(please confirm\):", "- 在仓库中发现的候选文件（请确认）："),
    (r"- No candidate files found automatically; please provide the intended target or remove/update reference\.", "- 未自动发现候选文件；请提供目标文件或移除/更新引用。"),
    (r"## Notes for editor", "## 编辑备注"),
    (r"- If the intended target exists under a different path, update the markdown to use a relative path from the source file \(example: `../appendix/<file>`\)\.", "- 如果目标在不同路径，请使用从源文件出发的相对路径（例如 `../appendix/<file>`）更新引用。"),
    (r"- If the file is missing, either add it to `appendix/` or change the reference to a correct location\.", "- 如果文件缺失，请把文件添加到 `appendix/` 或把引用改到正确位置。"),
    (r"- If this is a published external URL, consider replacing with the full URL\.", "- 如果这是外部已发布的链接，考虑直接替换为完整 URL。"),
    (r"This index lists editorial templates for appendix references that could not be resolved automatically\.", "该索引列出自动未能解析的附录引用的编辑模板。"),
    (r"Each entry links to the template for editorial action\.", "每项均链接至对应的编辑模板以供处理。"),
]

for p in files:
    txt = p.read_text(encoding='utf-8')
    out = txt
    # Apply common replacements
    for pat, rep in replacements:
        out = re.sub(pat, rep, out)
    # Additional gentle translations for common phrases
    out = out.replace('Context:', '上下文:')
    out = out.replace('Source', '来源')
    out = out.replace('line', '行')
    out = out.replace('Context', '上下文')
    out = out.replace('Title', '标题')
    # frontmatter label translation (keep original labels but add zh labels line)
    out = re.sub(r"labels:\s*(.+)\n", lambda m: f"labels: {m.group(1)}\nlabels_zh: 编辑, 附录, 缺失\n", out, count=1)

    # filename
    if p.name == 'appendix-missing-index.md':
        target = DIR / 'appendix-missing-index.zh.md'
    else:
        target = DIR / (p.stem + '.zh.md')
    target.write_text(out, encoding='utf-8')
    print('Wrote', target)

print('Translation complete: {} files'.format(len(files)))
