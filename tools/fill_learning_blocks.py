
#!/usr/bin/env python3

"""
Auto-fill learning blocks (学习目标 / 小结 / 练习) for the entire
book with selectable style.

Default input:  book/1022.2025.newbook.augmented.frozen.md
Default output: book/1022.2025.newbook.filled.md
Report:         tools/reports/learning-blocks-fill-<ts>.md

Styles (via --style or LEARNING_BLOCK_STYLE env):
    academic  - 强调理论、方法论、严谨表述与评价框架
    industry  - 强调指标、落地、风险控制、ROI、合规与性能
    balanced  - 兼顾概念与实践（默认）

Flags:
    --input <path>   指定源文件
    --output <path>  指定输出文件
    --style <name>
    --rewrite        强制重写之前已注入的学习块（即便已有内容或非占位）

Rerun idempotency:
    注入内容包裹在 <!-- LEARNING-BLOCKS-BEGIN --> / <!-- LEARNING-BLOCKS-END -->
    若未使用 --rewrite：仅在“块缺失”或“检测为占位”时生成/替换
    使用 --rewrite：已注入的块也会重新生成（保留块标题行）

Exit code 0 on success; prints summary.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import re
import sys
import os
import argparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SRC = ROOT / 'book' / '1022.2025.newbook.augmented.frozen.md'
DEFAULT_OUT = ROOT / 'book' / '1022.2025.newbook.filled.md'
REPORTS = ROOT / 'tools' / 'reports'

HEADING_RE = re.compile(r'^(#{1,6})\s+(.*\S)\s*$')
SUBHEAD_TITLES = ['学习目标', '小结', '练习']
SUBHEAD_LEVEL = 5  # "#####"
BEGIN_MARK = '<!-- LEARNING-BLOCKS-BEGIN -->'
END_MARK = '<!-- LEARNING-BLOCKS-END -->'

CN_STOPS_TEXT = '''
本节
本章
本篇
本书
本文
章节
小结
练习
学习
目标
介绍
概述
定义
内容
与
及
和
或
以及
持续
性能
安全
数据
系统
方法
技术
工具
应用
案例
场景
流程
模型
架构
设计
分析
测试
大数据
平台
组件
相关
常见
问题
说明
参考
示例
实践
最佳
框架
质量
指标
管理
方案
策略
结构
目的
范围
背景
'''
CN_STOPS = set(CN_STOPS_TEXT.split())

KEYWORD_HINTS = {
    '性能': ['基线', '吞吐/延迟', '容量规划', '资源效率'],
    '安全': ['访问控制', '数据脱敏', '审计追踪', '合规策略'],
    '数据质量': ['完整性', '准确性', '一致性', '可追溯性'],
    '自动化': ['用例复用', '流水线集成', '可维护性', '稳定性监控'],
    '可观测性': ['指标/日志/追踪', '告警阈值', '根因分析', '噪声抑制'],
}

STYLE_PROFILES = {
    'academic': {
        'goal_suffix': '形成结构化知识图谱并能解释关键概念间的逻辑关系',
        'summary_method': '强调理论依据、方法适用边界与评价指标的选择原则',
        'exercise_extra': '设计一个对照实验或基准试验，列出变量控制、测量方法与统计指标',
    },
    'industry': {
        'goal_suffix': '能在生产场景制定最小可行实施方案与监控指标（KPI/SLO）',
        'summary_method': '突出落地路径、风险缓释策略与成本/性能的权衡要点',
        'exercise_extra': '输出一份上线前检查清单（含风险、回滚、监控与验收指标）',
    },
    'balanced': {
        'goal_suffix': '既理解概念与方法也能规划最小实操路径并度量效果',
        'summary_method': '综合概念/流程/指标与实践要点，兼顾理论与落地',
        'exercise_extra': '撰写一个改进建议方案，列出现状、目标、指标与迭代步骤',
    }
}


def uprint(s: str):
    try:
        sys.stdout.buffer.write((s + '\n').encode('utf-8'))
    except Exception:
        print(s)


def tokenize_cn(text: str) -> list[str]:
    # very light tokenizer:
    # - split by punctuation / whitespace
    # - keep token length >= 2
    # - filter digits-only tokens
    parts = re.split(r'[\s\-/_,;:：，、。！!？?（）()《》<>\[\]{}|]+', text)
    toks = []
    for p in parts:
        p = p.strip()
        if len(p) < 2:
            continue
        if p.isdigit():
            continue
        toks.append(p)
    return toks


def top_keywords(title: str, body_lines: list[str], k: int = 5) -> list[str]:
    # Use title + first 80 lines of section (favor bullet lines)
    sample = [title]
    bullets = [
        line
        for line in body_lines[:80]
        if line.strip().startswith(('-', '*'))
    ]
    sample.extend(bullets[:40])
    text = '\n'.join(sample)
    counts: dict[str, int] = {}
    for tok in tokenize_cn(text):
        if tok in CN_STOPS:
            continue
        counts[tok] = counts.get(tok, 0) + 1
    by_freq = sorted(counts.items(), key=lambda x: (-x[1], -len(x[0]), x[0]))
    return [w for w, _ in by_freq[:k]]


def detect_domain(title: str, keywords: list[str]) -> str | None:
    pool = set(tokenize_cn(title)) | set(keywords)
    for k in KEYWORD_HINTS.keys():
        if any(k in w for w in pool):
            return k
    return None


def gen_learning_goals(title: str, kw: list[str], style: str) -> list[str]:
    domain = detect_domain(title, kw)
    # split longer strings into smaller pieces to avoid E501 (line-too-long)
    s1 = (
        f"理解“{title}”的关键概念与边界，"
        "能用自己的话归纳 3–5 条要点"
    )
    s2 = (
        f"掌握“{title}”的核心流程/方法/指标，"
        "并在示例中正确应用"
    )
    bullets = [s1, s2]
    if domain and domain in KEYWORD_HINTS:
        hints = '、'.join(KEYWORD_HINTS[domain][:3])
        bullets.append(f"面向“{domain}”场景，能设计可量化的验收标准（如：{hints}）")
    else:
        bullets.append("能为实际项目设计最小可行的验收标准（数据/功能/性能/安全中至少一种），并给出样例")
    profile = STYLE_PROFILES.get(style, STYLE_PROFILES['balanced'])
    bullets.append(profile['goal_suffix'])
    return bullets


def gen_summary(title: str, kw: list[str], style: str) -> list[str]:
    top = ' / '.join(kw[:5]) if kw else title
    profile = STYLE_PROFILES.get(style, STYLE_PROFILES['balanced'])
    s_a = (
        f"本节要点（3–5 条）：围绕“{title}”梳理概念、"
        "流程、方法与指标"
    )
    s_b = f"关键词：{top}"
    s_c = (
        "易错点/反模式：结合团队现状列举 2–3 个常见问题，"
        "并给出纠正建议"
    )
    s_d = f"方法论/实践：{profile['summary_method']}"
    s_e = (
        "实践建议：从小处着手（样例/基线/自动化），"
        "建立指标闭环并持续改进"
    )
    return [s_a, s_b, s_c, s_d, s_e]


def gen_exercises(title: str, style: str) -> list[str]:
    profile = STYLE_PROFILES.get(style, STYLE_PROFILES['balanced'])
    ex_a = (
        f"场景化练习：结合你的项目，描述“{title}”的一个实践场景，"
        "给出输入/步骤/预期输出"
    )
    ex_b = (
        f"指标设计：为“{title}”设计 3 个可量化指标（含基线/阈值/采样频率），"
        "并说明采集方式"
    )
    ex_c = (
        f"风险与对策：列出 2–3 个与“{title}”相关的风险点，"
        "并给出可执行的缓解方案"
    )
    return [ex_a, ex_b, ex_c, profile['exercise_extra']]


def section_ranges(lines: list[str]):
    # yield (start_idx, end_idx_exclusive, level, title)
    idxs = []
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m:
            lvl = len(m.group(1))
            title = m.group(2).strip()
            idxs.append((i, lvl, title))
    for j, (start, lvl, title) in enumerate(idxs):
        end = idxs[j+1][0] if j+1 < len(idxs) else len(lines)
        yield start, end, lvl, title


def find_subhead_block(
    lines: list[str],
    sec_start: int,
    sec_end: int,
    name: str,
):
    # returns (exists, sh_start, sh_end).
    # If not exists: (False, insert_pos, insert_pos)
    # more directly: exactly SUBHEAD_LEVEL hashes
    pat = re.compile(rf'^#{SUBHEAD_LEVEL}\s+{re.escape(name)}\s*$', re.UNICODE)
    sh_positions = []
    for i in range(sec_start+1, sec_end):
        if pat.match(lines[i]):
            sh_positions.append(i)
    if not sh_positions:
        # insert at end-1 to keep trailing newline structure
        return (False, sec_end-1, sec_end-1)
    # block until next heading level <= SUBHEAD_LEVEL
    # or next same-level subhead
    sh_start = sh_positions[0]
    k = sh_start + 1
    while k < sec_end:
        if HEADING_RE.match(lines[k]):
            break
        k += 1
    return (True, sh_start, k)


def is_placeholder_block(content_lines: list[str]) -> bool:
    text = '\n'.join(line.strip() for line in content_lines if line.strip())
    if not text:
        return True
    placeholders = ['待补充', 'TODO', '请补充', '占位', 'placeholder']
    return any(p.lower() in text.lower() for p in placeholders)


def remove_existing_markers(
    lines: list[str],
    start: int,
    end: int,
) -> list[str]:
    # within [start, end), strip previous injected block markers if present
    out = []
    i = start
    while i < end:
        if lines[i].strip() == BEGIN_MARK:
            # skip until END_MARK
            j = i + 1
            while j < end and lines[j].strip() != END_MARK:
                j += 1
            if j < end:
                i = j + 1
                continue
        out.append(lines[i])
        i += 1
    return lines[:start] + out + lines[end:]


def fill_book(args):
    src = Path(args.input)
    out = Path(args.output)
    style = args.style
    rewrite = args.rewrite
    if not src.exists():
        raise SystemExit(f'Source not found: {src}')
    raw = src.read_text(encoding='utf-8')
    lines = raw.splitlines()

    updates = 0
    sec_count = 0
    new_lines = lines[:]

    # We will process sections from bottom to top to keep indices stable
    secs = list(section_ranges(new_lines))
    # Process in reverse so earlier section indices remain valid
    # after insertions
    for sec_start, sec_end, lvl, title in reversed(secs):
        if lvl < 2:
            continue  # skip H1 intro
        sec_count += 1
        body = new_lines[sec_start+1:sec_end]
        kw = top_keywords(title, body)
    # changed_this_section tracked previously but not used; omit to avoid F841
        # for each subhead
        for name in SUBHEAD_TITLES:
            exists, sh_start, sh_end = find_subhead_block(
                new_lines, sec_start, sec_end, name
            )
            if exists:
                # determine if block is placeholder-like;
                # content is between sh_start+1 and sh_end
                content = new_lines[sh_start+1:sh_end]
                already_injected = any(BEGIN_MARK in line for line in content)
                if (
                    not rewrite
                    and not is_placeholder_block(content)
                    and not already_injected
                ):
                    continue  # keep authored content
                # replace content region with generated
                new_new = []
                if name == '学习目标':
                    new_new = [BEGIN_MARK] + [
                        f'- {b}'
                        for b in gen_learning_goals(title, kw, style)
                    ] + [END_MARK]
                elif name == '小结':
                    new_new = [BEGIN_MARK] + [
                        f'- {b}'
                        for b in gen_summary(title, kw, style)
                    ] + [END_MARK]
                else:
                    new_new = [BEGIN_MARK] + [
                        f'1. {b}'
                        for b in gen_exercises(title, style)
                    ] + [END_MARK]
                new_lines = (
                    new_lines[:sh_start+1]
                    + new_new
                    + new_lines[sh_end:]
                )
                updates += 1
            else:
                # insert a new subhead with content at insert position
                insert_at = sh_start
                block = [f"{('#'*SUBHEAD_LEVEL)} {name}"]
                if name == '学习目标':
                    block += [BEGIN_MARK] + [
                        f'- {b}'
                        for b in gen_learning_goals(title, kw, style)
                    ] + [END_MARK]
                elif name == '小结':
                    block += [BEGIN_MARK] + [
                        f'- {b}'
                        for b in gen_summary(title, kw, style)
                    ] + [END_MARK]
                else:
                    block += [BEGIN_MARK] + [
                        f'1. {b}'
                        for b in gen_exercises(title, style)
                    ] + [END_MARK]
                new_lines = (
                    new_lines[:insert_at]
                    + block
                    + new_lines[insert_at:]
                )
                updates += 1
    # refresh section boundaries after modifications
    # No need to recompute section ranges due to reverse-order insertion
    # strategy

    out.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    REPORTS.mkdir(parents=True, exist_ok=True)
    rep = REPORTS / f'learning-blocks-fill-{ts}.md'
    rep.write_text(
        (
            f'# Fill learning blocks report\n\n'
            f'Style: {style}\n'
            f'Rewrite: {rewrite}\n'
            f'Sections processed: {sec_count}\n'
            f'Blocks updated/inserted: {updates}\n'
            f'Output: {out.name}\n'
            f'Source: {src.name}\n'
        ),
        encoding='utf-8'
    )
    msg = (
        f'Filled learning blocks -> {out.as_posix()} | '
        f'style={style} rewrite={rewrite} | '
        f'sections={sec_count} updates={updates} | '
        f'Report: {rep.name}'
    )
    uprint(msg)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description='Fill 学习目标/小结/练习 blocks for book sections.'
    )
    ap.add_argument(
        '--input',
        default=os.environ.get('LEARNING_BLOCK_INPUT', str(DEFAULT_SRC)),
    )
    ap.add_argument(
        '--output',
        default=os.environ.get('LEARNING_BLOCK_OUTPUT', str(DEFAULT_OUT)),
    )
    ap.add_argument(
        '--style',
        choices=['academic', 'industry', 'balanced'],
        default=os.environ.get('LEARNING_BLOCK_STYLE', 'balanced'),
    )
    ap.add_argument(
        '--rewrite',
        action='store_true',
        default=os.environ.get('LEARNING_BLOCK_REWRITE', '0') == '1',
    )
    return ap.parse_args(argv)


if __name__ == '__main__':
    args = parse_args()
    fill_book(args)
