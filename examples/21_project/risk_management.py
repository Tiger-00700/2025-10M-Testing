# examples/21_project/risk_management.py
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
class RiskManagement:
    """风险管理配置"""
    risk_register: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    mitigation_strategies: Dict[str, Any]
    monitoring_mechanisms: Dict[str, Any]
    contingency_plans: Dict[str, Any]

@dataclass
class RiskValidation:
    """风险验证结果"""
    component: str
    status: str  # 'well_managed', 'needs_attention', 'critical'
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    issues: List[str]
    recommendations: List[str]
    risk_score: float

class RiskManagementValidator:
    """风险管理验证器"""

    def __init__(self, config_file: str = 'risk_management.yml'):
        self.config = self._load_config(config_file)

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate_risk_register(self) -> RiskValidation:
        """验证风险登记"""
        risk_register = self.config.get('risk_register', {})
        issues = []
        recommendations = []
        risk_score = 0.0

        # 检查风险识别
        identified_risks = risk_register.get('identified_risks', [])
        if len(identified_risks) >= 5:
            risk_score += 0.2
        else:
            issues.append("风险识别数量不足")
            recommendations.append("至少识别5个主要风险项目")

        # 检查风险字段完整性
        required_fields = ['risk_id', 'description', 'impact', 'probability', 'mitigation_strategy']
        total_completeness = 0

        for risk in identified_risks:
            completeness = sum(1 for field in required_fields if field in risk) / len(required_fields)
            total_completeness += completeness

            missing_fields = [field for field in required_fields if field not in risk]
            if missing_fields:
                issues.append(f"风险'{risk.get('risk_id', 'Unknown')}'缺少字段: {missing_fields}")
                recommendations.append(f"完善风险{risk.get('risk_id', 'Unknown')}的{missing_fields}")

        if len(identified_risks) > 0:
            avg_completeness = total_completeness / len(identified_risks)
            risk_score += avg_completeness * 0.3

        # 检查风险分类
        risk_categories = risk_register.get('risk_categories', {})
        if len(risk_categories) >= 4:
            risk_score += 0.2
            required_categories = ['technical', 'business', 'resource', 'external']
            missing_categories = [cat for cat in required_categories if cat not in risk_categories]
            if missing_categories:
                issues.append(f"缺少风险类别: {missing_categories}")
                recommendations.append(f"补充{missing_categories}类别的风险识别")
        else:
            issues.append("风险分类不完整")
            recommendations.append("按技术、业务、资源、外部等维度分类风险")

        # 检查风险所有者
        risks_with_owners = sum(1 for risk in identified_risks if 'owner' in risk)
        if len(identified_risks) > 0:
            owner_coverage = risks_with_owners / len(identified_risks)
            risk_score += owner_coverage * 0.3
            if owner_coverage < 0.8:
                issues.append("风险所有者分配不完整")
                recommendations.append("为所有风险分配明确的所有者")

        # 确定风险状态
        if risk_score >= 0.8:
            status = "well_managed"
            risk_level = "low"
        elif risk_score >= 0.6:
            status = "needs_attention"
            risk_level = "medium"
        else:
            status = "critical"
            risk_level = "high"

        return RiskValidation(
            component="风险登记",
            status=status,
            risk_level=risk_level,
            issues=issues,
            recommendations=recommendations,
            risk_score=risk_score
        )

    def validate_risk_assessment(self) -> RiskValidation:
        """验证风险评估"""
        assessment = self.config.get('risk_assessment', {})
        issues = []
        recommendations = []
        risk_score = 0.0

        # 检查评估方法
        assessment_methods = assessment.get('assessment_methods', [])
        if len(assessment_methods) >= 2:
            risk_score += 0.2
            required_methods = ['qualitative', 'quantitative']
            method_types = [m.get('type') for m in assessment_methods]
            missing_methods = [m for m in required_methods if m not in method_types]
            if missing_methods:
                issues.append(f"缺少评估方法: {missing_methods}")
                recommendations.append(f"补充{missing_methods}风险评估方法")
        else:
            issues.append("风险评估方法定义不足")
            recommendations.append("至少采用定性和定量两种评估方法")

        # 检查影响评估
        impact_assessment = assessment.get('impact_assessment', {})
        if impact_assessment:
            risk_score += 0.2
            required_scales = ['impact_scale', 'probability_scale']
            missing_scales = [scale for scale in required_scales if scale not in impact_assessment]
            if missing_scales:
                issues.append(f"影响评估缺少量表: {missing_scales}")
                recommendations.append(f"定义{missing_scales}")
        else:
            issues.append("缺少影响评估框架")
            recommendations.append("建立风险影响和概率量表")

        # 检查风险矩阵
        if 'risk_matrix' in assessment:
            risk_score += 0.2
        else:
            issues.append("缺少风险矩阵")
            recommendations.append("建立风险矩阵来确定风险优先级")

        # 检查阈值定义
        risk_thresholds = assessment.get('risk_thresholds', {})
        if risk_thresholds:
            risk_score += 0.2
            required_thresholds = ['high_risk_threshold', 'critical_risk_threshold']
            missing_thresholds = [t for t in required_thresholds if t not in risk_thresholds]
            if missing_thresholds:
                issues.append(f"缺少风险阈值: {missing_thresholds}")
                recommendations.append(f"定义{missing_thresholds}")
        else:
            issues.append("缺少风险阈值定义")
            recommendations.append("定义高风险和严重风险的阈值")

        # 检查评估频率
        if 'assessment_frequency' in assessment:
            risk_score += 0.2
        else:
            issues.append("缺少风险评估频率")
            recommendations.append("确定风险评估的执行频率")

        # 确定风险状态
        if risk_score >= 0.8:
            status = "well_managed"
            risk_level = "low"
        elif risk_score >= 0.6:
            status = "needs_attention"
            risk_level = "medium"
        else:
            status = "critical"
            risk_level = "high"

        return RiskValidation(
            component="风险评估",
            status=status,
            risk_level=risk_level,
            issues=issues,
            recommendations=recommendations,
            risk_score=risk_score
        )

    def validate_mitigation_strategies(self) -> RiskValidation:
        """验证缓解策略"""
        mitigation = self.config.get('mitigation_strategies', {})
        issues = []
        recommendations = []
        risk_score = 0.0

        # 检查策略类型
        strategy_types = mitigation.get('strategy_types', [])
        if len(strategy_types) >= 4:
            risk_score += 0.25
            required_strategies = ['avoid', 'mitigate', 'transfer', 'accept']
            strategy_names = [s.get('type') for s in strategy_types]
            missing_strategies = [s for s in required_strategies if s not in strategy_names]
            if missing_strategies:
                issues.append(f"缺少缓解策略类型: {missing_strategies}")
                recommendations.append(f"补充{missing_strategies}风险应对策略")
        else:
            issues.append("风险缓解策略类型不足")
            recommendations.append("定义规避、缓解、转移、接受四种基本策略")

        # 检查策略选择标准
        if 'strategy_selection_criteria' in mitigation:
            risk_score += 0.25
        else:
            issues.append("缺少策略选择标准")
            recommendations.append("定义选择风险应对策略的标准")

        # 检查策略实施计划
        implementation_plans = mitigation.get('implementation_plans', [])
        if len(implementation_plans) >= 3:
            risk_score += 0.25
            # 检查计划完整性
            for plan in implementation_plans:
                required_elements = ['actions', 'timeline', 'responsible_party', 'success_criteria']
                missing_elements = [elem for elem in required_elements if elem not in plan]
                if missing_elements:
                    issues.append(f"实施计划缺少要素: {missing_elements}")
        else:
            issues.append("策略实施计划不足")
            recommendations.append("为主要风险制定详细的实施计划")

        # 检查资源分配
        if 'resource_allocation' in mitigation:
            risk_score += 0.25
        else:
            issues.append("缺少缓解措施资源分配")
            recommendations.append("为风险缓解措施分配必要的资源")

        # 确定风险状态
        if risk_score >= 0.8:
            status = "well_managed"
            risk_level = "low"
        elif risk_score >= 0.6:
            status = "needs_attention"
            risk_level = "medium"
        else:
            status = "critical"
            risk_level = "high"

        return RiskValidation(
            component="缓解策略",
            status=status,
            risk_level=risk_level,
            issues=issues,
            recommendations=recommendations,
            risk_score=risk_score
        )

    def validate_monitoring_mechanisms(self) -> RiskValidation:
        """验证监控机制"""
        monitoring = self.config.get('monitoring_mechanisms', {})
        issues = []
        recommendations = []
        risk_score = 0.0

        # 检查监控指标
        monitoring_metrics = monitoring.get('monitoring_metrics', [])
        if len(monitoring_metrics) >= 4:
            risk_score += 0.25
            required_metrics = ['risk_status', 'mitigation_progress', 'trigger_events', 'residual_risk']
            metric_types = [m.get('type') for m in monitoring_metrics]
            missing_metrics = [m for m in required_metrics if m not in metric_types]
            if missing_metrics:
                issues.append(f"缺少监控指标: {missing_metrics}")
                recommendations.append(f"补充{missing_metrics}监控指标")
        else:
            issues.append("风险监控指标定义不足")
            recommendations.append("定义至少4个关键风险监控指标")

        # 检查监控频率
        if 'monitoring_frequency' in monitoring:
            risk_score += 0.25
        else:
            issues.append("缺少监控频率定义")
            recommendations.append("确定风险监控的频率")

        # 检查预警机制
        early_warning = monitoring.get('early_warning_system', {})
        if early_warning:
            risk_score += 0.25
            required_elements = ['triggers', 'escalation_procedures', 'response_times']
            missing_elements = [elem for elem in required_elements if elem not in early_warning]
            if missing_elements:
                issues.append(f"预警机制缺少要素: {missing_elements}")
                recommendations.append(f"完善预警机制的{missing_elements}")
        else:
            issues.append("缺少预警机制")
            recommendations.append("建立风险预警系统")

        # 检查报告机制
        reporting_mechanism = monitoring.get('reporting_mechanism', {})
        if reporting_mechanism:
            risk_score += 0.25
        else:
            issues.append("缺少风险报告机制")
            recommendations.append("建立风险监控报告机制")

        # 确定风险状态
        if risk_score >= 0.8:
            status = "well_managed"
            risk_level = "low"
        elif risk_score >= 0.6:
            status = "needs_attention"
            risk_level = "medium"
        else:
            status = "critical"
            risk_level = "high"

        return RiskValidation(
            component="监控机制",
            status=status,
            risk_level=risk_level,
            issues=issues,
            recommendations=recommendations,
            risk_score=risk_score
        )

    def validate_contingency_plans(self) -> RiskValidation:
        """验证应急预案"""
        contingency = self.config.get('contingency_plans', {})
        issues = []
        recommendations = []
        risk_score = 0.0

        # 检查预案覆盖
        contingency_plans = contingency.get('contingency_plans', [])
        if len(contingency_plans) >= 3:
            risk_score += 0.25
            # 检查预案完整性
            for plan in contingency_plans:
                required_elements = ['trigger_conditions', 'response_actions', 'timeline', 'resources_needed']
                missing_elements = [elem for elem in required_elements if elem not in plan]
                if missing_elements:
                    issues.append(f"应急预案缺少要素: {missing_elements}")
        else:
            issues.append("应急预案数量不足")
            recommendations.append("为主要风险制定应急预案")

        # 检查演练计划
        if 'drill_schedule' in contingency:
            risk_score += 0.25
        else:
            issues.append("缺少应急演练计划")
            recommendations.append("制定定期应急演练计划")

        # 检查资源储备
        resource_reserves = contingency.get('resource_reserves', [])
        if len(resource_reserves) >= 2:
            risk_score += 0.25
        else:
            issues.append("应急资源储备不足")
            recommendations.append("准备应急资源储备")

        # 检查恢复计划
        if 'recovery_procedures' in contingency:
            risk_score += 0.25
        else:
            issues.append("缺少恢复程序")
            recommendations.append("制定业务恢复和系统恢复程序")

        # 确定风险状态
        if risk_score >= 0.8:
            status = "well_managed"
            risk_level = "low"
        elif risk_score >= 0.6:
            status = "needs_attention"
            risk_level = "medium"
        else:
            status = "critical"
            risk_level = "high"

        return RiskValidation(
            component="应急预案",
            status=status,
            risk_level=risk_level,
            issues=issues,
            recommendations=recommendations,
            risk_score=risk_score
        )

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """运行综合验证"""
        logger.info("开始风险管理验证...")

        validations = [
            self.validate_risk_register(),
            self.validate_risk_assessment(),
            self.validate_mitigation_strategies(),
            self.validate_monitoring_mechanisms(),
            self.validate_contingency_plans()
        ]

        # 计算整体风险水平
        risk_levels = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        avg_risk_level = sum(risk_levels.get(v.risk_level, 2) for v in validations) / len(validations)

        if avg_risk_level <= 1.5:
            overall_risk_level = "low"
        elif avg_risk_level <= 2.5:
            overall_risk_level = "medium"
        elif avg_risk_level <= 3.5:
            overall_risk_level = "high"
        else:
            overall_risk_level = "critical"

        # 生成汇总报告
        summary = {
            'total_components': len(validations),
            'well_managed_components': sum(1 for v in validations if v.status == 'well_managed'),
            'needs_attention_components': sum(1 for v in validations if v.status == 'needs_attention'),
            'critical_components': sum(1 for v in validations if v.status == 'critical'),
            'average_risk_score': sum(v.risk_score for v in validations) / len(validations),
            'overall_risk_level': overall_risk_level,
            'overall_status': 'well_managed' if overall_risk_level == 'low' else 'needs_attention'
        }

        return {
            'summary': summary,
            'detailed_validations': [asdict(v) for v in validations]
        }

# 使用示例
if __name__ == "__main__":
    validator = RiskManagementValidator()

    # 运行验证
    validation_report = validator.run_comprehensive_validation()

    # 输出结果
    print("风险管理验证报告:")
    print(json.dumps(validation_report, indent=2, ensure_ascii=False))

    print("风险管理验证完成")