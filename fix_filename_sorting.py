import os
import re

def fix_filename_sorting():
    """修复文件名排序问题，确保章节按数字顺序排列"""
    chapter_new_dir = 'chapter-new'

    # 第2篇需要重新排序的文件
    part2_files = [
        ("第2篇-第6章.md", "第2篇-第06章.md"),
        ("第2篇-第7章.md", "第2篇-第07章.md"),
        ("第2篇-第8章.md", "第2篇-第08章.md"),
        ("第2篇-第9章.md", "第2篇-第09章.md"),
        ("第2篇-第10章.md", "第2篇-第10章.md"),  # 这个已经是两位数，不需要改
        ("第2篇-第11章.md", "第2篇-第11章.md"),  # 这个已经是两位数，不需要改
    ]

    print("修复第2篇文件名排序...")

    # 重命名文件
    for old_name, new_name in part2_files:
        if old_name != new_name:  # 只重命名需要改的文件
            old_path = os.path.join(chapter_new_dir, old_name)
            new_path = os.path.join(chapter_new_dir, new_name)

            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                print(f"重命名: {old_name} -> {new_name}")
            else:
                print(f"文件不存在: {old_name}")

    # 验证结果
    print("\n验证第2篇文件顺序:")
    part2_files_final = []
    for filename in sorted(os.listdir(chapter_new_dir)):
        if filename.startswith("第2篇-"):
            part2_files_final.append(filename)

    part2_files_final.sort()
    for filename in part2_files_final:
        print(f"  {filename}")

if __name__ == "__main__":
    fix_filename_sorting()