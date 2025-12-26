#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医疗行业大数据测试验证工具
Healthcare Big Data Testing Validator

验证医疗大数据测试的合规性、准确性和性能要求
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Tuple
import re

class HealthcareTestValidator:
    """医疗行业大数据测试验证器"""

    def __init__(self, config_path: str = None):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.compliance_rules = self._load_compliance_rules()

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        default_config = {
            'data_privacy_level': 'HIPAA',
            'latency_threshold_ms': 2000,
            'accuracy_threshold': 0.98,
            'data_retention_days': 2555,  # 7年
            'audit_log_level': 'DETAILED'
        }
        return default_config

    def _load_compliance_rules(self) -> Dict:
        """加载合规规则"""
        return {
            'HIPAA': {
                'phi_fields': ['patient_id', 'medical_record', 'diagnosis', 'treatment'],
                'encryption_required': True,
                'access_logging': True,
                'data_retention': '7_years'
            },
            'GDPR': {
                'consent_required': True,
                'data_portability': True,
                'right_to_erasure': True
            }
        }

    def validate_patient_data_quality(self, patient_data: pd.DataFrame) -> Dict:
        """
        验证患者数据质量

        Args:
            patient_data: 患者数据DataFrame

        Returns:
            验证结果字典
        """
        results = {
            'overall_quality_score': 0.0,
            'completeness_score': 0.0,
            'accuracy_score': 0.0,
            'consistency_score': 0.0,
            'issues': []
        }

        try:
            # 1. 完整性检查
            completeness = self._check_data_completeness(patient_data)
            results['completeness_score'] = completeness['score']
            results['issues'].extend(completeness['issues'])

            # 2. 准确性检查
            accuracy = self._check_data_accuracy(patient_data)
            results['accuracy_score'] = accuracy['score']
            results['issues'].extend(accuracy['issues'])

            # 3. 一致性检查
            consistency = self._check_data_consistency(patient_data)
            results['consistency_score'] = consistency['score']
            results['issues'].extend(consistency['issues'])

            # 4. 隐私合规检查
            privacy = self._check_privacy_compliance(patient_data)
            results['issues'].extend(privacy['issues'])

            # 计算综合质量分数
            results['overall_quality_score'] = (
                results['completeness_score'] * 0.3 +
                results['accuracy_score'] * 0.4 +
                results['consistency_score'] * 0.3
            )

        except Exception as e:
            self.logger.error(f"患者数据质量验证失败: {e}")
            results['issues'].append(f"验证过程出错: {str(e)}")

        return results

    def _check_data_completeness(self, data: pd.DataFrame) -> Dict:
        """检查数据完整性"""
        required_fields = ['patient_id', 'diagnosis_date', 'primary_diagnosis']
        completeness_scores = []
        issues = []

        for field in required_fields:
            if field in data.columns:
                non_null_ratio = data[field].notna().mean()
                completeness_scores.append(non_null_ratio)
                if non_null_ratio < 0.95:
                    issues.append(f"字段 {field} 完整性不足: {non_null_ratio:.2%}")
            else:
                completeness_scores.append(0.0)
                issues.append(f"缺少必需字段: {field}")

        return {
            'score': np.mean(completeness_scores),
            'issues': issues
        }

    def _check_data_accuracy(self, data: pd.DataFrame) -> Dict:
        """检查数据准确性"""
        issues = []
        accuracy_score = 1.0

        # 检查诊断代码格式
        if 'icd_code' in data.columns:
            valid_icd = data['icd_code'].str.match(r'^[A-Z]\d{2}(\.\d{1,3})?$', na=False)
            invalid_ratio = (~valid_icd).mean()
            if invalid_ratio > 0.05:
                accuracy_score *= 0.8
                issues.append(f"ICD代码格式错误率过高: {invalid_ratio:.2%}")

        # 检查日期逻辑
        if 'birth_date' in data.columns and 'diagnosis_date' in data.columns:
            invalid_dates = (data['diagnosis_date'] < data['birth_date']).sum()
            if invalid_dates > 0:
                accuracy_score *= 0.9
                issues.append(f"发现 {invalid_dates} 条诊断日期早于出生日期的记录")

        return {
            'score': accuracy_score,
            'issues': issues
        }

    def _check_data_consistency(self, data: pd.DataFrame) -> Dict:
        """检查数据一致性"""
        issues = []
        consistency_score = 1.0

        # 检查同一患者的不同记录一致性
        if 'patient_id' in data.columns:
            patient_groups = data.groupby('patient_id')
            for patient_id, group in patient_groups:
                if len(group) > 1:
                    # 检查性别一致性
                    if 'gender' in group.columns and group['gender'].nunique() > 1:
                        consistency_score *= 0.95
                        issues.append(f"患者 {patient_id} 性别信息不一致")

                    # 检查出生日期一致性
                    if 'birth_date' in group.columns and group['birth_date'].nunique() > 1:
                        consistency_score *= 0.95
                        issues.append(f"患者 {patient_id} 出生日期信息不一致")

        return {
            'score': consistency_score,
            'issues': issues
        }

    def _check_privacy_compliance(self, data: pd.DataFrame) -> Dict:
        """检查隐私合规性"""
        issues = []

        # 检查是否包含敏感字段
        sensitive_fields = ['ssn', 'phone', 'address', 'full_name']
        for field in sensitive_fields:
            if field in data.columns:
                issues.append(f"检测到敏感字段: {field}，建议进行数据脱敏")

        # 检查数据访问日志
        if not hasattr(self, '_access_log_enabled'):
            issues.append("未启用数据访问审计日志")

        return {'issues': issues}

    def validate_diagnostic_accuracy(self, predictions: pd.DataFrame,
                                   actuals: pd.Series) -> Dict:
        """
        验证诊断准确性

        Args:
            predictions: 预测结果DataFrame
            actuals: 实际结果Series

        Returns:
            准确性验证结果
        """
        results = {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'issues': []
        }

        try:
            from sklearn.metrics import accuracy_score, precision_recall_fscore_support

            # 计算准确性指标
            results['accuracy'] = accuracy_score(actuals, predictions['predicted_diagnosis'])

            precision, recall, f1, _ = precision_recall_fscore_support(
                actuals, predictions['predicted_diagnosis'], average='weighted'
            )

            results['precision'] = precision
            results['recall'] = recall
            results['f1_score'] = f1

            # 检查是否达到医疗标准
            if results['accuracy'] < self.config['accuracy_threshold']:
                results['issues'].append(
                    f"诊断准确率 {results['accuracy']:.3f} 低于阈值 {self.config['accuracy_threshold']}"
                )

            if results['f1_score'] < 0.95:
                results['issues'].append(
                    f"F1分数 {results['f1_score']:.3f} 偏低，可能影响诊断可靠性"
                )

        except Exception as e:
            results['issues'].append(f"诊断准确性验证失败: {str(e)}")

        return results

    def validate_system_performance(self, performance_metrics: Dict) -> Dict:
        """
        验证系统性能

        Args:
            performance_metrics: 性能指标字典

        Returns:
            性能验证结果
        """
        results = {
            'latency_compliant': True,
            'throughput_sufficient': True,
            'availability_high': True,
            'issues': []
        }

        # 检查延迟
        if 'avg_response_time_ms' in performance_metrics:
            if performance_metrics['avg_response_time_ms'] > self.config['latency_threshold_ms']:
                results['latency_compliant'] = False
                results['issues'].append(
                    f"平均响应时间 {performance_metrics['avg_response_time_ms']}ms 超过阈值 {self.config['latency_threshold_ms']}ms"
                )

        # 检查可用性
        if 'uptime_percentage' in performance_metrics:
            if performance_metrics['uptime_percentage'] < 99.9:
                results['availability_high'] = False
                results['issues'].append(
                    f"系统可用性 {performance_metrics['uptime_percentage']}% 低于医疗标准 99.9%"
                )

        return results

    def generate_compliance_report(self, validation_results: List[Dict]) -> str:
        """
        生成合规报告

        Args:
            validation_results: 验证结果列表

        Returns:
            合规报告字符串
        """
        report = []
        report.append("# 医疗大数据测试合规报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("## 验证结果汇总")

        total_tests = len(validation_results)
        passed_tests = sum(1 for r in validation_results if not r.get('issues', []))

        report.append(f"总测试数: {total_tests}")
        report.append(f"通过测试数: {passed_tests}")
        report.append(f"通过率: {passed_tests/total_tests*100:.1f}%")
        report.append("")
        # 详细问题列表
        all_issues = []
        for i, result in enumerate(validation_results):
            if result.get('issues'):
                all_issues.extend([f"测试 {i+1}: {issue}" for issue in result['issues']])

        if all_issues:
            report.append("## 发现的问题")
            for issue in all_issues:
                report.append(f"- {issue}")
        else:
            report.append("## 合规状态: ✅ 所有测试通过")

        report.append("")
        report.append("## 建议改进措施")
        if all_issues:
            report.append("1. 立即修复数据质量问题")
            report.append("2. 加强隐私保护措施")
            report.append("3. 优化系统性能")
            report.append("4. 完善审计日志")
        else:
            report.append("1. 继续保持当前合规水平")
            report.append("2. 定期进行合规审计")
            report.append("3. 关注新技术发展")

        return "\n".join(report)

def main():
    """主函数"""
    logging.basicConfig(level=logging.INFO)

    # 创建验证器实例
    validator = HealthcareTestValidator()

    # 示例：验证患者数据质量
    sample_data = pd.DataFrame({
        'patient_id': ['P001', 'P002', 'P003', 'P001'],
        'diagnosis_date': pd.date_range('2024-01-01', periods=4),
        'primary_diagnosis': ['肺炎', '糖尿病', '高血压', '肺炎'],
        'icd_code': ['J18.9', 'E11.9', 'I10', 'J18.9'],
        'birth_date': pd.date_range('1980-01-01', periods=4),
        'gender': ['M', 'F', 'M', 'M']
    })

    print("=== 医疗大数据测试验证 ===")

    # 数据质量验证
    quality_result = validator.validate_patient_data_quality(sample_data)
    print(f"数据质量评分: {quality_result['overall_quality_score']:.3f}")
    if quality_result['issues']:
        print("发现问题:")
        for issue in quality_result['issues']:
            print(f"  - {issue}")

    # 性能验证
    perf_metrics = {
        'avg_response_time_ms': 1500,
        'uptime_percentage': 99.95
    }
    perf_result = validator.validate_system_performance(perf_metrics)
    print(f"\n性能合规: {perf_result['latency_compliant'] and perf_result['availability_high']}")

    # 生成报告
    report = validator.generate_compliance_report([quality_result, perf_result])
    print(f"\n{report}")

if __name__ == "__main__":
    main()