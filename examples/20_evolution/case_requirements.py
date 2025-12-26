import yaml
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CaseRequirements:
    """案例需求配置"""
    case_info: Dict[str, Any]
    business_scenario: Dict[str, Any]
    technical_challenges: Dict[str, Any]
    quality_targets: Dict[str, Any]
    constraints: Dict[str, Any]

@dataclass
class RequirementsValidation:
    """需求验证结果"""
    component: str
    status: str  # 'pass', 'fail', 'warning'
    score: float
    findings: List[str]
    recommendations: List[str]

class CaseRequirementsFramework:
    """案例需求分析框架"""

    def __init__(self, config_file: str = None):
        if config_file is None:
            config_file = Path(__file__).parent / 'case_requirements.yml'
        self.config = self._load_config(str(config_file))
        self.validation_results: List[RequirementsValidation] = []

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate_case_info(self) -> RequirementsValidation:
        """验证案例基本信息"""
        case_info = self.config.get('case_info', {})
        findings = []
        recommendations = []
        score = 0.0

        # 检查必填字段
        required_fields = ['case_name', 'business_domain', 'case_version', 'start_date', 'end_date']
        for field in required_fields:
            if field in case_info:
                score += 1.0 / len(required_fields)
                findings.append(f"{field} 已配置")
            else:
                findings.append(f"缺少 {field}")
                recommendations.append(f"补充 {field} 配置")

        status = "pass" if score >= 0.8 else "warning" if score >= 0.5 else "fail"

        return RequirementsValidation(
            component="案例信息",
            status=status,
            score=score,
            findings=findings,
            recommendations=recommendations
        )

    def validate_business_scenario(self) -> RequirementsValidation:
        """验证业务场景"""
        scenario = self.config.get('business_scenario', {})
        findings = []
        recommendations = []
        score = 0.0

        # 检查业务场景维度
        scenario_types = ['real_time_requirements', 'batch_requirements', 'hybrid_requirements']
        for scenario_type in scenario_types:
            if scenario_type in scenario:
                score += 1.0 / len(scenario_types)
                findings.append(f"{scenario_type} 已定义")
            else:
                findings.append(f"缺少 {scenario_type}")
                recommendations.append(f"定义 {scenario_type}")

        status = "pass" if score >= 0.8 else "warning" if score >= 0.5 else "fail"

        return RequirementsValidation(
            component="业务场景",
            status=status,
            score=score,
            findings=findings,
            recommendations=recommendations
        )

    def validate_technical_challenges(self) -> RequirementsValidation:
        """验证技术挑战"""
        challenges = self.config.get('technical_challenges', {})
        findings = []
        recommendations = []
        score = 0.0

        # 检查技术挑战维度
        challenge_aspects = ['data_processing', 'system_complexity', 'consistency_requirements']
        for aspect in challenge_aspects:
            if aspect in challenges:
                score += 1.0 / len(challenge_aspects)
                findings.append(f"{aspect} 已评估")
            else:
                findings.append(f"缺少 {aspect} 评估")
                recommendations.append(f"评估 {aspect}")

        status = "pass" if score >= 0.8 else "warning" if score >= 0.5 else "fail"

        return RequirementsValidation(
            component="技术挑战",
            status=status,
            score=score,
            findings=findings,
            recommendations=recommendations
        )

    def validate_quality_targets(self) -> RequirementsValidation:
        """验证质量目标"""
        targets = self.config.get('quality_targets', {})
        findings = []
        recommendations = []
        score = 0.0

        # 检查质量目标维度
        target_types = ['performance_sla', 'data_quality', 'business_metrics']
        for target_type in target_types:
            if target_type in targets:
                score += 1.0 / len(target_types)
                findings.append(f"{target_type} 已设定")
            else:
                findings.append(f"缺少 {target_type}")
                recommendations.append(f"设定 {target_type}")

        status = "pass" if score >= 0.8 else "warning" if score >= 0.5 else "fail"

        return RequirementsValidation(
            component="质量目标",
            status=status,
            score=score,
            findings=findings,
            recommendations=recommendations
        )

    def validate_constraints(self) -> RequirementsValidation:
        """验证约束条件"""
        constraints = self.config.get('constraints', {})
        findings = []
        recommendations = []
        score = 0.0

        # 检查约束条件类型
        constraint_types = ['technical_constraints', 'resource_constraints',
                          'time_constraints', 'compliance_constraints']
        for constraint_type in constraint_types:
            if constraint_type in constraints:
                score += 1.0 / len(constraint_types)
                findings.append(f"{constraint_type} 已识别")
            else:
                findings.append(f"缺少 {constraint_type}")
                recommendations.append(f"识别 {constraint_type}")

        status = "pass" if score >= 0.8 else "warning" if score >= 0.5 else "fail"

        return RequirementsValidation(
            component="约束条件",
            status=status,
            score=score,
            findings=findings,
            recommendations=recommendations
        )

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """运行综合验证"""
        logger.info("开始案例需求验证...")

        validations = [
            self.validate_case_info(),
            self.validate_business_scenario(),
            self.validate_technical_challenges(),
            self.validate_quality_targets(),
            self.validate_constraints()
        ]

        self.validation_results = validations

        # 生成汇总报告
        summary = {
            'total_validations': len(validations),
            'passed_validations': sum(1 for v in validations if v.status == 'pass'),
            'warning_validations': sum(1 for v in validations if v.status == 'warning'),
            'failed_validations': sum(1 for v in validations if v.status == 'fail'),
            'average_score': sum(v.score for v in validations) / len(validations),
            'overall_status': 'pass' if all(v.status == 'pass' for v in validations) else 'needs_attention'
        }

        return {
            'summary': summary,
            'detailed_results': [asdict(v) for v in validations]
        }

# 使用示例
if __name__ == "__main__":
    framework = CaseRequirementsFramework()

    # 运行验证
    validation_report = framework.run_comprehensive_validation()

    # 输出结果
    print("案例需求验证报告:")
    print(json.dumps(validation_report, indent=2, ensure_ascii=False))

    print("案例需求验证完成")