"""Find highly similar section contents using a simple SimHash + Hamming threshold.

Heuristics:
- Parse headings (#..######). A section = heading + following lines until next heading of same or higher level.
- Compute SimHash (64-bit) over normalized tokens (lowercase, split on non-word, filter stop words, length>=2).
- Skip very short sections (< 50 tokens after filtering) and template titles (学习目标/小结/练习).
- Record path (stack of headings) for context.
- Use bucketization (LSH style) splitting 64 bits into 8 bands of 8 bits to pre-group candidates, then do exact Hamming distance <= 6 check.
- Output top pairs/groups sorted by similarity score (1 - hamming/64) descending, limited to first 200 pairs.

Output report: tools/reports/similar-sections-<ts>.md and a CSV alongside
"""

from __future__ import annotations

import re
from collections import defaultdict
import csv
from datetime import datetime, timezone
from pathlib import Path
from itertools import combinations

SRC = Path("book/1022.2025.newbook.augmented.frozen.md")
REPORT_DIR = Path("tools/reports")
MIN_TOKENS = 50
HAMMING_THRESHOLD = 6  # <= 6 differing bits (~90% similarity for 64-bit)
MAX_PAIRS = 200
SKIP_TITLES = {"学习目标", "小结", "练习"}

HEAD_RE = re.compile(r"^(?P<hash>#{1,6})\s+(?P<title>.*\S)\s*$")
TOKEN_RE = re.compile(r"[A-Za-z0-9_\u4e00-\u9fa5]+")

STOP = {"the","and","of","to","in","a","for","is","on","with","by","an","or","be","as","at","that","this","it"}


def parse_sections(text: str):
    lines = text.splitlines()
    stack: list[tuple[int,str]] = []  # (level,title)
    sections: list[dict] = []
    current = None
    for idx, raw in enumerate(lines, start=1):
        m = HEAD_RE.match(raw)
        if m:
            level = len(m.group("hash"))
            title = m.group("title").strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            if current:
                sections.append(current)
            current = {
                "line": idx,
                "level": level,
                "title": title,
                "path": " / ".join(t for _, t in stack),
                "content": []
            }
        else:
            if current:
                current["content"].append(raw)
    if current:
        sections.append(current)
    return sections


def tokenize(text: str):
    for t in TOKEN_RE.findall(text.lower()):
        if t in STOP:
            continue
        if len(t) < 2:
            continue
        yield t


def simhash(tokens):
    # 64-bit simhash
    v = [0]*64
    for tok in tokens:
        h = hash(tok) & 0xFFFFFFFFFFFFFFFF
        for i in range(64):
            bit = (h >> i) & 1
            v[i] += 1 if bit else -1
    out = 0
    for i, val in enumerate(v):
        if val > 0:
            out |= (1 << i)
    return out


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def lsh_buckets(sig: int, bands: int = 8, bits_per_band: int = 8):
    mask = (1 << bits_per_band) - 1
    for i in range(bands):
        yield (i, (sig >> (i*bits_per_band)) & mask)


def main():
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")
    text = SRC.read_text(encoding="utf-8")
    sections = parse_sections(text)

    enriched = []
    for s in sections:
        if s["title"] in SKIP_TITLES:
            continue
        tok_list = list(tokenize("\n".join(s["content"])))
        if len(tok_list) < MIN_TOKENS:
            continue
        sig = simhash(tok_list)
        s["tokens"] = len(tok_list)
        s["simhash"] = sig
        enriched.append(s)

    # LSH candidate grouping
    buckets = defaultdict(list)
    for idx, s in enumerate(enriched):
        for b in lsh_buckets(s["simhash"]):
            buckets[b].append(idx)

    seen_pairs = set()
    pairs = []  # (score, hamming, a_idx, b_idx)
    for bucket_indices in buckets.values():
        if len(bucket_indices) < 2:
            continue
        for a, b in combinations(bucket_indices, 2):
            if a > b:
                a, b = b, a
            key = (a, b)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            h = hamming(enriched[a]["simhash"], enriched[b]["simhash"])
            if h <= HAMMING_THRESHOLD:
                score = 1 - h/64
                pairs.append((score, h, a, b))

    pairs.sort(reverse=True)
    pairs = pairs[:MAX_PAIRS]

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report_lines = [f"# Similar Sections Report ({ts} UTC)", "", f"Source file: {SRC.as_posix()}"]
    report_lines.append(f"Total sections parsed: {len(sections)}")
    report_lines.append(f"Sections evaluated (after filters): {len(enriched)}")
    report_lines.append(f"Candidate similar pairs: {len(pairs)} (threshold hamming<={HAMMING_THRESHOLD})")
    report_lines.append("")
    report_lines.append("| Score | Hamming | A Line | A Path | B Line | B Path | A Tokens | B Tokens |")
    report_lines.append("|-------|---------|--------|--------|--------|--------|----------|----------|")
    for score, h, a_idx, b_idx in pairs:
        A = enriched[a_idx]
        B = enriched[b_idx]
        report_lines.append(
            f"| {score:.3f} | {h} | {A['line']} | {A['path']} | {B['line']} | {B['path']} | {A['tokens']} | {B['tokens']} |"
        )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts_simple = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out_md = REPORT_DIR / f"similar-sections-{ts_simple}.md"
    out_csv = REPORT_DIR / f"similar-sections-{ts_simple}.csv"
    out_md.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    # Write CSV for easier triage
    with out_csv.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(["score","hamming","a_line","a_path","b_line","b_path","a_tokens","b_tokens"])
        for score, h, a_idx, b_idx in pairs:
            A = enriched[a_idx]
            B = enriched[b_idx]
            writer.writerow([
                f"{score:.3f}", h, A['line'], A['path'], B['line'], B['path'], A['tokens'], B['tokens']
            ])

    print(f"Reports written: {out_md.as_posix()}, {out_csv.as_posix()}")


if __name__ == "__main__":
    main()
