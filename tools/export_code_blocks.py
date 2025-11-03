import re
import ast
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book" / "1022.2025.newbook.md"
OUTDIR = ROOT / "examples" / "99_book_exports"

FENCE_RE = re.compile(r"^```([a-zA-Z0-9_+-]*)\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
PUNCT_RE = re.compile(r"[!\"#$%&'()*+,\./:;<=>?@\[\\\]^_`{|}~，。、《》？；：‘’“”（）【】·—…]+")

EXT_MAP = {
    "python": ".py",
    "py": ".py",
    "bash": ".sh",
    "sh": ".sh",
    "powershell": ".ps1",
    "ps1": ".ps1",
    "sql": ".sql",
    "json": ".json",
    "yaml": ".yml",
    "yml": ".yml",
    "java": ".java",
    "scala": ".scala",
}


def slugify(text: str) -> str:
    t = text.strip().lower()
    t = PUNCT_RE.sub('', t)
    t = re.sub(r"\s+", "-", t)
    t = re.sub(r"-{2,}", "-", t)
    return t


def load_lines(p: Path) -> List[str]:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n")


def _sanitize_python_lines(lines: List[str]) -> List[str]:
    """Convert obvious narrative/markdown lines inside python fences into comments.
    This protects against injected reading tips like "> 【阅读提示】…" or list bullets.
    """
    out: List[str] = []
    bullet_re = re.compile(r"^\s*([-*]|\d+\.)\s+")
    for ln in lines:
        stripped = ln.lstrip()
        # Quote blocks or callouts
        if stripped.startswith('>'):
            out.append('# ' + stripped.lstrip('> ').rstrip())
            continue
        # Lines containing full-width brackets often indicate narrative blocks
        if '【' in ln or '】' in ln:
            out.append('# ' + ln.strip())
            continue
        # Markdown bullets and numbered items
        if bullet_re.match(stripped):
            out.append('# ' + stripped)
            continue
        out.append(ln)
    return out


def export_blocks(lines: List[str]) -> Tuple[int, List[Path]]:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    # Clean previous exports to avoid stale files (e.g., .py -> .txt downgrades leaving old .py)
    for old in OUTDIR.glob('newbook__block*.*'):
        try:
            old.unlink()
        except Exception:
            pass
    idx = 1
    paths: List[Path] = []
    inside = False
    lang: Optional[str] = None
    buf: List[str] = []
    section: List[str] = []

    def next_name(lg: Optional[str]) -> Path:
        nonlocal idx
        ext = EXT_MAP.get((lg or '').lower(), '.txt')
        p = OUTDIR / f"newbook__block{idx:03d}{ext}"
        idx += 1
        return p

    def next_name_with_ext(ext: str) -> Path:
        nonlocal idx
        p = OUTDIR / f"newbook__block{idx:03d}{ext}"
        idx += 1
        return p

    for i, ln in enumerate(lines):
        m = HEADING_RE.match(ln)
        if m:
            # update section path (keep last up to 3 titles)
            title = m.group(2)
            level = len(m.group(1))
            if level == 2:
                section = [title]
            elif level in (3, 4):
                if len(section) == 0:
                    section = ["", title]
                else:
                    if len(section) == 1:
                        section.append(title)
                    else:
                        if level == 3:
                            section = [section[0], title]
                        else:
                            if len(section) == 2:
                                section.append(title)
                            else:
                                section[2] = title
        fm = FENCE_RE.match(ln)
        if fm and not inside:
            inside = True
            lang = fm.group(1) or None
            buf = []
            continue
        if inside:
            if ln.strip() == '```':
                # close fence
                chosen_ext = EXT_MAP.get((lang or '').lower(), '.txt')
                content_lines = buf
                # If python, sanitize narrative lines to comments
                if (lang or '').lower() in {"python", "py"}:
                    content_lines = _sanitize_python_lines(buf)
                    # If still invalid Python, downgrade to .txt to avoid parse errors downstream
                    src = "\n".join(content_lines)
                    try:
                        ast.parse(src)
                    except SyntaxError:
                        chosen_ext = '.txt'
                p = next_name_with_ext(chosen_ext)
                Path(p).write_text("\n".join(content_lines), encoding='utf-8')
                paths.append(p)
                inside = False
                lang = None
                buf = []
            else:
                buf.append(ln)
    return len(paths), paths


def main():
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    lines = load_lines(BOOK)
    n, paths = export_blocks(lines)
    print(f"Exported {n} code blocks to {OUTDIR}")

if __name__ == '__main__':
    main()
