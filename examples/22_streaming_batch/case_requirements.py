# examples/22_streaming_batch/case_requirements.py
"""
流批一体案例需求分析脚本
用于分析和验证案例需求，生成需求分析报告
"""

import yaml
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BusinessScenario:
    """业务场景"""
    name: str
    description: str
    data_sources: List[str]
    processing_requirements: List[str]
    output_requirements: List[str]

@dataclass
class TechnicalChallenge:
    """技术挑战"""
    challenge: str
    impact: str
    mitigation_strategy: str
    priority: str

@dataclass
class QualityTarget:
    """质量目标"""
    metric: str
    target_value: str
    measurement_method: str
    acceptance_criteria: str

@dataclass
class Constraint:
    """约束条件"""
    constraint_type: str
    description: str
    impact: str
    workaround: Optional[str] = None

@dataclass
class SuccessCriteria:
    """成功标准"""
    criteria: str
    measurement: str
    acceptance_level: str
    verification_method: str

class CaseRequirementsAnalyzer:
    """案例需求分析器"""

    def __init__(self, config_file: str = 'case_requirements.yml'):
        self.config = self._load_config(config_file)
        self.business_scenarios: List[BusinessScenario] = []
        self.technical_challenges: List[TechnicalChallenge] = []
        self.quality_targets: List[QualityTarget] = []
        self.constraints: List[Constraint] = []
        self.success_criteria: List[SuccessCriteria] = []

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        config_path = Path(__file__).parent / config_file
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def analyze_business_scenarios(self) -> List[BusinessScenario]:
        """分析业务场景"""
        scenarios_config = self.config.get('business_scenarios', [])

        for scenario_data in scenarios_config:
            scenario = BusinessScenario(
                name=scenario_data['name'],
                description=scenario_data['description'],
                data_sources=scenario_data['data_sources'],
                processing_requirements=scenario_data['processing_requirements'],
                output_requirements=scenario_data['output_requirements']
            )
            self.business_scenarios.append(scenario)

        return self.business_scenarios

    def assess_technical_challenges(self) -> List[TechnicalChallenge]:
        """评估技术挑战"""
        challenges_config = self.config.get('technical_challenges', [])

        for challenge_data in challenges_config:
            challenge = TechnicalChallenge(
                challenge=challenge_data['challenge'],
                impact=challenge_data['impact'],
                mitigation_strategy=challenge_data['mitigation_strategy'],
                priority=challenge_data['priority']
            )
            self.technical_challenges.append(challenge)

        return self.technical_challenges

    def define_quality_targets(self) -> List[QualityTarget]:
        """定义质量目标"""
        targets_config = self.config.get('quality_targets', [])

        for target_data in targets_config:
            target = QualityTarget(
                metric=target_data['metric'],
                target_value=target_data['target_value'],
                measurement_method=target_data['measurement_method'],
                acceptance_criteria=target_data['acceptance_criteria']
            )
            self.quality_targets.append(target)

        return self.quality_targets

    def identify_constraints(self) -> List[Constraint]:
        """识别约束条件"""
        constraints_config = self.config.get('constraints', [])

        for constraint_data in constraints_config:
            constraint = Constraint(
                constraint_type=constraint_data['type'],
                description=constraint_data['description'],
                impact=constraint_data['impact'],
                workaround=constraint_data.get('workaround')
            )
            self.constraints.append(constraint)

        return self.constraints

    def define_success_criteria(self) -> List[SuccessCriteria]:
        """定义成功标准"""
        criteria_config = self.config.get('success_criteria', [])

        for criteria_data in criteria_config:
            criteria = SuccessCriteria(
                criteria=criteria_data['criteria'],
                measurement=criteria_data['measurement'],
                acceptance_level=criteria_data['acceptance_level'],
                verification_method=criteria_data['verification_method']
            )
            self.success_criteria.append(criteria)

        return self.success_criteria

    def generate_requirements_report(self) -> Dict[str, Any]:
        """生成需求分析报告"""
        logger.info("开始生成需求分析报告...")

        # 执行各项分析
        business_scenarios = self.analyze_business_scenarios()
        technical_challenges = self.assess_technical_challenges()
        quality_targets = self.define_quality_targets()
        constraints = self.identify_constraints()
        success_criteria = self.define_success_criteria()

        # 生成报告
        report = {
            'summary': {
                'business_scenarios_count': len(business_scenarios),
                'technical_challenges_count': len(technical_challenges),
                'quality_targets_count': len(quality_targets),
                'constraints_count': len(constraints),
                'success_criteria_count': len(success_criteria),
                'high_priority_challenges': len([c for c in technical_challenges if c.priority == 'high']),
                'critical_constraints': len([c for c in constraints if 'critical' in c.impact.lower()])
            },
            'business_scenarios': [asdict(scenario) for scenario in business_scenarios],
            'technical_challenges': [asdict(challenge) for challenge in technical_challenges],
            'quality_targets': [asdict(target) for target in quality_targets],
            'constraints': [asdict(constraint) for constraint in constraints],
            'success_criteria': [asdict(criteria) for criteria in success_criteria],
            'risk_assessment': {
                'high_risk_items': [
                    item for item in technical_challenges + constraints
                    if item.priority == 'high' or 'critical' in getattr(item, 'impact', '').lower()
                ],
                'mitigation_strategies': [
                    getattr(item, 'mitigation_strategy', getattr(item, 'workaround', '待制定'))
                    for item in technical_challenges + constraints
                    if item.priority == 'high' or 'critical' in getattr(item, 'impact', '').lower()
                ]
            },
            'recommendations': [
                "优先解决高优先级技术挑战",
                "制定约束条件应对策略",
                "建立质量目标监控机制",
                "明确成功标准验收流程",
                "开展原型验证降低风险"
            ]
        }

        return report

    def validate_requirements_completeness(self) -> Dict[str, Any]:
        """验证需求完整性"""
        validation_results = {
            'completeness_score': 0.0,
            'missing_elements': [],
            'recommendations': []
        }

        # 检查各项需求元素
        checks = {
            'business_scenarios': len(self.business_scenarios) > 0,
            'technical_challenges': len(self.technical_challenges) > 0,
            'quality_targets': len(self.quality_targets) > 0,
            'constraints': len(self.constraints) > 0,
            'success_criteria': len(self.success_criteria) > 0
        }

        completed_checks = sum(checks.values())
        validation_results['completeness_score'] = completed_checks / len(checks)

        # 识别缺失元素
        for element, completed in checks.items():
            if not completed:
                validation_results['missing_elements'].append(element)
                validation_results['recommendations'].append(f"需要补充{element}的详细分析")

        return validation_results

