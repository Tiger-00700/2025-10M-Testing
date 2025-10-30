# 并行执行管理器示例
import concurrent.futures
import time

class ParallelTestExecutor:
    
    def __init__(self, max_workers=4, timeout=300):
        self.max_workers = max_workers
        self.timeout = timeout
    
    def execute_test_suite(self, test_cases):
        """并行执行测试套件"""
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有测试用例
            future_to_test = {executor.submit(self._execute_test_with_timeout, test): test 
                             for test in test_cases}
            
            # 收集执行结果
            for future in concurrent.futures.as_completed(future_to_test):
                test = future_to_test[future]
                try:
                    result = future.result()
                    results[test.name] = result
                except Exception as e:
                    results[test.name] = {'status': 'error', 'error': str(e)}
        
        return results
    
    def _execute_test_with_timeout(self, test):
        """带超时控制的测试执行"""
        start_time = time.time()
        try:
            # 使用子线程执行，支持超时控制
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(test.run)
                result = future.result(timeout=self.timeout)
                execution_time = time.time() - start_time
                return {'status': 'success', 'result': result, 'execution_time': execution_time}
        except concurrent.futures.TimeoutError:
            return {'status': 'timeout', 'execution_time': self.timeout}
