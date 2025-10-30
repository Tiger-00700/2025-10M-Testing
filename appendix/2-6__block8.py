# 数据质量规则测试示例代码
import pandas as pd
import numpy as np
import re

class DataQualityRuleTester:
    """数据质量规则测试器"""
    
    def __init__(self, data):
        self.data = data
        self.rules = []
        self.results = {}
    
    def add_rule(self, rule_name, rule_func, severity='medium'):
        """添加数据质量规则"""
        self.rules.append({
            'name': rule_name,
            'func': rule_func,
            'severity': severity
        })
    
    def run_all_rules(self):
        """运行所有数据质量规则"""
        for rule in self.rules:
            try:
                result = rule['func'](self.data)
                self.results[rule['name']] = {
                    'passed': result['passed'],
                    'failed_count': result.get('failed_count', 0),
                    'failed_records': result.get('failed_records', None),
                    'severity': rule['severity'],
                    'details': result.get('details', '')
                }
            except Exception as e:
                self.results[rule['name']] = {
                    'passed': False,
                    'error': str(e),
                    'severity': 'high'
                }
        
        return self.results
    
    def generate_report(self):
        """生成数据质量规则测试报告"""
        report = {
            'summary': {
                'total_rules': len(self.rules),
                'passed_rules': sum(1 for r in self.results.values() if r.get('passed', False)),
                'failed_rules': sum(1 for r in self.results.values() if not r.get('passed', True)),
                'high_severity_issues': sum(1 for r in self.results.values() if r.get('severity') == 'high' and not r.get('passed', True))
            },
            'rule_details': self.results
        }
        
        return report
    
    def get_failed_records(self):
        """获取所有失败规则对应的记录"""
        failed_records = {}
        for rule_name, result in self.results.items():
            if not result.get('passed', True) and result.get('failed_records') is not None:
                failed_records[rule_name] = result['failed_records']
        
        return failed_records

# 定义常用的数据质量规则函数
def rule_not_null(data, column):
    """检查列是否有缺失值"""
    failed_count = data[column].isnull().sum()
    return {
        'passed': failed_count == 0,
        'failed_count': failed_count,
        'failed_records': data[data[column].isnull()].index.tolist() if failed_count > 0 else None,
        'details': f"列 '{column}' 有 {failed_count} 个缺失值"
    }

def rule_value_in_range(data, column, min_val=None, max_val=None):
    """检查列值是否在指定范围内"""
    mask = pd.Series([True] * len(data))
    
    if min_val is not None:
        mask = mask & (data[column] >= min_val)
    if max_val is not None:
        mask = mask & (data[column] <= max_val)
    
    # 忽略NaN值
    mask = mask | data[column].isnull()
    
    failed_count = len(data) - mask.sum()
    
    return {
        'passed': failed_count == 0,
        'failed_count': failed_count,
        'failed_records': data[~mask].index.tolist() if failed_count > 0 else None,
        'details': f"列 '{column}' 有 {failed_count} 个值超出范围 [{min_val}, {max_val}]"
    }

def rule_unique(data, column):
    """检查列值是否唯一"""
    duplicates = data[column].duplicated(keep=False)
    failed_count = duplicates.sum()
    
    return {
        'passed': failed_count == 0,
        'failed_count': failed_count,
        'failed_records': data[duplicates].index.tolist() if failed_count > 0 else None,
        'details': f"列 '{column}' 有 {failed_count} 个重复值"
    }

def rule_regex_match(data, column, pattern):
    """检查列值是否匹配正则表达式模式"""
    # 忽略NaN值
    mask = data[column].isnull() | data[column].astype(str).str.match(pattern)
    failed_count = len(data) - mask.sum()
    
    return {
        'passed': failed_count == 0,
        'failed_count': failed_count,
        'failed_records': data[~mask].index.tolist() if failed_count > 0 else None,
        'details': f"列 '{column}' 有 {failed_count} 个值不匹配模式 '{pattern}'"
    }

def rule_custom_function(data, condition_func, description=""):
    """使用自定义函数进行规则检查"""
    mask = condition_func(data)
    failed_count = len(data) - mask.sum()
    
    return {
        'passed': failed_count == 0,
        'failed_count': failed_count,
        'failed_records': data[~mask].index.tolist() if failed_count > 0 else None,
        'details': description or f"自定义规则检查失败 {failed_count} 条记录"
    }

# 使用示例
def run_quality_rules_example():
    # 创建测试数据
    np.random.seed(42)
    data = pd.DataFrame({
        'customer_id': range(1, 101),
        'age': np.random.randint(18, 75, 100),
        'email': [f'user{i}@example.com' for i in range(1, 101)],
        'phone': [f'1381234{i:04d}' for i in range(1, 101)],
        'score': np.random.normal(50, 15, 100),
        'registration_date': pd.date_range(start='2023-01-01', periods=100)
    })
    
    # 引入一些质量问题
    data.loc[5, 'email'] = 'invalid-email'
    data.loc[10:12, 'phone'] = ['123', '456', '789']
    data.loc[20, 'score'] = -10
    data.loc[30, 'customer_id'] = 5  # 重复ID
    data.loc[40, 'age'] = 15  # 年龄太小
    
    # 创建规则测试器
    tester = DataQualityRuleTester(data)
    
    # 添加规则
    tester.add_rule('customer_id_not_null', lambda d: rule_not_null(d, 'customer_id'), 'high')
    tester.add_rule('customer_id_unique', lambda d: rule_unique(d, 'customer_id'), 'high')
    tester.add_rule('age_in_range', lambda d: rule_value_in_range(d, 'age', 18, 120), 'medium')
    tester.add_rule('score_non_negative', lambda d: rule_value_in_range(d, 'score', 0), 'medium')
    tester.add_rule('email_format', lambda d: rule_regex_match(d, 'email', r'^[\w\.-]+@[\w\.-]+\.\w+$'), 'medium')
    tester.add_rule('phone_format', lambda d: rule_regex_match(d, 'phone', r'^1[3-9]\d{9}$'), 'medium')
    
    # 添加自定义规则
    tester.add_rule('registration_after_2022', 
                   lambda d: rule_custom_function(
                       d, 
                       lambda x: x['registration_date'] >= pd.Timestamp('2022-01-01'),
                       '注册日期必须在2022年1月1日之后'
                   ), 
                   'medium')
    
    # 运行规则测试
    results = tester.run_all_rules()
    
    # 生成报告
    report = tester.generate_report()
    
    # 打印报告
    print("\n=== 数据质量规则测试报告 ===")
    print(f"总规则数: {report['summary']['total_rules']}")
    print(f"通过规则数: {report['summary']['passed_rules']}")
    print(f"失败规则数: {report['summary']['failed_rules']}")
    print(f"高危问题数: {report['summary']['high_severity_issues']}")
    
    print("\n规则详情:")
    for rule_name, result in report['rule_details'].items():
        status = "通过" if result['passed'] else "失败"
        severity = result['severity']
        print(f"- {rule_name} [{severity}]: {status}")
        if not result['passed']:
            print(f"  详情: {result.get('details', '')}")
            print(f"  失败记录数: {result.get('failed_count', 0)}")
    
    # 获取失败记录
    failed_records = tester.get_failed_records()
    print("\n失败记录示例:")
    for rule_name, indices in failed_records.items():
        if indices:
            print(f"\n{rule_name} - 失败记录前3条:")
            print(data.iloc[indices[:3]])

# 运行示例
run_quality_rules_example()
