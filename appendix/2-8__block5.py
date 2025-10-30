class BIReportPerformanceTest(DataAnalysisTestBase):
    """BI报表性能测试"""
    
    def __init__(self, test_name, report_service, test_scenarios, performance_thresholds):
        super().__init__(test_name, "评估BI报表的性能和响应时间")
        self.report_service = report_service
        self.test_scenarios = test_scenarios  # 测试场景列表
        self.performance_thresholds = performance_thresholds  # 性能阈值
        
    def run(self):
        start_time = time.time()
        
        try:
            scenario_results = []
            all_passed = True
            
            for scenario in self.test_scenarios:
                scenario_name = scenario.get('name', 'Unnamed Scenario')
                params = scenario.get('parameters', {})
                iterations = scenario.get('iterations', 3)
                
                try:
                    # 执行多次以获得平均性能
                    execution_times = []
                    resource_usage = []
                    
                    for i in range(iterations):
                        logger.info(f"执行场景 '{scenario_name}'，迭代 {i+1}/{iterations}")
                        
                        # 记录开始时间
                        iter_start_time = time.time()
                        
                        # 模拟资源监控
                        start_memory = self._get_current_memory_usage()
                        
                        # 执行报表查询
                        result = self.report_service.get_report_data(params)
                        
                        # 记录结束时间和资源使用
                        iter_exec_time = time.time() - iter_start_time
                        execution_times.append(iter_exec_time)
                        
                        # 模拟内存使用计算
                        end_memory = self._get_current_memory_usage()
                        resource_usage.append({
                            'memory_used_mb': end_memory - start_memory
                        })
                    
                    # 计算统计信息
                    avg_exec_time = sum(execution_times) / len(execution_times)
                    min_exec_time = min(execution_times)
                    max_exec_time = max(execution_times)
                    
                    # 检查是否符合性能要求
                    passed = True
                    performance_issues = []
                    
                    if 'max_response_time' in self.performance_thresholds:
                        if avg_exec_time > self.performance_thresholds['max_response_time']:
                            passed = False
                            performance_issues.append(f"平均响应时间 {avg_exec_time:.2f}s 超过阈值 {self.performance_thresholds['max_response_time']}s")
                    
                    if 'max_memory_usage' in self.performance_thresholds:
                        avg_memory = sum(r['memory_used_mb'] for r in resource_usage) / len(resource_usage)
                        if avg_memory > self.performance_thresholds['max_memory_usage']:
                            passed = False
                            performance_issues.append(f"平均内存使用 {avg_memory:.2f}MB 超过阈值 {self.performance_thresholds['max_memory_usage']}MB")
                    
                    scenario_results.append({
                        'scenario_name': scenario_name,
                        'parameters': params,
                        'iterations': iterations,
                        'avg_execution_time': avg_exec_time,
                        'min_execution_time': min_exec_time,
                        'max_execution_time': max_exec_time,
                        'resource_usage': resource_usage,
                        'passed': passed,
                        'performance_issues': performance_issues
                    })
                    
                    if not passed:
                        all_passed = False
                        logger.warning(f"性能测试场景 '{scenario_name}' 未通过")
                    else:
                        logger.info(f"性能测试场景 '{scenario_name}' 通过")
                
                except Exception as e:
                    scenario_results.append({
                        'scenario_name': scenario_name,
                        'parameters': params,
                        'passed': False,
                        'error': str(e)
                    })
                    all_passed = False
                    logger.error(f"性能测试场景 '{scenario_name}' 执行失败: {str(e)}")
            
            self.passed = all_passed
            self.results = {
                'scenario_results': scenario_results,
                'passed_count': sum(1 for r in scenario_results if r['passed']),
                'failed_count': sum(1 for r in scenario_results if not r['passed'])
            }
            
        except Exception as e:
            logger.error(f"BI报表性能测试执行失败: {str(e)}")
            self.passed = False
            self.results['error'] = str(e)
        
        self.execution_time = time.time() - start_time
    
    def _get_current_memory_usage(self):
        """模拟获取当前内存使用情况"""
        # 实际实现中可以使用psutil等库获取真实内存使用
        # 这里返回模拟值
        import random
        return random.uniform(100, 500)

