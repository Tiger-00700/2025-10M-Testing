#!/usr/bin/env python3
"""Build a consistency report comparing book references vs repository
contents for appendix files and examples directories (smoke scripts).

Inputs:
    - tools/appendix-link-report.json (from check_appendix_links.py)
    - book/1022.2025.book.md (for examples/ references)

Outputs:
    - tools/consistency-report.json
    - tools/consistency-report.txt

Conservative rules:
    - Treat appendix/.gitlab-ci.yml as satisfied if
        appendix/.gitlab-ci.yml.example exists.
    - Map references like "E/examples/<topic>/smoke.sh" to
        examples/<topic>/smoke.sh for existence checks.
    - Ignore code-fence and duplicates; de-duplicate results.

This script only reads and reports; it does not modify repository content.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
APPENDIX = ROOT / "appendix"
EXAMPLES = ROOT / "examples"

LINK_REPORT_JSON = TOOLS / "appendix-link-report.json"
BOOK_FILE = ROOT / "book" / "1022.2025.book.md"

# Configuration: skeleton detection
# Prefer an explicit marker file `.skeleton` inside examples/<topic>/ to mark a
# topic as a skeleton. Optionally fall back to filename heuristics when the
# marker is absent (README.md, smoke.sh, smoke.ps1 only).
USE_SKELETON_MARKER: bool = True
USE_SKELETON_HEURISTIC_FALLBACK: bool = True


def load_link_report(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def enum_files(base: Path) -> Set[Path]:
    files: Set[Path] = set()
    if not base.exists():
        return files
    for p in base.rglob("*"):
        if p.is_file():
            files.add(p)
    return files


def normalize_rel(p: Path) -> str:
    try:
        return p.relative_to(ROOT).as_posix()
    except Exception:
        return p.as_posix()


def parse_examples_refs(book_text: str) -> Set[str]:
    # Capture both E/examples/<topic> and examples/<topic>, with optional smoke.*
    refs: Set[str] = set()
    # topics (legacy E/examples/...)
    pat_topic = re.compile(r"\bE/examples/([A-Za-z0-9_\-]+)\b")
    for m in pat_topic.finditer(book_text):
        topic = m.group(1)
        refs.add(f"E/examples/{topic}")
    # smoke files (legacy E/examples/...)
    pat_smoke_legacy = re.compile(r"\bE/examples/([A-Za-z0-9_\-]+)/smoke\.(sh|ps1)\b")
    for m in pat_smoke_legacy.finditer(book_text):
        topic = m.group(1)
        ext = m.group(2)
        refs.add(f"E/examples/{topic}/smoke.{ext}")
    # topics (new examples/...)
    pat_topic_new = re.compile(r"\bexamples/([A-Za-z0-9_\-]+)\b")
    for m in pat_topic_new.finditer(book_text):
        topic = m.group(1)
        refs.add(f"examples/{topic}")
    # smoke files (new examples/...)
    pat_smoke_new = re.compile(r"\bexamples/([A-Za-z0-9_\-]+)/smoke\.(sh|ps1)\b")
    for m in pat_smoke_new.finditer(book_text):
        topic = m.group(1)
        ext = m.group(2)
        refs.add(f"examples/{topic}/smoke.{ext}")
    return refs


def map_examples_ref_to_repo(ref: str) -> Path:
    """Map book's E/examples/... or examples/... to repo path examples/..."""
    if ref.startswith("E/examples/"):
        tail = ref[len("E/examples/"):]
    elif ref.startswith("examples/"):
        tail = ref[len("examples/"):]
    else:
        return Path("")
    return EXAMPLES / tail


