# 数据质量自动化测试框架示例代码
import pandas as pd
import numpy as np
import unittest
import json
from datetime import datetime

class DataQualityTestCase(unittest.TestCase):
    """数据质量测试用例基类"""
    
    def setUp(self):
        """测试前的设置"""
        self.test_results = {
            'test_name': self.__class__.__name__,
            'timestamp': datetime.now().isoformat(),
            'passed': True,
            'failures': []
        }
    
    def tearDown(self):
        """测试后的清理"""
        # 可以在这里保存测试结果到文件
        pass
    
    def assertDataQuality(self, condition, message):
        """数据质量断言，记录失败信息"""
        try:
            self.assertTrue(condition, message)
        except AssertionError as e:
            self.test_results['passed'] = False
            self.test_results['failures'].append(str(e))
            # 继续抛出异常，让unittest框架知道测试失败
            raise

class TestDataCompleteness(DataQualityTestCase):
    """数据完整性测试"""
    
    def setUp(self):
        super().setUp()
        # 加载测试数据
        self.data = self.get_test_data()
    
    def get_test_data(self):
        """获取测试数据"""
        # 在实际应用中，这里可能是从数据库或文件加载数据
        np.random.seed(42)
        data = pd.DataFrame({
            'id': range(1, 101),
            'name': [f'Name_{i}' for i in range(1, 101)],
            'email': [f'email_{i}@example.com' for i in range(1, 101)],
            'amount': np.random.normal(100, 20, 100)
        })
        
        # 引入一些缺失值
        data.loc[10:15, 'email'] = np.nan
        data.loc[20:22, 'amount'] = np.nan
        
        return data
    
    def test_required_columns_exist(self):
        """测试必需的列是否存在"""
        required_columns = ['id', 'name', 'email', 'amount']
        for col in required_columns:
            self.assertDataQuality(col in self.data.columns, f"缺少必需的列: {col}")
    
    def test_id_column_not_null(self):
        """测试ID列不应有缺失值"""
        null_count = self.data['id'].isnull().sum()
        self.assertDataQuality(null_count == 0, f"ID列有 {null_count} 个缺失值")
    
    def test_email_completeness_threshold(self):
        """测试email列的完整性是否达到阈值"""
        email_completeness = self.data['email'].count() / len(self.data)
        threshold = 0.9  # 90%的阈值
        self.assertDataQuality(email_completeness >= threshold, 
                              f"Email完整性 ({email_completeness:.2%}) 低于阈值 ({threshold:.2%})")

class TestDataAccuracy(DataQualityTestCase):
    """数据准确性测试"""
    
    def setUp(self):
        super().setUp()
        self.data = self.get_test_data()
    
    def get_test_data(self):
        """获取测试数据"""
        np.random.seed(42)
        data = pd.DataFrame({
            'id': range(1, 101),
            'age': np.random.randint(18, 75, 100),
            'amount': np.random.normal(100, 20, 100),
            'email': [f'email_{i}@example.com' for i in range(1, 101)]
        })
        
        # 引入一些错误值
        data.loc[5, 'age'] = 150  # 不合理的年龄
        data.loc[10, 'email'] = 'invalid-email'  # 无效的邮箱格式
        data.loc[15, 'amount'] = -50  # 负值金额
        
        return data
    
    def test_age_range(self):
        """测试年龄是否在合理范围内"""
        valid_age_mask = (self.data['age'] >= 0) & (self.data['age'] <= 120)
        invalid_count = len(self.data) - valid_age_mask.sum()
        self.assertDataQuality(invalid_count == 0, 
                              f"发现 {invalid_count} 个年龄值超出合理范围")
    
    def test_amount_positive(self):
        """测试金额是否为正数"""
        negative_amounts = self.data[self.data['amount'] < 0]
        self.assertDataQuality(len(negative_amounts) == 0, 
                              f"发现 {len(negative_amounts)} 个负金额值")
    
    def test_email_format(self):
        """测试邮箱格式是否正确"""
        import re
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        valid_emails = self.data['email'].str.match(email_pattern, na=False)
        invalid_count = len(self.data) - valid_emails.sum()
        self.assertDataQuality(invalid_count == 0, 
                              f"发现 {invalid_count} 个无效的邮箱格式")