# BI报表测试套件使用示例
def run_bi_report_test_suite():
    # 创建测试套件
    test_suite = DataAnalysisTestSuite()
    
    # 准备测试数据
    source_data = pd.DataFrame({
        'region': ['North', 'South', 'East', 'West'] * 10,
        'product': ['A', 'B', 'C'] * 13 + ['A'],
        'sales': np.random.randint(1000, 5000, size=40),
        'cost': np.random.randint(500, 3000, size=40),
        'profit': 0
    })
    source_data['profit'] = source_data['sales'] - source_data['cost']
    
    # 模拟报表数据（故意引入一些错误用于测试）
    report_data = source_data.copy()
    # 引入一些错误
    report_data.loc[0:5, 'sales'] = report_data.loc[0:5, 'sales'] * 1.05  # 5%的误差
    report_data.loc[10:15, 'profit'] = report_data.loc[10:15, 'profit'] * 0.95  # 5%的误差
    
    # 添加数据准确性测试
    accuracy_test = BIDataAccuracyTest(
        "销售报表数据准确性测试",
        source_data,
        report_data,
        key_columns=['region', 'product'],
        metrics_columns=['sales', 'cost', 'profit']
    )
    test_suite.add_test(accuracy_test)
    
    # 添加业务逻辑测试
    logic_test = BIBusinessLogicTest(
        "销售报表业务逻辑测试",
        report_data,
        business_rules=[validate_profit_calculation, validate_percentage_sum]
    )
    test_suite.add_test(logic_test)
    
    # 创建报表服务
    report_service = ReportService()
    
    # 添加参数化测试
    param_test = BIParameterizedTest(
        "销售报表参数化测试",
        report_service,
        parameter_combinations=[
            {'date_range': ('2023-01-01', '2023-01-31')},
            {'date_range': ('2023-02-01', '2023-02-28')}
        ],
        expected_results_func=lambda data, params: {
            'passed': len(data) > 0 and 'sales' in data.columns,
            'details': {'row_count': len(data) if isinstance(data, pd.DataFrame) else 0}
        }
    )
    test_suite.add_test(param_test)
    
    # 添加性能测试
    perf_test = BIReportPerformanceTest(
        "销售报表性能测试",
        report_service,
        test_scenarios=[
            {
                'name': '月度数据查询',
                'parameters': {'date_range': ('2023-01-01', '2023-01-31')},
                'iterations': 3
            },
            {
                'name': '季度数据查询',
                'parameters': {'date_range': ('2023-01-01', '2023-03-31')},
                'iterations': 3
            }
        ],
        performance_thresholds={
            'max_response_time': 2.0,  # 秒
            'max_memory_usage': 500  # MB
        }
    )
    test_suite.add_test(perf_test)
    
    # 运行测试
    summary = test_suite.run_all(parallel=True)
    
    # 生成报告
    report = test_suite.generate_report("bi_report_test_report.txt")
    print(report)
    
    return summary

## 8.3 数据可视化测试技术

### 8.3.1 数据可视化测试的重要性

数据可视化是数据分析结果直观展示的关键环节，良好的可视化能够帮助决策者快速理解数据趋势、识别异常模式并做出正确判断。在大数据时代，可视化测试变得尤为重要，因为数据的复杂性和规模不断增加，使得可视化错误可能导致严重的决策失误。

数据可视化测试不仅关注视觉呈现的美观性，更重要的是确保可视化准确反映了底层数据的真实含义。一个看似直观的图表，如果数据映射错误或交互逻辑有问题，可能会误导用户对数据的理解。

### 8.3.2 可视化数据正确性测试

可视化数据正确性测试确保图表中展示的数据与原始数据源保持一致。以下是一个基于前文框架实现的数据可视化正确性测试类：

