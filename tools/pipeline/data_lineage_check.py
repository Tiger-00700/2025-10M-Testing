#!/usr/bin/env python3
"""
数据血缘检查工具

用于分析和验证大数据系统中的数据血缘关系，确保数据流的完整性和正确性。
支持数据表、字段级别的血缘追踪和影响分析。
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

@dataclass
class DataLineageNode:
    """数据血缘节点"""
    node_id: str
    node_type: str  # 'table', 'column', 'pipeline', 'job'
    name: str
    database: Optional[str] = None
    schema: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class DataLineageEdge:
    """数据血缘边"""
    source_id: str
    target_id: str
    edge_type: str  # 'reads_from', 'writes_to', 'transforms', 'joins'
    transformation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class DataLineageTracker:
    """数据血缘追踪器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.nodes: Dict[str, DataLineageNode] = {}
        self.edges: List[DataLineageEdge] = []
        self.graph = nx.DiGraph()

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """加载配置"""
        default_config = {
            'storage': {
                'type': 'file',
                'path': './data_lineage.json'
            },
            'visualization': {
                'enabled': True,
                'format': 'png',
                'layout': 'hierarchical'
            },
            'analysis': {
                'max_depth': 10,
                'include_indirect': True
            }
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def add_node(self, node: DataLineageNode):
        """添加节点"""
        self.nodes[node.node_id] = node
        self.graph.add_node(node.node_id, **node.metadata)

    def add_edge(self, edge: DataLineageEdge):
        """添加边"""
        self.edges.append(edge)
        self.graph.add_edge(edge.source_id, edge.target_id,
                          edge_type=edge.edge_type,
                          transformation=edge.transformation,
                          **edge.metadata)

    def track_table_lineage(self, table_name: str, database: str = 'default',
                          operation: str = 'create') -> str:
        """追踪表级血缘"""
        node_id = f"table_{database}_{table_name}"

        node = DataLineageNode(
            node_id=node_id,
            node_type='table',
            name=table_name,
            database=database,
            metadata={
                'operation': operation,
                'table_type': 'managed'
            }
        )

        self.add_node(node)
        return node_id

    def track_column_lineage(self, table_id: str, column_name: str,
                           data_type: str, source_columns: List[str] = None) -> str:
        """追踪字段级血缘"""
        node_id = f"column_{table_id}_{column_name}"

        node = DataLineageNode(
            node_id=node_id,
            node_type='column',
            name=column_name,
            metadata={
                'data_type': data_type,
                'nullable': True,
                'source_columns': source_columns or []
            }
        )

        self.add_node(node)

        # 添加字段到表的边
        if table_id in self.nodes:
            edge = DataLineageEdge(
                source_id=table_id,
                target_id=node_id,
                edge_type='contains',
                metadata={'relationship': 'table_column'}
            )
            self.add_edge(edge)

        # 添加源字段的边
        if source_columns:
            for source_col in source_columns:
                source_col_id = f"column_{table_id}_{source_col}"
                if source_col_id in self.nodes:
                    edge = DataLineageEdge(
                        source_id=source_col_id,
                        target_id=node_id,
                        edge_type='transforms',
                        transformation='derived'
                    )
                    self.add_edge(edge)

        return node_id

    def track_pipeline_lineage(self, pipeline_name: str, input_tables: List[str],
                             output_tables: List[str], transformations: Dict[str, str]) -> str:
        """追踪管道级血缘"""
        pipeline_id = f"pipeline_{pipeline_name}"

        node = DataLineageNode(
            node_id=pipeline_id,
            node_type='pipeline',
            name=pipeline_name,
            metadata={
                'input_tables': input_tables,
                'output_tables': output_tables,
                'transformations': transformations
            }
        )

        self.add_node(node)

        # 添加输入表边
        for input_table in input_tables:
            input_table_id = f"table_default_{input_table}"
            if input_table_id in self.nodes:
                edge = DataLineageEdge(
                    source_id=input_table_id,
                    target_id=pipeline_id,
                    edge_type='reads_from'
                )
                self.add_edge(edge)

        # 添加输出表边
        for output_table in output_tables:
            output_table_id = f"table_default_{output_table}"
            if output_table_id in self.nodes:
                edge = DataLineageEdge(
                    source_id=pipeline_id,
                    target_id=output_table_id,
                    edge_type='writes_to'
                )
                self.add_edge(edge)

        return pipeline_id

    def get_upstream_lineage(self, node_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """获取上游血缘"""
        if node_id not in self.graph:
            return {'error': f'Node {node_id} not found'}

        upstream_nodes = set()
        visited = set()

        def traverse_upstream(current_id: str, depth: int):
            if depth >= max_depth or current_id in visited:
                return
            visited.add(current_id)

            for predecessor in self.graph.predecessors(current_id):
                upstream_nodes.add(predecessor)
                traverse_upstream(predecessor, depth + 1)

        traverse_upstream(node_id, 0)

        return {
            'target_node': node_id,
            'upstream_nodes': list(upstream_nodes),
            'upstream_count': len(upstream_nodes),
            'max_depth_reached': len(visited) >= max_depth
        }

    def get_downstream_lineage(self, node_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """获取下游血缘"""
        if node_id not in self.graph:
            return {'error': f'Node {node_id} not found'}

        downstream_nodes = set()
        visited = set()

        def traverse_downstream(current_id: str, depth: int):
            if depth >= max_depth or current_id in visited:
                return
            visited.add(current_id)

            for successor in self.graph.successors(current_id):
                downstream_nodes.add(successor)
                traverse_downstream(successor, depth + 1)

        traverse_downstream(node_id, 0)

        return {
            'source_node': node_id,
            'downstream_nodes': list(downstream_nodes),
            'downstream_count': len(downstream_nodes),
            'max_depth_reached': len(visited) >= max_depth
        }

    def analyze_impact(self, node_id: str) -> Dict[str, Any]:
        """分析变更影响"""
        upstream = self.get_upstream_lineage(node_id)
        downstream = self.get_downstream_lineage(node_id)

        impact_analysis = {
            'changed_node': node_id,
            'upstream_impact': upstream,
            'downstream_impact': downstream,
            'total_affected_nodes': upstream.get('upstream_count', 0) + downstream.get('downstream_count', 0),
            'risk_level': self._calculate_risk_level(upstream, downstream)
        }

        return impact_analysis

    def _calculate_risk_level(self, upstream: Dict, downstream: Dict) -> str:
        """计算风险等级"""
        upstream_count = upstream.get('upstream_count', 0)
        downstream_count = downstream.get('downstream_count', 0)

        total_impact = upstream_count + downstream_count

        if total_impact > 100:
            return 'critical'
        elif total_impact > 50:
            return 'high'
        elif total_impact > 20:
            return 'medium'
        else:
            return 'low'

    def detect_cycles(self) -> List[List[str]]:
        """检测循环依赖"""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except nx.NetworkXError:
            return []

    def validate_lineage(self) -> Dict[str, Any]:
        """验证血缘完整性"""
        validation_results = {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'orphaned_nodes': [],
            'invalid_edges': [],
            'cycles_detected': [],
            'is_valid': True
        }

        # 检查孤立节点
        for node_id in self.nodes:
            if self.graph.degree(node_id) == 0:
                validation_results['orphaned_nodes'].append(node_id)

        # 检查无效边
        for edge in self.edges:
            if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
                validation_results['invalid_edges'].append({
                    'source': edge.source_id,
                    'target': edge.target_id
                })

        # 检查循环
        cycles = self.detect_cycles()
        validation_results['cycles_detected'] = cycles

        # 确定整体有效性
        if (validation_results['orphaned_nodes'] or
            validation_results['invalid_edges'] or
            validation_results['cycles_detected']):
            validation_results['is_valid'] = False

        return validation_results

    def export_lineage(self, format: str = 'json') -> str:
        """导出血缘数据"""
        if format == 'json':
            data = {
                'nodes': [
                    {
                        'id': node.node_id,
                        'type': node.node_type,
                        'name': node.name,
                        'database': node.database,
                        'schema': node.schema,
                        'metadata': node.metadata,
                        'created_at': node.created_at.isoformat(),
                        'updated_at': node.updated_at.isoformat()
                    } for node in self.nodes.values()
                ],
                'edges': [
                    {
                        'source': edge.source_id,
                        'target': edge.target_id,
                        'type': edge.edge_type,
                        'transformation': edge.transformation,
                        'metadata': edge.metadata,
                        'created_at': edge.created_at.isoformat()
                    } for edge in self.edges
                ]
            }
            return json.dumps(data, indent=2, ensure_ascii=False)

        elif format == 'graphml':
            # 导出为GraphML格式用于可视化
            nx.write_graphml(self.graph, 'data_lineage.graphml')
            return 'Exported to data_lineage.graphml'

        return 'Unsupported format'

    def visualize_lineage(self, output_path: str = 'lineage_visualization.png',
                         layout: str = 'hierarchical'):
        """可视化血缘图"""
        if not self.config['visualization']['enabled']:
            return

        plt.figure(figsize=(12, 8))

        # 选择布局
        if layout == 'hierarchical':
            pos = nx.spring_layout(self.graph, k=2, iterations=50)
        elif layout == 'circular':
            pos = nx.circular_layout(self.graph)
        else:
            pos = nx.random_layout(self.graph)

        # 绘制节点
        node_colors = []
        for node_id in self.graph.nodes():
            node = self.nodes.get(node_id)
            if node:
                if node.node_type == 'table':
                    node_colors.append('lightblue')
                elif node.node_type == 'column':
                    node_colors.append('lightgreen')
                elif node.node_type == 'pipeline':
                    node_colors.append('orange')
                else:
                    node_colors.append('gray')
            else:
                node_colors.append('gray')

        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors,
                             node_size=500, alpha=0.8)

        # 绘制边
        nx.draw_networkx_edges(self.graph, pos, edge_color='gray', arrows=True,
                             arrowsize=20, alpha=0.6)

        # 添加标签
        labels = {node_id: self.nodes[node_id].name if node_id in self.nodes else node_id
                 for node_id in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)

        plt.title('Data Lineage Graph')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Lineage visualization saved to {output_path}")

    def save_lineage(self):
        """保存血缘数据"""
        storage_config = self.config['storage']

        if storage_config['type'] == 'file':
            data = self.export_lineage('json')
            with open(storage_config['path'], 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"Lineage data saved to {storage_config['path']}")

    def load_lineage(self):
        """加载血缘数据"""
        storage_config = self.config['storage']

        if storage_config['type'] == 'file' and os.path.exists(storage_config['path']):
            with open(storage_config['path'], 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 重新构建节点和边
            for node_data in data.get('nodes', []):
                node = DataLineageNode(
                    node_id=node_data['id'],
                    node_type=node_data['type'],
                    name=node_data['name'],
                    database=node_data.get('database'),
                    schema=node_data.get('schema'),
                    metadata=node_data.get('metadata', {}),
                    created_at=datetime.fromisoformat(node_data['created_at']),
                    updated_at=datetime.fromisoformat(node_data['updated_at'])
                )
                self.add_node(node)

            for edge_data in data.get('edges', []):
                edge = DataLineageEdge(
                    source_id=edge_data['source'],
                    target_id=edge_data['target'],
                    edge_type=edge_data['type'],
                    transformation=edge_data.get('transformation'),
                    metadata=edge_data.get('metadata', {}),
                    created_at=datetime.fromisoformat(edge_data['created_at'])
                )
                self.add_edge(edge)

            print(f"Lineage data loaded from {storage_config['path']}")

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='数据血缘检查工具')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--analyze', help='分析节点ID')
    parser.add_argument('--validate', action='store_true', help='验证血缘完整性')
    parser.add_argument('--visualize', action='store_true', help='生成可视化图')
    parser.add_argument('--export', help='导出格式 (json/graphml)')

    args = parser.parse_args()

    tracker = DataLineageTracker(args.config)

    # 示例：构建简单的数据血缘
    if not args.analyze and not args.validate and not args.visualize and not args.export:
        # 添加示例数据
        tracker.track_table_lineage('users', 'ecommerce')
        tracker.track_table_lineage('orders', 'ecommerce')
        tracker.track_table_lineage('user_summary', 'analytics')

        tracker.track_column_lineage('table_ecommerce_users', 'user_id', 'bigint')
        tracker.track_column_lineage('table_ecommerce_users', 'email', 'varchar(255)')
        tracker.track_column_lineage('table_ecommerce_orders', 'user_id', 'bigint')
        tracker.track_column_lineage('table_ecommerce_orders', 'amount', 'decimal(10,2)')

        tracker.track_pipeline_lineage(
            'user_order_summary',
            ['users', 'orders'],
            ['user_summary'],
            {'aggregation': 'sum(amount)', 'group_by': 'user_id'}
        )

        tracker.save_lineage()

    if args.analyze:
        result = tracker.analyze_impact(args.analyze)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.validate:
        result = tracker.validate_lineage()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    if args.visualize:
        tracker.visualize_lineage()

    if args.export:
        result = tracker.export_lineage(args.export)
        print(result)

if __name__ == "__main__":
    main()</content>
<parameter name="filePath">e:\DONT_TOUCH\10M-2025-Testing\tools\pipeline\data_lineage_check.py