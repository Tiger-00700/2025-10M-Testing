# 数据质量问题影响分析示例代码
import pandas as pd
import numpy as np

# 模拟业务决策与数据质量的关系
def simulate_data_quality_impact():
    # 生成不同质量级别的数据集
    data_sizes = [1000, 10000, 100000]
    quality_levels = ['低质量', '中等质量', '高质量']
    impact_results = []
    
    for size in data_sizes:
        for quality in quality_levels:
            # 根据质量级别设置错误率
            if quality == '低质量':
                error_rate = 0.25
            elif quality == '中等质量':
                error_rate = 0.1
            else:
                error_rate = 0.02
            
            # 计算业务损失影响
            decision_errors = size * error_rate
            avg_cost_per_error = 100  # 每个错误的平均成本
            total_cost = decision_errors * avg_cost_per_error
            
            impact_results.append({
                '数据量': size,
                '数据质量': quality,
                '错误率': error_rate,
                '决策错误数': decision_errors,
                '估计损失(元)': total_cost
            })
    
    return pd.DataFrame(impact_results)

# 执行分析并展示结果
df_impact = simulate_data_quality_impact()
print("数据质量对业务决策的影响分析：")
print(df_impact)