class TestDataConsistency(DataQualityTestCase):
    """数据一致性测试"""
    
    def setUp(self):
        super().setUp()
        self.source_data = self.get_source_data()
        self.target_data = self.get_target_data()
    
    def get_source_data(self):
        """获取源数据（例如，源系统中的数据）"""
        data = pd.DataFrame({
            'id': range(1, 101),
            'name': [f'Customer_{i}' for i in range(1, 101)],
            'value': np.random.normal(100, 20, 100)
        })
        return data
    
    def get_target_data(self):
        """获取目标数据（例如，ETL后的目标系统数据）"""
        # 创建一个与源数据相似但有一些差异的目标数据集
        data = self.get_source_data().copy()
        
        # 引入一些不一致
        data.loc[5, 'value'] = data.loc[5, 'value'] * 1.5  # 修改一个值
        data.loc[10, 'name'] = 'Different_Name'  # 修改名称
        data = data.drop(15)  # 删除一行
        
        return data
    
    def test_record_count_consistency(self):
        """测试记录数一致性"""
        source_count = len(self.source_data)
        target_count = len(self.target_data)
        self.assertDataQuality(source_count == target_count, 
                              f"记录数不一致: 源系统 {source_count}, 目标系统 {target_count}")
    
    def test_key_fields_consistency(self):
        """测试关键字段一致性"""
        # 找出共同的ID
        common_ids = set(self.source_data['id']).intersection(set(self.target_data['id']))
        
        # 只比较共同ID的记录
        source_subset = self.source_data[self.source_data['id'].isin(common_ids)]
        target_subset = self.target_data[self.target_data['id'].isin(common_ids)]
        
        # 按ID排序
        source_subset = source_subset.sort_values('id')
        target_subset = target_subset.sort_values('id')
        
        # 检查关键字段
        fields_to_check = ['name', 'value']
        for field in fields_to_check:
            inconsistencies = (source_subset[field] != target_subset[field]).sum()
            # 对于数值类型，使用近似比较
            if pd.api.types.is_numeric_dtype(source_subset[field]):
                inconsistencies = (~np.isclose(source_subset[field], target_subset[field])).sum()
            
            self.assertDataQuality(inconsistencies == 0, 
                                  f"字段 '{field}' 存在 {inconsistencies} 处不一致")

class DataQualityTestSuite:
    """数据质量测试套件，用于组织和运行多个测试用例"""
    
    def __init__(self):
        self.test_cases = []
    
    def add_test_case(self, test_case_class):
        """添加测试用例类"""
        self.test_cases.append(test_case_class)
    
    def run_all_tests(self):
        """运行所有测试"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_results': {}
        }
        
        for test_case_class in self.test_cases:
            # 创建测试加载器和测试套件
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromTestCase(test_case_class)
            
            # 创建测试运行器
            runner = unittest.TextTestRunner(verbosity=2)
            
            # 运行测试
            print(f"\n运行测试: {test_case_class.__name__}")
            result = runner.run(suite)
            
            # 记录结果
            test_name = test_case_class.__name__
            results['test_results'][test_name] = {
                'total': result.testsRun,
                'passed': result.testsRun - len(result.failures) - len(result.errors),
                'failed': len(result.failures) + len(result.errors),
                'failures': [str(f[0]) for f in result.failures],
                'errors': [str(e[0]) for e in result.errors]
            }
            
            results['total_tests'] += result.testsRun
            results['passed_tests'] += result.testsRun - len(result.failures) - len(result.errors)
            results['failed_tests'] += len(result.failures) + len(result.errors)
        
        # 保存结果到JSON文件
        with open('data_quality_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("\n=== 数据质量测试汇总报告 ===")
        print(f"总测试数: {results['total_tests']}")
        print(f"通过测试数: {results['passed_tests']}")
        print(f"失败测试数: {results['failed_tests']}")
        print(f"测试结果已保存到: data_quality_test_results.json")
        
        return results

# 运行自动化测试
def run_automated_tests():
    # 创建测试套件
    test_suite = DataQualityTestSuite()
    
    # 添加测试用例
    test_suite.add_test_case(TestDataCompleteness)
    test_suite.add_test_case(TestDataAccuracy)
    test_suite.add_test_case(TestDataConsistency)
    
    # 运行所有测试
    results = test_suite.run_all_tests()
    
    return results

# 运行自动化测试示例
print("\n=== 数据质量自动化测试示例 ===")
run_automated_tests()
