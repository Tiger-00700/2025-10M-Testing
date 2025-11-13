import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional


"""
Merge selected sections and path/style fixes into the canonical manuscript.

Strategy (conservative, idempotent):
- Target file: book/1022.2025.newbook.augmented.md
- Sources: book/1022.2025.newbook.links.md, book/1030.2025.book.md
- Enrichments: known technology sections (Hadoop/Spark/Kafka/HBase/Presto) if source text is longer; else add a "补充说明" block appended to that section.
- Normalizations:
  * Normalize example paths (e.g., examples/03_env -> examples/03_environment)
  * Remove provenance markers lines starting with "来自：" and similar.

The script is intentionally lightweight (no external deps). It uses naive markdown heading parsing
that is robust enough for H2/H3-level merges.

It prints a short summary and writes a backup file with suffix .bak once before first write.
"""


CANONICAL = Path("book/1022.2025.newbook.augmented.md")
SRC_LINKS = Path("book/1022.2025.newbook.links.md")
SRC_1030 = Path("book/1030.2025.book.md")

# Headings to consider for content enrichment (case-insensitive substring match)
ENRICH_KEYS = ["Hadoop", "Spark", "Kafka", "HBase", "Presto"]

# Optional config file to force-merge specific titles
CONFIG_YML = Path("tools/merge_config.yml")

# Simple path normalization mapping (extend as needed)
PATH_MAP = {
    "examples/03_env": "examples/03_environment",
    "examples\\03_env": "examples/03_environment",
}


def load_text(p: Path) -> str:
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")


HEADING_RE = re.compile(r"^(#{2,3})\s+(.+)$", re.MULTILINE)


def split_by_heading(md: str):
    """Return list of (level, title, start_index, end_index)."""
    matches = list(HEADING_RE.finditer(md))
    blocks = []
    for i, m in enumerate(matches):
        level = len(m.group(1))
        title = m.group(2).strip()
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        blocks.append((level, title, start, end))
    return blocks


def build_title_index(md: str):
    idx: Dict[str, List[tuple[int,int,int]]] = {}
    for level, title, start, end in split_by_heading(md):
        idx.setdefault(title, []).append((level, start, end))
    return idx


def normalize_paths(text: str) -> str:
    for k, v in PATH_MAP.items():
        text = text.replace(k, v)
    return text


def strip_provenance(text: str) -> str:
    # Drop lines starting with provenance markers
    lines = text.splitlines()
    out = []
    for ln in lines:
        if ln.strip().startswith("来自："):
            continue
        out.append(ln)
    return "\n".join(out)


def find_section_text(md: str, title: str):
    idx = build_title_index(md)
    if title not in idx:
        return None
    # Prefer first occurrence
    level, start, end = idx[title][0]
    return md[start:end]


def best_source_section(src_texts, title):
    candidates = []
    for label, text in src_texts:
        sec = find_section_text(text, title)
        if sec:
            candidates.append((label, sec, len(sec)))
    if not candidates:
        return None
    # choose longest
    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates[0]  # (label, section_text, length)


def enrich_section(target_md: str, title: str, extra_block: str, source_label: str) -> str:
    # Append a "补充说明" sub-section (###) at the end of the target section
    blocks = split_by_heading(target_md)
    # locate section bounds
    for i, (level, t, start, end) in enumerate(blocks):
        if t == title:
            insertion_point = end
            break
    else:
        # Not found; append at end
        insertion_point = len(target_md)

    supplement = (
        f"\n\n### 补充说明（合并自：{source_label}）\n\n" + extra_block.strip() + "\n"
    )
    return target_md[:insertion_point] + supplement + target_md[insertion_point:]


def replace_section(md: str, title: str, new_section: str) -> str:
    """Replace the section with 'title' with 'new_section' (which should include its own heading).
    If the title does not exist, append at end.
    """
    blocks = split_by_heading(md)
    for i, (level, t, start, end) in enumerate(blocks):
        if t == title:
            return md[:start] + new_section.rstrip() + "\n\n" + md[end:]
    # Not found → append
    return md.rstrip() + "\n\n" + new_section.rstrip() + "\n"