# 默认配置
DEFAULT_CONFIG = {
    'business_scenarios': [
        {
            'name': '实时用户行为分析',
            'description': '实时分析用户行为数据，支持个性化推荐和风控决策',
            'data_sources': ['用户点击流', '购买记录', '浏览历史'],
            'processing_requirements': ['实时处理', '低延迟响应', '高并发支持'],
            'output_requirements': ['实时推荐结果', '风险评分', '行为洞察报告']
        },
        {
            'name': '批量数据仓库构建',
            'description': '构建企业级数据仓库，支持历史数据分析和报表生成',
            'data_sources': ['业务数据库', '日志文件', '外部数据源'],
            'processing_requirements': ['批量处理', '数据清洗', 'ETL转换'],
            'output_requirements': ['数据仓库表', '汇总报表', '分析数据集']
        }
    ],
    'technical_challenges': [
        {
            'challenge': '数据延迟控制',
            'impact': '影响实时业务决策质量',
            'mitigation_strategy': '采用流处理框架，优化网络传输',
            'priority': 'high'
        },
        {
            'challenge': '数据一致性保障',
            'impact': '影响业务数据准确性',
            'mitigation_strategy': '实现Exactly-Once语义，数据校验机制',
            'priority': 'high'
        }
    ],
    'quality_targets': [
        {
            'metric': '端到端延迟',
            'target_value': '< 100ms',
            'measurement_method': '埋点监控',
            'acceptance_criteria': 'P99延迟不超过100ms'
        },
        {
            'metric': '数据准确性',
            'target_value': '> 99.9%',
            'measurement_method': '数据校验',
            'acceptance_criteria': '数据准确率达到99.9%以上'
        }
    ],
    'constraints': [
        {
            'type': '技术栈限制',
            'description': '必须使用现有Hadoop/Spark技术栈',
            'impact': '限制了技术选型的灵活性',
            'workaround': '在现有技术栈基础上进行优化'
        },
        {
            'type': '资源预算约束',
            'description': '计算资源预算有限',
            'impact': '影响系统扩展能力',
            'workaround': '优化资源利用率，采用弹性伸缩'
        }
    ],
    'success_criteria': [
        {
            'criteria': '功能完整性',
            'measurement': '需求覆盖率',
            'acceptance_level': '> 95%',
            'verification_method': '需求追溯矩阵'
        },
        {
            'criteria': '性能达标',
            'measurement': 'SLA达成率',
            'acceptance_level': '> 99%',
            'verification_method': '性能测试报告'
        }
    ]
}

# 使用示例
if __name__ == "__main__":
    # 创建默认配置文件
    config_path = Path(__file__).parent / 'case_requirements.yml'
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True)

    # 创建分析器并生成报告
    analyzer = CaseRequirementsAnalyzer()

    # 生成需求分析报告
    report = analyzer.generate_requirements_report()

    # 验证需求完整性
    validation = analyzer.validate_requirements_completeness()

    # 输出结果
    print("需求分析报告:")
    print(json.dumps(report['summary'], indent=2, ensure_ascii=False))

    print(f"\n需求完整性评分: {validation['completeness_score']:.2%}")

    if validation['missing_elements']:
        print("缺失元素:")
        for element in validation['missing_elements']:
            print(f"  - {element}")

    print("需求分析完成")