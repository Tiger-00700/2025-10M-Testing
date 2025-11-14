"""第5篇-第17章-17.2.1：自动化测试框架极简示例

极简的框架类，展示 setup / run / teardown 的调用流程。
"""

class BigDataTestFramework:
    def __init__(self, config=None):
        self.config = config or {}
        self.prepared = False

    def setup_environment(self):
        self.prepared = True
        return True

    def run_tests(self, test_suite=None):
        if not self.prepared:
            raise RuntimeError('Environment not prepared')
        # 模拟执行并返回结果摘要
        return {'tests_run': 1, 'failures': 0}

    def teardown_environment(self):
        self.prepared = False
        return True


def main():
    fw = BigDataTestFramework()
    fw.setup_environment()
    res = fw.run_tests('example')
    print('Run summary:', res)
    fw.teardown_environment()


if __name__ == '__main__':
    main()
    print('第17章 框架示例运行成功')
