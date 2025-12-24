# examples/21_project/project_retrospective.py
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
class ProjectRetrospective:
    """项目复盘配置"""
    retrospective_process: Dict[str, Any]
    data_collection: Dict[str, Any]
    analysis_framework: Dict[str, Any]
    improvement_actions: Dict[str, Any]
    knowledge_repository: Dict[str, Any]

@dataclass
class RetrospectiveValidation:
    """复盘验证结果"""
    component: str
    status: str  # 'effective', 'adequate', 'needs_improvement'
    quality_score: float
    issues: List[str]
    recommendations: List[str]

class ProjectRetrospectiveValidator:
    """项目复盘验证器"""

    def __init__(self, config_file: str = 'project_retrospective.yml'):
        self.config = self._load_config(config_file)

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def validate_retrospective_process(self) -> RetrospectiveValidation:
        """验证复盘流程"""
        process = self.config.get('retrospective_process', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查流程阶段
        process_phases = process.get('process_phases', [])
        if len(process_phases) >= 5:
            score += 0.25
            required_phases = ['preparation', 'data_collection', 'analysis', 'action_planning', 'follow_up']
            phase_names = [p.get('phase') for p in process_phases]
            missing_phases = [p for p in required_phases if p not in phase_names]
            if missing_phases:
                issues.append(f"复盘流程缺少阶段: {missing_phases}")
                recommendations.append(f"补充{missing_phases}复盘阶段")
        else:
            issues.append("复盘流程阶段定义不足")
            recommendations.append("定义准备、数据收集、分析、行动规划、跟进五个阶段")

        # 检查时间安排
        timeline = process.get('timeline', {})
        if timeline:
            score += 0.2
            required_elements = ['duration', 'frequency', 'milestone_projects']
            missing_elements = [elem for elem in required_elements if elem not in timeline]
            if missing_elements:
                issues.append(f"时间安排缺少要素: {missing_elements}")
        else:
            issues.append("缺少复盘时间安排")
            recommendations.append("确定复盘的持续时间、频率和适用项目")

        # 检查参与者
        participants = process.get('participants', {})
        if participants:
            score += 0.2
            required_roles = ['facilitator', 'participants', 'stakeholders']
            missing_roles = [role for role in required_roles if role not in participants]
            if missing_roles:
                issues.append(f"参与者定义缺少角色: {missing_roles}")
        else:
            issues.append("缺少参与者定义")
            recommendations.append("明确复盘的主持人、参与者和利益相关者")

        # 检查会议安排
        meeting_setup = process.get('meeting_setup', {})
        if meeting_setup:
            score += 0.2
            required_elements = ['format', 'agenda_template', 'ground_rules']
            missing_elements = [elem for elem in required_elements if elem not in meeting_setup]
            if missing_elements:
                issues.append(f"会议安排缺少要素: {missing_elements}")
        else:
            issues.append("缺少会议安排")
            recommendations.append("制定复盘会议的格式、议程模板和基本规则")

        # 检查工具和材料
        if 'tools_and_materials' in process:
            score += 0.15
        else:
            issues.append("缺少复盘工具和材料")
            recommendations.append("准备复盘所需的工具和材料")

        status = "effective" if score >= 0.8 else "adequate" if score >= 0.6 else "needs_improvement"

        return RetrospectiveValidation(
            component="复盘流程",
            status=status,
            quality_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def validate_data_collection(self) -> RetrospectiveValidation:
        """验证数据收集"""
        data_collection = self.config.get('data_collection', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查数据源
        data_sources = data_collection.get('data_sources', [])
        if len(data_sources) >= 4:
            score += 0.25
            required_sources = ['metrics', 'surveys', 'interviews', 'documents']
            source_types = [s.get('type') for s in data_sources]
            missing_sources = [s for s in required_sources if s not in source_types]
            if missing_sources:
                issues.append(f"数据收集缺少来源: {missing_sources}")
                recommendations.append(f"补充{missing_sources}数据来源")
        else:
            issues.append("数据来源定义不足")
            recommendations.append("至少包括度量、调查、访谈、文档四种数据来源")

        # 检查收集方法
        collection_methods = data_collection.get('collection_methods', [])
        if len(collection_methods) >= 3:
            score += 0.25
        else:
            issues.append("数据收集方法不足")
            recommendations.append("定义至少三种数据收集方法")

        # 检查时间点
        collection_timing = data_collection.get('collection_timing', {})
        if collection_timing:
            score += 0.2
            required_timings = ['during_project', 'at_completion', 'post_delivery']
            missing_timings = [t for t in required_timings if t not in collection_timing]
            if missing_timings:
                issues.append(f"数据收集缺少时间点: {missing_timings}")
        else:
            issues.append("缺少数据收集时间安排")
            recommendations.append("确定项目中、完成时、交付后的数据收集时间点")

        # 检查数据质量
        if 'data_quality_checks' in data_collection:
            score += 0.2
        else:
            issues.append("缺少数据质量检查")
            recommendations.append("建立数据收集的质量控制机制")

        # 检查匿名性保证
        if 'anonymity_assurance' in data_collection:
            score += 0.1
        else:
            issues.append("缺少匿名性保证")
            recommendations.append("确保数据收集的匿名性和保密性")

        status = "effective" if score >= 0.8 else "adequate" if score >= 0.6 else "needs_improvement"

        return RetrospectiveValidation(
            component="数据收集",
            status=status,
            quality_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def validate_analysis_framework(self) -> RetrospectiveValidation:
        """验证分析框架"""
        analysis = self.config.get('analysis_framework', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查分析维度
        analysis_dimensions = analysis.get('analysis_dimensions', [])
        if len(analysis_dimensions) >= 4:
            score += 0.25
            required_dimensions = ['process', 'technical', 'team', 'business']
            dimension_types = [d.get('dimension') for d in analysis_dimensions]
            missing_dimensions = [d for d in required_dimensions if d not in dimension_types]
            if missing_dimensions:
                issues.append(f"分析框架缺少维度: {missing_dimensions}")
                recommendations.append(f"补充{missing_dimensions}分析维度")
        else:
            issues.append("分析维度定义不足")
            recommendations.append("至少包括过程、技术、团队、业务四个分析维度")

        # 检查分析方法
        analysis_methods = analysis.get('analysis_methods', [])
        if len(analysis_methods) >= 3:
            score += 0.25
            required_methods = ['root_cause_analysis', 'trend_analysis', 'comparative_analysis']
            method_types = [m.get('method') for m in analysis_methods]
            missing_methods = [m for m in required_methods if m not in method_types]
            if missing_methods:
                issues.append(f"分析方法缺少: {missing_methods}")
        else:
            issues.append("分析方法定义不足")
            recommendations.append("定义根本原因分析、趋势分析、比较分析等方法")

        # 检查分析工具
        analysis_tools = analysis.get('analysis_tools', [])
        if len(analysis_tools) >= 2:
            score += 0.2
        else:
            issues.append("分析工具不足")
            recommendations.append("准备至少两种分析工具或技术")

        # 检查分类框架
        categorization_framework = analysis.get('categorization_framework', {})
        if categorization_framework:
            score += 0.15
            required_categories = ['what_went_well', 'what_went_wrong', 'improvement_opportunities']
            missing_categories = [c for c in required_categories if c not in categorization_framework]
            if missing_categories:
                issues.append(f"分类框架缺少类别: {missing_categories}")
        else:
            issues.append("缺少分类框架")
            recommendations.append("建立事情进展顺利、不顺利、改进机会的分类框架")

        # 检查优先级设置
        if 'prioritization_criteria' in analysis:
            score += 0.15
        else:
            issues.append("缺少优先级设置标准")
            recommendations.append("定义分析结果的优先级排序标准")

        status = "effective" if score >= 0.8 else "adequate" if score >= 0.6 else "needs_improvement"

        return RetrospectiveValidation(
            component="分析框架",
            status=status,
            quality_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def validate_improvement_actions(self) -> RetrospectiveValidation:
        """验证改进措施"""
        improvement = self.config.get('improvement_actions', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查行动规划
        action_planning = improvement.get('action_planning', {})
        if action_planning:
            score += 0.25
            required_elements = ['action_template', 'responsibility_assignment', 'timeline_setting']
            missing_elements = [elem for elem in required_elements if elem not in action_planning]
            if missing_elements:
                issues.append(f"行动规划缺少要素: {missing_elements}")
        else:
            issues.append("缺少行动规划框架")
            recommendations.append("建立改进行动的规划框架")

        # 检查跟踪机制
        tracking_mechanism = improvement.get('tracking_mechanism', {})
        if tracking_mechanism:
            score += 0.25
            required_elements = ['progress_tracking', 'status_reporting', 'completion_criteria']
            missing_elements = [elem for elem in required_elements if elem not in tracking_mechanism]
            if missing_elements:
                issues.append(f"跟踪机制缺少要素: {missing_elements}")
        else:
            issues.append("缺少改进措施跟踪机制")
            recommendations.append("建立改进行动的跟踪和报告机制")

        # 检查验收标准
        if 'acceptance_criteria' in improvement:
            score += 0.2
        else:
            issues.append("缺少改进措施验收标准")
            recommendations.append("定义改进行动的验收和成功标准")

        # 检查资源分配
        if 'resource_allocation' in improvement:
            score += 0.15
        else:
            issues.append("缺少改进资源分配")
            recommendations.append("为改进措施分配必要的资源")

        # 检查时间表
        if 'implementation_timeline' in improvement:
            score += 0.15
        else:
            issues.append("缺少实施时间表")
            recommendations.append("制定改进措施的实施时间表")

        status = "effective" if score >= 0.8 else "adequate" if score >= 0.6 else "needs_improvement"

        return RetrospectiveValidation(
            component="改进措施",
            status=status,
            quality_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def validate_knowledge_repository(self) -> RetrospectiveValidation:
        """验证知识库"""
        repository = self.config.get('knowledge_repository', {})
        issues = []
        recommendations = []
        score = 0.0

        # 检查知识分类
        knowledge_categories = repository.get('knowledge_categories', [])
        if len(knowledge_categories) >= 4:
            score += 0.25
            required_categories = ['lessons_learned', 'best_practices', 'case_studies', 'templates']
            category_types = [c.get('category') for c in knowledge_categories]
            missing_categories = [c for c in required_categories if c not in category_types]
            if missing_categories:
                issues.append(f"知识分类缺少: {missing_categories}")
        else:
            issues.append("知识分类定义不足")
            recommendations.append("至少定义经验教训、最佳实践、案例研究、模板四个类别")

        # 检查存储机制
        storage_mechanism = repository.get('storage_mechanism', {})
        if storage_mechanism:
            score += 0.2
            required_elements = ['format_standards', 'version_control', 'search_capability']
            missing_elements = [elem for elem in required_elements if elem not in storage_mechanism]
            if missing_elements:
                issues.append(f"存储机制缺少要素: {missing_elements}")
        else:
            issues.append("缺少知识存储机制")
            recommendations.append("建立知识的存储和管理机制")

        # 检查访问控制
        if 'access_control' in repository:
            score += 0.2
        else:
            issues.append("缺少访问控制")
            recommendations.append("建立知识库的访问权限控制")

        # 检查维护机制
        maintenance_process = repository.get('maintenance_process', {})
        if maintenance_process:
            score += 0.2
        else:
            issues.append("缺少知识库维护机制")
            recommendations.append("建立知识的更新、审核和维护流程")

        # 检查使用统计
        if 'usage_analytics' in repository:
            score += 0.15
        else:
            issues.append("缺少使用统计")
            recommendations.append("建立知识使用情况的统计和分析")

        status = "effective" if score >= 0.8 else "adequate" if score >= 0.6 else "needs_improvement"

        return RetrospectiveValidation(
            component="知识库",
            status=status,
            quality_score=score,
            issues=issues,
            recommendations=recommendations
        )

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """运行综合验证"""
        logger.info("开始项目复盘验证...")

        validations = [
            self.validate_retrospective_process(),
            self.validate_data_collection(),
            self.validate_analysis_framework(),
            self.validate_improvement_actions(),
            self.validate_knowledge_repository()
        ]

        # 生成汇总报告
        summary = {
            'total_components': len(validations),
            'effective_components': sum(1 for v in validations if v.status == 'effective'),
            'adequate_components': sum(1 for v in validations if v.status == 'adequate'),
            'needs_improvement_components': sum(1 for v in validations if v.status == 'needs_improvement'),
            'average_quality_score': sum(v.quality_score for v in validations) / len(validations),
            'overall_status': 'effective' if all(v.status == 'effective' for v in validations) else 'adequate'
        }

        return {
            'summary': summary,
            'detailed_validations': [asdict(v) for v in validations]
        }

# 使用示例
if __name__ == "__main__":
    validator = ProjectRetrospectiveValidator()

    # 运行验证
    validation_report = validator.run_comprehensive_validation()

    # 输出结果
    print("项目复盘验证报告:")
    print(json.dumps(validation_report, indent=2, ensure_ascii=False))

    print("项目复盘验证完成")