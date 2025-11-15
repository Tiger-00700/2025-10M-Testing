#!/usr/bin/env python3
"""Convert simple inline HTML <a href="...">text</a> to Markdown links [text](url).

This tool is conservative:
- Only converts <a> tags that have an href attribute.
- Strips inner HTML tags inside the anchor text when converting.
- Leaves other <a> forms (no href, anchors with name/id, complex nested HTML) untouched.

Usage:
    python tools/formatting/convert_inline_html_links.py -i input.md -o output.md
"""
import argparse
import re
import html
from pathlib import Path


def convert_a_to_md(text: str) -> str:
    # Regex: match <a ... href=('|")URL\1 ...>INNER</a>
    # Use non-greedy matches to avoid overcapture.
    pattern = re.compile(r"<a\s+([^>]*?)href=(['\"])(.*?)\2([^>]*)>(.*?)</a>", re.IGNORECASE | re.DOTALL)

    def repl(m: re.Match) -> str:
        href = m.group(3).strip()
        inner = m.group(5).strip()
        # Remove any inner HTML tags inside the anchor text (conservative)
        inner_text = re.sub(r"<[^>]+>", "", inner)
        inner_text = html.unescape(inner_text)
        # If inner text is empty, fallback to URL as link text
        if not inner_text:
            inner_text = href
        # If href contains double quotes or parentheses, escape parentheses
        href = href.replace(')', '%29')
        return f"[{inner_text}]({href})"

    # Apply repeatedly until no change (to handle multiple anchors)
    prev = None
    out = text
    while prev != out:
        prev = out
        out = pattern.sub(repl, out)
    return out


def main():
    p = argparse.ArgumentParser(description="Convert inline <a href> HTML to Markdown links")
    p.add_argument("-i", "--input", required=True, help="Input markdown file")
    p.add_argument("-o", "--output", required=True, help="Output candidate markdown file")
    args = p.parse_args()

    inp = Path(args.input)
    outp = Path(args.output)
    if not inp.exists():
        print(f"Input file not found: {inp}")
        raise SystemExit(2)

    text = inp.read_text(encoding="utf-8")
    converted = convert_a_to_md(text)
    outp.write_text(converted, encoding="utf-8")
    print(f"Wrote candidate file: {outp}")


if __name__ == '__main__':
    main()
