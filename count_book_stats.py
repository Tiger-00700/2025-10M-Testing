import docx
from docx.shared import Inches
import re

def count_docx_content(file_path):
    """
    统计docx文件内容：
    - 总字数（图片算1，表格算1，代码块算1）
    - 图片个数
    - 表格数
    - 代码块数
    忽略所有锚点内容块（以>锚点名称:开头的块）
    """
    doc = docx.Document(file_path)

    total_chars = 0
    image_count = 0
    table_count = 0
    code_block_count = 0

    in_anchor_block = False
    anchor_pattern = re.compile(r'^>\s*锚点名称:')

    for para in doc.paragraphs:
        text = para.text.strip()

        # 检查是否是锚点块的开始
        if anchor_pattern.match(text):
            in_anchor_block = True
            continue

        # 如果在锚点块中，检查是否是锚点块的结束（空行或者非>开头的行）
        if in_anchor_block:
            if not text.startswith('>') and text != '':
                in_anchor_block = False
            else:
                continue  # 跳过锚点块内容

        # 跳过空行
        if not text:
            continue

        # 检查是否是代码块（使用Source Code样式）
        if para.style and para.style.name == 'Source Code':
            code_block_count += 1
            total_chars += 1  # 代码块算1字
            continue

        # 检查是否是代码块（备用方法：缩进或```标记）
        if text.startswith('    ') or text.startswith('\t') or '```' in text:
            code_block_count += 1
            total_chars += 1  # 代码块算1字
            continue

        # 统计普通文字
        total_chars += len(text)

    # 统计图片
    for rel in doc.part.rels:
        if "image" in doc.part.rels[rel].target_ref:
            image_count += 1
            total_chars += 1  # 图片算1字

    # 统计表格
    table_count = len(doc.tables)
    total_chars += table_count  # 表格算1字

    return {
        'total_chars': total_chars,
        'image_count': image_count,
        'table_count': table_count,
        'code_block_count': code_block_count
    }

if __name__ == "__main__":
    file_path = r"e:\DONT_TOUCH\10M-2025-Testing\1225全书定稿_perfectly_fixed.docx"
    result = count_docx_content(file_path)

    print("=== 书稿统计结果 ===")
    print(f"总字数: {result['total_chars']}")
    print(f"图片个数: {result['image_count']}")
    print(f"表格数: {result['table_count']}")
    print(f"代码块数: {result['code_block_count']}")