from pathlib import Path
import re
import textwrap
import sys


def _cjk_chunk(text: str, width: int) -> str:
    # Fallback for long CJK lines without spaces
    return '\n'.join(text[i:i+width] for i in range(0, len(text), width))


def wrap_shell_command(cmd: str, width: int) -> str:
    # Wrap a shell command by breaking at spaces and adding line continuations
    tokens = re.split(r'\s+', cmd.strip())
    if not tokens:
        return cmd
    lines = []
    current = ''
    for tok in tokens:
        proposed = (current + ' ' + tok) if current else tok
        # Reserve 2 chars for line continuation on non-final lines
        if len(proposed) <= (width - 2):
            current = proposed
        else:
            if current:
                lines.append(current + ' \\')
                current = tok
            else:
                # single token longer than width, hard chunk it
                chunks = _cjk_chunk(tok, width - 2).split('\n')
                for i, ch in enumerate(chunks):
                    if i < len(chunks) - 1:
                        lines.append(ch + ' \\')
                    else:
                        current = ch
    if current:
        lines.append(current)
    # indent continuation lines for readability
    if len(lines) > 1:
        lines = [lines[0]] + [('  ' + ln if not ln.startswith('  ') else ln) for ln in lines[1:]]
    return '\n'.join(lines)


def wrap_paragraph(text: str, width: int, indent: int = 0) -> str:
    t = text.strip()
    if ((" " not in t) and re.search(r'[\u4e00-\u9fff]', t)):
        wrapped = _cjk_chunk(t, width)
    else:
        wrapped = textwrap.fill(t, width=width)
        # If still too long (e.g., no spaces), fallback to hard chunking
        if any(len(ln) > width for ln in wrapped.split('\n')):
            wrapped = _cjk_chunk(t, width)
    return '\n'.join((' ' * indent) + ln for ln in wrapped.split('\n'))


def wrap_with_prefix(prefix: str, text: str, width: int) -> str:
    # Ensure subsequent lines align after the prefix
    t = text.strip()
    subsequent = ' ' * len(prefix)
    if ((" " not in t) and re.search(r'[\u4e00-\u9fff]', t)):
        # CJK fallback: chunk, then add prefixes
        chunks = _cjk_chunk(t, width - len(prefix)).split('\n')
        lines = []
        for i, ch in enumerate(chunks):
            if i == 0:
                lines.append(prefix + ch)
            else:
                lines.append(subsequent + ch)
        return '\n'.join(lines)
    wrapped = textwrap.fill(t, width=width, initial_indent=prefix, subsequent_indent=subsequent)
    if any(len(ln) > width for ln in wrapped.split('\n')):
        chunks = _cjk_chunk(t, width - len(prefix)).split('\n')
        lines = []
        for i, ch in enumerate(chunks):
            if i == 0:
                lines.append(prefix + ch)
            else:
                lines.append(subsequent + ch)
        return '\n'.join(lines)
    return wrapped


