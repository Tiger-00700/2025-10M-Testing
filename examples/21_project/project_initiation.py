# examples/21_project/project_initiation.py
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
class ProjectInitiation:
    """项目启动配置"""
    project_info: Dict[str, Any]
    objectives: Dict[str, List[str]]
    scope: Dict[str, Any]
    stakeholders: Dict[str, List[Dict[str, str]]]
    risks: Dict[str, List[Dict[str, str]]]
    milestones: Dict[str, Dict[str, Any]]
    resources: Dict[str, Any]
    communication_plan: Dict[str, List[Dict[str, str]]]

@dataclass
class InitiationChecklist:
    """启动检查清单"""
    item: str
    status: str  # 'completed', 'pending', 'blocked'
    owner: str
    due_date: str
    notes: str

@dataclass
class ValidationResult:
    """验证结果"""
    checklist_item: str
    status: str
    score: float
    findings: List[str]
    recommendations: List[str]

class ProjectInitiationValidator:
    """项目启动验证器"""

    def __init__(self, config_file: str = 'project_initiation.yml'):
        self.config = self._load_config(config_file)
        self.checklist_items = self._init_checklist()

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _init_checklist(self) -> List[InitiationChecklist]:
        """初始化检查清单"""
        return [
            InitiationChecklist(
                item="项目目标明确",
                status="pending",
                owner="项目经理",
                due_date=(datetime.now() + timedelta(days=3)).isoformat(),
                notes="业务目标、技术目标、质量目标均需明确"
            ),
            InitiationChecklist(
                item="范围边界清晰",
                status="pending",
                owner="业务分析师",
                due_date=(datetime.now() + timedelta(days=5)).isoformat(),
                notes="明确包含/排除的内容，避免范围蔓延"
            ),
            InitiationChecklist(
                item="干系人识别完成",
                status="pending",
                owner="项目经理",
                due_date=(datetime.now() + timedelta(days=3)).isoformat(),
                notes="识别所有关键干系人及其职责"
            ),
            InitiationChecklist(
                item="风险评估完成",
                status="pending",
                owner="风险经理",
                due_date=(datetime.now() + timedelta(days=7)).isoformat(),
                notes="识别主要风险并制定应对策略"
            ),
            InitiationChecklist(
                item="里程碑计划制定",
                status="pending",
                owner="项目经理",
                due_date=(datetime.now() + timedelta(days=5)).isoformat(),
                notes="制定详细的项目里程碑计划"
            ),
            InitiationChecklist(
                item="资源需求评估",
                status="pending",
                owner="资源经理",
                due_date=(datetime.now() + timedelta(days=7)).isoformat(),
                notes="评估人员、环境、预算等资源需求"
            ),
            InitiationChecklist(
                item="沟通计划制定",
                status="pending",
                owner="项目经理",
                due_date=(datetime.now() + timedelta(days=5)).isoformat(),
                notes="制定项目沟通计划和机制"
            )
        ]

    def validate_project_objectives(self) -> ValidationResult:
        """验证项目目标"""
        findings = []
        recommendations = []
        score = 0.0

        objectives = self.config.get('objectives', {})

        # 检查业务目标
        business_goals = objectives.get('business_goals', [])
        if len(business_goals) >= 3:
            score += 0.3
            findings.append("业务目标数量充足")
        else:
            findings.append("业务目标数量不足")
            recommendations.append("建议明确至少3个业务目标")

        # 检查技术目标
        technical_goals = objectives.get('technical_goals', [])
        if len(technical_goals) >= 2:
            score += 0.3
            findings.append("技术目标明确")
        else:
            findings.append("技术目标不明确")
            recommendations.append("建议明确技术实现目标")

        # 检查质量目标
        quality_goals = objectives.get('quality_goals', [])
        if len(quality_goals) >= 2:
            score += 0.4
            findings.append("质量目标量化")
        else:
            findings.append("质量目标不量化")
            recommendations.append("建议量化质量验收标准")

        return ValidationResult(
            checklist_item="项目目标明确",
            status="pass" if score >= 0.8 else "warning",
            score=score,
            findings=findings,
            recommendations=recommendations
        )

    def validate_scope_definition(self) -> ValidationResult:
        """验证范围界定"""
        findings = []
        recommendations = []
        score = 0.0

        scope = self.config.get('scope', {})

        # 检查包含范围
        in_scope = scope.get('in_scope', [])
        if len(in_scope) >= 3:
            score += 0.3
            findings.append("包含范围明确")
        else:
            findings.append("包含范围不明确")
            recommendations.append("建议明确项目包含的具体内容")

        # 检查排除范围
        out_scope = scope.get('out_scope', [])
        if len(out_scope) >= 2:
            score += 0.3
            findings.append("排除范围清晰")
        else:
            findings.append("排除范围不清晰")
            recommendations.append("建议明确项目不包含的内容")

        # 检查假设条件
        assumptions = scope.get('assumptions', [])
        if len(assumptions) >= 2:
            score += 0.4
            findings.append("假设条件明确")
        else:
            findings.append("假设条件不明确")
            recommendations.append("建议明确项目假设条件")

        return ValidationResult(
            checklist_item="范围边界清晰",
            status="pass" if score >= 0.8 else "warning",
            score=score,
            findings=findings,
            recommendations=recommendations
        )

    def validate_stakeholder_identification(self) -> ValidationResult:
        """验证干系人识别"""
        findings = []
        recommendations = []
        score = 0.0

        stakeholders = self.config.get('stakeholders', {})

        required_roles = ['business_owners', 'technical_leads', 'testing_team', 'operations_team']
        identified_roles = 0

        for role in required_roles:
            if role in stakeholders and len(stakeholders[role]) > 0:
                identified_roles += 1
                findings.append(f"{role}已识别")
            else:
                findings.append(f"{role}未识别")
                recommendations.append(f"建议识别{role}")

        score = identified_roles / len(required_roles)

        # 检查联系方式
        contact_complete = True
        for role_group in stakeholders.values():
            for stakeholder in role_group:
                if 'contact' not in stakeholder:
                    contact_complete = False
                    break

        if contact_complete:
            score += 0.2
            findings.append("联系方式完整")
        else:
            recommendations.append("建议补充所有干系人的联系方式")

        return ValidationResult(
            checklist_item="干系人识别完成",
            status="pass" if score >= 0.9 else "warning",
            score=min(score, 1.0),
            findings=findings,
            recommendations=recommendations
        )

    def validate_risk_assessment(self) -> ValidationResult:
        """验证风险评估"""
        findings = []
        recommendations = []
        score = 0.0

        risks = self.config.get('risks', {})

        # 检查高风险识别
        high_risks = risks.get('high_risk', [])
        if len(high_risks) >= 2:
            score += 0.4
            findings.append("高风险项目识别充分")
        else:
            findings.append("高风险项目识别不足")
            recommendations.append("建议识别至少2个高风险项目")

        # 检查风险字段完整性
        required_fields = ['risk', 'impact', 'probability', 'mitigation']
        field_completeness = 0

        for risk_level in risks.values():
            for risk in risk_level:
                complete_fields = sum(1 for field in required_fields if field in risk)
                field_completeness += complete_fields / len(required_fields)

        if len(high_risks) > 0:
            avg_completeness = field_completeness / len(high_risks)
            score += avg_completeness * 0.6

            if avg_completeness >= 0.8:
                findings.append("风险信息完整")
            else:
                recommendations.append("建议完善风险描述、影响、概率和应对措施")

        return ValidationResult(
            checklist_item="风险评估完成",
            status="pass" if score >= 0.8 else "warning",
            score=score,
            findings=findings,
            recommendations=recommendations
        )

    def validate_milestone_planning(self) -> ValidationResult:
        """验证里程碑计划"""
        findings = []
        recommendations = []
        score = 0.0

        milestones = self.config.get('milestones', {})

        if len(milestones) >= 2:
            score += 0.3
            findings.append("里程碑数量合理")
        else:
            findings.append("里程碑数量不足")
            recommendations.append("建议制定至少2个主要里程碑")

        # 检查里程碑完整性
        total_phases = len(milestones)
        complete_phases = 0

        for phase_name, phase_info in milestones.items():
            required_fields = ['name', 'duration', 'deliverables', 'acceptance_criteria']
            if all(field in phase_info for field in required_fields):
                complete_phases += 1
            else:
                recommendations.append(f"建议完善{phase_name}里程碑信息")

        if total_phases > 0:
            completeness_score = complete_phases / total_phases
            score += completeness_score * 0.7

            if completeness_score >= 0.8:
                findings.append("里程碑信息完整")
            else:
                findings.append("里程碑信息不完整")

        return ValidationResult(
            checklist_item="里程碑计划制定",
            status="pass" if score >= 0.8 else "warning",
            score=score,
            findings=findings,
            recommendations=recommendations
        )

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """运行综合验证"""
        logger.info("开始项目启动验证...")

        validation_results = [
            self.validate_project_objectives(),
            self.validate_scope_definition(),
            self.validate_stakeholder_identification(),
            self.validate_risk_assessment(),
            self.validate_milestone_planning()
        ]

        # 生成汇总报告
        summary = {
            'total_checks': len(validation_results),
            'passed_checks': sum(1 for r in validation_results if r.status == 'pass'),
            'warning_checks': sum(1 for r in validation_results if r.status == 'warning'),
            'failed_checks': sum(1 for r in validation_results if r.status == 'fail'),
            'average_score': sum(r.score for r in validation_results) / len(validation_results),
            'overall_status': 'pass' if all(r.status == 'pass' for r in validation_results) else 'warning'
        }

        # 更新检查清单状态
        for result in validation_results:
            for item in self.checklist_items:
                if item.item == result.checklist_item:
                    item.status = result.status
                    break

        return {
            'summary': summary,
            'detailed_results': [asdict(r) for r in validation_results],
            'checklist_status': [asdict(item) for item in self.checklist_items]
        }

# 使用示例
if __name__ == "__main__":
    validator = ProjectInitiationValidator()

    # 运行验证
    validation_report = validator.run_comprehensive_validation()

    # 输出结果
    print("项目启动验证报告:")
    print(json.dumps(validation_report, indent=2, ensure_ascii=False))

    print("项目启动验证完成")