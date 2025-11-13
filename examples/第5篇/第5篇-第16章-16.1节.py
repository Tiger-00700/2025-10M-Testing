"""第5篇-第16章-16.1节：测试项目规划与最小实操路径 - 占位脚本

演示：生成一个最小项目交付清单并打印，便于在 playbook 中引用。
"""

def generate_project_checklist():
    checklist = [
        'scope.md',
        'example-repo (examples/第5篇)',
        'smoke-test.sh',
        'ci-release-check.yml',
        'rollback-playbook.md'
    ]
    return checklist


def main():
    for item in generate_project_checklist():
        print('- ', item)


if __name__ == '__main__':
    main()
    print('第16章 16.1节 示例运行成功')
