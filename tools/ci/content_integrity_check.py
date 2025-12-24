#!/usr/bin/env python3
"""
内容完整性验证脚本
验证framework目录下的篇章文档是否包含了所有相应的章节内容
"""

import os
import re
from pathlib import Path

# 项目根目录
REPO_ROOT = Path(__file__).parent.parent.parent

# 期望的篇章结构
EXPECTED_STRUCTURE = {
    "第1篇-大数据测试基础.md": list(range(1, 6)),  # 第1-5章
    "第2篇-大数据测试方法与技术.md": list(range(6, 12)),  # 第6-11章
    "第3篇-环境与工程化.md": list(range(12, 17)),  # 第12-16章
    "第4篇-测试案例与性能优化.md": list(range(17, 21)),  # 第17-20章
    "第5篇-项目实施与运维.md": list(range(21, 26)),  # 第21-25章
    "第6篇-质量保障与平台治理.md": list(range(26, 31)),  # 第26-30章
    "第7篇-趋势与未来发展.md": list(range(31, 35)),  # 第31-34章
}

def check_framework_files():
    """检查framework目录下的文件"""
    framework_dir = REPO_ROOT / "framework"
    if not framework_dir.exists():
        print(f"❌ framework目录不存在: {framework_dir}")
        return False

    existing_files = list(framework_dir.glob("*.md"))
    existing_names = {f.name for f in existing_files}

    expected_names = set(EXPECTED_STRUCTURE.keys())

    missing_files = expected_names - existing_names
    extra_files = existing_names - expected_names

    if missing_files:
        print(f"❌ 缺少以下framework文件: {missing_files}")
        return False

    if extra_files:
        print(f"⚠️  发现额外framework文件: {extra_files}")

    print(f"✅ framework目录检查通过，共{len(existing_files)}个文件")
    return True

def check_chapter_content():
    """检查每篇文档是否包含了相应的章节"""
    framework_dir = REPO_ROOT / "framework"
    all_good = True

    for filename, expected_chapters in EXPECTED_STRUCTURE.items():
        filepath = framework_dir / filename
        if not filepath.exists():
            continue

        try:
            content = filepath.read_text(encoding='utf-8')

            missing_chapters = []
            for chapter_num in expected_chapters:
                chapter_pattern = f"第{chapter_num}章"
                if chapter_pattern not in content:
                    missing_chapters.append(chapter_num)

            if missing_chapters:
                print(f"❌ {filename} 缺少以下章节: {missing_chapters}")
                all_good = False
            else:
                print(f"✅ {filename} 包含所有{len(expected_chapters)}个章节")

        except Exception as e:
            print(f"❌ 读取{filename}失败: {e}")
            all_good = False

    return all_good

def check_chapter_directory():
    """检查chapter目录下的章节文件"""
    chapter_dir = REPO_ROOT / "chapter"
    if not chapter_dir.exists():
        print(f"❌ chapter目录不存在: {chapter_dir}")
        return False

    chapter_files = list(chapter_dir.glob("第*篇-第*章.md"))
    chapter_nums = []

    for filepath in chapter_files:
        filename = filepath.name
        # 提取章节号
        match = re.search(r'第(\d+)章', filename)
        if match:
            chapter_nums.append(int(match.group(1)))

    chapter_nums.sort()

    # 检查章节编号连续性
    expected_total = 34
    if len(chapter_nums) != expected_total:
        print(f"❌ chapter目录应有{expected_total}个章节文件，实际有{len(chapter_nums)}个")
        return False

    # 检查是否连续
    if chapter_nums != list(range(1, expected_total + 1)):
        missing = set(range(1, expected_total + 1)) - set(chapter_nums)
        extra = set(chapter_nums) - set(range(1, expected_total + 1))
        if missing:
            print(f"❌ 缺少章节: {sorted(missing)}")
        if extra:
            print(f"❌ 多余章节: {sorted(extra)}")
        return False

    print(f"✅ chapter目录检查通过，共{len(chapter_files)}个章节文件，编号连续")
    return True

def main():
    """主函数"""
    print("🔍 开始内容完整性验证...")
    print()

    checks = [
        ("Framework文件存在性", check_framework_files),
        ("Framework内容完整性", check_chapter_content),
        ("Chapter目录完整性", check_chapter_directory),
    ]

    all_passed = True
    for check_name, check_func in checks:
        print(f"📋 检查: {check_name}")
        if not check_func():
            all_passed = False
        print()

    if all_passed:
        print("🎉 所有检查通过！内容完整性验证成功。")
        return 0
    else:
        print("❌ 发现问题，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    exit(main())