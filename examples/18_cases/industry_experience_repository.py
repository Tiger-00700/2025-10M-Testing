# examples/18_cases/industry_experience_repository.py
"""
行业经验沉淀知识库
收集和管理各行业大数据测试的经验教训和最佳实践
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
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IndustryLesson:
    """行业经验教训"""
    lesson_id: str
    industry: str
    category: str
    title: str
    description: str
    business_context: str
    technical_context: str
    challenges: List[str]
    solutions: List[str]
    outcomes: List[str]
    key_insights: List[str]
    applicability: str
    tags: List[str]
    created_date: str
    updated_date: str
    author: str
    quality_score: int
    adoption_count: int

@dataclass
class IndustryBestPractice:
    """行业最佳实践"""
    practice_id: str
    industry: str
    category: str
    title: str
    description: str
    business_value: str
    implementation_guide: str
    prerequisites: List[str]
    success_metrics: List[str]
    case_studies: List[str]
    limitations: List[str]
    tags: List[str]
    created_date: str
    updated_date: str
    author: str
    adoption_rate: float
    validation_status: str

class IndustryExperienceRepository:
    """行业经验知识库"""

    def __init__(self, db_path: str = 'industry_experience_repository.db'):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS industry_lessons (
                    lesson_id TEXT PRIMARY KEY,
                    industry TEXT,
                    category TEXT,
                    title TEXT,
                    description TEXT,
                    business_context TEXT,
                    technical_context TEXT,
                    challenges TEXT,
                    solutions TEXT,
                    outcomes TEXT,
                    key_insights TEXT,
                    applicability TEXT,
                    tags TEXT,
                    created_date TEXT,
                    updated_date TEXT,
                    author TEXT,
                    quality_score INTEGER,
                    adoption_count INTEGER
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS industry_best_practices (
                    practice_id TEXT PRIMARY KEY,
                    industry TEXT,
                    category TEXT,
                    title TEXT,
                    description TEXT,
                    business_value TEXT,
                    implementation_guide TEXT,
                    prerequisites TEXT,
                    success_metrics TEXT,
                    case_studies TEXT,
                    limitations TEXT,
                    tags TEXT,
                    created_date TEXT,
                    updated_date TEXT,
                    author TEXT,
                    adoption_rate REAL,
                    validation_status TEXT
                )
            ''')

    def add_industry_lesson(self, lesson: IndustryLesson):
        """添加行业经验教训"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO industry_lessons
                (lesson_id, industry, category, title, description, business_context,
                 technical_context, challenges, solutions, outcomes, key_insights,
                 applicability, tags, created_date, updated_date, author,
                 quality_score, adoption_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lesson.lesson_id, lesson.industry, lesson.category, lesson.title,
                lesson.description, lesson.business_context, lesson.technical_context,
                json.dumps(lesson.challenges), json.dumps(lesson.solutions),
                json.dumps(lesson.outcomes), json.dumps(lesson.key_insights),
                lesson.applicability, json.dumps(lesson.tags),
                lesson.created_date, lesson.updated_date, lesson.author,
                lesson.quality_score, lesson.adoption_count
            ))

        logger.info(f"Added industry lesson: {lesson.lesson_id}")

    def add_industry_best_practice(self, practice: IndustryBestPractice):
        """添加行业最佳实践"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO industry_best_practices
                (practice_id, industry, category, title, description, business_value,
                 implementation_guide, prerequisites, success_metrics, case_studies,
                 limitations, tags, created_date, updated_date, author,
                 adoption_rate, validation_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                practice.practice_id, practice.industry, practice.category, practice.title,
                practice.description, practice.business_value, practice.implementation_guide,
                json.dumps(practice.prerequisites), json.dumps(practice.success_metrics),
                json.dumps(practice.case_studies), json.dumps(practice.limitations),
                json.dumps(practice.tags), practice.created_date, practice.updated_date,
                practice.author, practice.adoption_rate, practice.validation_status
            ))

        logger.info(f"Added industry best practice: {practice.practice_id}")

    def search_industry_lessons(self, industry: str = "", category: str = "",
                              query: str = "", tags: List[str] = None,
                              min_score: int = 0) -> List[IndustryLesson]:
        """搜索行业经验教训"""
        conditions = []
        params = []

        if industry:
            conditions.append("industry = ?")
            params.append(industry)

        if category:
            conditions.append("category = ?")
            params.append(category)

        if query:
            conditions.append("(title LIKE ? OR description LIKE ? OR business_context LIKE ?)")
            params.extend([f"%{query}%"] * 3)

        if tags:
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")
            conditions.append(f"({' OR '.join(tag_conditions)})")

        if min_score > 0:
            conditions.append("quality_score >= ?")
            params.append(min_score)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f'''
                SELECT * FROM industry_lessons WHERE {where_clause}
                ORDER BY quality_score DESC, adoption_count DESC, updated_date DESC
            ''', params)

            rows = cursor.fetchall()

        lessons = []
        for row in rows:
            lesson = IndustryLesson(
                lesson_id=row[0], industry=row[1], category=row[2], title=row[3],
                description=row[4], business_context=row[5], technical_context=row[6],
                challenges=json.loads(row[7]), solutions=json.loads(row[8]),
                outcomes=json.loads(row[9]), key_insights=json.loads(row[10]),
                applicability=row[11], tags=json.loads(row[12]),
                created_date=row[13], updated_date=row[14], author=row[15],
                quality_score=row[16], adoption_count=row[17]
            )
            lessons.append(lesson)

        return lessons

    def search_industry_best_practices(self, industry: str = "", category: str = "",
                                     query: str = "", tags: List[str] = None,
                                     min_adoption: float = 0.0) -> List[IndustryBestPractice]:
        """搜索行业最佳实践"""
        conditions = []
        params = []

        if industry:
            conditions.append("industry = ?")
            params.append(industry)

        if category:
            conditions.append("category = ?")
            params.append(category)

        if query:
            conditions.append("(title LIKE ? OR description LIKE ?)")
            params.extend([f"%{query}%"] * 2)

        if tags:
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")
            conditions.append(f"({' OR '.join(tag_conditions)})")

        if min_adoption > 0:
            conditions.append("adoption_rate >= ?")
            params.append(min_adoption)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f'''
                SELECT * FROM industry_best_practices WHERE {where_clause}
                ORDER BY adoption_rate DESC, updated_date DESC
            ''', params)

            rows = cursor.fetchall()

        practices = []
        for row in rows:
            practice = IndustryBestPractice(
                practice_id=row[0], industry=row[1], category=row[2], title=row[3],
                description=row[4], business_value=row[5], implementation_guide=row[6],
                prerequisites=json.loads(row[7]), success_metrics=json.loads(row[8]),
                case_studies=json.loads(row[9]), limitations=json.loads(row[10]),
                tags=json.loads(row[11]), created_date=row[12], updated_date=row[13],
                author=row[14], adoption_rate=row[15], validation_status=row[16]
            )
            practices.append(practice)

        return practices

    def generate_industry_report(self, industry: str) -> str:
        """生成行业报告"""
        lessons = self.search_industry_lessons(industry=industry)
        practices = self.search_industry_best_practices(industry=industry)

        report = f"# {industry}行业大数据测试经验报告\n\n"
        report += f"生成时间: {datetime.now().isoformat()}\n\n"

        # 统计信息
        report += "## 统计概览\n\n"
        report += f"- 经验教训数量: {len(lessons)}\n"
        report += f"- 最佳实践数量: {len(practices)}\n"
        report += f"- 平均经验质量评分: {sum(l.quality_score for l in lessons) / len(lessons) if lessons else 0:.1f}\n"
        report += f"- 平均实践采纳率: {sum(p.adoption_rate for p in practices) / len(practices) if practices else 0:.1%}\n\n"

        # 关键洞察
        if lessons:
            report += "## 关键经验教训\n\n"
            top_lessons = sorted(lessons, key=lambda x: x.quality_score, reverse=True)[:5]
            for lesson in top_lessons:
                report += f"### {lesson.title}\n\n"
                report += f"**类别**: {lesson.category}\n\n"
                report += f"**描述**: {lesson.description}\n\n"
                report += f"**关键洞察**:\n"
                for insight in lesson.key_insights:
                    report += f"- {insight}\n"
                report += f"\n**适用性**: {lesson.applicability}\n\n"

        # 最佳实践
        if practices:
            report += "## 推荐最佳实践\n\n"
            top_practices = sorted(practices, key=lambda x: x.adoption_rate, reverse=True)[:5]
            for practice in top_practices:
                report += f"### {practice.title}\n\n"
                report += f"**业务价值**: {practice.business_value}\n\n"
                report += f"**采纳率**: {practice.adoption_rate:.1%}\n\n"
                report += f"**成功指标**:\n"
                for metric in practice.success_metrics:
                    report += f"- {metric}\n"
                report += "\n"

        return report

    def export_industry_knowledge_base(self, output_dir: str = 'industry_knowledge_export'):
        """导出行业知识库"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # 获取所有行业
        with sqlite3.connect(self.db_path) as conn:
            industries = conn.execute("SELECT DISTINCT industry FROM industry_lessons").fetchall()
            industries = [row[0] for row in industries]

        # 为每个行业生成报告
        for industry in industries:
            report = self.generate_industry_report(industry)
            with open(output_path / f'{industry}_report.md', 'w', encoding='utf-8') as f:
                f.write(report)

        # 生成综合统计
        all_lessons = self.search_industry_lessons()
        all_practices = self.search_industry_best_practices()

        stats_report = f"""# 行业知识库综合统计报告

生成时间: {datetime.now().isoformat()}

## 总体统计
- 覆盖行业数量: {len(industries)}
- 总经验教训数: {len(all_lessons)}
- 总最佳实践数: {len(all_practices)}

## 行业分布
"""
        for industry in industries:
            industry_lessons = [l for l in all_lessons if l.industry == industry]
            industry_practices = [p for p in all_practices if p.industry == industry]
            stats_report += f"- {industry}: {len(industry_lessons)}个经验教训, {len(industry_practices)}个最佳实践\n"

        stats_report += "\n## 质量评估\n"
        if all_lessons:
            avg_quality = sum(l.quality_score for l in all_lessons) / len(all_lessons)
            stats_report += f"- 平均经验质量评分: {avg_quality:.1f}/5.0\n"

        if all_practices:
            avg_adoption = sum(p.adoption_rate for p in all_practices) / len(all_practices)
            stats_report += f"- 平均实践采纳率: {avg_adoption:.1%}\n"

        with open(output_path / 'comprehensive_statistics.md', 'w', encoding='utf-8') as f:
            f.write(stats_report)

        logger.info(f"行业知识库已导出到: {output_dir}")

