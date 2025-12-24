# 重新生成书籍以应用所有优化
import os
import glob
from datetime import datetime

def build_book():
    framework_dir = 'framework'
    output_file = 'book/1208.2025.newbook.update.md'

    # Get all framework files in order
    framework_files = sorted(glob.glob(os.path.join(framework_dir, '*.md')))

    # Start building the book
    book_content = []
    book_content.append('<!-- 自动生成：已按 /framework/ 目录顺序插入 第1篇～第8篇 的完整内容（{}）。来源：/framework/*.md -->\n'.format(datetime.now().strftime('%Y-%m-%d')))

    for i, framework_file in enumerate(framework_files, 1):
        print(f'Processing {framework_file}')

        # Add section marker
        book_content.append(f'\n<!-- BEGIN 第{i}篇 -->\n')

        # Read and add content
        with open(framework_file, 'r', encoding='utf-8') as f:
            content = f.read()
            book_content.append(content)

        # Add end marker
        book_content.append(f'\n<!-- END 第{i}篇 -->\n')

    # Add final note
    note = f'\n<!-- 自动化注记：已按 /framework/ 目录顺序插入第1篇～第8篇（{datetime.now().strftime("%Y-%m-%d")}）。下一步：运行验证脚本检查残留占位标记（如"12.16建议"）、移除任意"truncated"占位并修正重复段落，以及统计行数对比与生成 QA 报告。 -->\n'
    book_content.append(note)

    # Write the book
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(book_content))

    print(f'Book built successfully: {output_file}')

if __name__ == '__main__':
    build_book()