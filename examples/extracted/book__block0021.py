
     # 性能数据高级分析工具
     import pandas as pd
     import numpy as np
     import matplotlib.pyplot as plt
     from statsmodels.tsa.seasonal import seasonal_decompose
     from sklearn.ensemble import IsolationForest
     from sklearn.preprocessing import StandardScaler

     def analyze_performance_time_series(metrics_data, metric_name, window=60):
         # 转换为时间序列
         metrics_data['timestamp'] = pd.to_datetime(metrics_data['timestamp'])
         metrics_data.set_index('timestamp', inplace=True)

         # 1. 计算基本统计量
         basic_stats = {
             'mean': metrics_data[metric_name].mean(),
             'median': metrics_data[metric_name].median(),
             'std': metrics_data[metric_name].std(),
             'min': metrics_data[metric_name].min(),
             'max': metrics_data[metric_name].max(),
             'p50': metrics_data[metric_name].quantile(0.5),
             'p95': metrics_data[metric_name].quantile(0.95),
             'p99': metrics_data[metric_name].quantile(0.99)
         }

         # 2. 时间序列分解（如果有足够的数据点）
         if len(metrics_data) >= 2 * 24 * 7:  # 至少两周数据
             try:
                 result = seasonal_decompose(
                     metrics_data[metric_name],
                     model='additive',
                     period=24  # 假设24小时周期
                 )

                 # 绘制分解图
                 plt.figure(figsize=(15, 10))
                 plt.subplot(411)
                 plt.plot(result.observed)
                 plt.title('观测值')
                 plt.subplot(412)
                 plt.plot(result.trend)
                 plt.title('趋势')
                 plt.subplot(413)
                 plt.plot(result.seasonal)
                 plt.title('季节性')
                 plt.subplot(414)
                 plt.plot(result.resid)
                 plt.title('残差')
                 plt.tight_layout()
                 plt.savefig(f'{metric_name}_decomposition.png')
             except Exception as e:
                 print(f"时间序列分解失败: {e}")

         # 3. 异常检测
         scaler = StandardScaler()
         scaled_data = scaler.fit_transform(metrics_data[[metric_name]])

         # 使用Isolation Forest进行异常检测
         iso_forest = IsolationForest(contamination=0.01, random_state=42)
         outliers = iso_forest.fit_predict(scaled_data)

         # 标记异常点
         metrics_data['is_outlier'] = outliers == -1
         outlier_count = metrics_data['is_outlier'].sum()

         # 4. 计算动态阈值（基于移动统计量）
         metrics_data['rolling_mean'] = metrics_data[metric_name].rolling(window=window).mean()
         metrics_data['rolling_std'] = metrics_data[metric_name].rolling(window=window).std()
         metrics_data['upper_threshold'] = metrics_data['rolling_mean'] + 3 * metrics_data['rolling_std']
         metrics_data['lower_threshold'] = metrics_data['rolling_mean'] - 3 * metrics_data['rolling_std']

         # 绘制带阈值的时间序列图
         plt.figure(figsize=(12, 6))
         plt.plot(metrics_data.index, metrics_data[metric_name], label=metric_name)
         plt.plot(metrics_data.index, metrics_data['rolling_mean'], label='移动平均')
         plt.fill_between(
             metrics_data.index,
             metrics_data['lower_threshold'],
             metrics_data['upper_threshold'],
             alpha=0.2,
             label='动态阈值范围'
         )
         plt.scatter(
             metrics_data[metrics_data['is_outlier']].index,
             metrics_data[metrics_data['is_outlier']][metric_name],
             color='red',
             label='异常点'
         )
         plt.title(f'{metric_name}时间序列分析')
         plt.legend()
         plt.grid(True)
         plt.savefig(f'{metric_name}_analysis.png')

         return {
             'basic_stats': basic_stats,
             'outlier_count': outlier_count,
             'outlier_percentage': (outlier_count / len(metrics_data)) * 100
         }
