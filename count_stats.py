import re
import os

def count_stats(text):
    # 统计mermaid数量
    mermaid_count = len(re.findall(r'```mermaid', text))
    
    # 统计表格数量：每个以|开头的独立块
    table_lines = [line for line in text.split('\n') if line.strip().startswith('|')]
    table_count = 0
    in_table = False
    for line in table_lines:
        if line.strip() and not in_table:
            table_count += 1
            in_table = True
        elif not line.strip():
            in_table = False
    # 简化：每个|行算1，但实际是块
    # 为了简单，每个包含|的行算1，但用户说每个独立|表格算1表
    # 假设表格是连续的|行
    table_blocks = re.findall(r'(?:^\|.*\n?)+', text, re.MULTILINE)
    table_count = len(table_blocks)
    
    # 统计代码数量：```块（非mermaid）
    code_blocks = re.findall(r'```(?!mermaid)', text)
    code_count = len(code_blocks)
    
    # 纯文本字数：去除代码块、mermaid、表格
    # 去除```块
    text_no_code = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # 去除表格行
    text_no_table = re.sub(r'^\|.*$', '', text_no_code, flags=re.MULTILINE)
    # 去除空行和markdown标记
    # 字数：字符数
    word_count = len(text_no_table.replace('\n', '').replace(' ', '').replace('\t', ''))
    
    return word_count, mermaid_count, table_count, code_count

def main():
    file_path = r'e:\DONT_TOUCH\10M-2025-Testing\book\1225.2025.newbook.md'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 章节行号（从grep）
    chapters = [
        (1, 5),
        (2, 1777),
        (3, 2690),
        (4, 3335),
        (5, 3949),
        (6, 4428),
        (7, 5782),
        (8, 9785),
        (9, 12740),
        (10, 13032),
        (11, 13484),
        (13, 14284),
        (14, 14967),
        (15, 15489),
        (16, 20316),
        (17, 25799),
        (18, 27857),
        (19, 31978),
        (20, 32611),
        (21, 37474),
        (22, 37964),
    ]
    
    lines = content.split('\n')
    total_word = 0
    total_mermaid = 0
    total_table = 0
    total_code = 0
    
    part_stats = {}
    
    for i, (chap_num, start_line) in enumerate(chapters):
        end_line = chapters[i+1][1] - 1 if i+1 < len(chapters) else len(lines)
        chap_content = '\n'.join(lines[start_line-1:end_line])  # 1-based
        
        word, mermaid, table, code = count_stats(chap_content)
        
        # 确定篇
        if chap_num <= 3:
            part = 1
        elif chap_num <= 6:
            part = 2
        elif chap_num <= 9:
            part = 3
        elif chap_num <= 15:
            part = 4
        elif chap_num <= 20:
            part = 5
        elif chap_num <= 30:
            part = 6
        else:
            part = 7
        
        if part not in part_stats:
            part_stats[part] = {'word':0, 'mermaid':0, 'table':0, 'code':0, 'chapters':{}}
        
        part_stats[part]['word'] += word
        part_stats[part]['mermaid'] += mermaid
        part_stats[part]['table'] += table
        part_stats[part]['code'] += code
        part_stats[part]['chapters'][chap_num] = (word, mermaid, table, code)
        
        total_word += word
        total_mermaid += mermaid
        total_table += table
        total_code += code
    
    # 输出
    print(f"总字数：{total_word}")
    for part in sorted(part_stats.keys()):
        stats = part_stats[part]
        print(f"第{part}篇总字数：{stats['word']}")
        print(f"第{part}篇图片数：{stats['mermaid']}")
        print(f"第{part}篇表格数：{stats['table']}")
        print(f"第{part}篇代码数：{stats['code']}")
        for chap in sorted(stats['chapters'].keys()):
            w, m, t, c = stats['chapters'][chap]
            print(f"第{part}篇-第{chap}章总字数：{w}")
            print(f"第{part}篇-第{chap}章图片数：{m}")
            print(f"第{part}篇-第{chap}章表格数：{t}")
            print(f"第{part}篇-第{chap}章代码数：{c}")

if __name__ == "__main__":
    main()