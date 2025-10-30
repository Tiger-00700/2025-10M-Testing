class BIDataAccuracyTest(DataAnalysisTestBase):
    """BI报表数据准确性测试"""
    
    def __init__(self, test_name, source_data, report_data, key_columns, metrics_columns):
        super().__init__(test_name, "验证BI报表数据与源数据的一致性")
        self.source_data = source_data
        self.report_data = report_data
        self.key_columns = key_columns  # 用于关联的键列
        self.metrics_columns = metrics_columns  # 需要验证的度量列
        
    def run(self):
        start_time = time.time()
        
        try:
            # 验证输入数据
            self.validate_input(self.source_data, self.key_columns + self.metrics_columns)
            self.validate_input(self.report_data, self.key_columns + self.metrics_columns)
            
            # 按键列进行关联比较
            comparison_results = {}
            all_passed = True
            
            # 计算源数据和报表数据的聚合结果
            source_agg = self.source_data.groupby(self.key_columns).agg({col: ['sum', 'mean', 'count'] for col in self.metrics_columns})
            report_agg = self.report_data.groupby(self.key_columns).agg({col: ['sum', 'mean', 'count'] for col in self.metrics_columns})
            
            # 检查键值集合是否一致
            source_keys = set(tuple(x) for x in source_agg.index)
            report_keys = set(tuple(x) for x in report_agg.index)
            
            missing_in_report = source_keys - report_keys
            extra_in_report = report_keys - source_keys
            
            comparison_results['key_comparison'] = {
                'missing_in_report': list(missing_in_report),
                'extra_in_report': list(extra_in_report),
                'matching_keys_count': len(source_keys & report_keys)
            }
            
            # 验证度量值
            metric_comparisons = {}
            common_keys = source_keys & report_keys
            
            for col in self.metrics_columns:
                col_results = []
                
                for agg_type in ['sum', 'mean']:
                    diffs = []
                    for key in common_keys:
                        if isinstance(key, tuple) and len(key) == 1:
                            key = key[0]  # 处理单列索引情况
                        
                        source_val = source_agg.loc[key, (col, agg_type)]
                        report_val = report_agg.loc[key, (col, agg_type)]
                        
                        # 计算差异
                        if isinstance(source_val, (int, float)) and isinstance(report_val, (int, float)):
                            if source_val != 0:
                                diff_pct = abs((report_val - source_val) / source_val) * 100
                            else:
                                diff_pct = 0 if report_val == 0 else 100
                                
                            diffs.append({
                                'key': key,
                                'source_value': source_val,
                                'report_value': report_val,
                                'diff_pct': diff_pct,
                                'passed': diff_pct < 0.1  # 允许0.1%的误差
                            })
                    
                    col_results.append({
                        'aggregation': agg_type,
                        'comparisons': diffs,
                        'passed_count': sum(1 for d in diffs if d['passed']),
                        'failed_count': sum(1 for d in diffs if not d['passed']),
                        'passed': sum(1 for d in diffs if not d['passed']) == 0
                    })
                
                metric_comparisons[col] = col_results
            
            comparison_results['metric_comparisons'] = metric_comparisons
            
            # 判断整体是否通过
            all_key_checks_passed = len(missing_in_report) == 0 and len(extra_in_report) == 0
            all_metric_checks_passed = all(all(agg['passed'] for agg in checks) for checks in metric_comparisons.values())
            
            self.passed = all_key_checks_passed and all_metric_checks_passed
            self.results = comparison_results
            
        except Exception as e:
            logger.error(f"BI报表数据准确性测试执行失败: {str(e)}")
            self.passed = False
            self.results['error'] = str(e)
        
        self.execution_time = time.time() - start_time
