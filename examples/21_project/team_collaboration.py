# examples/21_project/team_collaboration.py
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
class TeamCollaboration:
    """团队协作配置"""
    team_structure: Dict[str, Any]
    communication_mechanisms: Dict[str, Any]
    collaboration_processes: Dict[str, Any]
    conflict_resolution: Dict[str, Any]
    knowledge_sharing: Dict[str, Any]

@dataclass
class CollaborationValidation:
    """协作验证结果"""
    component: str
    status: str  # 'effective', 'needs_improvement', 'ineffective'
    effectiveness_score: float
    issues: List[str]
    recommendations: List[str]

class TeamCollaborationValidator:
    """团队协作验证器"""

    def __init__(self, config_file: str = 'team_collaboration.yml'):
        self.config = self._load_config(config_file)

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate_team_structure(self) -> CollaborationValidation:
        """验证团队结构"""
        structure = self.config.get('team_structure', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查角色定义
        roles = structure.get('project_roles', [])
        if len(roles) >= 4:
            score += 0.3
            # 检查角色完整性
            for role in roles:
                required_fields = ['responsibilities', 'authority_level', 'key_competencies']
                missing_fields = [field for field in required_fields if field not in role]
                if missing_fields:
                    issues.append(f"角色'{role.get('role', 'Unknown')}'缺少字段: {missing_fields}")
                    recommendations.append(f"完善{role.get('role', 'Unknown')}角色的{missing_fields}")
        else:
            issues.append("项目角色定义不足")
            recommendations.append("至少定义项目经理、测试经理、高级测试工程师等4个关键角色")

        # 检查RACI矩阵
        raci_matrix = structure.get('raci_matrix', {})
        activities = raci_matrix.get('activities', [])
        if len(activities) >= 3:
            score += 0.4
            # 检查RACI完整性
            for activity in activities:
                required_roles = ['responsible', 'accountable', 'consulted', 'informed']
                missing_roles = [role for role in required_roles if role not in activity]
                if missing_roles:
                    issues.append(f"活动'{activity.get('activity', 'Unknown')}'缺少RACI角色: {missing_roles}")
        else:
            issues.append("RACI矩阵定义不足")
            recommendations.append("为至少3个关键活动定义RACI矩阵")

        # 检查职责边界
        if 'responsibility_matrix' in structure:
            score += 0.3
        else:
            issues.append("缺少职责边界定义")
            recommendations.append("建立明确的职责边界矩阵")

        status = "effective" if score >= 0.8 else "needs_improvement" if score >= 0.5 else "ineffective"

        return CollaborationValidation(
            component="团队结构",
            status=status,
            effectiveness_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def validate_communication_mechanisms(self) -> CollaborationValidation:
        """验证沟通机制"""
        communication = self.config.get('communication_mechanisms', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查定期会议
        regular_meetings = communication.get('regular_meetings', [])
        if len(regular_meetings) >= 3:
            score += 0.3
            # 检查会议完整性
            for meeting in regular_meetings:
                required_fields = ['frequency', 'duration', 'attendees', 'agenda']
                missing_fields = [field for field in required_fields if field not in meeting]
                if missing_fields:
                    issues.append(f"会议'{meeting.get('meeting', 'Unknown')}'缺少字段: {missing_fields}")
        else:
            issues.append("定期会议机制定义不足")
            recommendations.append("至少建立每日站会、周会、月会三种会议机制")

        # 检查沟通工具
        communication_tools = communication.get('communication_tools', [])
        if len(communication_tools) >= 2:
            score += 0.2
            # 检查工具适用性
            tool_types = [tool.get('type') for tool in communication_tools]
            required_types = ['instant_messaging', 'project_management', 'documentation']
            missing_types = [t for t in required_types if t not in tool_types]
            if missing_types:
                issues.append(f"缺少沟通工具类型: {missing_types}")
                recommendations.append(f"补充{missing_types}类型的沟通工具")
        else:
            issues.append("沟通工具配置不足")
            recommendations.append("至少配置即时通讯和项目管理工具")

        # 检查状态报告
        status_reporting = communication.get('status_reporting', {})
        if status_reporting:
            score += 0.3
            required_reports = ['daily', 'weekly', 'monthly']
            missing_reports = [r for r in required_reports if r not in status_reporting]
            if missing_reports:
                issues.append(f"缺少状态报告类型: {missing_reports}")
                recommendations.append(f"建立{missing_reports}状态报告机制")
        else:
            issues.append("缺少状态报告机制")
            recommendations.append("建立日报、周报、月报等状态报告机制")

        # 检查升级机制
        if 'escalation_procedures' in communication:
            score += 0.2
        else:
            issues.append("缺少问题升级机制")
            recommendations.append("建立明确的问题升级流程")

        status = "effective" if score >= 0.8 else "needs_improvement" if score >= 0.5 else "ineffective"

        return CollaborationValidation(
            component="沟通机制",
            status=status,
            effectiveness_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def validate_collaboration_processes(self) -> CollaborationValidation:
        """验证协作流程"""
        processes = self.config.get('collaboration_processes', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查需求评审流程
        requirement_review = processes.get('requirement_review', {})
        if requirement_review:
            score += 0.25
            required_steps = ['review_criteria', 'review_process', 'approval_workflow']
            missing_steps = [step for step in required_steps if step not in requirement_review]
            if missing_steps:
                issues.append(f"需求评审流程缺少步骤: {missing_steps}")
        else:
            issues.append("缺少需求评审流程定义")
            recommendations.append("建立标准的需求评审流程")

        # 检查缺陷管理流程
        defect_management = processes.get('defect_management', {})
        if defect_management:
            score += 0.25
            required_elements = ['prioritization', 'assignment', 'resolution_tracking', 'closure_criteria']
            missing_elements = [elem for elem in required_elements if elem not in defect_management]
            if missing_elements:
                issues.append(f"缺陷管理流程缺少要素: {missing_elements}")
        else:
            issues.append("缺少缺陷管理流程定义")
            recommendations.append("建立完整的缺陷生命周期管理流程")

        # 检查发布协调流程
        release_coordination = processes.get('release_coordination', {})
        if release_coordination:
            score += 0.25
        else:
            issues.append("缺少发布协调流程")
            recommendations.append("建立发布协调和部署流程")

        # 检查变更管理流程
        if 'change_management' in processes:
            score += 0.25
        else:
            issues.append("缺少变更管理流程")
            recommendations.append("建立变更请求和审批流程")

        status = "effective" if score >= 0.8 else "needs_improvement" if score >= 0.5 else "ineffective"

        return CollaborationValidation(
            component="协作流程",
            status=status,
            effectiveness_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def validate_conflict_resolution(self) -> CollaborationValidation:
        """验证冲突解决机制"""
        conflict_resolution = self.config.get('conflict_resolution', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查冲突识别
        if 'conflict_identification' in conflict_resolution:
            score += 0.2
        else:
            issues.append("缺少冲突识别机制")
            recommendations.append("建立冲突早期识别机制")

        # 检查调解机制
        mediation_mechanisms = conflict_resolution.get('mediation_mechanisms', [])
        if len(mediation_mechanisms) >= 2:
            score += 0.3
            # 检查调解方式
            mediation_types = [m.get('type') for m in mediation_mechanisms]
            if 'peer_mediation' not in mediation_types:
                issues.append("缺少同级调解机制")
                recommendations.append("建立同级调解机制")
            if 'management_intervention' not in mediation_types:
                issues.append("缺少管理介入机制")
                recommendations.append("建立管理层介入机制")
        else:
            issues.append("调解机制定义不足")
            recommendations.append("至少建立两种调解机制")

        # 检查决策机制
        if 'decision_making' in conflict_resolution:
            score += 0.3
        else:
            issues.append("缺少冲突决策机制")
            recommendations.append("建立冲突解决的决策机制")

        # 检查预防措施
        preventive_measures = conflict_resolution.get('preventive_measures', [])
        if len(preventive_measures) >= 2:
            score += 0.2
        else:
            issues.append("预防措施定义不足")
            recommendations.append("建立至少两种冲突预防措施")

        status = "effective" if score >= 0.8 else "needs_improvement" if score >= 0.5 else "ineffective"

        return CollaborationValidation(
            component="冲突解决",
            status=status,
            effectiveness_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def validate_knowledge_sharing(self) -> CollaborationValidation:
        """验证知识共享机制"""
        knowledge_sharing = self.config.get('knowledge_sharing', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查知识库
        knowledge_base = knowledge_sharing.get('knowledge_base', {})
        if knowledge_base:
            score += 0.25
            required_elements = ['structure', 'maintenance', 'access_control']
            missing_elements = [elem for elem in required_elements if elem not in knowledge_base]
            if missing_elements:
                issues.append(f"知识库缺少要素: {missing_elements}")
        else:
            issues.append("缺少知识库建设")
            recommendations.append("建立项目知识库")

        # 检查经验分享机制
        experience_sharing = knowledge_sharing.get('experience_sharing', [])
        if len(experience_sharing) >= 2:
            score += 0.25
        else:
            issues.append("经验分享机制不足")
            recommendations.append("建立定期经验分享机制")

        # 检查培训机制
        training_programs = knowledge_sharing.get('training_programs', [])
        if len(training_programs) >= 1:
            score += 0.25
        else:
            issues.append("缺少培训培养机制")
            recommendations.append("建立培训和培养计划")

        # 检查最佳实践推广
        if 'best_practices' in knowledge_sharing:
            score += 0.25
        else:
            issues.append("缺少最佳实践推广机制")
            recommendations.append("建立最佳实践识别和推广机制")

        status = "effective" if score >= 0.8 else "needs_improvement" if score >= 0.5 else "ineffective"

        return CollaborationValidation(
            component="知识共享",
            status=status,
            effectiveness_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """运行综合验证"""
        logger.info("开始团队协作验证...")

        validations = [
            self.validate_team_structure(),
            self.validate_communication_mechanisms(),
            self.validate_collaboration_processes(),
            self.validate_conflict_resolution(),
            self.validate_knowledge_sharing()
        ]

        # 生成汇总报告
        summary = {
            'total_components': len(validations),
            'effective_components': sum(1 for v in validations if v.status == 'effective'),
            'needs_improvement_components': sum(1 for v in validations if v.status == 'needs_improvement'),
            'ineffective_components': sum(1 for v in validations if v.status == 'ineffective'),
            'average_effectiveness': sum(v.effectiveness_score for v in validations) / len(validations),
            'overall_status': 'effective' if all(v.status == 'effective' for v in validations) else 'needs_improvement'
        }

        return {
            'summary': summary,
            'detailed_validations': [asdict(v) for v in validations]
        }

# 使用示例
if __name__ == "__main__":
    validator = TeamCollaborationValidator()

    # 运行验证
    validation_report = validator.run_comprehensive_validation()

    # 输出结果
    print("团队协作验证报告:")
    print(json.dumps(validation_report, indent=2, ensure_ascii=False))

    print("团队协作验证完成")