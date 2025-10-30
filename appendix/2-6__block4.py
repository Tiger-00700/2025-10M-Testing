# 数据一致性评估示例代码
import pandas as pd
import numpy as np

def evaluate_consistency(data, reference_data=None):
    """评估数据集的一致性指标"""
    results = {}
    
    # 格式一致性 - 检查日期格式一致性
    if 'order_date' in data.columns:
        # 确保所有非空日期格式一致
        date_series = pd.to_datetime(data['order_date'], errors='coerce')
        non_null_dates = date_series.dropna()
        # 检查日期格式是否统一为日期类型
        format_consistency = (len(non_null_dates) / len(date_series)) * 100 if len(date_series) > 0 else 0
        results['日期格式一致性'] = f"{format_consistency:.2f}%"
    
    # 业务规则一致性 - 检查金额与订单状态的一致性
    if all(col in data.columns for col in ['amount', 'order_status']):
        # 假设已取消订单的金额应为0
        cancelled_orders = data[data['order_status'] == 'cancelled']
        invalid_cancelled = cancelled_orders[cancelled_orders['amount'] != 0]
        if len(cancelled_orders) > 0:
            rule_consistency = ((len(cancelled_orders) - len(invalid_cancelled)) / len(cancelled_orders)) * 100
        else:
            rule_consistency = 100.0
        results['订单状态金额一致性'] = f"{rule_consistency:.2f}%"
    
    # 跨系统一致性 - 如果提供了参考数据
    if reference_data is not None and 'id' in data.columns and 'id' in reference_data.columns:
        # 合并两个数据集以比较共同ID的记录
        merged_data = pd.merge(data, reference_data, on='id', how='inner', suffixes=('_source', '_reference'))
        
        if len(merged_data) > 0:
            # 比较关键字段的一致性
            consistency_checks = []
            common_columns = [col.split('_source')[0] for col in merged_data.columns if '_source' in col]
            
            for col in common_columns:
                if f'{col}_source' in merged_data.columns and f'{col}_reference' in merged_data.columns:
                    # 处理浮点数比较时的精度问题
                    if merged_data[f'{col}_source'].dtype.kind in 'fc' and merged_data[f'{col}_reference'].dtype.kind in 'fc':
                        is_consistent = np.isclose(merged_data[f'{col}_source'], merged_data[f'{col}_reference'], atol=1e-6)
                    else:
                        is_consistent = merged_data[f'{col}_source'] == merged_data[f'{col}_reference']
                    
                    consistency_rate = (is_consistent.sum() / len(merged_data)) * 100
                    consistency_checks.append((col, consistency_rate))
            
            results['跨系统字段一致性'] = {col: f"{rate:.2f}%" for col, rate in consistency_checks}
    
    return results

# 创建参考数据用于一致性检查
def create_reference_data(source_data):
    # 创建一个稍有差异的参考数据集
    reference_data = source_data.copy()
    # 修改部分金额值以模拟不一致
    mask = np.random.choice([True, False], size=len(reference_data), p=[0.05, 0.95])
    reference_data.loc[mask, 'amount'] = reference_data.loc[mask, 'amount'] * 1.1  # 增加5%的金额
    return reference_data

# 添加订单状态列用于业务规则一致性检查
test_data['order_status'] = np.random.choice(['completed', 'pending', 'cancelled'], size=len(test_data))
# 确保一些已取消订单的金额不为0，以测试一致性检查
cancelled_mask = test_data['order_status'] == 'cancelled'
test_data.loc[cancelled_mask, 'amount'] = np.where(np.random.random(sum(cancelled_mask)) < 0.2, 100, 0)

# 创建参考数据
reference_data = create_reference_data(test_data)

# 运行一致性评估
consistency_results = evaluate_consistency(test_data, reference_data)
print("\n数据一致性评估结果：")
for key, value in consistency_results.items():
    if isinstance(value, dict):
        print(f"\n{key}:")
        for field, percent in value.items():
            print(f"  {field}: {percent}")
    else:
        print(f"{key}: {value}")
