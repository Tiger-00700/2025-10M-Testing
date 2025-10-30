class TestDataCleanupManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.cleanup_tasks = []
    
    def register_cleanup_task(self, task):
        """注册清理任务"""
        self.cleanup_tasks.append(task)
    
    def execute_cleanup(self):
        """执行所有清理任务"""
        for task in self.cleanup_tasks:
            try:
                task()
                print(f"Cleanup task completed: {task.__name__}")
            except Exception as e:
                print(f"Error executing cleanup task: {str(e)}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 自动执行清理
        self.execute_cleanup()

# 使用示例
with TestDataCleanupManager(data_manager) as cleanup:
    # 生成测试数据
    test_data = generate_test_data()
    # 注册清理任务
    cleanup.register_cleanup_task(lambda: delete_test_data(test_data))
    # 执行测试
    run_tests()
