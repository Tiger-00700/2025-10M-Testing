# 数据时效性评估示例代码
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def evaluate_timeliness(data):
    """评估数据集的时效性指标"""
    results = {}
    current_time = datetime.now()
    
    # 数据新鲜度 - 计算数据最后更新时间到当前的时间差
    if 'order_date' in data.columns:
        # 转换为datetime类型
        data['order_date'] = pd.to_datetime(data['order_date'])
        latest_date = data['order_date'].max()
        days_since_latest = (current_time - latest_date).days
        results['数据新鲜度'] = f"{days_since_latest} 天"
    
    # 更新及时性 - 检查数据是否按照预期频率更新
    if 'order_date' in data.columns:
        # 计算每日记录数，评估更新频率
        daily_counts = data.groupby(data['order_date'].dt.date).size()
        expected_updates = 30  # 假设期望最近30天每天都有更新
        actual_updates = len(daily_counts)
        update_timeliness = (actual_updates / expected_updates) * 100 if expected_updates > 0 else 0
        results['更新及时性'] = f"{update_timeliness:.2f}%"
    
    # 处理延迟 - 模拟计算从数据生成到处理完成的时间
    if 'processing_time' in data.columns:
        avg_delay = data['processing_time'].mean()
        max_delay = data['processing_time'].max()
        results['平均处理延迟'] = f"{avg_delay:.2f} 秒"
        results['最大处理延迟'] = f"{max_delay:.2f} 秒"
    
    # 时效性分级 - 根据数据年龄进行分级
    if 'order_date' in data.columns:
        # 定义时效性级别
        data_age = (current_time - data['order_date']).dt.days
        
        # 计算各级别数据的比例
        fresh_data = (data_age <= 7).sum()  # 7天内的数据
        recent_data = ((data_age > 7) & (data_age <= 30)).sum()  # 7-30天的数据
        old_data = (data_age > 30).sum()  # 30天以上的数据
        
        total = len(data)
        results['数据时效性分级'] = {
            '新鲜数据(7天内)': f"{fresh_data/total*100:.2f}%",
            '近期数据(7-30天)': f"{recent_data/total*100:.2f}%",
            '历史数据(30天以上)': f"{old_data/total*100:.2f}%"
        }
    
    return results

# 添加处理时间列用于延迟评估
test_data['processing_time'] = np.random.exponential(scale=5, size=len(test_data))

# 运行时效性评估
timeliness_results = evaluate_timeliness(test_data)
print("\n数据时效性评估结果：")
for key, value in timeliness_results.items():
    if isinstance(value, dict):
        print(f"\n{key}:")
        for level, percent in value.items():
            print(f"  {level}: {percent}")
    else:
        print(f"{key}: {value}")
