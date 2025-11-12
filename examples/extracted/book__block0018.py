
     # 扩展性分析工具
     import pandas as pd
     import matplotlib.pyplot as plt

     def calculate_scalability_metrics(node_counts, throughput_values):
         # 构建数据框
         df = pd.DataFrame({
             'nodes': node_counts,
             'throughput': throughput_values
         })

         # 计算理论理想吞吐量（线性扩展）
         baseline_throughput = throughput_values[0]
         df['ideal_throughput'] = baseline_throughput * (df['nodes'] / df['nodes'].iloc[0])

         # 计算扩展性系数
         df['scalability_factor'] = df['throughput'] / df['ideal_throughput']

         # 计算加速比
         df['speedup'] = df['throughput'] / df['throughput'].iloc[0]

         # 计算效率
         df['efficiency'] = (df['throughput'] / df['nodes']) / (df['throughput'].iloc[0] / df['nodes'].iloc[0])

         # 绘制扩展性图表
         plt.figure(figsize=(12, 6))
         plt.subplot(1, 2, 1)
         plt.plot(df['nodes'], df['throughput'], 'o-', label='实际吞吐量')
         plt.plot(df['nodes'], df['ideal_throughput'], '--', label='理想线性扩展')
         plt.xlabel('节点数量')
         plt.ylabel('吞吐量')
         plt.title('系统水平扩展性')
         plt.legend()
         plt.grid(True)

         plt.subplot(1, 2, 2)
         plt.plot(df['nodes'], df['efficiency'] * 100, 'o-', color='orange')
         plt.xlabel('节点数量')
         plt.ylabel('效率 (%)')
         plt.title('扩展效率')
         plt.grid(True)
         plt.ylim(0, 105)

         plt.tight_layout()
         plt.savefig('scalability_analysis.png')

         return df

     # 示例使用
     node_counts = [2, 4, 8, 16, 32]
     throughput_values = [1000, 1950, 3800, 7200, 13000]

     result = calculate_scalability_metrics(node_counts, throughput_values)
     print(result)