ANCHOR_RE = re.compile(r"<a\s+id=\"([^\"]+)\"\s*>\s*</a>")


def fix_duplicate_anchors(text: str) -> str:
    seen: Dict[str, int] = {}

    def repl(m: re.Match) -> str:
        aid = m.group(1)
        cnt = seen.get(aid, 0)
        seen[aid] = cnt + 1
        if cnt == 0:
            return m.group(0)
        # suffix duplicates deterministically: -{cnt}
        return m.group(0).replace(f'"{aid}"', f'"{aid}-{cnt}"')

    return ANCHOR_RE.sub(repl, text)


def load_config() -> Dict[str, Any]:
    if not CONFIG_YML.exists():
        return {}
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    try:
        return yaml.safe_load(CONFIG_YML.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def main():
    canonical = load_text(CANONICAL)
    if not canonical:
        print(f"[WARN] Canonical manuscript not found: {CANONICAL}")
        sys.exit(0)

    links = load_text(SRC_LINKS)
    md1030 = load_text(SRC_1030)

    original = canonical

    # Normalize paths and strip provenance first
    canonical = normalize_paths(canonical)
    canonical = strip_provenance(canonical)

    srcs = []
    if links:
        srcs.append((SRC_LINKS.name, links))
    if md1030:
        # also normalize in sources to avoid path churn
        srcs.append((SRC_1030.name, normalize_paths(md1030)))

    # Build title indices
    tgt_idx = build_title_index(canonical)

    merged = canonical
    enrich_count = 0

    cfg = load_config()
    forced = cfg.get("forced", []) if isinstance(cfg, dict) else []
    # Build source dict for fast lookup
    src_map = {SRC_LINKS.name: links, SRC_1030.name: md1030}
    # Forced replacements (match by contains by default)
    for item in forced:
        try:
            title_pat: str = item.get("title")
            source_sel: str = (item.get("source") or "links").lower()
            match_by: str = (item.get("match_by") or "contains").lower()
        except Exception:
            continue

        if not title_pat:
            continue

        # Find target title
        target_title: Optional[str] = None
        for t in tgt_idx.keys():
            if (match_by == "exact" and t == title_pat) or (
                match_by != "exact" and title_pat.lower() in t.lower()
            ):
                target_title = t
                break
        if not target_title:
            continue

        # Choose source text
        src_label = SRC_LINKS.name if source_sel == "links" else SRC_1030.name
        src_text = src_map.get(src_label) or ""
        sec = find_section_text(src_text, target_title) or find_section_text(src_text, title_pat)
        if not sec:
            continue
        # Replace entire section
        merged = replace_section(merged, target_title, sec)

    # Heuristic enrichments where source is significantly longer
    tgt_idx = build_title_index(merged)
    for title in list(tgt_idx.keys()):
        # Only consider enrich keys
        if not any(k.lower() in title.lower() for k in ENRICH_KEYS):
            continue
        best = best_source_section(srcs, title)
        if not best:
            continue
        label, src_sec, _ = best
        tgt_sec = find_section_text(merged, title) or ""
        # If source section is significantly longer than target, append supplement
        if len(src_sec) > len(tgt_sec) * 1.25:
            merged = enrich_section(merged, title, src_sec, label)
            enrich_count += 1

    # De-duplicate anchors deterministically
    merged = fix_duplicate_anchors(merged)

    if merged != original:
        bak = CANONICAL.with_suffix(CANONICAL.suffix + ".bak")
        if not bak.exists():
            bak.write_text(original, encoding="utf-8")
        CANONICAL.write_text(merged, encoding="utf-8")
        print(f"[OK] Canonical updated. Enriched sections: {enrich_count}. Backup: {bak}")
    else:
        print("[OK] No changes applied (canonical already normalized and enriched).")


if __name__ == "__main__":
    main()