```python
class VisualizationDataAccuracyTest(DataAnalysisTestBase):
    """数据可视化正确性测试"""
    
    def __init__(self, test_name, source_data, visualization, mappings):
        super().__init__(test_name, "验证可视化展示的数据与原始数据的一致性")
        self.source_data = source_data
        self.visualization = visualization  # 可视化对象或组件
        self.mappings = mappings  # 数据映射规则，如{'x': 'date', 'y': 'sales', 'color': 'category'}
        
    def run(self):
        start_time = time.time()
        
        try:
            # 验证输入数据
            self.validate_input(self.source_data)
            
            # 提取可视化数据
            visual_data = self._extract_visualization_data(self.visualization)
            
            # 验证数据映射
            mapping_validation = self._validate_mappings(visual_data)
            
            # 验证数据值一致性
            value_validation = self._validate_data_values(visual_data)
            
            # 判断整体是否通过
            self.passed = mapping_validation['passed'] and value_validation['passed']
            self.results = {
                'mapping_validation': mapping_validation,
                'value_validation': value_validation
            }
            
        except Exception as e:
            logger.error(f"可视化数据正确性测试执行失败: {str(e)}")
            self.passed = False
            self.results['error'] = str(e)
        
        self.execution_time = time.time() - start_time
    
    def _extract_visualization_data(self, visualization):
        """从可视化对象中提取数据"""
        # 这是一个模拟实现，实际实现取决于具体的可视化库
        # 例如使用matplotlib、plotly、seaborn等
        if hasattr(visualization, 'data'):
            return visualization.data
        elif hasattr(visualization, 'get_data'):
            return visualization.get_data()
        else:
            # 模拟从图表元素中提取数据
            import pandas as pd
            
            # 假设mappings中指定了关键列
            if 'x' in self.mappings and 'y' in self.mappings:
                x_col = self.mappings['x']
                y_col = self.mappings['y']
                
                # 如果有color映射，按类别分组提取数据
                if 'color' in self.mappings:
                    color_col = self.mappings['color']
                    data_dict = {}
                    
                    for color_val in self.source_data[color_col].unique():
                        subset = self.source_data[self.source_data[color_col] == color_val]
                        # 这里模拟可视化可能进行的聚合操作
                        # 在实际应用中，需要根据具体可视化类型调整
                        data_dict[color_val] = subset[[x_col, y_col]].to_dict('records')
                    
                    return data_dict
                else:
                    # 返回所有数据点
                    return {'data': self.source_data[[x_col, y_col]].to_dict('records')}
            
        raise ValueError("无法从可视化对象中提取数据")
    
    def _validate_mappings(self, visual_data):
        """验证数据映射的正确性"""
        errors = []
        warnings = []
        
        # 检查所有映射列是否存在于源数据中
        for visual_key, source_col in self.mappings.items():
            if source_col not in self.source_data.columns:
                errors.append(f"映射列 '{source_col}' 在源数据中不存在")
        
        # 检查视觉数据的结构是否符合映射规则
        if isinstance(visual_data, dict):
            # 检查是否有颜色分组（如果指定了color映射）
            if 'color' in self.mappings:
                color_col = self.mappings['color']
                expected_groups = set(self.source_data[color_col].unique())
                actual_groups = set(k for k in visual_data.keys() if k != 'data')
                
                missing_groups = expected_groups - actual_groups
                extra_groups = actual_groups - expected_groups
                
                if missing_groups:
                    warnings.append(f"部分颜色分组在视觉数据中缺失: {missing_groups}")
                if extra_groups:
                    warnings.append(f"视觉数据中存在额外的颜色分组: {extra_groups}")
        
        passed = len(errors) == 0
        
        return {
            'passed': passed,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_data_values(self, visual_data):
        """验证数据值的一致性"""
        errors = []
        
        # 检查x和y数据的一致性
        if 'x' in self.mappings and 'y' in self.mappings:
            x_col = self.mappings['x']
            y_col = self.mappings['y']
            
            if isinstance(visual_data, dict):
                # 处理分组数据
                for group, data_points in visual_data.items():
                    if group == 'data':  # 未分组数据
                        for point in data_points:
                            # 在源数据中查找对应点
                            x_val = point.get('x', None)
                            y_val = point.get('y', None)
                            
                            if x_val is not None:
                                source_row = self.source_data[self.source_data[x_col] == x_val]
                                if len(source_row) > 0:
                                    expected_y = source_row[y_col].iloc[0]
                                    if abs(float(y_val) - expected_y) > 0.01:  # 允许0.01的误差
                                        errors.append(f"点 ({x_val}, {y_val}) 与源数据 ({x_val}, {expected_y}) 不匹配")
                                else:
                                    errors.append(f"x值 {x_val} 在源数据中不存在")
            
            # 验证聚合统计数据（如条形图的高度等）
            if 'color' in self.mappings:
                color_col = self.mappings['color']
                # 按颜色分组计算聚合值
                for color_val in self.source_data[color_col].unique():
                    if color_val in visual_data:
                        # 模拟从视觉数据中提取聚合值
                        visual_sum = sum(float(p.get('y', 0)) for p in visual_data[color_val])
                        source_sum = self.source_data[self.source_data[color_col] == color_val][y_col].sum()
                        
                        # 计算差异百分比
                        diff_pct = abs(visual_sum - source_sum) / max(source_sum, 0.001) * 100
                        if diff_pct > 0.1:  # 允许0.1%的误差
                            errors.append(f"{color_val} 组聚合值不匹配: 视觉={visual_sum}, 源数据={source_sum}, 差异={diff_pct:.2f}%")
        
        passed = len(errors) == 0
        
        return {
            'passed': passed,
            'errors': errors,
            'checked_points_count': len(visual_data.get('data', [])) if isinstance(visual_data, dict) else 0
        }
