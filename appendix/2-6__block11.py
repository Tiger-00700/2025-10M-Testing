# 数据血缘分析示例代码
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from graphviz import Digraph
from collections import defaultdict

class DataLineageTracker:
    """数据血缘追踪器"""
    
    def __init__(self):
        # 使用NetworkX构建有向图表示数据血缘
        self.graph = nx.DiGraph()
        # 存储转换关系的详细信息
        self.transformations = {}
    
    def add_data_source(self, source_name, source_type='database', description=''):
        """添加数据源节点"""
        self.graph.add_node(source_name, type=source_type, description=description, node_type='source')
    
    def add_data_target(self, target_name, target_type='database', description=''):
        """添加数据目标节点"""
        self.graph.add_node(target_name, type=target_type, description=description, node_type='target')
    
    def add_transformation(self, source, target, transform_type, description='', columns_mapping=None):
        """添加数据转换关系
        
        参数:
        source: 源数据节点名称
        target: 目标数据节点名称
        transform_type: 转换类型 (如 'ETL', 'JOIN', 'AGGREGATION' 等)
        description: 转换描述
        columns_mapping: 列映射关系，格式为 {target_col: [source_col1, source_col2, ...]}
        """
        # 确保源节点和目标节点存在
        if source not in self.graph.nodes:
            self.graph.add_node(source, type='unknown', description='', node_type='intermediate')
        
        if target not in self.graph.nodes:
            self.graph.add_node(target, type='unknown', description='', node_type='intermediate')
        
        # 添加边表示数据流向
        edge_id = f"{source}->{target}"
        self.graph.add_edge(source, target, transform_type=transform_type, edge_id=edge_id)
        
        # 存储转换的详细信息
        self.transformations[edge_id] = {
            'source': source,
            'target': target,
            'transform_type': transform_type,
            'description': description,
            'columns_mapping': columns_mapping or {}
        }
    
    def get_upstream_dependencies(self, node_name):
        """获取节点的所有上游依赖"""
        if node_name not in self.graph.nodes:
            return []
        
        # 使用广度优先搜索获取所有上游节点
        upstream_nodes = set()
        queue = [node_name]
        
        while queue:
            current = queue.pop(0)
            predecessors = list(self.graph.predecessors(current))
            upstream_nodes.update(predecessors)
            queue.extend(predecessors)
        
        return list(upstream_nodes)
    
    def get_downstream_impacts(self, node_name):
        """获取节点的所有下游影响"""
        if node_name not in self.graph.nodes:
            return []
        
        # 使用广度优先搜索获取所有下游节点
        downstream_nodes = set()
        queue = [node_name]
        
        while queue:
            current = queue.pop(0)
            successors = list(self.graph.successors(current))
            downstream_nodes.update(successors)
            queue.extend(successors)
        
        return list(downstream_nodes)
    
    def get_column_lineage(self, target_node, target_column):
        """追踪目标列的血缘关系"""
        lineage_path = []
        visited = set()
        
        def dfs(current_node, current_col):
            # 标记已访问的路径
            path_key = (current_node, current_col)
            if path_key in visited:
                return
            visited.add(path_key)
            
            # 遍历所有进入当前节点的边
            for pred in self.graph.predecessors(current_node):
                edge_id = f"{pred}->{current_node}"
                
                if edge_id in self.transformations:
                    transform_info = self.transformations[edge_id]
                    columns_mapping = transform_info.get('columns_mapping', {})
                    
                    # 查找当前列对应的源列
                    for t_col, s_cols in columns_mapping.items():
                        if t_col == current_col:
                            lineage_path.append({
                                'source_node': pred,
                                'target_node': current_node,
                                'source_columns': s_cols,
                                'target_column': current_col,
                                'transform_type': transform_info['transform_type']
                            })
                            
                            # 递归追踪源列
                            for s_col in s_cols:
                                dfs(pred, s_col)
        
        dfs(target_node, target_column)
        return lineage_path
    
    def visualize_lineage_graph(self, output_file='data_lineage_graph.png', highlight_node=None):
        """可视化数据血缘图"""
        # 使用Graphviz创建更美观的图形
        dot = Digraph(comment='Data Lineage')
        dot.attr(rankdir='LR')  # 从左到右布局
        dot.attr(size='12,8')
        
        # 设置节点样式
        for node in self.graph.nodes:
            node_attrs = self.graph.nodes[node]
            node_type = node_attrs.get('node_type', 'intermediate')
            
            # 根据节点类型设置不同的样式
            if node_type == 'source':
                dot.node(node, node, shape='box', style='filled', fillcolor='#90EE90')  # 浅绿色
            elif node_type == 'target':
                dot.node(node, node, shape='box', style='filled', fillcolor='#FFB6C1')  # 浅红色
            else:
                dot.node(node, node, shape='box')
            
            # 高亮特定节点
            if highlight_node and node == highlight_node:
                dot.node(node, node, shape='box', style='filled, bold', fillcolor='#FFFF99')  # 浅黄色
        
        # 添加边
        for source, target, attrs in self.graph.edges(data=True):
            transform_type = attrs.get('transform_type', '')
            dot.edge(source, target, label=transform_type)
        
        # 保存图形
        dot.render(output_file.replace('.png', ''), format='png', cleanup=True)
        print(f"数据血缘图已保存至: {output_file}")
    
    def generate_impact_analysis_report(self, affected_node):
        """生成影响分析报告"""
        report = {
            'affected_node': affected_node,
            'upstream_dependencies': self.get_upstream_dependencies(affected_node),
            'downstream_impacts': self.get_downstream_impacts(affected_node),
            'transformations_affected': []
        }
        
        # 找出受影响的转换
        for edge_id, transform in self.transformations.items():
            if transform['source'] == affected_node or transform['target'] == affected_node:
                report['transformations_affected'].append(transform)
        
        return report

