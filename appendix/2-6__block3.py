# 数据准确性评估示例代码
import pandas as pd
import numpy as np
import re

def evaluate_accuracy(data):
    """评估数据集的准确性指标"""
    results = {}
    total_records = len(data)
    
    # 数值准确性 - 检查异常值
    if 'amount' in data.columns:
        # 使用IQR方法检测异常值
        Q1 = data['amount'].quantile(0.25)
        Q3 = data['amount'].quantile(0.75)
        IQR = Q3 - Q1
        outliers = data[(data['amount'] < Q1 - 1.5 * IQR) | (data['amount'] > Q3 + 1.5 * IQR)]
        outlier_percent = (len(outliers) / total_records) * 100 if total_records > 0 else 0
        results['数值异常率'] = f"{outlier_percent:.2f}%"
    
    # 格式准确性 - 检查日期格式
    if 'order_date' in data.columns:
        # 检查是否为有效的日期类型
        is_date = pd.to_datetime(data['order_date'], errors='coerce').notna()
        date_format_accuracy = (is_date.sum() / total_records) * 100 if total_records > 0 else 0
        results['日期格式准确性'] = f"{date_format_accuracy:.2f}%"
    
    # 业务规则准确性 - 检查金额是否为正数
    if 'amount' in data.columns:
        valid_amounts = data[data['amount'] > 0]['amount'].count()
        amount_validity = (valid_amounts / total_records) * 100 if total_records > 0 else 0
        results['金额有效性'] = f"{amount_validity:.2f}%"
    
    # 引用准确性 - 检查customer_id是否在有效范围内
    if 'customer_id' in data.columns:
        # 过滤掉NaN值
        valid_customer_ids = data['customer_id'].dropna()
        # 假设有效ID是1-1000的整数
        valid_range_ids = valid_customer_ids[(valid_customer_ids >= 1) & (valid_customer_ids <= 1000)]
        ref_accuracy = (len(valid_range_ids) / len(valid_customer_ids)) * 100 if len(valid_customer_ids) > 0 else 0
        results['引用准确性'] = f"{ref_accuracy:.2f}%"
    
    return results

# 使用之前生成的测试数据进行准确性评估
accuracy_results = evaluate_accuracy(test_data)
print("\n数据准确性评估结果：")
for key, value in accuracy_results.items():
    print(f"{key}: {value}")
