# 数据可靠性评估示例代码
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def evaluate_reliability(monitoring_data):
    """评估数据系统的可靠性指标"""
    results = {}
    
    # 系统可用性 - 基于监控数据计算
    if 'system_status' in monitoring_data.columns:
        total_time = len(monitoring_data)
        available_time = (monitoring_data['system_status'] == 'available').sum()
        availability_rate = (available_time / total_time) * 100 if total_time > 0 else 0
        results['系统可用性'] = f"{availability_rate:.4f}%"
    
    # 错误率 - 计算数据处理错误
    if 'error_count' in monitoring_data.columns and 'total_processed' in monitoring_data.columns:
        total_errors = monitoring_data['error_count'].sum()
        total_processed = monitoring_data['total_processed'].sum()
        error_rate = (total_errors / total_processed) * 100 if total_processed > 0 else 0
        results['错误率'] = f"{error_rate:.4f}%"
    
    # 平均故障间隔时间(MTBF) - 模拟计算
    if 'downtime_start' in monitoring_data.columns and 'downtime_end' in monitoring_data.columns:
        # 过滤出有故障记录的行
        failures = monitoring_data[monitoring_data['downtime_start'].notna()]
        if len(failures) > 1:
            # 计算故障间隔时间
            failure_times = sorted(pd.to_datetime(failures['downtime_start']))
            intervals = [(failure_times[i] - failure_times[i-1]).total_seconds()/3600 for i in range(1, len(failure_times))]
            mtbf = sum(intervals) / len(intervals)
            results['平均故障间隔时间'] = f"{mtbf:.2f} 小时"
    
    # 平均修复时间(MTTR) - 模拟计算
    if 'downtime_start' in monitoring_data.columns and 'downtime_end' in monitoring_data.columns:
        # 计算修复时间
        repairs = monitoring_data[monitoring_data['downtime_start'].notna() & monitoring_data['downtime_end'].notna()]
        if len(repairs) > 0:
            repair_times = (pd.to_datetime(repairs['downtime_end']) - pd.to_datetime(repairs['downtime_start'])).dt.total_seconds()/60
            mttr = repair_times.mean()
            results['平均修复时间'] = f"{mttr:.2f} 分钟"
    
    # 备份有效性 - 模拟备份成功率
    if 'backup_status' in monitoring_data.columns:
        total_backups = len(monitoring_data)
        successful_backups = (monitoring_data['backup_status'] == 'success').sum()
        backup_success_rate = (successful_backups / total_backups) * 100 if total_backups > 0 else 0
        results['备份成功率'] = f"{backup_success_rate:.2f}%"
    
    return results

# 生成系统监控数据
def generate_monitoring_data():
    # 创建过去30天的监控数据，每分钟一条记录
    dates = pd.date_range(end=datetime.now(), periods=30*24*60, freq='min')
    
    # 生成系统状态数据
    # 99.9%的时间系统可用
    system_status = np.random.choice(['available', 'unavailable'], size=len(dates), p=[0.999, 0.001])
    
    # 生成错误计数和处理记录数
    total_processed = np.random.randint(1000, 10000, size=len(dates))
    # 错误率约为0.05%
    error_count = np.random.binomial(total_processed, 0.0005)
    
    # 生成备份状态
    # 每天进行一次备份，成功率99%
    backup_status = ['none'] * len(dates)
    backup_indices = [i for i, date in enumerate(dates) if date.hour == 2 and date.minute == 0]
    for idx in backup_indices:
        backup_status[idx] = np.random.choice(['success', 'failed'], p=[0.99, 0.01])
    
    # 生成故障时间
    downtime_start = [None] * len(dates)
    downtime_end = [None] * len(dates)
    
    # 随机插入几次故障
    for _ in range(5):
        idx = np.random.randint(0, len(dates) - 10)
        downtime_start[idx] = dates[idx]
        # 故障持续5-15分钟
        duration = np.random.randint(5, 16)
        downtime_end[idx + duration - 1] = dates[idx + duration - 1]
    
    return pd.DataFrame({
        'timestamp': dates,
        'system_status': system_status,
        'total_processed': total_processed,
        'error_count': error_count,
        'backup_status': backup_status,
        'downtime_start': downtime_start,
        'downtime_end': downtime_end
    })

# 生成监控数据并评估可靠性
monitoring_data = generate_monitoring_data()
reliability_results = evaluate_reliability(monitoring_data)
print("\n数据系统可靠性评估结果：")
for key, value in reliability_results.items():
    print(f"{key}: {value}")
