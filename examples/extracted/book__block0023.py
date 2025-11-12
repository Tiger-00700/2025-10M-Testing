
     # 基线趋势分析工具
     import pandas as pd
     import matplotlib.pyplot as plt
     import seaborn as sns
     import numpy as np
     from scipy.stats import linregress
     import glob
     import json

     def analyze_baseline_trends(baselines_dir, metric_name):
         # 收集所有基线数据
         baseline_files = glob.glob(f"{baselines_dir}/baseline_*.json")
         baseline_data = []

         for file in sorted(baseline_files):
             with open(file, 'r') as f:
                 data = json.load(f)
                 timestamp = datetime.strptime(data['timestamp'], "%Y%m%d_%H%M%S")

                 if metric_name in data['metrics']:
                     baseline_data.append({
                         'timestamp': timestamp,
                         'version': data['version'],
                         'value': data['metrics'][metric_name],
                         'system_version': data['metadata'].get('system_version', 'unknown')
                     })

         if not baseline_data:
             print(f"未找到指标 {metric_name} 的基线数据")
             return

         # 创建DataFrame
         df = pd.DataFrame(baseline_data)
         df.sort_values('timestamp', inplace=True)

         # 计算趋势线
         x = np.arange(len(df))
         slope, intercept, r_value, p_value, std_err = linregress(x, df['value'])
         trend_line = intercept + slope * x

         # 计算百分比变化
         df['percent_change'] = df['value'].pct_change() * 100

         # 绘图
         plt.figure(figsize=(14, 8))

         # 主图：指标趋势
         ax1 = plt.subplot(2, 1, 1)
         ax1.plot(df['timestamp'], df['value'], 'o-', label=metric_name)
         ax1.plot(df['timestamp'], trend_line, '--', label=f'趋势线 (斜率: {slope:.6f})')

         # 标记系统版本变更
         version_changes = df[df['system_version'] != df['system_version'].shift()]
         for _, row in version_changes.iterrows():
             if pd.notna(row['timestamp']):  # 确保timestamp不为None
                 ax1.axvline(x=row['timestamp'], color='r', linestyle='--', alpha=0.5)
                 ax1.text(row['timestamp'], df['value'].max() * 0.95,
                         f"v{row['system_version']}", rotation=90, verticalalignment='top')

         ax1.set_title(f"基线指标 {metric_name} 趋势分析")
         ax1.set_ylabel(metric_name)
         ax1.grid(True)
         ax1.legend()

         # 次图：百分比变化
         ax2 = plt.subplot(2, 1, 2, sharex=ax1)
         ax2.bar(df['timestamp'], df['percent_change'], alpha=0.6, label='环比变化率 (%)')
         ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
         ax2.set_ylabel('环比变化率 (%)')
         ax2.set_xlabel('时间')
         ax2.grid(True)
         ax2.legend()

         plt.tight_layout()
         plt.savefig(f"{metric_name}_trend_analysis.png")

         # 打印分析结果
         print(f"趋势分析结果: {metric_name}")
         print(f"线性相关系数 (R²): {r_value**2:.4f}")
         print(f"趋势显著性 (p值): {p_value:.4f}")
         print(f"平均变化率: {np.mean(df['percent_change'].dropna()):.4f}%")
         print(f"最大正向变化: {np.max(df['percent_change'].dropna()):.4f}%")
         print(f"最大负向变化: {np.min(df['percent_change'].dropna()):.4f}%")

         # 性能退化预警
         if slope > 0 and metric_name in ['response_time', 'execution_time', 'latency']:
             print("⚠️ 警告: 响应时间/执行时间/延迟呈上升趋势")
         elif slope < 0 and metric_name in ['throughput', 'bandwidth']:
             print("⚠️ 警告: 吞吐量/带宽呈下降趋势")