def main() -> int:
    report = load_link_report(LINK_REPORT_JSON)

    # Appendix referenced set from link report
    appendix_referenced: Set[str] = set()
    appendix_missing: Dict[str, Dict] = {}

    for ref in report.get("references", []):
        resolved = Path(ref.get("resolved", ""))
        exists = ref.get("exists", False)
        matched = ref.get("matched", "")
        # Only consider items that resolve under appendix
        try:
            resolved.relative_to(APPENDIX)
        except Exception:
            continue

        rel_norm = normalize_rel(resolved)
        appendix_referenced.add(rel_norm)

        if not exists:
            # Skip .gitlab-ci.yml when .example exists (treat as satisfied)
            gitlab_example = (APPENDIX / ".gitlab-ci.yml.example").exists()
            if resolved.name == ".gitlab-ci.yml" and gitlab_example:
                continue
            # For references of E/examples/... mapped into appendix,
            # we still count them as missing in appendix
            appendix_missing[rel_norm] = {
                "matched": matched,
                "resolved": rel_norm,
                "note": "Missing in appendix"
            }

    appendix_all_files = {normalize_rel(p) for p in enum_files(APPENDIX)}
    # Suppress known ignorable appendix files from reporting noise
    ignored_appendix_files = {
        "appendix/.gitlab-ci.yml.example",
    }
    appendix_all_files = {
        p for p in appendix_all_files if p not in ignored_appendix_files
    }
    appendix_unreferenced = sorted(list(appendix_all_files - appendix_referenced))

    # Examples referenced set from book
    book_text = BOOK_FILE.read_text(encoding="utf-8") if BOOK_FILE.exists() else ""
    examples_refs_raw = parse_examples_refs(book_text)

    examples_referenced_paths: Set[str] = set()
    examples_missing: Dict[str, Dict] = {}
    for r in examples_refs_raw:
        repo_path = map_examples_ref_to_repo(r)
        if not repo_path:
            continue
        rel = normalize_rel(repo_path)
        examples_referenced_paths.add(rel)
        if not repo_path.exists():
            examples_missing[rel] = {
                "matched": r,
                "resolved": rel,
                "note": "Missing in examples"
            }

    examples_all_files = {normalize_rel(p) for p in enum_files(EXAMPLES)}

    # Only compare directories and smoke scripts explicitly referenced
    # Derive directory-level topics from references and filesystem
    ref_topics = set()
    for r in examples_refs_raw:
        if r.startswith("E/examples/"):
            tail = r[len("E/examples/"):]
            topic = tail.split("/")[0]
            if topic:
                ref_topics.add(topic)
    fs_topics = set()
    for s in examples_all_files:
        if not s.startswith("examples/"):
            continue
        parts = s.split("/")
        if len(parts) >= 2:
            fs_topics.add(parts[1])

    examples_topics_missing = sorted(list(ref_topics - fs_topics))

    # Determine skeleton-only topics to suppress from unreferenced noise
    topic_files: Dict[str, Set[str]] = {}
    for s in examples_all_files:
        if not s.startswith("examples/"):
            continue
        parts = s.split("/")
        if len(parts) < 3:
            # examples/<topic> (directory itself not in files set)
            continue
        topic = parts[1]
        fname = parts[-1]
        topic_files.setdefault(topic, set()).add(fname)

    skeleton_allow = {"README.md", "smoke.sh", "smoke.ps1"}
    skeleton_topics: Set[str] = set()
    # Prefer marker-based detection
    if USE_SKELETON_MARKER:
        for t in set(topic_files.keys()):
            marker = EXAMPLES / t / ".skeleton"
            if marker.exists():
                skeleton_topics.add(t)
    # Optional heuristic fallback
    if USE_SKELETON_HEURISTIC_FALLBACK:
        for t, files in topic_files.items():
            if t in skeleton_topics:
                continue
            if files and files.issubset(skeleton_allow):
                skeleton_topics.add(t)

    # Compute unreferenced and suppress skeleton-only topics
    examples_unreferenced_files_all = sorted(
        list(examples_all_files - examples_referenced_paths)
    )
    def _is_suppressed(path: str) -> bool:
        if not path.startswith("examples/"):
            return False
        parts = path.split("/")
        if len(parts) < 3:
            return False
        topic = parts[1]
        return topic in skeleton_topics

    examples_unreferenced_files = []
    for p in examples_unreferenced_files_all:
        if not _is_suppressed(p):
            examples_unreferenced_files.append(p)

    out_json: dict[str, Any] = {
        "appendix": {
            "total_files": len(appendix_all_files),
            "referenced": len(appendix_referenced),
            "unreferenced_count": len(appendix_unreferenced),
            "unreferenced_samples": appendix_unreferenced[:30],
            "missing_count": len(appendix_missing),
            "missing": appendix_missing,
        },
        "examples": {
            "total_files": len(examples_all_files),
            "referenced_entities": sorted(list(examples_referenced_paths)),
            "missing_count": len(examples_missing),
            "missing": examples_missing,
            "missing_topics": examples_topics_missing,
            "skeleton_topics_count": len(skeleton_topics),
            "skeleton_topics": sorted(list(skeleton_topics)),
            "unreferenced_files_count": len(examples_unreferenced_files),
            "unreferenced_files_samples": examples_unreferenced_files[:30],
        }
    }

    TOOLS.mkdir(parents=True, exist_ok=True)
    json_path = TOOLS / "consistency-report.json"
    json_text = json.dumps(out_json, ensure_ascii=False, indent=2)
    json_path.write_text(json_text, encoding="utf-8")

    # Human-readable summary
    lines: List[str] = []
    lines.append("Appendix vs References:\n")
    lines.append(f"- Files present: {len(appendix_all_files)}")
    lines.append(f"- Referenced (unique): {len(appendix_referenced)}")
    lines.append(f"- Unreferenced: {len(appendix_unreferenced)} (showing up to 30)")
    for s in out_json["appendix"]["unreferenced_samples"]:
        lines.append(f"  * {s}")
    lines.append(f"- Missing referenced items: {len(appendix_missing)}")
    for k, v in list(appendix_missing.items())[:20]:
        lines.append(f"  ! {v['matched']} -> {k}")

    lines.append("\nExamples vs References:\n")
    lines.append(f"- Files present: {len(examples_all_files)}")
    lines.append(f"- Referenced paths: {len(examples_referenced_paths)}")
    lines.append(f"- Missing referenced: {len(examples_missing)}")
    for k, v in list(examples_missing.items())[:20]:
        lines.append(f"  ! {v['matched']} -> {k}")
    lines.append(f"- Missing topics (by directory): {len(examples_topics_missing)}")
    for t in examples_topics_missing:
        lines.append(f"  ! {t}")
    msg = "- Skeleton topics: " + str(len(skeleton_topics))
    msg += " (suppressed in Unreferenced)"
    lines.append(msg)
    for t in sorted(list(skeleton_topics))[:30]:
        lines.append(f"  ~ {t}")
    msg2 = "- Unreferenced files: " + str(len(examples_unreferenced_files))
    msg2 += " (showing up to 30)"
    lines.append(msg2)
    for s in out_json["examples"]["unreferenced_files_samples"]:
        lines.append(f"  * {s}")

    txt_path = TOOLS / "consistency-report.txt"
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Wrote tools/consistency-report.json and tools/consistency-report.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