# 使用示例
if __name__ == "__main__":
    repo = IndustryExperienceRepository()

    # 添加金融行业经验教训
    lesson = IndustryLesson(
        lesson_id="FIN_LESSON_001",
        industry="financial_services",
        category="technical",
        title="金融风控测试环境一致性保障",
        description="通过构建生产镜像测试环境，提升风控模型验证的准确性和可靠性",
        business_context="金融风控系统升级项目，涉及实时反欺诈和信用评分",
        technical_context="基于Hadoop和Spark的大数据风控平台",
        challenges=[
            "测试环境与生产环境数据分布不一致",
            "模型验证缺乏实时数据流",
            "性能基准测试环境不稳定"
        ],
        solutions=[
            "构建生产数据流的实时复制机制",
            "采用容器化技术确保环境一致性",
            "建立自动化性能基准测试体系"
        ],
        outcomes=[
            "测试发现缺陷率提升60%",
            "模型上线稳定性提高80%",
            "测试周期缩短40%"
        ],
        key_insights=[
            "测试环境应尽可能接近生产环境",
            "实时数据流对风控测试至关重要",
            "环境一致性是测试质量的基础"
        ],
        applicability="适用于所有需要高可靠性的金融科技系统",
        tags=["金融", "风控", "测试环境", "一致性"],
        created_date="2025-12-23",
        updated_date="2025-12-23",
        author="金融测试专家",
        quality_score=5,
        adoption_count=15
    )

    repo.add_industry_lesson(lesson)

    # 添加最佳实践
    practice = IndustryBestPractice(
        practice_id="FIN_PRACTICE_001",
        industry="financial_services",
        category="methodology",
        title="金融大数据风险导向测试策略",
        description="基于风险评估的金融大数据测试优先级排序和资源分配方法",
        business_value="提升测试效率，降低业务风险，确保合规要求",
        implementation_guide="""1. 建立风险评估矩阵
2. 识别关键风险指标
3. 制定测试优先级策略
4. 优化资源分配方案
5. 实施持续监控机制""",
        prerequisites=[
            "完善的业务风险识别体系",
            "测试用例优先级评估模型",
            "跨部门协作机制"
        ],
        success_metrics=[
            "关键风险测试覆盖率≥95%",
            "测试资源利用率提升50%",
            "缺陷发现提前率≥60%"
        ],
        case_studies=[
            "某银行风控系统升级项目",
            "保险公司大数据平台建设"
        ],
        limitations=[
            "需要业务专家深度参与",
            "风险评估模型需要持续优化"
        ],
        tags=["金融", "风险测试", "优先级", "资源分配"],
        created_date="2025-12-23",
        updated_date="2025-12-23",
        author="测试架构师",
        adoption_rate=0.78,
        validation_status="validated"
    )

    repo.add_industry_best_practice(practice)

    # 搜索和展示
    financial_lessons = repo.search_industry_lessons(industry="financial_services")
    print(f"找到 {len(financial_lessons)} 条金融行业经验教训")

    risk_practices = repo.search_industry_best_practices(query="风险")
    print(f"找到 {len(risk_practices)} 条风险相关最佳实践")

    # 生成行业报告
    financial_report = repo.generate_industry_report("financial_services")
    with open('financial_testing_report.md', 'w', encoding='utf-8') as f:
        f.write(financial_report)

    # 导出知识库
    repo.export_industry_knowledge_base()

    print("行业经验沉淀完成")