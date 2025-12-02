import re
from pathlib import Path


TARGET_FILE = Path('book') / '附录-课后思考练习题索引.md'


def replace_links(text: str) -> tuple[str, int]:
    # Match any markdown link whose URL targets ./1022.2025.newbook(.cleaned).md#...
    pattern = re.compile(r"\[[^\]]*\]\(\.\/1022\.2025\.newbook(?:\.cleaned)?\.md#[^)]+\)")
    replacement = "（跳转占位，待迁移到 1116/1130）"
    new_text, n = pattern.subn(replacement, text)
    return new_text, n


def main() -> int:
    if not TARGET_FILE.exists():
        print(f"ERROR: Target file not found: {TARGET_FILE}")
        return 2

    original = TARGET_FILE.read_text(encoding='utf-8')
    updated, count = replace_links(original)

    if count == 0:
        print("No matching links found; no changes made.")
        return 0

    TARGET_FILE.write_text(updated, encoding='utf-8', newline='\n')
    print(f"Patched {TARGET_FILE}: replaced {count} legacy links.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
