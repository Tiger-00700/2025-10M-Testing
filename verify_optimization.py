import re

def verify_optimization(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    print('=== 优化结果验证 ===')
    print()

    # 检查第2篇标题修改
    if '## 第2篇 数据处理测试（进阶）' in content:
        print('✓ 第2篇标题已成功修改为"数据处理测试（进阶）"')
    else:
        print('✗ 第2篇标题修改失败')

    # 检查第8篇是否创建
    if '## 第8篇 数据质量安全（进阶）' in content:
        print('✓ 第8篇"数据质量安全（进阶）"已成功创建')
    else:
        print('✗ 第8篇创建失败')

    # 检查第3篇新章节
    new_chapters = ['第14章 测试环境监控与告警体系', '第15章 数据血缘治理与元数据管理', '第16章 多云环境测试策略']
    for chapter in new_chapters:
        if chapter in content:
            print('✓ 新章节"' + chapter + '"已添加到第3篇')
        else:
            print('✗ 新章节"' + chapter + '"添加失败')

    # 检查第22章扩充
    expanded_sections = ['22.2 案例背景与需求分析', '22.3 系统架构设计', '22.4 实施步骤与关键技术']
    expanded_count = sum(1 for section in expanded_sections if section in content)
    print('✓ 第22章已扩充了' + str(expanded_count) + '个小节')

    # 统计篇章数量
    part_count = len(re.findall(r'^## 第\d+篇', content, re.MULTILINE))
    print('✓ 书籍现在包含' + str(part_count) + '篇')

    # 统计章节数量
    chapter_count = len(re.findall(r'^### 第\d+章', content, re.MULTILINE))
    print('✓ 书籍现在包含' + str(chapter_count) + '章')

    print()
    print('=== 结构分析 ===')

    # 分析各篇的章节分布
    parts = re.findall(r'^## 第(\d+)篇 (.+)', content, re.MULTILINE)
    for part_num, part_title in parts:
        part_num = int(part_num)
        # 找到该篇的所有章节
        part_start = content.find('## 第' + str(part_num) + '篇')
        next_part = content.find('## 第' + str(part_num+1) + '篇') if part_num < part_count else len(content)
        part_content = content[part_start:next_part]
        chapter_count_in_part = len(re.findall(r'^### 第\d+章', part_content, re.MULTILINE))
        print('  第' + str(part_num) + '篇 (' + part_title + '): ' + str(chapter_count_in_part) + '章')

if __name__ == "__main__":
    verify_optimization('book/1208.2025.newbook.update.md')