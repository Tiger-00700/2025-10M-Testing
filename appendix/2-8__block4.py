class BIParameterizedTest(DataAnalysisTestBase):
    """BI报表参数化测试"""
    
    def __init__(self, test_name, report_service, parameter_combinations, expected_results_func):
        super().__init__(test_name, "验证BI报表在不同参数组合下的行为")
        self.report_service = report_service  # 报表服务接口
        self.parameter_combinations = parameter_combinations  # 参数组合列表
        self.expected_results_func = expected_results_func  # 用于验证结果的函数
        
    def run(self):
        start_time = time.time()
        
        try:
            parameter_results = []
            all_passed = True
            
            for params in self.parameter_combinations:
                param_str = ', '.join([f"{k}={v}" for k, v in params.items()])
                try:
                    # 获取报表数据
                    report_data = self.report_service.get_report_data(params)
                    
                    # 验证结果
                    validation_result = self.expected_results_func(report_data, params)
                    passed = validation_result.get('passed', False)
                    
                    parameter_results.append({
                        'parameters': params,
                        'passed': passed,
                        'details': validation_result.get('details', {})
                    })
                    
                    if not passed:
                        all_passed = False
                        logger.warning(f"参数组合测试失败: {param_str}")
                    else:
                        logger.info(f"参数组合测试通过: {param_str}")
                
                except Exception as e:
                    parameter_results.append({
                        'parameters': params,
                        'passed': False,
                        'error': str(e)
                    })
                    all_passed = False
                    logger.error(f"参数组合执行失败: {param_str}, 错误: {str(e)}")
            
            self.passed = all_passed
            self.results = {
                'parameter_results': parameter_results,
                'passed_count': sum(1 for r in parameter_results if r['passed']),
                'failed_count': sum(1 for r in parameter_results if not r['passed'])
            }
            
        except Exception as e:
            logger.error(f"BI报表参数化测试执行失败: {str(e)}")
            self.passed = False
            self.results['error'] = str(e)
        
        self.execution_time = time.time() - start_time

# 示例: 报表服务接口
class ReportService:
    """报表服务接口示例"""
    
    def get_report_data(self, parameters):
        """获取报表数据"""
        # 这里是实际调用BI工具API的逻辑
        # 示例实现
        import pandas as pd
        import numpy as np
        
        # 模拟根据参数生成数据
        if 'date_range' in parameters:
            start_date, end_date = parameters['date_range']
            # 模拟生成日期范围内的数据
            date_range = pd.date_range(start=start_date, end=end_date)
            data = pd.DataFrame({
                'date': date_range,
                'sales': np.random.randint(1000, 5000, size=len(date_range)),
                'customers': np.random.randint(50, 200, size=len(date_range))
            })
            return data
        else:
            raise ValueError("未提供必要的日期范围参数")
