# examples/09_quality/quality_monitoring.py
# 数据质量监控工具示例

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

class DataQualityMonitor:
    """数据质量监控器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.quality_rules = {
            'completeness': self._check_completeness,
            'accuracy': self._check_accuracy,
            'consistency': self._check_consistency,
            'timeliness': self._check_timeliness,
            'validity': self._check_validity
        }

    def monitor_dataset(self, data: pd.DataFrame, rules_config: Dict) -> Dict:
        """监控数据集质量"""
        results = {
            'timestamp': datetime.now(),
            'dataset_info': {
                'rows': len(data),
                'columns': len(data.columns),
                'size_mb': data.memory_usage(deep=True).sum() / 1024 / 1024
            },
            'quality_scores': {},
            'issues': []
        }

        for rule_name, rule_config in rules_config.items():
            if rule_name in self.quality_rules:
                score, issues = self.quality_rules[rule_name](data, rule_config)
                results['quality_scores'][rule_name] = score
                results['issues'].extend(issues)

        # 计算综合质量分数
        results['overall_score'] = np.mean(list(results['quality_scores'].values()))

        return results

    def _check_completeness(self, data: pd.DataFrame, config: Dict) -> tuple:
        """检查完整性"""
        issues = []
        total_cells = data.shape[0] * data.shape[1]
        null_cells = data.isnull().sum().sum()
        completeness_score = 1 - (null_cells / total_cells)

        if completeness_score < config.get('threshold', 0.95):
            issues.append({
                'type': 'completeness',
                'severity': 'warning',
                'message': f'数据完整性分数过低: {completeness_score:.2%}',
                'details': {'null_ratio': null_cells / total_cells}
            })

        return completeness_score, issues

    def _check_accuracy(self, data: pd.DataFrame, config: Dict) -> tuple:
        """检查准确性"""
        issues = []
        accuracy_score = 1.0  # 简化实现

        # 检查数据类型一致性
        for col in data.columns:
            if config.get('check_data_types'):
                dtype_issues = self._check_column_data_types(data[col])
                issues.extend(dtype_issues)

        return accuracy_score, issues

    def _check_consistency(self, data: pd.DataFrame, config: Dict) -> tuple:
        """检查一致性"""
        issues = []
        consistency_score = 1.0

        # 检查引用完整性
        if 'foreign_keys' in config:
            for fk_config in config['foreign_keys']:
                ref_issues = self._check_foreign_key_integrity(
                    data, fk_config['column'], fk_config['reference_table']
                )
                issues.extend(ref_issues)

        return consistency_score, issues

    def _check_timeliness(self, data: pd.DataFrame, config: Dict) -> tuple:
        """检查时效性"""
        issues = []
        timeliness_score = 1.0

        if 'timestamp_column' in config:
            timestamp_col = config['timestamp_column']
            if timestamp_col in data.columns:
                max_age_days = config.get('max_age_days', 1)
                latest_timestamp = data[timestamp_col].max()
                age_days = (datetime.now() - latest_timestamp).days

                if age_days > max_age_days:
                    timeliness_score = max(0, 1 - (age_days - max_age_days) / max_age_days)
                    issues.append({
                        'type': 'timeliness',
                        'severity': 'warning',
                        'message': f'数据时效性不足，最新数据已过期 {age_days} 天',
                        'details': {'age_days': age_days, 'max_age_days': max_age_days}
                    })

        return timeliness_score, issues

    def _check_validity(self, data: pd.DataFrame, config: Dict) -> tuple:
        """检查有效性"""
        issues = []
        validity_score = 1.0

        for col, rules in config.get('column_rules', {}).items():
            if col in data.columns:
                col_issues = self._validate_column(data[col], rules)
                issues.extend(col_issues)

        return validity_score, issues

    def _check_column_data_types(self, series: pd.Series) -> List[Dict]:
        """检查列数据类型一致性"""
        issues = []
        # 简化实现
        return issues

    def _check_foreign_key_integrity(self, data: pd.DataFrame, column: str, ref_table: str) -> List[Dict]:
        """检查外键完整性"""
        issues = []
        # 简化实现
        return issues

    def _validate_column(self, series: pd.Series, rules: Dict) -> List[Dict]:
        """验证列数据"""
        issues = []

        if 'regex' in rules:
            invalid_count = (~series.astype(str).str.match(rules['regex'])).sum()
            if invalid_count > 0:
                issues.append({
                    'type': 'validity',
                    'severity': 'error',
                    'message': f'列 {series.name} 有 {invalid_count} 个无效值',
                    'details': {'invalid_count': invalid_count, 'regex': rules['regex']}
                })

        if 'range' in rules:
            min_val, max_val = rules['range']
            out_of_range = ((series < min_val) | (series > max_val)).sum()
            if out_of_range > 0:
                issues.append({
                    'type': 'validity',
                    'severity': 'warning',
                    'message': f'列 {series.name} 有 {out_of_range} 个值超出范围 [{min_val}, {max_val}]',
                    'details': {'out_of_range_count': out_of_range, 'range': [min_val, max_val]}
                })

        return issues

    def generate_report(self, monitoring_results: Dict) -> str:
        """生成监控报告"""
        report = []
        report.append("# 数据质量监控报告")
        report.append(f"生成时间: {monitoring_results['timestamp']}")
        report.append("")

        # 数据集信息
        info = monitoring_results['dataset_info']
        report.append("## 数据集概况")
        report.append(f"- 行数: {info['rows']:,}")
        report.append(f"- 列数: {info['columns']}")
        report.append(".1f"        report.append("")

        # 质量分数
        report.append("## 质量评分")
        for rule, score in monitoring_results['quality_scores'].items():
            report.append(".2%")
        report.append(".2%"        report.append("")

        # 问题列表
        if monitoring_results['issues']:
            report.append("## 发现的问题")
            for issue in monitoring_results['issues']:
                severity_icon = {'error': '🔴', 'warning': '🟡', 'info': 'ℹ️'}.get(issue['severity'], '❓')
                report.append(f"- {severity_icon} **{issue['type']}**: {issue['message']}")
            report.append("")

        return "\n".join(report)