# 示例：构建和分析数据血缘
def data_lineage_example():
    # 创建数据血缘追踪器
    tracker = DataLineageTracker()
    
    # 添加数据源
    tracker.add_data_source('customers_raw', 'database', '原始客户数据')
    tracker.add_data_source('orders_raw', 'database', '原始订单数据')
    tracker.add_data_source('products_raw', 'database', '原始产品数据')
    
    # 添加中间转换节点
    tracker.add_transformation(
        'customers_raw', 
        'customers_cleaned', 
        'CLEAN', 
        '客户数据清洗',
        {'customer_id': ['customer_id'], 'name': ['name'], 'email': ['email'], 'region': ['region']}
    )
    
    tracker.add_transformation(
        'orders_raw', 
        'orders_cleaned', 
        'CLEAN', 
        '订单数据清洗',
        {'order_id': ['order_id'], 'customer_id': ['customer_id'], 'product_id': ['product_id'], 
         'amount': ['amount'], 'order_date': ['order_date']}
    )
    
    tracker.add_transformation(
        'products_raw', 
        'products_cleaned', 
        'CLEAN', 
        '产品数据清洗',
        {'product_id': ['product_id'], 'product_name': ['name'], 'category': ['category'], 'price': ['price']}
    )
    
    # 添加数据集成转换
    tracker.add_transformation(
        'orders_cleaned', 
        'order_customer_joined', 
        'JOIN', 
        '订单与客户数据关联',
        {'order_id': ['order_id'], 'customer_id': ['customer_id'], 'amount': ['amount'],
         'customer_name': ['customer_id'], 'customer_region': ['customer_id']}
    )
    
    tracker.add_transformation(
        'customers_cleaned', 
        'order_customer_joined', 
        'JOIN', 
        '客户数据关联到订单',
        {'customer_name': ['name'], 'customer_region': ['region']}
    )
    
    # 添加数据聚合转换
    tracker.add_transformation(
        'order_customer_joined', 
        'sales_by_region', 
        'AGGREGATION', 
        '按地区聚合销售数据',
        {'region': ['customer_region'], 'total_sales': ['amount'], 'order_count': ['order_id']}
    )
    
    # 添加产品关联
    tracker.add_transformation(
        'order_customer_joined', 
        'order_details', 
        'JOIN', 
        '订单详情数据',
        {'order_id': ['order_id'], 'customer_id': ['customer_id'], 'amount': ['amount'],
         'customer_name': ['customer_name'], 'product_id': ['product_id']}
    )
    
    tracker.add_transformation(
        'products_cleaned', 
        'order_details', 
        'JOIN', 
        '产品数据关联到订单详情',
        {'product_name': ['product_name'], 'product_category': ['category']}
    )
    
    # 添加数据目标
    tracker.add_data_target('sales_by_region', 'dashboard', '地区销售报表')
    tracker.add_data_target('order_details', 'datawarehouse', '订单详情数据仓库表')
    
    # 生成数据血缘可视化
    tracker.visualize_lineage_graph()
    
    # 执行影响分析
    print("\n=== 影响分析示例 ===")
    
    # 分析customers_raw数据变更的影响
    impact_report = tracker.generate_impact_analysis_report('customers_raw')
    print(f"\n节点 'customers_raw' 变更的影响:")
    print(f"上游依赖: {impact_report['upstream_dependencies']}")
    print(f"下游影响: {impact_report['downstream_impacts']}")
    print(f"受影响的转换数量: {len(impact_report['transformations_affected'])}")
    
    # 分析sales_by_region的上游依赖
    print(f"\n节点 'sales_by_region' 的上游依赖:")
    for dep in tracker.get_upstream_dependencies('sales_by_region'):
        print(f"- {dep}")
    
    # 追踪特定列的血缘关系
    print("\n=== 列血缘追踪示例 ===")
    column_lineage = tracker.get_column_lineage('sales_by_region', 'total_sales')
    print(f"列 'total_sales' 的血缘路径:")
    for step in column_lineage:
        print(f"从 '{step['source_node']}' 列 {step['source_columns']} 通过 '{step['transform_type']}' 转换到 '{step['target_node']}' 列 '{step['target_column']}'")
    
    # 生成特定节点的高亮血缘图
    tracker.visualize_lineage_graph('sales_by_region_impact.png', highlight_node='sales_by_region')
    print("\n高亮显示 'sales_by_region' 节点的血缘图已保存至: sales_by_region_impact.png")

# 运行数据血缘分析示例
data_lineage_example()
