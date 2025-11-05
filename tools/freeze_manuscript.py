import re
from pathlib import Path

CANONICAL = Path("book/1022.2025.newbook.augmented.md")
FROZEN = Path("book/1022.2025.newbook.augmented.frozen.md")

PATH_MAP = {
    "examples/03_env": "examples/03_environment",
    "examples\\03_env": "examples/03_environment",
}

ANCHOR_RE = re.compile(r"<a\s+id=\"([^\"]+)\"\s*>\s*</a>")


def load() -> str:
    return CANONICAL.read_text(encoding="utf-8", errors="ignore")


def normalize_paths(text: str) -> str:
    for k, v in PATH_MAP.items():
        text = text.replace(k, v)
    return text


def strip_provenance_everywhere(text: str) -> str:
    # Remove lines that are only provenance
    lines = []
    for ln in text.splitlines():
        if ln.strip().startswith("来自："):
            continue
        lines.append(ln)
    text = "\n".join(lines)
    # Remove inline provenance markers in headings or paragraphs: （来自：...） or (来自：...)
    text = re.sub(r"（来自：[^）]+）", "", text)
    text = re.sub(r"\(来自：[^\)]+\)", "", text)
    return text


def remove_scope_notes(text: str) -> str:
    # Remove scope-note markers comments
    text = text.replace("<!-- scope-note-start -->", "")
    text = text.replace("<!-- scope-note-end -->", "")
    return text


def fix_duplicate_anchors(text: str) -> str:
    seen = {}

    def repl(m: re.Match) -> str:
        aid = m.group(1)
        cnt = seen.get(aid, 0)
        seen[aid] = cnt + 1
        if cnt == 0:
            return m.group(0)
        return m.group(0).replace(f'"{aid}"', f'"{aid}-{cnt}"')

    return ANCHOR_RE.sub(repl, text)


def strip_placeholders(text: str) -> str:
    # Remove bare TODO/TO_FILL tags but keep content otherwise
    text = re.sub(r"\bTO_FILL\b", "", text)
    text = re.sub(r"\bTODO\b", "", text)
    return text


def tidy_whitespace(text: str) -> str:
    # Trim trailing spaces
    text = "\n".join(ln.rstrip() for ln in text.splitlines())
    # Collapse 3+ consecutive blank lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def main():
    src = load()
    out = src
    out = normalize_paths(out)
    out = strip_provenance_everywhere(out)
    out = remove_scope_notes(out)
    out = fix_duplicate_anchors(out)
    out = strip_placeholders(out)
    out = tidy_whitespace(out)

    FROZEN.write_text(out, encoding="utf-8")
    print(f"[OK] Frozen manuscript written: {FROZEN}")


if __name__ == "__main__":
    main()
