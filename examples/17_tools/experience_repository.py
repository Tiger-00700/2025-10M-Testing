# 大数据测试经验知识库系统

## 概述

本系统提供了完整的经验知识库管理功能，包括经验收集、存储、检索、分享和分析，帮助测试团队积累和复用测试经验，提升测试质量和效率。

## 核心组件

### 经验数据模型

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

@dataclass
class Experience:
    """经验实体类"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    category: str = ""
    subcategory: Optional[str] = None
    description: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    lessons_learned: str = ""
    impact: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    author: str = ""
    rating: int = 0
    usage_count: int = 0
    created_date: datetime = field(default_factory=datetime.now)
    updated_date: datetime = field(default_factory=datetime.now)
    related_experiences: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    verification_status: str = "draft"  # draft, verified, deprecated

@dataclass
class ExperienceSearchResult:
    """搜索结果类"""
    experience: Experience
    relevance_score: float
    matched_terms: List[str]

@dataclass
class ExperienceStatistics:
    """经验统计类"""
    total_experiences: int
    category_distribution: Dict[str, int]
    popular_tags: List[tuple]
    average_rating: float
    top_contributors: List[tuple]
    usage_trends: Dict[str, Any]
```

### 经验收集器

```python
import re
from typing import List, Dict, Any
from datetime import datetime

class ExperienceCollector:
    """经验收集器"""

    def __init__(self):
        self.experience_patterns = {
            'success_pattern': r'成功|有效|改进|优化|提升',
            'failure_pattern': r'失败|问题|错误|缺陷|风险',
            'lesson_pattern': r'教训|经验|发现|总结',
            'recommendation_pattern': r'建议|措施|方法|做法'
        }

    def collect_from_retrospective(self, retrospective_data: Dict[str, Any]) -> List[Experience]:
        """从复盘会议收集经验"""
        experiences = []

        # 从KPT分析中提取经验
        kpt_data = retrospective_data.get('kpt_analysis', {})
        experiences.extend(self._extract_from_kpt(kpt_data))

        # 从根本原因分析中提取经验
        rca_data = retrospective_data.get('root_cause_analysis', {})
        experiences.extend(self._extract_from_rca(rca_data))

        # 从度量分析中提取经验
        metrics_data = retrospective_data.get('metrics_analysis', {})
        experiences.extend(self._extract_from_metrics(metrics_data))

        return experiences

    def _extract_from_kpt(self, kpt_data: Dict[str, Any]) -> List[Experience]:
        """从KPT分析提取经验"""
        experiences = []

        # 处理Keep项
        for keep_item in kpt_data.get('keep_items', []):
            experience = Experience(
                title=f"成功的实践: {keep_item['item']}",
                category="successful_practice",
                description=keep_item['reason'],
                lessons_learned=f"保持{keep_item['item']}的做法是有效的",
                impact={'benefit': keep_item.get('impact', '积极影响')},
                recommendations=[f"继续保持并推广{keep_item['item']}的做法"],
                tags=['success', 'best_practice', 'keep'],
                author=kpt_data.get('facilitator', 'retrospective_team')
            )
            experiences.append(experience)

        # 处理Problem项
        for problem_item in kpt_data.get('problem_items', []):
            experience = Experience(
                title=f"需要解决的问题: {problem_item['item']}",
                category="problem_solution",
                description=problem_item['item'],
                context={'root_cause': problem_item.get('root_cause', '')},
                lessons_learned=f"发现问题: {problem_item['item']}",
                recommendations=problem_item.get('solutions', []),
                tags=['problem', 'improvement_needed'],
                author=kpt_data.get('facilitator', 'retrospective_team')
            )
            experiences.append(experience)

        # 处理Try项
        for try_item in kpt_data.get('try_items', []):
            experience = Experience(
                title=f"尝试的新方法: {try_item['item']}",
                category="innovation",
                description=try_item['expected_benefit'],
                context={'risk_assessment': try_item.get('risk_assessment', '')},
                recommendations=[f"尝试实施{try_item['item']}"],
                tags=['experiment', 'innovation', 'try'],
                author=kpt_data.get('facilitator', 'retrospective_team')
            )
            experiences.append(experience)

        return experiences

    def _extract_from_rca(self, rca_data: Dict[str, Any]) -> List[Experience]:
        """从根本原因分析提取经验"""
        experiences = []

        for issue in rca_data.get('issues', []):
            experience = Experience(
                title=f"问题根因分析: {issue['description']}",
                category="root_cause_analysis",
                description=issue['description'],
                context={
                    'root_causes': issue.get('root_causes', []),
                    'severity': issue.get('severity', 'medium')
                },
                lessons_learned=f"问题根因: {', '.join(issue.get('root_causes', []))}",
                recommendations=rca_data.get('corrective_actions', []),
                tags=['root_cause', 'problem_analysis', issue.get('severity', 'medium')],
                author=rca_data.get('analyst', 'rca_team')
            )
            experiences.append(experience)

        return experiences

    def _extract_from_metrics(self, metrics_data: Dict[str, Any]) -> List[Experience]:
        """从度量分析提取经验"""
        experiences = []

        trends = metrics_data.get('trends', {})
        for metric_name, trend_data in trends.items():
            if trend_data.get('improvement_needed', False):
                experience = Experience(
                    title=f"度量改进经验: {metric_name}",
                    category="metrics_improvement",
                    description=f"{metric_name}指标需要改进",
                    context={
                        'current_value': trend_data.get('current_average'),
                        'target_value': trend_data.get('target'),
                        'trend': trend_data.get('trend_slope', 0)
                    },
                    lessons_learned=f"{metric_name}指标呈{ '上升' if trend_data.get('trend_slope', 0) > 0 else '下降' }趋势",
                    recommendations=metrics_data.get('improvement_suggestions', []),
                    tags=['metrics', 'trend_analysis', 'improvement'],
                    author=metrics_data.get('analyst', 'metrics_team')
                )
                experiences.append(experience)

        return experiences

    def collect_from_incident(self, incident_data: Dict[str, Any]) -> Experience:
        """从故障事件收集经验"""
        return Experience(
            title=f"故障处理经验: {incident_data['title']}",
            category="incident_response",
            description=incident_data['description'],
            context={
                'incident_type': incident_data.get('type'),
                'severity': incident_data.get('severity'),
                'duration': incident_data.get('duration'),
                'impact': incident_data.get('impact')
            },
            lessons_learned=incident_data.get('lessons_learned', ''),
            recommendations=incident_data.get('preventive_measures', []),
            tags=['incident', 'failure', 'recovery', incident_data.get('severity', 'medium')],
            author=incident_data.get('owner', 'incident_team')
        )

    def collect_from_success_story(self, success_data: Dict[str, Any]) -> Experience:
        """从成功案例收集经验"""
        return Experience(
            title=f"成功案例: {success_data['title']}",
            category="success_story",
            description=success_data['description'],
            context={
                'approach': success_data.get('approach'),
                'challenges': success_data.get('challenges'),
                'results': success_data.get('results')
            },
            lessons_learned=success_data.get('key_success_factors', ''),
            recommendations=success_data.get('replicable_practices', []),
            tags=['success', 'best_practice', 'case_study'],
            author=success_data.get('owner', 'success_team')
        )
```

### 经验存储系统

```python
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

class ExperienceRepository:
    """经验知识库"""

    def __init__(self, db_path: str = 'experience_repository.db'):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS experiences (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    description TEXT,
                    context TEXT,
                    lessons_learned TEXT,
                    impact TEXT,
                    recommendations TEXT,
                    tags TEXT,
                    author TEXT,
                    rating INTEGER DEFAULT 0,
                    usage_count INTEGER DEFAULT 0,
                    created_date TEXT,
                    updated_date TEXT,
                    related_experiences TEXT,
                    attachments TEXT,
                    verification_status TEXT DEFAULT 'draft'
                )
            ''')

            # 创建索引
            conn.execute('CREATE INDEX IF NOT EXISTS idx_category ON experiences(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tags ON experiences(tags)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_author ON experiences(author)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_created_date ON experiences(created_date)')

    def save_experience(self, experience: Experience) -> bool:
        """保存经验"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO experiences (
                        id, title, category, subcategory, description, context,
                        lessons_learned, impact, recommendations, tags, author,
                        rating, usage_count, created_date, updated_date,
                        related_experiences, attachments, verification_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    experience.id,
                    experience.title,
                    experience.category,
                    experience.subcategory,
                    experience.description,
                    json.dumps(experience.context),
                    experience.lessons_learned,
                    json.dumps(experience.impact),
                    json.dumps(experience.recommendations),
                    json.dumps(experience.tags),
                    experience.author,
                    experience.rating,
                    experience.usage_count,
                    experience.created_date.isoformat(),
                    experience.updated_date.isoformat(),
                    json.dumps(experience.related_experiences),
                    json.dumps(experience.attachments),
                    experience.verification_status
                ))
            return True
        except Exception as e:
            print(f"保存经验失败: {e}")
            return False

    def get_experience(self, experience_id: str) -> Optional[Experience]:
        """获取经验"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM experiences WHERE id = ?', (experience_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_experience(row)
            return None

    def search_experiences(self, query: str = "", category: Optional[str] = None,
                          tags: Optional[List[str]] = None, author: Optional[str] = None,
                          limit: int = 50) -> List[ExperienceSearchResult]:
        """搜索经验"""
        sql = 'SELECT * FROM experiences WHERE 1=1'
        params = []

        if query:
            sql += ' AND (title LIKE ? OR description LIKE ? OR lessons_learned LIKE ?)'
            params.extend([f'%{query}%'] * 3)

        if category:
            sql += ' AND category = ?'
            params.append(category)

        if author:
            sql += ' AND author = ?'
            params.append(author)

        if tags:
            tag_conditions = ' OR '.join(['tags LIKE ?'] * len(tags))
            sql += f' AND ({tag_conditions})'
            params.extend([f'%{tag}%' for tag in tags])

        sql += ' ORDER BY rating DESC, usage_count DESC LIMIT ?'
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(sql, params)
            results = []

            for row in cursor.fetchall():
                experience = self._row_to_experience(row)
                relevance_score = self._calculate_relevance_score(experience, query, tags)
                matched_terms = self._find_matched_terms(experience, query, tags)

                results.append(ExperienceSearchResult(
                    experience=experience,
                    relevance_score=relevance_score,
                    matched_terms=matched_terms
                ))

            return results

    def _row_to_experience(self, row) -> Experience:
        """将数据库行转换为Experience对象"""
        return Experience(
            id=row[0],
            title=row[1],
            category=row[2],
            subcategory=row[3],
            description=row[4],
            context=json.loads(row[5] or '{}'),
            lessons_learned=row[6],
            impact=json.loads(row[7] or '{}'),
            recommendations=json.loads(row[8] or '[]'),
            tags=json.loads(row[9] or '[]'),
            author=row[10],
            rating=row[11],
            usage_count=row[12],
            created_date=datetime.fromisoformat(row[13]),
            updated_date=datetime.fromisoformat(row[14]),
            related_experiences=json.loads(row[15] or '[]'),
            attachments=json.loads(row[16] or '[]'),
            verification_status=row[17]
        )

    def _calculate_relevance_score(self, experience: Experience, query: str,
                                 tags: Optional[List[str]]) -> float:
        """计算相关性得分"""
        score = 0.0

        if query:
            query_lower = query.lower()
            # 标题匹配
            if query_lower in experience.title.lower():
                score += 1.0
            # 描述匹配
            if query_lower in experience.description.lower():
                score += 0.8
            # 经验教训匹配
            if query_lower in experience.lessons_learned.lower():
                score += 0.6

        if tags:
            # 标签匹配
            experience_tags = set(experience.tags)
            query_tags = set(tags)
            tag_matches = len(experience_tags.intersection(query_tags))
            score += tag_matches * 0.5

        # 基于评分的加权
        score += experience.rating * 0.1

        # 基于使用次数的加权
        score += min(experience.usage_count * 0.01, 1.0)

        return score

    def _find_matched_terms(self, experience: Experience, query: str,
                          tags: Optional[List[str]]) -> List[str]:
        """查找匹配的术语"""
        matched_terms = []

        if query:
            query_lower = query.lower()
            if query_lower in experience.title.lower():
                matched_terms.append(f"标题: {experience.title}")
            if query_lower in experience.description.lower():
                matched_terms.append("描述")
            if query_lower in experience.lessons_learned.lower():
                matched_terms.append("经验教训")

        if tags:
            matched_tags = set(experience.tags).intersection(set(tags))
            matched_terms.extend([f"标签: {tag}" for tag in matched_tags])

        return matched_terms

    def update_rating(self, experience_id: str, rating: int) -> bool:
        """更新评分"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE experiences
                    SET rating = ?, updated_date = ?
                    WHERE id = ?
                ''', (rating, datetime.now().isoformat(), experience_id))
            return True
        except Exception as e:
            print(f"更新评分失败: {e}")
            return False

    def increment_usage(self, experience_id: str) -> bool:
        """增加使用计数"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE experiences
                    SET usage_count = usage_count + 1, updated_date = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), experience_id))
            return True
        except Exception as e:
            print(f"增加使用计数失败: {e}")
            return False

    def get_statistics(self) -> ExperienceStatistics:
        """获取统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            # 总数
            cursor = conn.execute('SELECT COUNT(*) FROM experiences')
            total_experiences = cursor.fetchone()[0]

            # 分类分布
            cursor = conn.execute('''
                SELECT category, COUNT(*) as count
                FROM experiences
                GROUP BY category
                ORDER BY count DESC
            ''')
            category_distribution = dict(cursor.fetchall())

            # 热门标签
            cursor = conn.execute('SELECT tags FROM experiences')
            all_tags = []
            for row in cursor.fetchall():
                tags = json.loads(row[0] or '[]')
                all_tags.extend(tags)

            from collections import Counter
            popular_tags = Counter(all_tags).most_common(10)

            # 平均评分
            cursor = conn.execute('SELECT AVG(rating) FROM experiences WHERE rating > 0')
            avg_rating = cursor.fetchone()[0] or 0.0

            # 顶级贡献者
            cursor = conn.execute('''
                SELECT author, COUNT(*) as count
                FROM experiences
                WHERE author IS NOT NULL AND author != ''
                GROUP BY author
                ORDER BY count DESC
                LIMIT 10
            ''')
            top_contributors = cursor.fetchall()

            # 使用趋势（简化的实现）
            usage_trends = {'total_usage': 0, 'recent_activity': 0}

            return ExperienceStatistics(
                total_experiences=total_experiences,
                category_distribution=category_distribution,
                popular_tags=popular_tags,
                average_rating=avg_rating,
                top_contributors=top_contributors,
                usage_trends=usage_trends
            )

    def export_to_csv(self, file_path: str):
        """导出为CSV"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query('SELECT * FROM experiences', conn)
            df.to_csv(file_path, index=False)

    def import_from_csv(self, file_path: str):
        """从CSV导入"""
        df = pd.read_csv(file_path)

        for _, row in df.iterrows():
            experience = Experience(
                id=row['id'],
                title=row['title'],
                category=row['category'],
                subcategory=row.get('subcategory'),
                description=row['description'],
                context=json.loads(row.get('context', '{}')),
                lessons_learned=row['lessons_learned'],
                impact=json.loads(row.get('impact', '{}')),
                recommendations=json.loads(row.get('recommendations', '[]')),
                tags=json.loads(row.get('tags', '[]')),
                author=row['author'],
                rating=row.get('rating', 0),
                usage_count=row.get('usage_count', 0),
                created_date=datetime.fromisoformat(row['created_date']),
                updated_date=datetime.fromisoformat(row['updated_date']),
                related_experiences=json.loads(row.get('related_experiences', '[]')),
                attachments=json.loads(row.get('attachments', '[]')),
                verification_status=row.get('verification_status', 'draft')
            )
            self.save_experience(experience)
```

### 经验推荐引擎

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
import numpy as np

class ExperienceRecommender:
    """经验推荐引擎"""

    def __init__(self, repository: ExperienceRepository):
        self.repository = repository
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.experience_vectors = {}
        self._build_vectors()

    def _build_vectors(self):
        """构建经验向量"""
        experiences = self.repository.search_experiences(limit=1000)
        texts = []

        for result in experiences:
            exp = result.experience
            # 组合文本用于向量化
            text = f"{exp.title} {exp.description} {exp.lessons_learned} {' '.join(exp.tags)}"
            texts.append(text)

        if texts:
            self.experience_vectors = {
                exp.experience.id: vector
                for exp, vector in zip(experiences, self.vectorizer.fit_transform(texts).toarray())
            }

    def recommend_similar_experiences(self, experience_id: str, limit: int = 5) -> List[ExperienceSearchResult]:
        """推荐相似经验"""
        if experience_id not in self.experience_vectors:
            return []

        target_vector = self.experience_vectors[experience_id]
        similarities = {}

        for exp_id, vector in self.experience_vectors.items():
            if exp_id != experience_id:
                similarity = cosine_similarity([target_vector], [vector])[0][0]
                similarities[exp_id] = similarity

        # 按相似度排序
        sorted_similar = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:limit]

        results = []
        for exp_id, similarity in sorted_similar:
            experience = self.repository.get_experience(exp_id)
            if experience:
                results.append(ExperienceSearchResult(
                    experience=experience,
                    relevance_score=float(similarity),
                    matched_terms=["相似度匹配"]
                ))

        return results

    def recommend_by_context(self, context: Dict[str, Any], limit: int = 5) -> List[ExperienceSearchResult]:
        """基于上下文推荐经验"""
        # 根据上下文构建查询
        query_parts = []

        if 'project_type' in context:
            query_parts.append(context['project_type'])

        if 'technology' in context:
            query_parts.append(context['technology'])

        if 'problem_type' in context:
            query_parts.append(context['problem_type'])

        if 'phase' in context:
            query_parts.append(context['phase'])

        query = ' '.join(query_parts)

        if not query:
            return []

        # 使用向量空间模型进行推荐
        query_vector = self.vectorizer.transform([query]).toarray()[0]
        similarities = {}

        for exp_id, vector in self.experience_vectors.items():
            similarity = cosine_similarity([query_vector], [vector])[0][0]
            similarities[exp_id] = similarity

        # 按相似度排序
        sorted_similar = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:limit]

        results = []
        for exp_id, similarity in sorted_similar:
            experience = self.repository.get_experience(exp_id)
            if experience:
                results.append(ExperienceSearchResult(
                    experience=experience,
                    relevance_score=float(similarity),
                    matched_terms=["上下文匹配"]
                ))

        return results

    def recommend_by_user_history(self, user_id: str, limit: int = 5) -> List[ExperienceSearchResult]:
        """基于用户历史推荐经验"""
        # 获取用户的历史行为（简化的实现）
        # 在实际系统中，这应该从用户行为数据库中获取

        # 假设我们有用户偏好的类别
        user_preferences = self._get_user_preferences(user_id)

        recommendations = []
        for category in user_preferences:
            results = self.repository.search_experiences(category=category, limit=limit//len(user_preferences))
            recommendations.extend([r for r in results])

        # 去重并排序
        seen_ids = set()
        unique_recommendations = []
        for result in recommendations:
            if result.experience.id not in seen_ids:
                unique_recommendations.append(result)
                seen_ids.add(result.experience.id)

        return unique_recommendations[:limit]

    def _get_user_preferences(self, user_id: str) -> List[str]:
        """获取用户偏好（简化的实现）"""
        # 在实际系统中，这应该基于用户的浏览、评分、使用历史计算
        return ['successful_practice', 'problem_solution', 'best_practice']
```

### 经验分析器

```python
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter, defaultdict
import pandas as pd
from typing import Dict, List, Any

class ExperienceAnalyzer:
    """经验分析器"""

    def __init__(self, repository: ExperienceRepository):
        self.repository = repository

    def analyze_category_trends(self) -> Dict[str, Any]:
        """分析分类趋势"""
        experiences = self.repository.search_experiences(limit=10000)

        # 按类别分组
        category_stats = defaultdict(lambda: {'count': 0, 'avg_rating': 0, 'total_usage': 0})

        for result in experiences:
            exp = result.experience
            cat = exp.category
            category_stats[cat]['count'] += 1
            category_stats[cat]['avg_rating'] += exp.rating
            category_stats[cat]['total_usage'] += exp.usage_count

        # 计算平均值
        for cat, stats in category_stats.items():
            if stats['count'] > 0:
                stats['avg_rating'] /= stats['count']

        return dict(category_stats)

    def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """分析时间模式"""
        experiences = self.repository.search_experiences(limit=10000)

        # 按月份统计
        monthly_stats = defaultdict(lambda: {'count': 0, 'categories': defaultdict(int)})

        for result in experiences:
            exp = result.experience
            month_key = exp.created_date.strftime('%Y-%m')
            monthly_stats[month_key]['count'] += 1
            monthly_stats[month_key]['categories'][exp.category] += 1

        return dict(monthly_stats)

    def extract_common_themes(self) -> Dict[str, List[str]]:
        """提取常见主题"""
        experiences = self.repository.search_experiences(limit=10000)

        # 分析标签共现
        tag_cooccurrence = defaultdict(lambda: defaultdict(int))

        for result in experiences:
            exp = result.experience
            tags = exp.tags
            for i, tag1 in enumerate(tags):
                for tag2 in tags[i+1:]:
                    tag_cooccurrence[tag1][tag2] += 1
                    tag_cooccurrence[tag2][tag1] += 1

        # 找出强关联的标签对
        strong_associations = []
        for tag1, associations in tag_cooccurrence.items():
            for tag2, count in associations.items():
                if count >= 3:  # 至少出现3次
                    strong_associations.append((tag1, tag2, count))

        strong_associations.sort(key=lambda x: x[2], reverse=True)

        return {
            'tag_associations': strong_associations[:20],  # 前20个强关联
            'common_tag_combinations': self._find_common_combinations(experiences)
        }

    def _find_common_combinations(self, experiences: List[ExperienceSearchResult]) -> List[tuple]:
        """找出常见标签组合"""
        combinations = Counter()

        for result in experiences:
            exp = result.experience
            if len(exp.tags) >= 2:
                # 取最常见的标签组合
                sorted_tags = sorted(exp.tags)
                for i in range(len(sorted_tags)):
                    for j in range(i+1, len(sorted_tags)):
                        combinations[(sorted_tags[i], sorted_tags[j])] += 1

        return combinations.most_common(10)

    def generate_insights_report(self) -> Dict[str, Any]:
        """生成洞察报告"""
        category_trends = self.analyze_category_trends()
        temporal_patterns = self.analyze_temporal_patterns()
        common_themes = self.extract_common_themes()

        insights = []

        # 类别洞察
        if category_trends:
            top_category = max(category_trends.items(), key=lambda x: x[1]['count'])
            insights.append(f"最活跃的经验类别是 '{top_category[0]}'，共有 {top_category[1]['count']} 条经验")

            high_rated_category = max(category_trends.items(), key=lambda x: x[1]['avg_rating'])
            insights.append(f"评分最高的经验类别是 '{high_rated_category[0]}'，平均评分为 {high_rated_category[1]['avg_rating']:.1f}")

        # 时间洞察
        if temporal_patterns:
            recent_months = sorted(temporal_patterns.keys())[-3:]  # 最近3个月
            recent_activity = sum(temporal_patterns[month]['count'] for month in recent_months)
            insights.append(f"最近3个月新增了 {recent_activity} 条经验")

        # 主题洞察
        if common_themes['tag_associations']:
            top_association = common_themes['tag_associations'][0]
            insights.append(f"最常见的标签关联是 '{top_association[0]}' 和 '{top_association[1]}'，共出现 {top_association[2]} 次")

        return {
            'category_trends': category_trends,
            'temporal_patterns': temporal_patterns,
            'common_themes': common_themes,
            'insights': insights
        }

    def create_visualizations(self, output_dir: str = 'visualizations'):
        """创建可视化图表"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        # 类别分布图
        category_data = self.analyze_category_trends()
        if category_data:
            categories = list(category_data.keys())
            counts = [data['count'] for data in category_data.values()]

            plt.figure(figsize=(10, 6))
            sns.barplot(x=counts, y=categories)
            plt.title('经验类别分布')
            plt.xlabel('经验数量')
            plt.ylabel('类别')
            plt.tight_layout()
            plt.savefig(f'{output_dir}/category_distribution.png')
            plt.close()

        # 时间趋势图
        temporal_data = self.analyze_temporal_patterns()
        if temporal_data:
            months = sorted(temporal_data.keys())
            counts = [temporal_data[month]['count'] for month in months]

            plt.figure(figsize=(12, 6))
            plt.plot(months, counts, marker='o')
            plt.title('经验创建时间趋势')
            plt.xlabel('月份')
            plt.ylabel('经验数量')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'{output_dir}/temporal_trends.png')
            plt.close()

        # 标签词云
        experiences = self.repository.search_experiences(limit=1000)
        all_tags = []
        for result in experiences:
            all_tags.extend(result.experience.tags)

        if all_tags:
            tag_text = ' '.join(all_tags)
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(tag_text)

            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('经验标签词云')
            plt.tight_layout()
            plt.savefig(f'{output_dir}/tag_wordcloud.png')
            plt.close()
```

## 使用示例

### 基本使用

```python
# 初始化系统
collector = ExperienceCollector()
repository = ExperienceRepository()
recommender = ExperienceRecommender(repository)
analyzer = ExperienceAnalyzer(repository)

# 从复盘会议收集经验
retrospective_data = {
    'kpt_analysis': {
        'keep_items': [{'item': '每日站会', 'reason': '提高团队沟通效率'}],
        'problem_items': [{'item': '测试环境不稳定', 'root_cause': '配置管理不善'}],
        'try_items': [{'item': '自动化部署', 'expected_benefit': '减少手动错误'}]
    }
}

experiences = collector.collect_from_retrospective(retrospective_data)

# 保存经验
for exp in experiences:
    repository.save_experience(exp)

# 搜索经验
results = repository.search_experiences(query="测试环境", limit=5)
for result in results:
    print(f"找到经验: {result.experience.title} (相关性: {result.relevance_score:.2f})")

# 获取推荐
recommendations = recommender.recommend_similar_experiences(experiences[0].id)
for rec in recommendations:
    print(f"推荐经验: {rec.experience.title}")

# 生成分析报告
insights = analyzer.generate_insights_report()
print("关键洞察:")
for insight in insights['insights']:
    print(f"- {insight}")

# 创建可视化
analyzer.create_visualizations()
```

这个经验知识库系统为大数据测试团队提供了完整的经验管理解决方案，支持经验的收集、存储、检索、推荐和分析，帮助团队不断积累知识，提升测试质量和效率。