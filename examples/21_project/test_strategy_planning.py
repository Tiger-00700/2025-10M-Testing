# examples/21_project/test_strategy_planning.py
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
class TestStrategy:
    """测试策略配置"""
    overall_approach: Dict[str, Any]
    test_scope: Dict[str, Any]
    testing_methods: Dict[str, Any]
    resource_allocation: Dict[str, Any]
    test_schedule: Dict[str, Any]
    risk_management: Dict[str, Any]
    quality_gates: Dict[str, Any]
    metrics_reporting: Dict[str, Any]

@dataclass
class StrategyValidation:
    """策略验证结果"""
    component: str
    status: str  # 'complete', 'incomplete', 'missing'
    completeness_score: float
    issues: List[str]
    recommendations: List[str]

class TestStrategyValidator:
    """测试策略验证器"""

    def __init__(self, config_file: str = 'test_strategy.yml'):
        self.config = self._load_config(config_file)

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate_overall_approach(self) -> StrategyValidation:
        """验证总体策略"""
        approach = self.config.get('overall_approach', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查测试方法论
        if 'testing_methodology' in approach:
            score += 0.2
        else:
            issues.append("缺少测试方法论定义")
            recommendations.append("明确测试方法论（如敏捷测试、传统测试等）")

        # 检查测试级别
        test_levels = approach.get('test_levels', [])
        if len(test_levels) >= 3:
            score += 0.2
        else:
            issues.append("测试级别定义不完整")
            recommendations.append("至少定义单元测试、集成测试、系统测试三个级别")

        # 检查测试类型
        test_types = approach.get('test_types', [])
        if len(test_types) >= 3:
            score += 0.2
        else:
            issues.append("测试类型定义不完整")
            recommendations.append("至少定义功能、性能、安全三种测试类型")

        # 检查自动化目标
        if 'automation_goal' in approach:
            score += 0.2
        else:
            issues.append("缺少自动化目标")
            recommendations.append("设定明确的自动化覆盖率目标")

        # 检查回归频率
        if 'regression_frequency' in approach:
            score += 0.2
        else:
            issues.append("缺少回归测试频率")
            recommendations.append("明确回归测试执行频率")

        status = "complete" if score >= 0.8 else "incomplete" if score >= 0.5 else "missing"

        return StrategyValidation(
            component="总体策略",
            status=status,
            completeness_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def validate_test_scope(self) -> StrategyValidation:
        """验证测试范围"""
        scope = self.config.get('test_scope', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查包含范围
        in_scope = scope.get('in_scope', [])
        if len(in_scope) >= 3:
            score += 0.3
        else:
            issues.append("包含范围定义不足")
            recommendations.append("明确至少3个测试包含范围")

        # 检查排除范围
        out_scope = scope.get('out_scope', [])
        if len(out_scope) >= 1:
            score += 0.3
        else:
            issues.append("缺少排除范围定义")
            recommendations.append("明确测试排除范围")

        # 检查假设条件
        assumptions = scope.get('assumptions', [])
        if len(assumptions) >= 2:
            score += 0.4
        else:
            issues.append("假设条件定义不足")
            recommendations.append("明确项目假设条件")

        status = "complete" if score >= 0.8 else "incomplete" if score >= 0.5 else "missing"

        return StrategyValidation(
            component="测试范围",
            status=status,
            completeness_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def validate_resource_allocation(self) -> StrategyValidation:
        """验证资源配置"""
        resources = self.config.get('resource_allocation', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查人员配置
        personnel = resources.get('personnel', {})
        if len(personnel) >= 3:
            score += 0.3
        else:
            issues.append("人员配置定义不足")
            recommendations.append("明确测试、自动化、性能等角色配置")

        # 检查环境配置
        environments = resources.get('environments', {})
        if len(environments) >= 2:
            score += 0.3
            # 检查环境可用性
            for env_name, env_config in environments.items():
                if 'availability' not in env_config:
                    issues.append(f"{env_name}缺少可用性定义")
                    recommendations.append(f"明确{env_name}的可用性要求")
        else:
            issues.append("环境配置定义不足")
            recommendations.append("至少配置开发和测试环境")

        # 检查预算
        if 'tools_budget' in resources:
            score += 0.4
        else:
            issues.append("缺少预算规划")
            recommendations.append("制定测试工具和资源预算")

        status = "complete" if score >= 0.8 else "incomplete" if score >= 0.5 else "missing"

        return StrategyValidation(
            component="资源配置",
            status=status,
            completeness_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def validate_test_schedule(self) -> StrategyValidation:
        """验证测试进度"""
        schedule = self.config.get('test_schedule', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查测试阶段
        phases = schedule.get('phases', {})
        if len(phases) >= 3:
            score += 0.4
            # 检查阶段完整性
            for phase_name, phase_info in phases.items():
                required_fields = ['duration', 'deliverables']
                missing_fields = [field for field in required_fields if field not in phase_info]
                if missing_fields:
                    issues.append(f"{phase_name}阶段缺少字段: {missing_fields}")
                    recommendations.append(f"完善{phase_name}阶段的{', '.join(missing_fields)}")
        else:
            issues.append("测试阶段定义不足")
            recommendations.append("至少定义单元测试、集成测试、系统测试三个阶段")

        # 检查里程碑
        milestones = schedule.get('milestones', [])
        if len(milestones) >= 3:
            score += 0.6
        else:
            issues.append("里程碑设定不足")
            recommendations.append("设定至少3个关键里程碑")

        status = "complete" if score >= 0.8 else "incomplete" if score >= 0.5 else "missing"

        return StrategyValidation(
            component="测试进度",
            status=status,
            completeness_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def validate_quality_gates(self) -> StrategyValidation:
        """验证质量门限"""
        gates = self.config.get('quality_gates', {})
        issues = []
        recommendations = []
        score = 0.0

        if len(gates) >= 3:
            score += 0.5
            # 检查门限完整性
            for gate_name, gate_config in gates.items():
                if 'criteria' not in gate_config:
                    issues.append(f"{gate_name}缺少通过准则")
                    recommendations.append(f"明确{gate_name}的通过准则")
        else:
            issues.append("质量门限定义不足")
            recommendations.append("至少定义单元测试、集成测试、系统测试三个质量门")

        # 检查关键指标
        metrics = self.config.get('metrics_reporting', {}).get('key_metrics', [])
        if len(metrics) >= 3:
            score += 0.5
        else:
            issues.append("关键指标定义不足")
            recommendations.append("定义测试覆盖率、缺陷密度等关键指标")

        status = "complete" if score >= 0.8 else "incomplete" if score >= 0.5 else "missing"

        return StrategyValidation(
            component="质量门限",
            status=status,
            completeness_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """运行综合验证"""
        logger.info("开始测试策略验证...")

        validations = [
            self.validate_overall_approach(),
            self.validate_test_scope(),
            self.validate_resource_allocation(),
            self.validate_test_schedule(),
            self.validate_quality_gates()
        ]

        # 生成汇总报告
        summary = {
            'total_components': len(validations),
            'complete_components': sum(1 for v in validations if v.status == 'complete'),
            'incomplete_components': sum(1 for v in validations if v.status == 'incomplete'),
            'missing_components': sum(1 for v in validations if v.status == 'missing'),
            'average_completeness': sum(v.completeness_score for v in validations) / len(validations),
            'overall_status': 'complete' if all(v.status == 'complete' for v in validations) else 'needs_improvement'
        }

        return {
            'summary': summary,
            'detailed_validations': [asdict(v) for v in validations]
        }

# 使用示例
if __name__ == "__main__":
    validator = TestStrategyValidator()

    # 运行验证
    validation_report = validator.run_comprehensive_validation()

    # 输出结果
    print("测试策略验证报告:")
    print(json.dumps(validation_report, indent=2, ensure_ascii=False))