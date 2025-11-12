# Placeholder example file.

     # 分布式系统自上而下性能分析框架
     import pandas as pd
     import matplotlib.pyplot as plt
     import seaborn as sns
     import networkx as nx
     from datetime import datetime, timedelta

     class PerformanceAnalyzer:
         def __init__(self):
             self.service_graph = nx.DiGraph()

         def load_service_metrics(self, metrics_data_path):
             """加载服务性能指标数据"""
             return pd.read_csv(metrics_data_path)

         def build_service_dependency_graph(self, dependencies_path):
             """构建服务依赖关系图"""
             dependencies = pd.read_csv(dependencies_path)

             for _, row in dependencies.iterrows():
                 self.service_graph.add_edge(row['source_service'], row['target_service'],
                                           latency=row['avg_latency'], throughput=row['throughput'])

             return self.service_graph

         def identify_bottlenecks_top_down(self, metrics_data, threshold_percent=20):
             """自上而下识别性能瓶颈"""
             # 1. 计算每个服务的性能退化百分比
             baseline_metrics = metrics_data[metrics_data['is_baseline'] == True]
             current_metrics = metrics_data[metrics_data['is_baseline'] == False]

             bottlenecks = []

             # 按服务分组分析
             for service in metrics_data['service_name'].unique():
                 baseline = baseline_metrics[baseline_metrics['service_name'] == service]
                 current = current_metrics[current_metrics['service_name'] == service]

                 if len(baseline) > 0 and len(current) > 0:
                     # 计算关键指标的变化
                     rt_change = ((current['p95_response_time'].mean() -
                                 baseline['p95_response_time'].mean()) /
                                 baseline['p95_response_time'].mean()) * 100

                     tp_change = ((current['throughput'].mean() -
                                 baseline['throughput'].mean()) /
                                 baseline['throughput'].mean()) * 100

                     # 判断是否为瓶颈
                     if rt_change > threshold_percent or tp_change < -threshold_percent:
                         bottlenecks.append({
                             'service': service,
                             'response_time_degradation': rt_change,
                             'throughput_degradation': tp_change,
                             'severity': 'high' if rt_change > 50 or tp_change < -50 else 'medium'
                         })

             # 按严重程度排序
             bottlenecks.sort(key=lambda x: (x['severity'], abs(x['response_time_degradation']), abs(x['throughput_degradation'])),
                            reverse=True)

             return bottlenecks

         def visualize_bottlenecks(self, bottlenecks, output_path='bottleneck_visualization.png'):
             """可视化瓶颈服务"""
             if not self.service_graph:
                 print("请先构建服务依赖图")
                 return

             # 设置节点颜色和大小
             node_colors = []
             node_sizes = []

             for node in self.service_graph.nodes():
                 # 查找该服务是否是瓶颈
                 is_bottleneck = any(b['service'] == node for b in bottlenecks)
                 if is_bottleneck:
                     # 获取瓶颈严重程度
                     bottleneck = next(b for b in bottlenecks if b['service'] == node)
                     node_colors.append('red' if bottleneck['severity'] == 'high' else 'orange')
                     node_sizes.append(700)
                 else:
                     node_colors.append('lightblue')
                     node_sizes.append(300)

             # 绘制图
             plt.figure(figsize=(12, 8))
             pos = nx.spring_layout(self.service_graph, k=0.3)

             # 绘制节点和边
             nx.draw_networkx_nodes(self.service_graph, pos, node_color=node_colors,
                                  node_size=node_sizes, alpha=0.8)
             nx.draw_networkx_edges(self.service_graph, pos, width=1.0, alpha=0.5)
             nx.draw_networkx_labels(self.service_graph, pos, font_size=10)

             # 添加瓶颈标签
             bottleneck_labels = {b['service']: f"{b['service']}\nRT: {b['response_time_degradation']:.1f}%"
                                 for b in bottlenecks}
             nx.draw_networkx_labels(self.service_graph, pos, labels=bottleneck_labels,
                                  font_size=8, font_color='black', font_weight='bold')

             plt.title('分布式系统性能瓶颈可视化')
             plt.axis('off')
             plt.tight_layout()
             plt.savefig(output_path)
             print(f"瓶颈可视化图已保存至: {output_path}")
