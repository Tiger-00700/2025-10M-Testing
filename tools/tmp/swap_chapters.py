# 交换第18章和第24章的内容
import re

def swap_chapters():
    # 第3篇文件（包含第18章 - 数据血缘治理）
    file3_path = r'e:\DONT_TOUCH\10M-2025-Testing\framework\第3篇-进阶篇-环境与数据治理.md'
    # 第4篇文件（包含第24章 - 可观测性）
    file4_path = r'e:\DONT_TOUCH\10M-2025-Testing\framework\第4篇-进阶篇-自动化、工具与可观测性.md'

    # 读取第3篇文件，提取第18章内容
    with open(file3_path, 'r', encoding='utf-8') as f:
        content3 = f.read()

    # 找到第18章的开始和结束
    chapter18_start = content3.find('### 第18章 数据血缘治理与元数据管理')
    # 找到下一章的开始作为结束
    next_chapter_match = re.search(r'^### 第\d+章', content3[chapter18_start+1:], re.MULTILINE)
    if next_chapter_match:
        chapter18_end = chapter18_start + next_chapter_match.start()
    else:
        chapter18_end = len(content3)

    chapter18_content = content3[chapter18_start:chapter18_end]

    # 读取第4篇文件，提取第24章内容
    with open(file4_path, 'r', encoding='utf-8') as f:
        content4 = f.read()

    # 找到第24章的开始和结束
    chapter24_start = content4.find('### 第24章 大数据系统可观测性与监控测试')
    # 找到下一章的开始作为结束
    next_chapter_match = re.search(r'^### 第\d+章', content4[chapter24_start+1:], re.MULTILINE)
    if next_chapter_match:
        chapter24_end = chapter24_start + next_chapter_match.start()
    else:
        chapter24_end = len(content4)

    chapter24_content = content4[chapter24_start:chapter24_end]

    # 交换内容
    new_content3 = content3[:chapter18_start] + chapter24_content.replace('### 第24章', '### 第18章') + content3[chapter18_end:]
    new_content4 = content4[:chapter24_start] + chapter18_content.replace('### 第18章', '### 第24章') + content4[chapter24_end:]

    # 写回文件
    with open(file3_path, 'w', encoding='utf-8') as f:
        f.write(new_content3)

    with open(file4_path, 'w', encoding='utf-8') as f:
        f.write(new_content4)

    print("Successfully swapped Chapter 18 and Chapter 24 content!")

if __name__ == '__main__':
    swap_chapters()