def wrap_file(path):
    p = Path(path)
    s = p.read_text(encoding='utf8')
    lines = s.splitlines()
    out = []
    in_code = False
    code_lang = None
    fence_indent = 0
    for L in lines:
        if L.strip().startswith('```'):
            fence = L.strip()
            if not in_code:
                m_lang = re.match(r'^```\s*([a-zA-Z0-9_+-]+)?', fence)
                code_lang = m_lang.group(1).lower() if (m_lang and m_lang.group(1)) else None
                fence_indent = len(L) - len(L.lstrip(' '))
                # MD040: add default language if missing
                if code_lang is None:
                    L = (' ' * fence_indent) + '```text'
                    code_lang = 'text'
                in_code = True
            else:
                in_code = False
                code_lang = None
                fence_indent = 0
            out.append(L)
            continue
        if in_code:
            orig_leading = re.match(r'^\s*', L).group(0)
            enforced_leading = ' ' * max(fence_indent, len(orig_leading))
            if code_lang in ('bash', 'sh') and len(L) > 80 and not L.strip().startswith('#'):
                # wrap shell commands with line continuations, preserving leading indentation
                stripped = L.strip()
                available = 80 - len(enforced_leading)
                wrapped_cmd = wrap_shell_command(stripped, available)
                for wline in wrapped_cmd.split('\n'):
                    out.append(enforced_leading + wline)
                continue
            # ensure enforced indentation for other code lines
            if L.startswith(enforced_leading) or L.strip() == '':
                out.append(L)
            else:
                out.append(enforced_leading + L.lstrip(' '))
            continue
        if L.strip().startswith('|'):
            out.append(L)
            continue

        # Headings: try not to break heading, but if too long and contains a trailing note like （来自：...）
        m_h = re.match(r'^(#{1,6}\s+)(.+)$', L)
        if m_h:
            prefix, text = m_h.group(1), m_h.group(2)
            # If heading包含来源注记（来自：...），无论长度，拆分为标题行 + 下一段注记
            if ('（' in text and '）' in text and '来自' in text) or (len(L) > 80 and '（' in text and '）' in text):
                # split at first Chinese left parenthesis
                idx = text.find('（')
                head_text = text[:idx].rstrip()
                note_text = text[idx:].rstrip()
                out.append(f"{prefix}{head_text}")
                # ensure blank line after heading
                out.append("")
                out.append(note_text)
                continue
            out.append(L)
            continue

        # Blockquote
        m_q = re.match(r'^(\s*>+\s+)(.+)$', L)
        if m_q and len(L) > 80:
            out.append(wrap_with_prefix(m_q.group(1), m_q.group(2), 80))
            continue

        # List item (unordered or ordered)
        m_li = re.match(r'^(\s*(?:[-*+]|\d+\.)\s+)(.+)$', L)
        if m_li and len(L) > 80:
            out.append(wrap_with_prefix(m_li.group(1), m_li.group(2), 80))
            continue

        # Normal paragraph
        # Normal paragraph (skip link-dense lines)
        if len(L) > 80 and L.strip() != '':
            # Heuristic: skip wrapping if link-dense or many URLs
            url_count = len(re.findall(r'https?://', L))
            mdlink_count = len(re.findall(r'\[[^\]]*\]\([^\)]*\)', L))
            if (url_count + mdlink_count) >= 2:
                out.append(L)
                continue
            indent = len(L) - len(L.lstrip(' '))
            out.append(wrap_paragraph(L, width=80, indent=indent))
        else:
            out.append(L)

    # Ensure blank lines around headings (MD022)
    # First, convert emphasis-only lines (e.g., **标题**) into proper headings based on context
    out_emph = []
    in_code_e = False
    in_html_e = False
    last_heading_level = 0
    last_emph_level = None
    for i, L in enumerate(out):
        if L.strip().startswith('```'):
            in_code_e = not in_code_e
            out_emph.append(L)
            continue
        if in_code_e:
            out_emph.append(L)
            continue
        # Track HTML comment blocks
        if not in_html_e and '<!--' in L:
            start = L.find('<!--')
            end = L.find('-->')
            if end == -1 or end < start:
                in_html_e = True
        elif in_html_e and '-->' in L:
            in_html_e = False
        m_head = re.match(r'^(#{1,6})\s+(.+)$', L)
        if m_head and not in_html_e:
            last_heading_level = len(m_head.group(1))
            last_emph_level = None
            out_emph.append(L)
            continue
        # Bold-only line to be treated as a heading (avoid list/code/blockquote prefixes)
        if (not in_html_e and re.match(r'^\s*\*\*(.+?)\*\*\s*$', L)
                and not re.match(r'^\s*(?:[-*+]|\d+\.)\s+', L)
                and not L.strip().startswith('>')):
            text = re.sub(r'^\s*\*\*(.+?)\*\*\s*$', r'\1', L)
            base_level = last_heading_level + 1 if last_heading_level > 0 else 2
            level = last_emph_level if last_emph_level is not None else base_level
            if level > 6:
                level = 6
            out_emph.append('#' * level + ' ' + text)
            last_heading_level = level
            last_emph_level = level
            continue
        out_emph.append(L)

    # Normalize heading level increments (MD001): do not jump by >1 level
    out_norm = []
    in_code_n = False
    in_html_n = False
    last_level = 0
    for L in out_emph:
        if L.strip().startswith('```'):
            in_code_n = not in_code_n
            out_norm.append(L)
            continue
        if in_code_n:
            out_norm.append(L)
            continue
        # Track HTML comment blocks
        if not in_html_n and '<!--' in L:
            start = L.find('<!--')
            end = L.find('-->')
            if end == -1 or end < start:
                in_html_n = True
        elif in_html_n and '-->' in L:
            in_html_n = False
        m = re.match(r'^(#{1,6})(\s+)(.+)$', L)
        if m and not in_html_n:
            hashes, space, text = m.groups()
            level = len(hashes)
            if last_level > 0 and level > last_level + 1:
                level = last_level + 1
                L = ('#' * level) + space + text
            last_level = level
            out_norm.append(L)
        else:
            out_norm.append(L)

    out2 = []
    in_code2 = False
    in_html2 = False
    for i, L in enumerate(out_norm):
        if L.strip().startswith('```'):
            in_code2 = not in_code2
            out2.append(L)
            continue
        if in_code2:
            out2.append(L)
            continue
        # Track HTML comment blocks
        if not in_html2 and '<!--' in L:
            start = L.find('<!--')
            end = L.find('-->')
            if end == -1 or end < start:
                in_html2 = True
        elif in_html2 and '-->' in L:
            in_html2 = False
        is_heading = bool(re.match(r'^#{1,6}\s+', L))
        if is_heading and not in_html2:
            if out2 and out2[-1].strip() != '':
                out2.append('')
            out2.append(L)
            # lookahead for next line to decide on blank line below
            nxt = out_norm[i+1] if i + 1 < len(out_norm) else ''
            if nxt.strip() != '':
                out2.append('')
            continue
        out2.append(L)

    # Deduplicate headings (MD024): append a small suffix to repeated headings
    dedup = []
    seen = {}
    in_code3 = False
    in_html3 = False
    for L in out2:
        if L.strip().startswith('```'):
            in_code3 = not in_code3
            dedup.append(L)
            continue
        if in_code3:
            dedup.append(L)
            continue
        # Track HTML comment blocks
        if not in_html3 and '<!--' in L:
            start = L.find('<!--')
            end = L.find('-->')
            if end == -1 or end < start:
                in_html3 = True
        elif in_html3 and '-->' in L:
            in_html3 = False
        m = re.match(r'^(#{1,6}\s+)(.+)$', L)
        if m and not in_html3:
            prefix, content = m.group(1), m.group(2)
            cnt = seen.get(content, 0)
            if cnt == 0:
                seen[content] = 1
                dedup.append(L)
            else:
                seen[content] = cnt + 1
                dedup.append(f"{prefix}{content}（续{cnt}）")
            continue
        dedup.append(L)

    # Coalesce orphaned ordered list markers like "1." with following content line
    coalesced = []
    i = 0
    n = len(dedup)
    in_code_orphan = False
    while i < n:
        L = dedup[i]
        if L.strip().startswith('```'):
            in_code_orphan = not in_code_orphan
            coalesced.append(L)
            i += 1
            continue
        if in_code_orphan:
            coalesced.append(L)
            i += 1
            continue
        m_orphan = re.match(r'^(\s*)(\d+)\.\s*$', L)
        if m_orphan:
            nxt = dedup[i+1] if i + 1 < n else ''
            if nxt.strip() != '':
                indent = m_orphan.group(1)
                num = m_orphan.group(2)
                coalesced.append(f"{indent}{num}. {nxt.strip()}")
                i += 2
                continue
        coalesced.append(L)
        i += 1

    # Fix ordered list numbering (MD029) and ensure blank lines around lists (MD032)
    list_fixed = []
    i = 0
    n = len(coalesced)
    in_code4 = False
    while i < n:
        L = coalesced[i]
        if L.strip().startswith('```'):
            in_code4 = not in_code4
            list_fixed.append(L)
            i += 1
            continue
        if in_code4:
            list_fixed.append(L)
            i += 1
            continue

        m = re.match(r'^(\s*)(\d+)\.\s+(.*)$', L)
        if m:
            block_start = i
            indent = m.group(1)
            items = []
            while i < n:
                L2 = coalesced[i]
                m2 = re.match(r'^(\s*)(\d+)\.\s+(.*)$', L2)
                if m2 and m2.group(1) == indent:
                    items.append(m2)
                    i += 1
                else:
                    break
            # ensure blank line above list block
            if list_fixed and list_fixed[-1].strip() != '':
                list_fixed.append('')
            # renumber sequentially starting at 1
            for idx, mitem in enumerate(items, start=1):
                list_fixed.append(f"{indent}{idx}. {mitem.group(3)}")
            # ensure blank line after list block if next line is non-blank and not another list with less indent
            nxt = coalesced[i] if i < n else ''
            if nxt.strip() != '':
                list_fixed.append('')
            continue
        else:
            list_fixed.append(L)
            i += 1

    new = '\n'.join(list_fixed)
    if s.endswith('\n'):
        new += '\n'
    p.write_text(new, encoding='utf8')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: wrap_long_lines.py <file>')
        raise SystemExit(2)
    wrap_file(sys.argv[1])
