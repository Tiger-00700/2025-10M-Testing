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

    def __init__(self, config_file: str = None):
        if config_file is None:
            config_file = Path(__file__).parent / 'lessons_learned.yml'
        self.config = self._load_config(str(config_file))
        self.lessons: List[LessonLearned] = []
        self.best_practices: List[BestPractice] = []
        self.improvements: List[ContinuousImprovement] = []

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

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

# 使用示例
if __name__ == "__main__":
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