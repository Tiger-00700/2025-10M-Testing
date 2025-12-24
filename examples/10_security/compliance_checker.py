# examples/10_security/compliance_checker.py
# 合规性检查工具示例

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ComplianceLevel(Enum):
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"

@dataclass
class ComplianceRule:
    """合规性规则"""
    rule_id: str
    name: str
    description: str
    category: str
    severity: str
    check_function: callable
    remediation: str

@dataclass
class ComplianceResult:
    """合规性检查结果"""
    rule_id: str
    level: ComplianceLevel
    message: str
    details: Dict
    timestamp: datetime

class ComplianceChecker:
    """合规性检查器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compliance_rules = self._load_default_rules()

    def check_dataset_compliance(self, dataset_info: Dict) -> List[ComplianceResult]:
        """检查数据集合规性"""
        results = []

        for rule in self.compliance_rules:
            try:
                level, message, details = rule.check_function(dataset_info)
                result = ComplianceResult(
                    rule_id=rule.rule_id,
                    level=level,
                    message=message,
                    details=details,
                    timestamp=datetime.now()
                )
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error checking rule {rule.rule_id}: {e}")
                results.append(ComplianceResult(
                    rule_id=rule.rule_id,
                    level=ComplianceLevel.VIOLATION,
                    message=f"检查失败: {str(e)}",
                    details={},
                    timestamp=datetime.now()
                ))

        return results

    def check_data_content_compliance(self, data_sample: str, data_type: str = "general") -> List[ComplianceResult]:
        """检查数据内容合规性"""
        results = []

        # 敏感数据检测规则
        sensitive_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        }

        for data_type_name, pattern in sensitive_patterns.items():
            matches = re.findall(pattern, data_sample)
            if matches:
                results.append(ComplianceResult(
                    rule_id=f"sensitive_data_{data_type_name}",
                    level=ComplianceLevel.VIOLATION if len(matches) > 0 else ComplianceLevel.WARNING,
                    message=f"检测到{len(matches)}个潜在的{data_type_name}数据",
                    details={'matches': matches[:5], 'total_count': len(matches)},  # 只显示前5个
                    timestamp=datetime.now()
                ))

        return results

    def generate_compliance_report(self, results: List[ComplianceResult]) -> Dict:
        """生成合规性报告"""
        report = {
            'summary': {
                'total_checks': len(results),
                'compliant': 0,
                'warnings': 0,
                'violations': 0,
                'compliance_rate': 0.0
            },
            'details': [],
            'generated_at': datetime.now().isoformat()
        }

        for result in results:
            if result.level == ComplianceLevel.COMPLIANT:
                report['summary']['compliant'] += 1
            elif result.level == ComplianceLevel.WARNING:
                report['summary']['warnings'] += 1
            elif result.level == ComplianceLevel.VIOLATION:
                report['summary']['violations'] += 1

            report['details'].append({
                'rule_id': result.rule_id,
                'level': result.level.value,
                'message': result.message,
                'details': result.details,
                'timestamp': result.timestamp.isoformat()
            })

        total = report['summary']['total_checks']
        compliant = report['summary']['compliant']
        report['summary']['compliance_rate'] = (compliant / total * 100) if total > 0 else 0.0

        return report

    def _load_default_rules(self) -> List[ComplianceRule]:
        """加载默认合规性规则"""
        return [
            ComplianceRule(
                rule_id="retention_policy",
                name="数据保留策略检查",
                description="检查数据保留期是否符合要求",
                category="data_governance",
                severity="high",
                check_function=self._check_retention_policy,
                remediation="更新数据保留策略或清理过期数据"
            ),
            ComplianceRule(
                rule_id="data_classification",
                name="数据分类检查",
                description="检查数据是否正确分类",
                category="data_security",
                severity="high",
                check_function=self._check_data_classification,
                remediation="为数据分配正确的分类标签"
            ),
            ComplianceRule(
                rule_id="access_control",
                name="访问控制检查",
                description="检查访问控制是否正确配置",
                category="access_management",
                severity="medium",
                check_function=self._check_access_control,
                remediation="配置适当的访问控制策略"
            ),
            ComplianceRule(
                rule_id="encryption",
                name="加密检查",
                description="检查敏感数据是否加密",
                category="data_security",
                severity="high",
                check_function=self._check_encryption,
                remediation="为敏感数据启用加密"
            )
        ]

    def _check_retention_policy(self, dataset_info: Dict) -> Tuple[ComplianceLevel, str, Dict]:
        """检查数据保留策略"""
        retention_days = dataset_info.get('retention_days', 0)
        data_type = dataset_info.get('data_type', 'unknown')

        # 根据数据类型定义最小保留期
        min_retention = {
            'financial': 2555,  # 7年
            'healthcare': 2555,
            'personal': 1095,  # 3年
            'test': 90         # 90天
        }.get(data_type, 365)

        if retention_days >= min_retention:
            return ComplianceLevel.COMPLIANT, "保留策略符合要求", {'retention_days': retention_days}
        else:
            return ComplianceLevel.VIOLATION, f"保留期不足，至少需要{min_retention}天", {
                'current_retention': retention_days,
                'required_retention': min_retention
            }

    def _check_data_classification(self, dataset_info: Dict) -> Tuple[ComplianceLevel, str, Dict]:
        """检查数据分类"""
        classification = dataset_info.get('classification', '').lower()
        contains_sensitive = dataset_info.get('contains_sensitive_data', False)

        if contains_sensitive and classification not in ['confidential', 'restricted']:
            return ComplianceLevel.VIOLATION, "敏感数据分类不足", {'current_classification': classification}
        elif not contains_sensitive and classification in ['public', 'internal']:
            return ComplianceLevel.COMPLIANT, "数据分类适当", {'classification': classification}
        else:
            return ComplianceLevel.WARNING, "数据分类需要复核", {'classification': classification}

    def _check_access_control(self, dataset_info: Dict) -> Tuple[ComplianceLevel, str, Dict]:
        """检查访问控制"""
        access_level = dataset_info.get('access_level', 'unknown')
        required_approval = dataset_info.get('requires_approval', False)

        if access_level == 'restricted' and not required_approval:
            return ComplianceLevel.VIOLATION, "受限数据需要审批流程", {'access_level': access_level}
        elif access_level in ['internal', 'public']:
            return ComplianceLevel.COMPLIANT, "访问控制配置正确", {'access_level': access_level}
        else:
            return ComplianceLevel.WARNING, "访问控制配置需要确认", {'access_level': access_level}

    def _check_encryption(self, dataset_info: Dict) -> Tuple[ComplianceLevel, str, Dict]:
        """检查加密配置"""
        is_encrypted = dataset_info.get('encrypted', False)
        classification = dataset_info.get('classification', '').lower()

        if classification in ['confidential', 'restricted'] and not is_encrypted:
            return ComplianceLevel.VIOLATION, "敏感数据必须加密", {'classification': classification}
        elif is_encrypted:
            return ComplianceLevel.COMPLIANT, "数据已加密", {'encrypted': True}
        else:
            return ComplianceLevel.WARNING, "考虑为数据启用加密", {'encrypted': False}


# 使用示例
if __name__ == "__main__":
    checker = ComplianceChecker()

    # 检查数据集合规性
    dataset_info = {
        'name': 'customer_data',
        'data_type': 'personal',
        'retention_days': 365,
        'classification': 'confidential',
        'contains_sensitive_data': True,
        'access_level': 'restricted',
        'encrypted': True,
        'requires_approval': True
    }

    results = checker.check_dataset_compliance(dataset_info)

    # 检查数据内容
    sample_data = "Contact: john.doe@example.com, Phone: 123-456-7890"
    content_results = checker.check_data_content_compliance(sample_data)

    # 生成报告
    all_results = results + content_results
    report = checker.generate_compliance_report(all_results)

    print(json.dumps(report, indent=2, ensure_ascii=False))