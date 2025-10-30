class BIBusinessLogicTest(DataAnalysisTestBase):
    """BI报表业务逻辑验证"""
    
    def __init__(self, test_name, report_data, business_rules):
        super().__init__(test_name, "验证BI报表中的业务逻辑和计算规则")
        self.report_data = report_data
        self.business_rules = business_rules  # 业务规则列表，每个规则是一个函数
        
    def run(self):
        start_time = time.time()
        
        try:
            # 验证输入数据
            self.validate_input(self.report_data)
            
            # 执行所有业务规则检查
            rule_results = []
            all_passed = True
            
            for i, rule_func in enumerate(self.business_rules):
                rule_name = getattr(rule_func, '__name__', f'Rule_{i+1}')
                try:
                    rule_result = rule_func(self.report_data)
                    passed = rule_result.get('passed', False)
                    rule_results.append({
                        'rule_name': rule_name,
                        'passed': passed,
                        'details': rule_result.get('details', {})
                    })
                    if not passed:
                        all_passed = False
                except Exception as e:
                    rule_results.append({
                        'rule_name': rule_name,
                        'passed': False,
                        'error': str(e)
                    })
                    all_passed = False
            
            self.passed = all_passed
            self.results = {
                'rule_results': rule_results,
                'passed_rules_count': sum(1 for r in rule_results if r['passed']),
                'failed_rules_count': sum(1 for r in rule_results if not r['passed'])
            }
            
        except Exception as e:
            logger.error(f"BI报表业务逻辑验证执行失败: {str(e)}")
            self.passed = False
            self.results['error'] = str(e)
        
        self.execution_time = time.time() - start_time

# 业务规则示例
def validate_profit_calculation(data):
    """验证利润计算是否正确: 利润 = 收入 - 成本"""
    if 'revenue' not in data.columns or 'cost' not in data.columns or 'profit' not in data.columns:
        return {'passed': False, 'details': '缺少必要的列'}
    
    # 计算预期利润
    expected_profit = data['revenue'] - data['cost']
    
    # 比较实际利润和预期利润
    differences = data[abs(data['profit'] - expected_profit) > 0.01]  # 允许0.01的误差
    
    return {
        'passed': len(differences) == 0,
        'details': {
            'differences_count': len(differences),
            'sample_differences': differences.head(5).to_dict('records') if len(differences) > 0 else []
        }
    }

def validate_percentage_sum(data):
    """验证百分比列的总和是否为100%"""
    percentage_columns = [col for col in data.columns if 'percentage' in col.lower()]
    if not percentage_columns:
        return {'passed': True, 'details': '未找到百分比列'}
    
    results = {}
    all_passed = True
    
    for col in percentage_columns:
        sum_diff = abs(data[col].sum() - 100)
        passed = sum_diff < 0.1  # 允许0.1%的误差
        results[col] = {
            'sum_value': data[col].sum(),
            'difference': sum_diff,
            'passed': passed
        }
        if not passed:
            all_passed = False
    
    return {
        'passed': all_passed,
        'details': results
    }
