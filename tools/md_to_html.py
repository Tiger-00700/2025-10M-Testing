import sys
from pathlib import Path

TEMPLATE = """<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
<meta charset=\"utf-8\" />
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
<title>{title}</title>
<style>
body{{max-width:900px;margin:2rem auto;padding:0 1rem;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,\"Noto Sans\",sans-serif;line-height:1.6;color:#222}}
h1,h2,h3,h4{{line-height:1.25}}
pre{{background:#f6f8fa;padding:1rem;overflow:auto}}
code{{background:#f6f8fa;padding:0 .2rem}}
.toc{{background:#fffbe6;border:1px solid #ffe58f;padding:1rem;margin:1rem 0}}
.toc ul{{list-style:disc;margin-left:1.25rem}}
a{{color:#0969da;text-decoration:none}}
a:hover{{text-decoration:underline}}
{extra_css}
</style>
</head>
<body>
<div class=\"toc\"><strong>目录</strong>{toc}</div>
{body}
</body>
</html>
"""

def main():
    try:
        import markdown
    except Exception as e:
        raise SystemExit("Missing dependency: markdown. Install with 'pip install markdown'.")
    if len(sys.argv) < 3:
        raise SystemExit("Usage: md_to_html.py <input.md> <output.html>")
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    text = src.read_text(encoding="utf-8", errors="ignore")
    md = markdown.Markdown(extensions=[
        'extra',
        'toc',
        'sane_lists',
        'tables',
        'fenced_code'
    ], extension_configs={
        'toc': {
            'toc_depth': '2-4',
            'permalink': True
        }
    })
    body = md.convert(text)
    toc = md.toc
    # Optionally embed external CSS from tools/templates/book.css
    extra_css = ""
    try:
        tpl_css = (Path(__file__).resolve().parent / 'templates' / 'book.css')
        if tpl_css.exists():
            css_raw = tpl_css.read_text(encoding='utf-8')
            # Escape braces to avoid str.format conflicts
            extra_css = css_raw.replace('{', '{{').replace('}', '}}')
    except Exception:
        extra_css = ""

    html = TEMPLATE.format(title=src.stem, toc=toc, body=body, extra_css=extra_css)
    dst.write_text(html, encoding="utf-8")
    print(f"[OK] HTML written: {dst}")

if __name__ == '__main__':
    main()
