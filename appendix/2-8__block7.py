class VisualizationBoundaryTest(DataAnalysisTestBase):
    """数据可视化边界情况测试"""
    
    def __init__(self, test_name, visualization_class, boundary_cases):
        super().__init__(test_name, "验证可视化在边界情况下的表现")
        self.visualization_class = visualization_class  # 可视化类
        self.boundary_cases = boundary_cases  # 边界情况列表
        
    def run(self):
        start_time = time.time()
        
        try:
            case_results = []
            all_passed = True
            
            for case in self.boundary_cases:
                case_name = case.get('name', 'Unnamed Boundary Case')
                data_generator = case.get('data_generator')
                assertions = case.get('assertions', [])
                
                try:
                    # 生成边界测试数据
                    logger.info(f"执行边界情况测试: {case_name}")
                    test_data = data_generator()
                    
                    # 创建可视化
                    visualization = self.visualization_class(test_data)
                    
                    # 验证断言
                    assertion_results = []
                    case_passed = True
                    
                    for assertion in assertions:
                        assertion_name = assertion.get('name', 'Unnamed Assertion')
                        assertion_func = assertion.get('assertion')
                        
                        try:
                            assertion_result = assertion_func(visualization, test_data)
                            passed = assertion_result.get('passed', False)
                            
                            assertion_results.append({
                                'assertion_name': assertion_name,
                                'passed': passed,
                                'details': assertion_result.get('details', {})
                            })
                            
                            if not passed:
                                case_passed = False
                        except Exception as e:
                            assertion_results.append({
                                'assertion_name': assertion_name,
                                'passed': False,
                                'error': str(e)
                            })
                            case_passed = False
                    
                    case_results.append({
                        'case_name': case_name,
                        'passed': case_passed,
                        'assertion_results': assertion_results
                    })
                    
                    if not case_passed:
                        all_passed = False
                
                except Exception as e:
                    case_results.append({
                        'case_name': case_name,
                        'passed': False,
                        'error': str(e)
                    })
                    all_passed = False
                    logger.error(f"边界情况测试执行失败: {case_name}, 错误: {str(e)}")
            
            self.passed = all_passed
            self.results = {
                'case_results': case_results,
                'passed_count': sum(1 for r in case_results if r['passed']),
                'failed_count': sum(1 for r in case_results if not r['passed'])
            }
            
        except Exception as e:
            logger.error(f"可视化边界情况测试执行失败: {str(e)}")
            self.passed = False
            self.results['error'] = str(e)
        
        self.execution_time = time.time() - start_time

# 边界情况测试示例
def generate_empty_data():
    """生成空数据集"""
    import pandas as pd
    return pd.DataFrame(columns=['date', 'value'])

def generate_single_data_point():
    """生成单个数据点"""
    import pandas as pd
    return pd.DataFrame({
        'date': ['2023-01-01'],
        'value': [100]
    })

def generate_extreme_values():
    """生成包含极值的数据"""
    import pandas as pd
    import numpy as np
    return pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=10),
        'value': [1, 2, 3, 4, 5, 6, 7, 8, 9, 1000000]  # 最后一个值为异常大值
    })

def generate_negative_values():
    """生成包含负值的数据"""
    import pandas as pd
    import numpy as np
    return pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=10),
        'value': np.random.randint(-100, 100, size=10)
    })

# 断言函数示例
def assert_not_crash(visualization, data):
    """断言可视化不会崩溃"""
    try:
        # 尝试渲染可视化
        if hasattr(visualization, 'render'):
            visualization.render()
        return {'passed': True}
    except Exception as e:
        return {
            'passed': False,
            'details': {'error': str(e)}
        }

def assert_proper_scaling(visualization, data):
    """断言可视化正确缩放以显示所有数据"""
    try:
        # 获取可视化的数据范围
        if hasattr(visualization, 'get_data_range'):
            data_range = visualization.get_data_range()
            actual_min = data['value'].min()
            actual_max = data['value'].max()
            
            # 检查数据范围是否包含了所有实际数据
            range_includes_data = (data_range['min'] <= actual_min) and (data_range['max'] >= actual_max)
            return {
                'passed': range_includes_data,
                'details': {
                    'visual_range': data_range,
                    'actual_min': actual_min,
                    'actual_max': actual_max
                }
            }
        return {'passed': True}  # 如果无法获取数据范围，则默认通过
    except Exception as e:
        return {
            'passed': False,
            'details': {'error': str(e)}
        }

def assert_handles_negative_values(visualization, data):
    """断言可视化能正确处理负值"""
    try:
        # 检查数据是否包含负值
        has_negatives = (data['value'] < 0).any()
        
        if has_negatives:
            # 检查可视化是否有适当的Y轴范围
            if hasattr(visualization, 'get_y_range'):
                y_range = visualization.get_y_range()
                includes_negative = y_range['min'] < 0
                return {
                    'passed': includes_negative,
                    'details': {'y_range': y_range}
                }
        return {'passed': True}  # 如果没有负值，则默认通过
    except Exception as e:
        return {
            'passed': False,
            'details': {'error': str(e)}
        }

# 边界情况测试用例
boundary_test_cases = [
    {
        'name': '空数据集测试',
        'data_generator': generate_empty_data,
        'assertions': [
            {'name': '不崩溃', 'assertion': assert_not_crash}
        ]
    },
    {
        'name': '单数据点测试',
        'data_generator': generate_single_data_point,
        'assertions': [
            {'name': '不崩溃', 'assertion': assert_not_crash},
            {'name': '正确缩放', 'assertion': assert_proper_scaling}
        ]
    },
    {
        'name': '极值测试',
        'data_generator': generate_extreme_values,
        'assertions': [
            {'name': '不崩溃', 'assertion': assert_not_crash},
            {'name': '正确缩放', 'assertion': assert_proper_scaling}
        ]
    },
    {
        'name': '负值测试',
        'data_generator': generate_negative_values,
        'assertions': [
            {'name': '不崩溃', 'assertion': assert_not_crash},
            {'name': '正确处理负值', 'assertion': assert_handles_negative_values}
        ]
    }
]
