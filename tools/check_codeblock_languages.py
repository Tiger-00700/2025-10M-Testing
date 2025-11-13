"""Audit and optionally annotate unlabeled code fences in the cleaned book.

Usage:
    python tools/check_codeblock_languages.py            # dry-run, report only
        python tools/check_codeblock_languages.py --apply
            # write language labels where guessed

Heuristics (summary):
    - bash/sh: shebang or typical shell constructs
    - python: import/def/class, .py snippets
    - sql: common SQL keywords (SELECT/CREATE/INSERT/UPDATE)
    - yaml: starts with '---' or key: value patterns
    - json: starts with { or [ (basic detection)
    - powershell: 'param(', 'Write-Host', '$env:'
    - fallback: text

Writes a report under tools/reports/ and can update the book in-place
when --apply.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'book' / '1022.2025.newbook.cleaned.md'
REPORTS = ROOT / 'tools' / 'reports'

FENCE_OPEN_RE = re.compile(r'^```(\w+)?\s*$')
FENCE_CLOSE_RE = re.compile(r'^```\s*$')


def load_lines(p: Path) -> list[str]:
    txt = p.read_text(encoding='utf-8')
    txt = txt.replace('\r\n', '\n').replace('\r', '\n')
    return txt.split('\n')


def save_lines(p: Path, lines: list[str]):
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def guess_language(block_lines: list[str]) -> str:
    text = '\n'.join(block_lines)
    head = (block_lines[0] if block_lines else '').strip()
    if head.startswith('#!/usr/bin/env bash') or head.startswith('#!/bin/bash'):
        return 'bash'
    if ' set -e' in text:
        return 'bash'
    if re.search(r'\bimport\b|\bdef\b|\bclass\b|\bprint\(', text):
        return 'python'
    sql_pat = re.compile(
        r'\bSELECT\b|\bCREATE\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bWITH\b',
        re.IGNORECASE,
    )
    if sql_pat.search(text):
        return 'sql'
    if head.startswith('{') or head.startswith('['):
        return 'json'
    if head.startswith('---') or re.search(r'^\s*\w+\s*:', text, re.MULTILINE):
        return 'yaml'
    if re.search(r'\bWrite-Host\b|\$env:|\bparam\(', text):
        return 'powershell'
    return 'text'


def audit(lines: list[str]):
    i = 0
    findings = []
    n = len(lines)
    while i < n:
        m = FENCE_OPEN_RE.match(lines[i])
        if m:
            lang = m.group(1) or ''
            # collect block until closing fence
            j = i + 1
            block = []
            while j < n and not FENCE_CLOSE_RE.match(lines[j]):
                block.append(lines[j])
                j += 1
            # if no language, guess
            if not lang:
                guess = guess_language(block)
                findings.append((i, j, guess))  # open_idx, close_idx, guess
            i = j + 1
        else:
            i += 1
    return findings


def apply_annotations(lines: list[str], findings):
    # Apply from bottom to top to keep indices stable
    for open_idx, close_idx, guess in reversed(findings):
        lines[open_idx] = f'```{guess}'
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '--apply', action='store_true',
        help='Write guessed languages to unlabeled fences'
    )
    args = ap.parse_args()

    if not BOOK.exists():
        raise SystemExit(f'Book not found: {BOOK}')
    lines = load_lines(BOOK)
    findings = audit(lines)
    counts = {}
    for _, _, g in findings:
        counts[g] = counts.get(g, 0) + 1
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    REPORTS.mkdir(parents=True, exist_ok=True)
    rep_path = REPORTS / f'codeblock-language-audit-{ts}.md'
    rep_lines = [
        f'# Codeblock Language Audit ({ts})',
        '',
        f'Unlabeled code fences: {len(findings)}',
        'By guessed language:'
    ]
    for k in sorted(counts):
        rep_lines.append(f'- {k}: {counts[k]}')
    rep_lines.append('')
    # Include up to 10 samples
    for idx, (open_idx, close_idx, guess) in enumerate(findings[:10]):
        rep_lines.append(f'## sample[{idx}] lines {open_idx}-{close_idx} guess={guess}')
        snippet = '\n'.join(lines[open_idx: min(close_idx+1, open_idx+10)])
        rep_lines.append('```')
        rep_lines.append(snippet)
        rep_lines.append('```')
        rep_lines.append('')
    rep_path.write_text('\n'.join(rep_lines) + '\n', encoding='utf-8')
    print(f'Unlabeled fences={len(findings)} report={rep_path.name}')

    if args.apply and findings:
        new_lines = apply_annotations(lines, findings)
        save_lines(BOOK, new_lines)
        print('Applied language annotations to book.')


if __name__ == '__main__':
    main()
