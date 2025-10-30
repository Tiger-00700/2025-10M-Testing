class VisualizationInteractionTest(DataAnalysisTestBase):
    """数据可视化交互功能测试"""
    
    def __init__(self, test_name, visualization, interaction_tests):
        super().__init__(test_name, "验证可视化的交互功能是否正常工作")
        self.visualization = visualization  # 可视化对象
        self.interaction_tests = interaction_tests  # 交互测试用例列表
        
    def run(self):
        start_time = time.time()
        
        try:
            test_results = []
            all_passed = True
            
            for test_case in self.interaction_tests:
                test_name = test_case.get('name', 'Unnamed Interaction Test')
                interaction_type = test_case.get('type', '')
                params = test_case.get('params', {})
                expected_result = test_case.get('expected_result', None)
                
                try:
                    # 执行交互操作
                    logger.info(f"执行交互测试: {test_name} ({interaction_type})")
                    result = self._execute_interaction(interaction_type, params)
                    
                    # 验证结果
                    validation_result = self._validate_interaction_result(result, expected_result)
                    
                    test_results.append({
                        'test_name': test_name,
                        'interaction_type': interaction_type,
                        'params': params,
                        'passed': validation_result['passed'],
                        'details': validation_result.get('details', {})
                    })
                    
                    if not validation_result['passed']:
                        all_passed = False
                
                except Exception as e:
                    test_results.append({
                        'test_name': test_name,
                        'interaction_type': interaction_type,
                        'params': params,
                        'passed': False,
                        'error': str(e)
                    })
                    all_passed = False
                    logger.error(f"交互测试执行失败: {test_name}, 错误: {str(e)}")
            
            self.passed = all_passed
            self.results = {
                'test_results': test_results,
                'passed_count': sum(1 for r in test_results if r['passed']),
                'failed_count': sum(1 for r in test_results if not r['passed'])
            }
            
        except Exception as e:
            logger.error(f"可视化交互功能测试执行失败: {str(e)}")
            self.passed = False
            self.results['error'] = str(e)
        
        self.execution_time = time.time() - start_time
    
    def _execute_interaction(self, interaction_type, params):
        """执行交互操作"""
        # 这里是一个模拟实现，实际实现取决于具体的可视化库
        if interaction_type == 'filter':
            # 模拟筛选操作
            return self._simulate_filter(params)
        elif interaction_type == 'zoom':
            # 模拟缩放操作
            return self._simulate_zoom(params)
        elif interaction_type == 'hover':
            # 模拟悬停操作
            return self._simulate_hover(params)
        elif interaction_type == 'click':
            # 模拟点击操作
            return self._simulate_click(params)
        else:
            raise ValueError(f"不支持的交互类型: {interaction_type}")
    
    def _simulate_filter(self, params):
        """模拟筛选交互"""
        # 实际应用中，这里会调用可视化库的筛选API
        # 模拟返回筛选后的数据
        filter_col = params.get('column', None)
        filter_val = params.get('value', None)
        
        if filter_col and filter_val and filter_col in self.source_data.columns:
            filtered_data = self.source_data[self.source_data[filter_col] == filter_val]
            return {
                'type': 'filter_result',
                'column': filter_col,
                'value': filter_val,
                'row_count': len(filtered_data),
                'sample_data': filtered_data.head(3).to_dict('records')
            }
        return {'type': 'filter_result', 'error': '无效的筛选参数'}
    
    def _simulate_zoom(self, params):
        """模拟缩放交互"""
        x_range = params.get('x_range', None)
        y_range = params.get('y_range', None)
        
        return {
            'type': 'zoom_result',
            'x_range': x_range,
            'y_range': y_range,
            'applied': True
        }
    
    def _simulate_hover(self, params):
        """模拟悬停交互"""
        x_pos = params.get('x', 0)
        y_pos = params.get('y', 0)
        
        # 模拟返回悬停提示信息
        return {
            'type': 'hover_result',
            'position': {'x': x_pos, 'y': y_pos},
            'tooltip_content': f"位置: ({x_pos}, {y_pos})"
        }
    
    def _simulate_click(self, params):
        """模拟点击交互"""
        x_pos = params.get('x', 0)
        y_pos = params.get('y', 0)
        
        # 模拟返回点击后的交互结果
        return {
            'type': 'click_result',
            'position': {'x': x_pos, 'y': y_pos},
            'selected_element': f"element_at_{x_pos}_{y_pos}"
        }
    
    def _validate_interaction_result(self, result, expected_result):
        """验证交互结果"""
        if expected_result is None:
            return {'passed': True}
        
        errors = []
        
        # 检查结果类型
        if 'type' in expected_result:
            if result.get('type') != expected_result['type']:
                errors.append(f"期望的结果类型: {expected_result['type']}, 实际结果类型: {result.get('type')}")
        
        # 检查特定字段的值
        if 'expected_fields' in expected_result:
            for field, expected_value in expected_result['expected_fields'].items():
                actual_value = result.get(field)
                if actual_value != expected_value:
                    errors.append(f"字段 '{field}': 期望 {expected_value}, 实际 {actual_value}")
        
        # 检查筛选结果
        if result.get('type') == 'filter_result' and 'min_row_count' in expected_result:
            actual_count = result.get('row_count', 0)
            if actual_count < expected_result['min_row_count']:
                errors.append(f"筛选结果行数 {actual_count} 小于预期 {expected_result['min_row_count']}")
        
        passed = len(errors) == 0
        
        return {
            'passed': passed,
            'errors': errors,
            'details': {'actual_result': result}
        }

# 交互测试用例示例
interaction_test_cases = [
    {
        'name': '按区域筛选',
        'type': 'filter',
        'params': {'column': 'region', 'value': 'North'},
        'expected_result': {
            'expected_fields': {'column': 'region', 'value': 'North'},
            'min_row_count': 1  # 至少有一行结果
        }
    },
    {
        'name': 'X轴缩放',
        'type': 'zoom',
        'params': {'x_range': [10, 20]},
        'expected_result': {
            'expected_fields': {'x_range': [10, 20]}
        }
    },
    {
        'name': '数据点悬停',
        'type': 'hover',
        'params': {'x': 5, 'y': 1500},
        'expected_result': {
            'expected_fields': {'type': 'hover_result'}
        }
    }
]
