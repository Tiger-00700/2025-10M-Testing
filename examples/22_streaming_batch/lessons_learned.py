# examples/22_streaming_batch/lessons_learned.py
"""
流批一体经验总结脚本
用于收集和分析经验教训，生成经验总结报告
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
class LessonLearned:
    """经验教训"""
    category: str
    lesson: str
    context: str
    key_insight: str
    implementation: str
    impact: str

@dataclass
class BestPractice:
    """最佳实践"""
    area: str
    practice: str
    description: str
    benefits: List[str]
    implementation_guide: str

@dataclass
class ContinuousImprovement:
    """持续改进"""
    initiative: str
    status: str
    progress: float
    next_steps: List[str]

class LessonsLearnedFramework:
    """经验总结框架"""

    def __init__(self, config_file: str = 'lessons_learned.yml'):
        self.config = self._load_config(config_file)
        self.lessons: List[LessonLearned] = []
        self.best_practices: List[BestPractice] = []
        self.improvements: List[ContinuousImprovement] = []

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        config_path = Path(__file__).parent / config_file
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def extract_technical_lessons(self) -> List[LessonLearned]:
        """提取技术经验教训"""
        technical_config = self.config.get('technical_lessons', {})
        lessons = []

        for category, category_lessons in technical_config.items():
            for lesson_data in category_lessons:
                lesson = LessonLearned(
                    category=f"技术-{category.replace('_', ' ')}",
                    lesson=lesson_data['lesson'],
                    context=lesson_data['context'],
                    key_insight=lesson_data['key_insight'],
                    implementation=lesson_data['implementation'],
                    impact=lesson_data['impact']
                )
                lessons.append(lesson)

        return lessons

    def extract_process_lessons(self) -> List[LessonLearned]:
        """提取过程经验教训"""
        process_config = self.config.get('process_lessons', {})
        lessons = []

        for category, category_lessons in process_config.items():
            for lesson_data in category_lessons:
                lesson = LessonLearned(
                    category=f"过程-{category.replace('_', ' ')}",
                    lesson=lesson_data['lesson'],
                    context=lesson_data['context'],
                    key_insight=lesson_data['key_insight'],
                    implementation=lesson_data['implementation'],
                    impact=lesson_data['impact']
                )
                lessons.append(lesson)

        return lessons

    def extract_business_lessons(self) -> List[LessonLearned]:
        """提取业务经验教训"""
        business_config = self.config.get('business_lessons', {})
        lessons = []

        for category, category_lessons in business_config.items():
            for lesson_data in category_lessons:
                lesson = LessonLearned(
                    category=f"业务-{category.replace('_', ' ')}",
                    lesson=lesson_data['lesson'],
                    context=lesson_data['context'],
                    key_insight=lesson_data['key_insight'],
                    implementation=lesson_data['implementation'],
                    impact=lesson_data['impact']
                )
                lessons.append(lesson)

        return lessons

    def identify_best_practices(self) -> List[BestPractice]:
        """识别最佳实践"""
        # 从经验教训中提炼最佳实践
        all_lessons = (self.extract_technical_lessons() +
                      self.extract_process_lessons() +
                      self.extract_business_lessons())

        best_practices = []

        # 技术最佳实践
        tech_practices = [
            BestPractice(
                area="架构设计",
                practice="分层架构模式",
                description="采用清晰的分层架构，提高系统可维护性和扩展性",
                benefits=["降低耦合度", "提高可维护性", "便于扩展"],
                implementation_guide="数据源层/采集层/存储层/处理层/服务层/应用层的六层架构"
            ),
            BestPractice(
                area="技术选型",
                practice="成熟度评估框架",
                description="建立技术选型评估框架，确保技术选择的合理性",
                benefits=["降低技术风险", "提高成功率", "优化投资回报"],
                implementation_guide="社区活跃度/文档完善度/生态丰富度/维护状态评估"
            )
        ]

        # 过程最佳实践
        process_practices = [
            BestPractice(
                area="开发流程",
                practice="敏捷开发模式",
                description="采用敏捷开发方法，提高开发效率和响应速度",
                benefits=["快速迭代", "持续反馈", "灵活适应"],
                implementation_guide="2周迭代周期，持续集成，自动化测试"
            ),
            BestPractice(
                area="测试策略",
                practice="测试左移",
                description="将测试前移到开发早期，提高质量保障效率",
                benefits=["早期发现缺陷", "降低修复成本", "提高质量"],
                implementation_guide="TDD开发模式，自动化单元测试，持续集成"
            )
        ]

        # 业务最佳实践
        business_practices = [
            BestPractice(
                area="需求管理",
                practice="业务共创模式",
                description="业务方深度参与需求分析和验证过程",
                benefits=["准确理解需求", "减少需求变更", "提升满意度"],
                implementation_guide="联合需求分析，原型验证，迭代确认"
            ),
            BestPractice(
                area="价值衡量",
                practice="多维度价值评估",
                description="从用户、业务、技术多个维度评估项目价值",
                benefits=["全面价值认知", "科学决策依据", "持续优化方向"],
                implementation_guide="用户价值+业务价值+技术价值综合评估体系"
            )
        ]

        best_practices.extend(tech_practices + process_practices + business_practices)
        return best_practices

    def track_continuous_improvements(self) -> List[ContinuousImprovement]:
        """跟踪持续改进举措"""
        improvement_config = self.config.get('continuous_improvement', {})
        improvements = []

        # 知识库建设
        knowledge_initiatives = [
            ContinuousImprovement(
                initiative="技术文档体系建设",
                status="in_progress",
                progress=0.7,
                next_steps=["完善API文档", "建立故障排查指南", "创建最佳实践库"]
            ),
            ContinuousImprovement(
                initiative="培训体系建立",
                status="completed",
                progress=1.0,
                next_steps=["持续更新培训内容", "扩展培训覆盖范围"]
            )
        ]

        # 工具链完善
        toolchain_initiatives = [
            ContinuousImprovement(
                initiative="CI/CD流水线优化",
                status="in_progress",
                progress=0.8,
                next_steps=["集成安全扫描", "完善回滚机制", "添加性能测试"]
            ),
            ContinuousImprovement(
                initiative="监控告警体系建设",
                status="completed",
                progress=1.0,
                next_steps=["优化告警规则", "扩展监控覆盖", "建立监控大屏"]
            )
        ]

        improvements.extend(knowledge_initiatives + toolchain_initiatives)
        return improvements

    def generate_lessons_report(self) -> Dict[str, Any]:
        """生成经验总结报告"""
        logger.info("开始生成经验总结报告...")

        technical_lessons = self.extract_technical_lessons()
        process_lessons = self.extract_process_lessons()
        business_lessons = self.extract_business_lessons()
        best_practices = self.identify_best_practices()
        improvements = self.track_continuous_improvements()

        # 分类统计
        lessons_by_category = {}
        for lesson in technical_lessons + process_lessons + business_lessons:
            category = lesson.category.split('-')[0]
            lessons_by_category[category] = lessons_by_category.get(category, 0) + 1

        # 生成报告
        report = {
            'summary': {
                'total_lessons': len(technical_lessons + process_lessons + business_lessons),
                'technical_lessons': len(technical_lessons),
                'process_lessons': len(process_lessons),
                'business_lessons': len(business_lessons),
                'best_practices': len(best_practices),
                'active_improvements': len([i for i in improvements if i.status == 'in_progress']),
                'lessons_by_category': lessons_by_category
            },
            'technical_lessons': [asdict(lesson) for lesson in technical_lessons],
            'process_lessons': [asdict(lesson) for lesson in process_lessons],
            'business_lessons': [asdict(lesson) for lesson in business_lessons],
            'best_practices': [asdict(practice) for practice in best_practices],
            'continuous_improvements': [asdict(improvement) for improvement in improvements],
            'key_insights': [
                "分层架构是复杂系统成功的关键",
                "测试左移能显著提升质量和效率",
                "业务共创模式减少需求理解偏差",
                "持续改进文化推动长期发展",
                "技术选型应基于成熟度和生态评估"
            ],
            'recommendations': [
                "建立经验教训定期回顾机制",
                "完善知识库和最佳实践分享",
                "加强团队培训和技能发展",
                "持续优化工具链和流程",
                "培养质量和创新文化"
            ]
        }

        return report

# 默认配置
DEFAULT_CONFIG = {
    'technical_lessons': {
        'architecture_design_lessons': [
            {
                'lesson': "分层架构设计的重要性",
                'context': "流批一体系统架构设计过程中",
                'key_insight': "清晰的分层架构是系统可维护性和扩展性的基础",
                'implementation': "数据源层/采集层/存储层/处理层/服务层/应用层的六层架构",
                'impact': "减少了70%的跨层耦合问题"
            },
            {
                'lesson': "存储系统选型的权衡",
                'context': "HDFS/HBase/Redis存储选型决策",
                'key_insight': "根据数据访问模式选择合适的存储系统",
                'implementation': "HDFS用于批量存储，HBase用于实时查询，Redis用于缓存",
                'impact': "提升了50%的查询性能，降低了30%的存储成本"
            }
        ],
        'technology_selection_lessons': [
            {
                'lesson': "框架成熟度评估",
                'context': "Flink vs Spark技术选型",
                'key_insight': "优先选择社区活跃、文档完善、生态丰富的框架",
                'implementation': "选择Flink作为流处理框架，Spark作为批处理框架",
                'impact': "减少了40%的技术风险，加快了开发进度"
            }
        ],
        'performance_optimization_lessons': [
            {
                'lesson': "数据倾斜处理",
                'context': "Spark作业数据倾斜问题",
                'key_insight': "识别和解决数据倾斜是性能优化的关键",
                'implementation': "使用salting技术和动态分区调整",
                'impact': "提升了3倍的作业执行效率"
            }
        ],
        'failure_handling_lessons': [
            {
                'lesson': "容错机制设计",
                'context': "系统故障恢复处理",
                'key_insight': "完善的容错机制是系统高可用的保障",
                'implementation': "多级重试策略，优雅降级机制",
                'impact': "将系统可用性提升到99.9%"
            }
        ]
    },
    'process_lessons': {
        'development_process_lessons': [
            {
                'lesson': "敏捷开发实践",
                'context': "流批一体系统开发过程",
                'key_insight': "小步快跑，快速迭代是复杂系统开发的有效方法",
                'implementation': "2周迭代周期，持续集成和部署",
                'impact': "提高了开发效率，加快了交付速度"
            }
        ],
        'testing_process_lessons': [
            {
                'lesson': "测试左移策略",
                'context': "测试流程优化",
                'key_insight': "尽早开展测试，发现问题于早期阶段",
                'implementation': "单元测试先行，TDD开发模式",
                'impact': "将缺陷发现时间提前了50%"
            }
        ],
        'deployment_process_lessons': [
            {
                'lesson': "蓝绿部署实践",
                'context': "生产环境部署过程",
                'key_insight': "蓝绿部署提供了零停机部署的能力",
                'implementation': "自动化蓝绿部署流程",
                'impact': "实现了零停机部署，提高了系统可用性"
            }
        ],
        'operations_process_lessons': [
            {
                'lesson': "监控驱动运维",
                'context': "日常运维工作",
                'key_insight': "基于监控数据的运维决策更加科学有效",
                'implementation': "建立全面的监控指标体系",
                'impact': "提高了运维效率，减少了故障处理时间"
            }
        ]
    },
    'business_lessons': {
        'requirement_understanding_lessons': [
            {
                'lesson': "业务需求澄清",
                'context': "需求分析过程",
                'key_insight': "深入理解业务场景是项目成功的基础",
                'implementation': "业务方深度参与，原型验证需求",
                'impact': "减少了30%的需求变更"
            }
        ],
        'business_value_realization_lessons': [
            {
                'lesson': "KPI设定合理性",
                'context': "业务目标设定",
                'key_insight': "可衡量、可达成的KPI是业务成功的保障",
                'implementation': "SMART原则设定KPI",
                'impact': "提高了目标达成率30%"
            }
        ],
        'user_experience_lessons': [
            {
                'lesson': "用户中心设计",
                'context': "产品设计过程",
                'key_insight': "以用户为中心的设计能提升用户满意度",
                'implementation': "用户旅程图，用户体验测试",
                'impact': "提升了用户满意度25%"
            }
        ],
        'market_adaptation_lessons': [
            {
                'lesson': "市场趋势把握",
                'context': "技术选型决策",
                'key_insight': "紧跟技术发展趋势，选择有前景的技术",
                'implementation': "技术雷达，行业分析报告",
                'impact': "选择了合适的技术栈"
            }
        ]
    },
    'continuous_improvement': {
        'knowledge_base_construction': {
            'documentation_standards': "ADRs (Architecture Decision Records)",
            'knowledge_sharing_platforms': "内部Wiki，技术博客",
            'lessons_learned_repository': "经验教训数据库"
        },
        'training_system_establishment': {
            'technical_training': "新人培训，技能提升培训",
            'process_training': "流程培训，工具培训",
            'soft_skills_training': "沟通技巧，领导力培训"
        },
        'toolchain_perfection': {
            'development_tools': "IDE优化，代码质量工具",
            'testing_tools': "自动化测试框架，性能测试工具",
            'deployment_tools': "CI/CD流水线，配置管理工具"
        },
        'culture_building_promotion': {
            'innovation_culture': "黑客马拉松，创新奖励",
            'learning_culture': "读书会，技术大会参与",
            'quality_culture': "质量意识宣传，持续改进奖励"
        }
    }
}

# 使用示例
if __name__ == "__main__":
    # 创建默认配置文件
    config_path = Path(__file__).parent / 'lessons_learned.yml'
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True)

    # 创建框架并生成报告
    framework = LessonsLearnedFramework()

    # 生成报告
    report = framework.generate_lessons_report()

    # 输出结果
    print("经验总结报告:")
    print(json.dumps(report['summary'], indent=2, ensure_ascii=False))

    print(f"\n共总结了 {report['summary']['total_lessons']} 条经验教训")
    print(f"识别了 {report['summary']['best_practices']} 个最佳实践")
    print(f"有 {report['summary']['active_improvements']} 个持续改进举措正在进行中")

    print("经验总结完成")