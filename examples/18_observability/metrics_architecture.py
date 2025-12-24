#!/usr/bin/env python3
"""
指标体系架构设计与测试工具
提供指标分层设计、采集验证、阈值测试等功能

作者: 2025-10M-Testing Team
版本: 1.0.0
"""

import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import statistics

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricLayer(Enum):
    """指标层次枚举"""
    BUSINESS = "business"
    SERVICE = "service"
    SYSTEM = "system"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class MetricDefinition:
    """指标定义"""
    name: str
    type: str  # counter, gauge, histogram, summary
    description: str
    layer: MetricLayer
    unit: str
    threshold: Optional[float] = None
    alert_level: Optional[str] = None
    collection_interval: int = 60  # seconds


@dataclass
class MetricValue:
    """指标值"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]


class MetricsArchitectureManager:
    """指标体系架构管理器"""

    def __init__(self, config_path: str = "metrics_architecture.yml"):
        self.config = self._load_config(config_path)
        self.metrics_definitions: Dict[str, MetricDefinition] = {}
        self.metrics_data: List[MetricValue] = []
        self._load_metric_definitions()

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except ImportError:
            with open(config_path.replace('.yml', '.json'), 'r', encoding='utf-8') as f:
                return json.load(f)

    def _load_metric_definitions(self):
        """加载指标定义"""
        for layer_name, layer_config in self.config['layers'].items():
            layer = MetricLayer(layer_name)

            for metric_config in layer_config['metrics']:
                metric = MetricDefinition(
                    name=metric_config['name'],
                    type=metric_config['type'],
                    description=metric_config['description'],
                    layer=layer,
                    unit=metric_config.get('unit', ''),
                    threshold=metric_config.get('threshold'),
                    alert_level=metric_config.get('alert_level'),
                    collection_interval=layer_config['collection'].get('interval', 60)
                )
                self.metrics_definitions[metric.name] = metric

    def validate_metrics_architecture(self) -> Dict[str, Any]:
        """验证指标体系架构"""
        logger.info("开始验证指标体系架构")

        results = {
            'layer_completeness': self._check_layer_completeness(),
            'metric_definitions': self._validate_metric_definitions(),
            'collection_coverage': self._check_collection_coverage(),
            'threshold_reasonableness': self._validate_thresholds(),
            'naming_consistency': self._check_naming_consistency()
        }

        # 计算整体评分
        scores = [result.get('score', 0) for result in results.values() if isinstance(result, dict)]
        overall_score = statistics.mean(scores) if scores else 0

        results['overall_score'] = overall_score
        results['recommendations'] = self._generate_recommendations(results)

        return results

    def _check_layer_completeness(self) -> Dict[str, Any]:
        """检查层次完整性"""
        expected_layers = {layer.value for layer in MetricLayer}
        actual_layers = {layer.value for layer in {m.layer.value for m in self.metrics_definitions.values()}}

        completeness_score = len(actual_layers & expected_layers) / len(expected_layers)

        return {
            'expected_layers': list(expected_layers),
            'actual_layers': list(actual_layers),
            'missing_layers': list(expected_layers - actual_layers),
            'score': completeness_score * 100
        }

    def _validate_metric_definitions(self) -> Dict[str, Any]:
        """验证指标定义"""
        issues = []

        for name, metric in self.metrics_definitions.items():
            # 检查必需字段
            if not metric.description:
                issues.append(f"指标 {name} 缺少描述")

            if not metric.unit and metric.type in ['gauge', 'counter']:
                issues.append(f"指标 {name} 缺少单位定义")

            # 检查阈值合理性
            if metric.threshold is not None:
                if metric.type == 'histogram' and not isinstance(metric.threshold, list):
                    issues.append(f"直方图指标 {name} 的阈值应为列表")

        return {
            'total_metrics': len(self.metrics_definitions),
            'issues': issues,
            'score': 100 - (len(issues) * 10)  # 每个问题扣10分
        }

    def _check_collection_coverage(self) -> Dict[str, Any]:
        """检查采集覆盖率"""
        # 模拟采集覆盖率检查
        coverage_by_layer = {}
        for layer in MetricLayer:
            layer_metrics = [m for m in self.metrics_definitions.values() if m.layer == layer]
            # 假设80%的指标能正常采集
            coverage_by_layer[layer.value] = len(layer_metrics) * 0.8

        overall_coverage = statistics.mean(coverage_by_layer.values())

        return {
            'coverage_by_layer': coverage_by_layer,
            'overall_coverage': overall_coverage,
            'score': overall_coverage * 100
        }

    def _validate_thresholds(self) -> Dict[str, Any]:
        """验证阈值合理性"""
        issues = []

        for name, metric in self.metrics_definitions.items():
            if metric.threshold is not None:
                # 检查阈值是否在合理范围内
                if metric.name.endswith('_rate') and metric.threshold > 1:
                    issues.append(f"比率指标 {name} 的阈值 {metric.threshold} 超过1")

                if metric.name.endswith('_latency') and metric.threshold < 0:
                    issues.append(f"延迟指标 {name} 的阈值 {metric.threshold} 为负数")

        return {
            'threshold_issues': issues,
            'score': 100 - (len(issues) * 5)  # 每个问题扣5分
        }

    def _check_naming_consistency(self) -> Dict[str, Any]:
        """检查命名一致性"""
        naming_patterns = {
            'counter': ['_count', '_total'],
            'gauge': ['_current', '_usage'],
            'histogram': ['_duration', '_size'],
            'summary': ['_summary']
        }

        consistency_score = 0
        total_metrics = len(self.metrics_definitions)

        for name, metric in self.metrics_definitions.items():
            expected_suffixes = naming_patterns.get(metric.type, [])
            if expected_suffixes and any(name.endswith(suffix) for suffix in expected_suffixes):
                consistency_score += 1

        return {
            'consistency_score': consistency_score / total_metrics if total_metrics > 0 else 0,
            'score': (consistency_score / total_metrics * 100) if total_metrics > 0 else 100
        }

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if results['layer_completeness']['score'] < 80:
            recommendations.append("完善指标层次结构，确保各层指标都得到覆盖")

        if results['metric_definitions']['score'] < 90:
            recommendations.append("完善指标定义，添加缺失的描述和单位信息")

        if results['collection_coverage']['score'] < 85:
            recommendations.append("提高指标采集覆盖率，检查采集Agent配置")

        if results['threshold_reasonableness']['score'] < 95:
            recommendations.append("调整不合理的指标阈值，确保符合业务实际")

        if results['naming_consistency']['score'] < 80:
            recommendations.append("统一指标命名规范，提高可读性和维护性")

        return recommendations

    def run_accuracy_test(self, golden_dataset: List[Dict]) -> Dict[str, Any]:
        """运行指标准确性测试"""
        logger.info("开始指标准确性测试")

        test_results = []

        for data_point in golden_dataset:
            expected_value = data_point['expected_value']
            actual_value = self._collect_metric_value(data_point['metric_name'], data_point['labels'])

            if actual_value is not None:
                accuracy = 1 - abs(expected_value - actual_value) / expected_value
                test_results.append({
                    'metric': data_point['metric_name'],
                    'expected': expected_value,
                    'actual': actual_value,
                    'accuracy': accuracy,
                    'passed': accuracy >= self.config['testing']['accuracy_test']['tolerance']
                })

        passed_count = sum(1 for r in test_results if r['passed'])
        pass_rate = passed_count / len(test_results) if test_results else 0

        return {
            'total_tests': len(test_results),
            'passed': passed_count,
            'pass_rate': pass_rate,
            'results': test_results
        }

    def run_completeness_test(self) -> Dict[str, Any]:
        """运行指标完整性测试"""
        logger.info("开始指标完整性测试")

        completeness_results = {}

        for name, metric in self.metrics_definitions.items():
            # 检查最近一段时间内的采集完整性
            completeness = self._check_metric_completeness(name)
            completeness_results[name] = completeness

        overall_completeness = statistics.mean(completeness_results.values())

        return {
            'completeness_by_metric': completeness_results,
            'overall_completeness': overall_completeness,
            'threshold': self.config['testing']['completeness_test']['coverage_threshold'],
            'passed': overall_completeness >= self.config['testing']['completeness_test']['coverage_threshold']
        }

    def run_timeliness_test(self) -> Dict[str, Any]:
        """运行指标时效性测试"""
        logger.info("开始指标时效性测试")

        timeliness_results = {}

        for name, metric in self.metrics_definitions.items():
            # 检查采集延迟
            delay = self._measure_collection_delay(name)
            timeliness_results[name] = delay

        max_delay = max(timeliness_results.values()) if timeliness_results else 0
        max_allowed_delay = self.config['testing']['timeliness_test']['max_delay']

        return {
            'delay_by_metric': timeliness_results,
            'max_delay': max_delay,
            'max_allowed_delay': max_allowed_delay,
            'passed': max_delay <= max_allowed_delay
        }

    def _collect_metric_value(self, metric_name: str, labels: Dict[str, str]) -> Optional[float]:
        """采集指标值（模拟）"""
        # 实际实现中需要连接到指标存储系统
        return 42.0  # 示例返回值

    def _check_metric_completeness(self, metric_name: str) -> float:
        """检查指标完整性（模拟）"""
        return 0.95  # 示例返回值

    def _measure_collection_delay(self, metric_name: str) -> float:
        """测量采集延迟（模拟）"""
        return 15.0  # 示例返回值，单位秒


def main():
    """主函数"""
    # 创建指标架构管理器
    manager = MetricsArchitectureManager()

    # 验证架构
    architecture_results = manager.validate_metrics_architecture()

    print("\n=== 指标体系架构验证结果 ===")
    print(f"整体评分: {architecture_results['overall_score']:.1f}/100")
    print("\n各维度评分:")
    for key, result in architecture_results.items():
        if isinstance(result, dict) and 'score' in result:
            print(f"  {key}: {result['score']:.1f}/100")

    print("\n改进建议:")
    for rec in architecture_results['recommendations']:
        print(f"  - {rec}")

    # 运行测试
    print("\n=== 运行指标测试 ===")

    # 完整性测试
    completeness_result = manager.run_completeness_test()
    print(f"完整性测试: {'通过' if completeness_result['passed'] else '失败'}")
    print(".2%")

    # 时效性测试
    timeliness_result = manager.run_timeliness_test()
    print(f"时效性测试: {'通过' if timeliness_result['passed'] else '失败'}")
    print(f"最大延迟: {timeliness_result['max_delay']}秒")


if __name__ == "__main__":
    main()