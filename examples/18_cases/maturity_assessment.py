# examples/18_cases/maturity_assessment.py
"""
行业测试能力成熟度评估框架
评估和提升测试团队的专业能力和组织水平
"""

import json
import yaml
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
from pathlib import Path
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MaturityAssessment:
    """成熟度评估结果"""
    assessment_id: str
    organization_name: str
    industry: str
    assessment_date: str
    assessor: str
    overall_score: float
    maturity_level: int
    level_name: str
    dimension_scores: Dict[str, float]
    detailed_scores: Dict[str, float]
    recommendations: List[str]
    improvement_plan: Dict[str, Any]

@dataclass
class MaturityCriteria:
    """成熟度评估标准"""
    dimension: str
    criterion: str
    description: str
    weight: float
    level_definitions: Dict[int, str]
    assessment_questions: List[str]

class IndustryTestingMaturityAssessment:
    """行业测试能力成熟度评估"""

    def __init__(self, config_file: str = 'maturity_config.yml'):
        self.config = self._load_config(config_file)
        self.db_path = 'maturity_assessments.db'
        self._init_database()
        self._load_assessment_criteria()

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        if Path(config_file).exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'assessment_criteria': {
                'process_maturity': {
                    'test_planning': {'weight': 0.15, 'description': '测试规划能力'},
                    'test_execution': {'weight': 0.20, 'description': '测试执行能力'},
                    'defect_management': {'weight': 0.15, 'description': '缺陷管理能力'},
                    'quality_assurance': {'weight': 0.15, 'description': '质量保障能力'},
                    'continuous_improvement': {'weight': 0.15, 'description': '持续改进能力'},
                    'tool_automation': {'weight': 0.20, 'description': '工具自动化能力'}
                },
                'domain_knowledge': {
                    'industry_understanding': {'weight': 0.25, 'description': '行业理解深度'},
                    'regulatory_compliance': {'weight': 0.25, 'description': '合规知识掌握'},
                    'technical_expertise': {'weight': 0.25, 'description': '技术专长水平'},
                    'business_acumen': {'weight': 0.25, 'description': '业务洞察能力'}
                },
                'organizational_capability': {
                    'team_competence': {'weight': 0.30, 'description': '团队能力水平'},
                    'knowledge_management': {'weight': 0.25, 'description': '知识管理能力'},
                    'collaboration_culture': {'weight': 0.20, 'description': '协作文化建设'},
                    'leadership_support': {'weight': 0.25, 'description': '领导支持力度'}
                }
            },
            'maturity_levels': {
                1: {'name': 'Initial', 'score_range': [0, 1.5]},
                2: {'name': 'Managed', 'score_range': [1.5, 2.5]},
                3: {'name': 'Defined', 'score_range': [2.5, 3.5]},
                4: {'name': 'Quantitatively Managed', 'score_range': [3.5, 4.5]},
                5: {'name': 'Optimizing', 'score_range': [4.5, 5.0]}
            }
        }

    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS maturity_assessments (
                    assessment_id TEXT PRIMARY KEY,
                    organization_name TEXT,
                    industry TEXT,
                    assessment_date TEXT,
                    assessor TEXT,
                    overall_score REAL,
                    maturity_level INTEGER,
                    level_name TEXT,
                    dimension_scores TEXT,
                    detailed_scores TEXT,
                    recommendations TEXT,
                    improvement_plan TEXT
                )
            ''')

    def _load_assessment_criteria(self):
        """加载评估标准"""
        self.criteria_definitions = {
            'process_maturity': {
                'test_planning': {
                    'description': '测试规划和策略制定能力',
                    'questions': [
                        '是否有完整的测试规划流程？',
                        '测试策略是否基于风险评估？',
                        '资源分配是否合理有效？'
                    ]
                },
                'test_execution': {
                    'description': '测试用例设计和执行能力',
                    'questions': [
                        '测试用例覆盖是否全面？',
                        '测试执行是否规范高效？',
                        '测试结果是否准确可靠？'
                    ]
                },
                'defect_management': {
                    'description': '缺陷发现、跟踪和管理能力',
                    'questions': [
                        '缺陷发现率是否达标？',
                        '缺陷跟踪流程是否完善？',
                        '缺陷修复效率如何？'
                    ]
                },
                'quality_assurance': {
                    'description': '质量保障和控制能力',
                    'questions': [
                        '质量标准是否明确？',
                        '质量监控是否到位？',
                        '质量改进是否有效？'
                    ]
                },
                'continuous_improvement': {
                    'description': '持续改进和优化能力',
                    'questions': [
                        '是否有改进机制？',
                        '改进措施是否有效？',
                        '经验教训是否积累？'
                    ]
                },
                'tool_automation': {
                    'description': '测试工具和自动化能力',
                    'questions': [
                        '自动化覆盖率如何？',
                        '工具使用是否熟练？',
                        '自动化效果是否显著？'
                    ]
                }
            },
            'domain_knowledge': {
                'industry_understanding': {
                    'description': '行业业务和特点理解',
                    'questions': [
                        '对行业业务是否熟悉？',
                        '行业发展趋势是否了解？',
                        '行业挑战是否认识清楚？'
                    ]
                },
                'regulatory_compliance': {
                    'description': '监管要求和合规知识',
                    'questions': [
                        '合规要求是否掌握？',
                        '合规测试是否到位？',
                        '合规风险是否控制？'
                    ]
                },
                'technical_expertise': {
                    'description': '技术专长和解决方案能力',
                    'questions': [
                        '技术栈是否熟练？',
                        '问题解决能力如何？',
                        '技术创新能力怎样？'
                    ]
                },
                'business_acumen': {
                    'description': '业务洞察和价值理解',
                    'questions': [
                        '业务价值是否理解？',
                        '测试决策是否合理？',
                        '业务影响是否评估？'
                    ]
                }
            },
            'organizational_capability': {
                'team_competence': {
                    'description': '测试团队能力和素质',
                    'questions': [
                        '团队技能是否匹配？',
                        '人员配置是否合理？',
                        '能力发展是否规划？'
                    ]
                },
                'knowledge_management': {
                    'description': '知识积累和管理能力',
                    'questions': [
                        '知识库是否完善？',
                        '经验分享是否有效？',
                        '知识传承是否顺畅？'
                    ]
                },
                'collaboration_culture': {
                    'description': '协作文化和沟通机制',
                    'questions': [
                        '跨部门协作是否顺畅？',
                        '沟通机制是否有效？',
                        '合作文化是否形成？'
                    ]
                },
                'leadership_support': {
                    'description': '领导支持和资源保障',
                    'questions': [
                        '领导重视程度如何？',
                        '资源投入是否充足？',
                        '政策支持是否到位？'
                    ]
                }
            }
        }

    def conduct_assessment(self, organization_name: str, industry: str,
                          assessor: str, assessment_data: Dict[str, Any]) -> MaturityAssessment:
        """进行成熟度评估"""
        logger.info(f"开始对 {organization_name} 进行成熟度评估...")

        # 计算各维度得分
        dimension_scores = {}
        detailed_scores = {}

        for dimension, criteria in self.config['assessment_criteria'].items():
            dimension_total = 0
            dimension_weight_total = 0

            for criterion, config in criteria.items():
                if criterion in assessment_data:
                    score = assessment_data[criterion]
                    weight = config['weight']
                    dimension_total += score * weight
                    dimension_weight_total += weight
                    detailed_scores[criterion] = score

            if dimension_weight_total > 0:
                dimension_scores[dimension] = dimension_total / dimension_weight_total
            else:
                dimension_scores[dimension] = 0

        # 计算综合得分
        overall_score = (
            dimension_scores.get('process_maturity', 0) * 0.4 +
            dimension_scores.get('domain_knowledge', 0) * 0.35 +
            dimension_scores.get('organizational_capability', 0) * 0.25
        )

        # 确定成熟度等级
        maturity_level, level_name = self._determine_maturity_level(overall_score)

        # 生成建议
        recommendations = self._generate_recommendations(maturity_level, dimension_scores)

        # 生成改进计划
        improvement_plan = self._generate_improvement_plan(maturity_level, dimension_scores)

        # 创建评估结果
        assessment = MaturityAssessment(
            assessment_id=f"MA_{organization_name}_{int(datetime.now().timestamp())}",
            organization_name=organization_name,
            industry=industry,
            assessment_date=datetime.now().isoformat(),
            assessor=assessor,
            overall_score=round(overall_score, 2),
            maturity_level=maturity_level,
            level_name=level_name,
            dimension_scores=dimension_scores,
            detailed_scores=detailed_scores,
            recommendations=recommendations,
            improvement_plan=improvement_plan
        )

        # 保存评估结果
        self._save_assessment(assessment)

        logger.info(f"成熟度评估完成: {organization_name} - Level {maturity_level} ({level_name})")
        return assessment

    def _determine_maturity_level(self, overall_score: float) -> Tuple[int, str]:
        """确定成熟度等级"""
        for level, config in self.config['maturity_levels'].items():
            min_score, max_score = config['score_range']
            if min_score <= overall_score < max_score:
                return level, config['name']

        # 默认返回最高等级
        return 5, 'Optimizing'

    def _generate_recommendations(self, current_level: int, dimension_scores: Dict[str, float]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 基于当前等级的通用建议
        level_recommendations = {
            1: [
                "建立标准化的测试流程和规范",
                "加强行业知识和业务理解培训",
                "引入基本的测试工具和自动化",
                "构建测试案例和脚本的基础库"
            ],
            2: [
                "完善测试框架和方法论体系",
                "加强质量度量和监控机制",
                "建立行业经验积累机制",
                "提升测试团队的专业能力"
            ],
            3: [
                "实施基于数据的质量管理",
                "建立测试过程优化机制",
                "制定行业测试标准和最佳实践",
                "加强跨部门协作和沟通"
            ],
            4: [
                "引入AI/ML技术优化测试过程",
                "建立预测性质量管理机制",
                "开展测试创新研究和应用",
                "构建行业测试生态系统"
            ],
            5: [
                "持续引领行业测试技术发展",
                "建立全球测试标准和规范",
                "开展前瞻性测试研究",
                "构建测试技术创新生态"
            ]
        }

        recommendations.extend(level_recommendations.get(current_level, []))

        # 基于维度得分的具体建议
        for dimension, score in dimension_scores.items():
            if score < 3.0:
                dimension_specific = {
                    'process_maturity': [
                        "优化测试规划和执行流程",
                        "加强缺陷管理和质量控制",
                        "提升测试自动化水平"
                    ],
                    'domain_knowledge': [
                        "加强行业知识和合规培训",
                        "提升技术专长和业务理解",
                        "建立知识分享和学习机制"
                    ],
                    'organizational_capability': [
                        "提升团队能力和素质水平",
                        "完善知识管理和传承体系",
                        "加强领导支持和资源保障"
                    ]
                }
                recommendations.extend(dimension_specific.get(dimension, []))

        return list(set(recommendations))  # 去重

    def _generate_improvement_plan(self, current_level: int, dimension_scores: Dict[str, float]) -> Dict[str, Any]:
        """生成改进计划"""
        plan = {
            'current_level': current_level,
            'target_level': min(current_level + 1, 5),
            'timeline_months': 12,
            'milestones': [],
            'action_items': [],
            'success_metrics': []
        }

        # 根据当前等级设置改进计划
        if current_level < 5:
            if current_level == 1:
                plan['milestones'] = [
                    {'month': 3, 'achievement': '建立基础测试流程'},
                    {'month': 6, 'achievement': '完成团队培训'},
                    {'month': 9, 'achievement': '引入基础工具'},
                    {'month': 12, 'achievement': '达到Level 2标准'}
                ]
                plan['action_items'] = [
                    '制定测试流程规范',
                    '开展行业知识培训',
                    '采购测试工具',
                    '建立测试案例库'
                ]
            elif current_level == 2:
                plan['milestones'] = [
                    {'month': 3, 'achievement': '完善测试框架'},
                    {'month': 6, 'achievement': '建立度量体系'},
                    {'month': 9, 'achievement': '积累行业经验'},
                    {'month': 12, 'achievement': '达到Level 3标准'}
                ]
                plan['action_items'] = [
                    '设计测试框架',
                    '实施质量度量',
                    '开展经验复盘',
                    '提升团队能力'
                ]
            elif current_level == 3:
                plan['milestones'] = [
                    {'month': 3, 'achievement': '量化质量管理'},
                    {'month': 6, 'achievement': '优化测试过程'},
                    {'month': 9, 'achievement': '制定行业标准'},
                    {'month': 12, 'achievement': '达到Level 4标准'}
                ]
                plan['action_items'] = [
                    '建立数据驱动管理',
                    '优化测试流程',
                    '制定测试标准',
                    '加强协作机制'
                ]
            elif current_level == 4:
                plan['milestones'] = [
                    {'month': 6, 'achievement': '引入AI技术'},
                    {'month': 12, 'achievement': '达到Level 5标准'}
                ]
                plan['action_items'] = [
                    '研究AI测试应用',
                    '建立创新机制',
                    '构建测试生态',
                    '引领行业发展'
                ]

            plan['success_metrics'] = [
                f'达到Level {plan["target_level"]}标准',
                '关键指标提升20%以上',
                '团队满意度提升15%',
                '客户满意度提升10%'
            ]

        return plan

    def _save_assessment(self, assessment: MaturityAssessment):
        """保存评估结果"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO maturity_assessments
                (assessment_id, organization_name, industry, assessment_date, assessor,
                 overall_score, maturity_level, level_name, dimension_scores,
                 detailed_scores, recommendations, improvement_plan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                assessment.assessment_id,
                assessment.organization_name,
                assessment.industry,
                assessment.assessment_date,
                assessment.assessor,
                assessment.overall_score,
                assessment.maturity_level,
                assessment.level_name,
                json.dumps(assessment.dimension_scores),
                json.dumps(assessment.detailed_scores),
                json.dumps(assessment.recommendations),
                json.dumps(assessment.improvement_plan)
            ))

    def get_assessment_history(self, organization_name: Optional[str] = None,
                              industry: Optional[str] = None) -> List[MaturityAssessment]:
        """获取评估历史"""
        conditions = []
        params = []

        if organization_name:
            conditions.append("organization_name = ?")
            params.append(organization_name)

        if industry:
            conditions.append("industry = ?")
            params.append(industry)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f'''
                SELECT * FROM maturity_assessments WHERE {where_clause}
                ORDER BY assessment_date DESC
            ''', params)

            rows = cursor.fetchall()

        assessments = []
        for row in rows:
            assessment = MaturityAssessment(
                assessment_id=row[0],
                organization_name=row[1],
                industry=row[2],
                assessment_date=row[3],
                assessor=row[4],
                overall_score=row[5],
                maturity_level=row[6],
                level_name=row[7],
                dimension_scores=json.loads(row[8]),
                detailed_scores=json.loads(row[9]),
                recommendations=json.loads(row[10]),
                improvement_plan=json.loads(row[11])
            )
            assessments.append(assessment)

        return assessments

    def generate_maturity_report(self, assessment: MaturityAssessment) -> str:
        """生成成熟度评估报告"""
        report = f"""# 行业测试能力成熟度评估报告

## 基本信息
- **评估ID**: {assessment.assessment_id}
- **组织名称**: {assessment.organization_name}
- **行业**: {assessment.industry}
- **评估日期**: {assessment.assessment_date}
- **评估师**: {assessment.assessor}

## 评估结果
- **综合得分**: {assessment.overall_score}/5.0
- **成熟度等级**: Level {assessment.maturity_level} - {assessment.level_name}

## 维度得分
"""

        for dimension, score in assessment.dimension_scores.items():
            dimension_name = {
                'process_maturity': '过程成熟度',
                'domain_knowledge': '领域知识',
                'organizational_capability': '组织能力'
            }.get(dimension, dimension)
            report += f"- **{dimension_name}**: {score:.2f}/5.0\n"

        report += "\n## 详细得分\n"
        for criterion, score in assessment.detailed_scores.items():
            criterion_name = {
                'test_planning': '测试规划',
                'test_execution': '测试执行',
                'defect_management': '缺陷管理',
                'quality_assurance': '质量保障',
                'continuous_improvement': '持续改进',
                'tool_automation': '工具自动化',
                'industry_understanding': '行业理解',
                'regulatory_compliance': '合规知识',
                'technical_expertise': '技术专长',
                'business_acumen': '业务洞察',
                'team_competence': '团队能力',
                'knowledge_management': '知识管理',
                'collaboration_culture': '协作文化',
                'leadership_support': '领导支持'
            }.get(criterion, criterion)
            report += f"- **{criterion_name}**: {score:.2f}/5.0\n"

        report += "\n## 改进建议\n"
        for i, rec in enumerate(assessment.recommendations, 1):
            report += f"{i}. {rec}\n"

        if assessment.improvement_plan['target_level'] > assessment.maturity_level:
            report += "\n## 改进计划\n"
            report += f"- **目标等级**: Level {assessment.improvement_plan['target_level']}\n"
            report += f"- **计划周期**: {assessment.improvement_plan['timeline_months']}个月\n"

            report += "\n### 里程碑\n"
            for milestone in assessment.improvement_plan['milestones']:
                report += f"- **{milestone['month']}个月**: {milestone['achievement']}\n"

            report += "\n### 行动项\n"
            for item in assessment.improvement_plan['action_items']:
                report += f"- {item}\n"

            report += "\n### 成功指标\n"
            for metric in assessment.improvement_plan['success_metrics']:
                report += f"- {metric}\n"

        return report

# 使用示例
if __name__ == "__main__":
    assessor = IndustryTestingMaturityAssessment()

    # 模拟评估数据
    assessment_data = {
        'test_planning': 3.5,
        'test_execution': 3.2,
        'defect_management': 3.8,
        'quality_assurance': 3.6,
        'continuous_improvement': 3.4,
        'tool_automation': 3.1,
        'industry_understanding': 4.0,
        'regulatory_compliance': 3.9,
        'technical_expertise': 3.7,
        'business_acumen': 3.8,
        'team_competence': 3.5,
        'knowledge_management': 3.3,
        'collaboration_culture': 3.6,
        'leadership_support': 3.9
    }

    # 进行评估
    result = assessor.conduct_assessment(
        organization_name="示例科技公司",
        industry="financial_services",
        assessor="测试架构师",
        assessment_data=assessment_data
    )

    # 生成报告
    report = assessor.generate_maturity_report(result)
    with open('maturity_assessment_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"成熟度评估完成: Level {result.maturity_level} ({result.level_name})")
    print(f"综合得分: {result.overall_score}/5.0")

    # 查看历史记录
    history = assessor.get_assessment_history("示例科技公司")
    print(f"历史评估次数: {len(history)}")