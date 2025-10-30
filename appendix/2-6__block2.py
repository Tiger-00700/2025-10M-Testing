# 数据完整性评估示例代码
import pandas as pd
import numpy as np
from collections import Counter

def evaluate_completeness(data):
    """评估数据集的完整性指标"""
    results = {}
    
    # 记录完整性
    total_records = len(data)
    expected_records = total_records  # 示例中使用实际记录数作为期望值
    record_completeness = (total_records / expected_records) * 100 if expected_records > 0 else 0
    results['记录完整性'] = f"{record_completeness:.2f}%"
    
    # 字段完整性
    field_completeness = {}
    for column in data.columns:
        non_null_count = data[column].count()
        completeness_percent = (non_null_count / total_records) * 100
        field_completeness[column] = f"{completeness_percent:.2f}%"
    results['字段完整性'] = field_completeness
    
    # 实体完整性 - 检查主键唯一性（假设'id'列是主键）
    if 'id' in data.columns:
        duplicates = data['id'].duplicated().sum()
        unique_ratio = ((total_records - duplicates) / total_records) * 100 if total_records > 0 else 0
        results['主键唯一性'] = f"{unique_ratio:.2f}%"
    
    # 参照完整性示例（假设'customer_id'引用'customers'表）
    if 'customer_id' in data.columns:
        # 模拟customers表的ID集合
        valid_customer_ids = set(range(1, 1001))  # 假设有效ID范围是1-1000
        
        # 检查无效的外键引用
        invalid_refs = data[~data['customer_id'].isin(valid_customer_ids)]['customer_id'].count()
        ref_integrity = ((total_records - invalid_refs) / total_records) * 100 if total_records > 0 else 0
        results['参照完整性'] = f"{ref_integrity:.2f}%"
    
    return results

# 生成测试数据
def generate_test_data():
    # 创建包含1000行的测试数据
    n = 1000
    data = pd.DataFrame({
        'id': range(1, n + 1),
        'customer_id': np.random.randint(1, 1100, size=n),  # 故意引入一些无效ID
        'order_date': pd.date_range(start='2023-01-01', periods=n),
        'amount': np.random.normal(100, 30, size=n)
    })
    
    # 故意引入一些缺失值
    data.loc[np.random.choice(n, 50), 'customer_id'] = np.nan
    data.loc[np.random.choice(n, 30), 'amount'] = np.nan
    
    # 故意引入一些重复ID
    data.loc[995:999, 'id'] = [10, 20, 30, 40, 50]
    
    return data

# 运行完整性评估
test_data = generate_test_data()
completeness_results = evaluate_completeness(test_data)
print("数据完整性评估结果：")
for key, value in completeness_results.items():
    if isinstance(value, dict):
        print(f"\n{key}:")
        for field, percent in value.items():
            print(f"  {field}: {percent}")
    else:
        print(f"{key}: {value}")
