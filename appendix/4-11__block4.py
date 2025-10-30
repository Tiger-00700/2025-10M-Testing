# 模块化设计示例 - 测试执行引擎
class TestExecutor:
    def __init__(self, config_manager, logger, reporter):
        self.config_manager = config_manager
        self.logger = logger
        self.reporter = reporter
    
    def execute_test(self, test_case):
        self.logger.info(f"开始执行测试用例: {test_case.name}")
        try:
            result = test_case.run()
            self.reporter.report_result(test_case.name, result)
            return result
        except Exception as e:
            self.logger.error(f"测试用例执行失败: {str(e)}")
            self.reporter.report_failure(test_case.name, str(e))
            return False
