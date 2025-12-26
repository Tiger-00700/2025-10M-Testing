# 大数据测试工具选型方法与评估框架

## 概述

本文档详细介绍大数据测试工具的选型方法、评估框架和决策流程，为测试团队提供科学、系统的工具选型指导。

## 选型方法论

### 多维度评估框架

评估框架基于以下核心原则：
- **科学性**: 基于数据和事实的量化评估
- **全面性**: 覆盖功能、技术、成本等多个维度
- **实用性**: 结合实际项目需求和约束条件
- **可持续性**: 考虑长期发展和维护成本

### 评估维度体系

#### 1. 功能完整性 (25%)
评估工具是否满足核心测试需求

**子维度**:
- **核心功能覆盖**: 基本测试功能是否完备
- **扩展能力**: 插件和定制开发能力
- **集成能力**: 与其他工具的集成程度
- **自动化程度**: 测试流程自动化水平

**评分标准**:
- 5分: 功能完备，扩展性强，高度自动化
- 4分: 功能较全，扩展性好，自动化水平高
- 3分: 功能基本满足，有一定扩展性
- 2分: 功能不全，扩展性有限
- 1分: 功能缺失，难以扩展

#### 2. 技术成熟度 (20%)
评估工具的技术稳定性和发展状况

**子维度**:
- **版本稳定性**: 版本发布频率和稳定性
- **社区活跃度**: 社区规模和贡献度
- **文档完善度**: 文档质量和更新频率
- **技术支持**: 官方和社区支持力度

**评分标准**:
- 5分: 版本稳定，社区活跃，文档完善
- 4分: 版本较稳定，社区较活跃
- 3分: 版本一般，社区一般
- 2分: 版本不稳定，社区不活跃
- 1分: 版本混乱，缺乏支持

#### 3. 集成友好性 (15%)
评估工具与其他系统的集成难易程度

**子维度**:
- **API丰富度**: 提供的API数量和质量
- **标准支持**: 对行业标准的支持程度
- **生态兼容**: 与现有技术栈的兼容性
- **配置复杂度**: 集成配置的难易程度

**评分标准**:
- 5分: API丰富，标准支持完善，配置简单
- 4分: API较多，标准支持良好
- 3分: API一般，标准支持一般
- 2分: API有限，标准支持不足
- 1分: 无API，难以集成

#### 4. 成本效益 (15%)
评估工具的总拥有成本和投资回报

**子维度**:
- **许可证费用**: 软件授权和使用费用
- **实施成本**: 部署和配置成本
- **维护成本**: 运维和升级成本
- **培训成本**: 团队学习和培训成本

**评分标准** (成本型指标，越低越好):
- 5分: 极低成本 (<5万/年)
- 4分: 较低成本 (5-15万/年)
- 3分: 中等成本 (15-30万/年)
- 2分: 较高成本 (30-50万/年)
- 1分: 极高成本 (>50万/年)

#### 5. 厂商支持 (10%)
评估厂商的服务质量和技术支持

**子维度**:
- **技术支持**: 支持渠道和响应质量
- **响应时间**: 问题解决的及时性
- **服务水平**: SLA保证和承诺
- **培训资源**: 提供的培训和文档资源

**评分标准**:
- 5分: 7×24支持，<2小时响应，完善培训
- 4分: 工作时间支持，<4小时响应
- 3分: 工作时间支持，<8小时响应
- 2分: 有限支持，响应较慢
- 1分: 缺乏有效支持

#### 6. 扩展性 (10%)
评估工具的性能和扩展能力

**子维度**:
- **并发能力**: 支持的并发测试规模
- **数据规模**: 处理的数据量上限
- **集群部署**: 分布式部署能力
- **资源效率**: 资源利用率和性能表现

**评分标准**:
- 5分: 并发能力强，扩展性极好
- 4分: 并发能力良好，扩展性好
- 3分: 并发能力一般，扩展性一般
- 2分: 并发能力有限，扩展性不足
- 1分: 并发能力弱，难以扩展

#### 7. 安全性 (5%)
评估工具的安全性和合规性

**子维度**:
- **安全认证**: 支持的安全认证机制
- **数据保护**: 数据加密和保护能力
- **合规性**: 符合的安全标准和认证
- **漏洞管理**: 安全漏洞的发现和修复

**评分标准**:
- 5分: 安全认证完善，合规性强
- 4分: 安全认证良好，基本合规
- 3分: 安全认证一般，部分合规
- 2分: 安全认证不足，合规性弱
- 1分: 缺乏安全措施，不合规

## 评估流程

### 第一阶段：需求分析

```python
# 需求分析框架
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ProjectScale(Enum):
    SMALL = "small"      # < 10人团队
    MEDIUM = "medium"    # 10-50人团队
    LARGE = "large"      # 50-200人团队
    ENTERPRISE = "enterprise"  # > 200人团队

class BudgetLevel(Enum):
    LOW = "low"          # < 10万/年
    MEDIUM = "medium"    # 10-50万/年
    HIGH = "high"        # > 50万/年

class TestType(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DATA_QUALITY = "data_quality"
    MONITORING = "monitoring"

@dataclass
class ProjectRequirements:
    """项目需求分析"""
    name: str
    scale: ProjectScale
    budget: BudgetLevel
    test_types: List[TestType]
    languages: List[str]
    platforms: List[str]
    integrations: List[str]
    constraints: List[str]
    priorities: Dict[str, int]  # 需求优先级

class RequirementsAnalyzer:
    """需求分析器"""

    def __init__(self):
        self.templates = self._load_requirement_templates()

    def _load_requirement_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载需求模板"""
        return {
            "small_startup": {
                "scale": ProjectScale.SMALL,
                "budget": BudgetLevel.LOW,
                "test_types": [TestType.UNIT, TestType.INTEGRATION],
                "languages": ["python", "javascript"],
                "platforms": ["linux"],
                "integrations": ["github", "docker"],
                "constraints": ["快速迭代", "成本控制"],
                "priorities": {"cost": 5, "ease_of_use": 4, "functionality": 3}
            },

            "medium_enterprise": {
                "scale": ProjectScale.MEDIUM,
                "budget": BudgetLevel.MEDIUM,
                "test_types": [TestType.UNIT, TestType.INTEGRATION, TestType.PERFORMANCE],
                "languages": ["java", "python"],
                "platforms": ["linux", "windows"],
                "integrations": ["jenkins", "kubernetes", "aws"],
                "constraints": ["企业安全", "合规要求"],
                "priorities": {"security": 5, "scalability": 4, "support": 3}
            },

            "large_corporation": {
                "scale": ProjectScale.LARGE,
                "budget": BudgetLevel.HIGH,
                "test_types": [TestType.UNIT, TestType.INTEGRATION, TestType.PERFORMANCE,
                             TestType.SECURITY, TestType.DATA_QUALITY],
                "languages": ["java", "scala", "python"],
                "platforms": ["linux", "windows", "kubernetes"],
                "integrations": ["jenkins", "kubernetes", "aws", "azure"],
                "constraints": ["企业级支持", "高可用性"],
                "priorities": {"reliability": 5, "enterprise_support": 4, "compliance": 3}
            }
        }

    def analyze_requirements(self, project_context: Dict[str, Any]) -> ProjectRequirements:
        """分析项目需求"""

        # 从模板匹配
        template_key = self._match_template(project_context)
        template = self.templates.get(template_key, {})

        # 自定义调整
        requirements = ProjectRequirements(
            name=project_context.get("name", "Unknown Project"),
            scale=project_context.get("scale", template.get("scale", ProjectScale.MEDIUM)),
            budget=project_context.get("budget", template.get("budget", BudgetLevel.MEDIUM)),
            test_types=project_context.get("test_types", template.get("test_types", [])),
            languages=project_context.get("languages", template.get("languages", [])),
            platforms=project_context.get("platforms", template.get("platforms", [])),
            integrations=project_context.get("integrations", template.get("integrations", [])),
            constraints=project_context.get("constraints", template.get("constraints", [])),
            priorities=project_context.get("priorities", template.get("priorities", {}))
        )

        return requirements

    def _match_template(self, context: Dict[str, Any]) -> str:
        """匹配需求模板"""
        scale = context.get("team_size", 10)

        if scale < 10:
            return "small_startup"
        elif scale < 50:
            return "medium_enterprise"
        else:
            return "large_corporation"

    def generate_requirements_report(self, requirements: ProjectRequirements) -> str:
        """生成需求分析报告"""

        report = f"""
# 项目需求分析报告

## 项目概况

- **项目名称**: {requirements.name}
- **项目规模**: {requirements.scale.value}
- **预算水平**: {requirements.budget.value}

## 测试需求

### 测试类型
{chr(10).join(f"- {t.value}" for t in requirements.test_types)}

### 技术栈
- **编程语言**: {', '.join(requirements.languages)}
- **部署平台**: {', '.join(requirements.platforms)}
- **集成需求**: {', '.join(requirements.integrations)}

## 约束条件

{chr(10).join(f"- {c}" for c in requirements.constraints)}

## 优先级排序

"""

        # 按优先级排序
        sorted_priorities = sorted(requirements.priorities.items(), key=lambda x: x[1], reverse=True)

        for item, priority in sorted_priorities:
            report += f"- {item}: {priority}/5\n"

        report += """
## 建议的评估权重调整

基于项目特点，建议调整评估框架的权重：

"""

        # 根据需求调整权重建议
        if requirements.scale == ProjectScale.SMALL:
            report += "- 降低扩展性权重，增加易用性权重\n"
        elif requirements.scale == ProjectScale.ENTERPRISE:
            report += "- 提高厂商支持权重，增加安全性权重\n"

        if requirements.budget == BudgetLevel.LOW:
            report += "- 提高成本效益权重\n"
        elif requirements.budget == BudgetLevel.HIGH:
            report += "- 降低成本效益权重，增加功能完整性权重\n"

        return report

# 使用示例
if __name__ == "__main__":
    analyzer = RequirementsAnalyzer()

    # 项目上下文
    context = {
        "name": "大数据测试平台",
        "team_size": 25,
        "test_types": ["unit", "integration", "performance", "data_quality"],
        "languages": ["python", "java"],
        "platforms": ["kubernetes", "aws"],
        "integrations": ["jenkins", "prometheus"],
        "constraints": ["云原生架构", "DevOps流程"],
        "priorities": {"scalability": 5, "integration": 4, "cost": 3}
    }

    requirements = analyzer.analyze_requirements(context)
    report = analyzer.generate_requirements_report(requirements)

    print("需求分析报告:")
    print(report)
```

### 第二阶段：工具调研

```python
# 工具调研框架
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
import json
from datetime import datetime

@dataclass
class ToolInfo:
    """工具信息"""
    name: str
    category: str
    description: str
    website: str
    repository: str
    license: str
    latest_version: str
    release_date: str
    stars: int
    forks: int
    issues: int
    contributors: int

@dataclass
class ToolReview:
    """工具评价"""
    tool_name: str
    reviewer: str
    rating: int  # 1-5分
    pros: List[str]
    cons: List[str]
    use_case: str
    review_date: str

class ToolResearcher:
    """工具调研器"""

    def __init__(self):
        self.tool_database = {}
        self.reviews = {}
        self.sources = {
            "github": "https://api.github.com",
            "libraries.io": "https://libraries.io/api",
            "alternativeto": "https://alternativeto.net/api"
        }

    def research_tool(self, tool_name: str, category: str) -> ToolInfo:
        """调研工具信息"""

        # 从GitHub获取信息
        github_info = self._get_github_info(tool_name)

        # 从其他来源补充信息
        additional_info = self._get_additional_info(tool_name)

        tool_info = ToolInfo(
            name=tool_name,
            category=category,
            description=github_info.get("description", ""),
            website=additional_info.get("website", ""),
            repository=github_info.get("html_url", ""),
            license=github_info.get("license", {}).get("name", "Unknown"),
            latest_version=github_info.get("tag_name", "Unknown"),
            release_date=github_info.get("published_at", "Unknown"),
            stars=github_info.get("stargazers_count", 0),
            forks=github_info.get("forks_count", 0),
            issues=github_info.get("open_issues_count", 0),
            contributors=self._get_contributor_count(tool_name)
        )

        self.tool_database[tool_name] = tool_info
        return tool_info

    def _get_github_info(self, tool_name: str) -> Dict[str, Any]:
        """从GitHub获取工具信息"""
        try:
            # 假设工具名格式为 owner/repo
            if "/" in tool_name:
                owner, repo = tool_name.split("/", 1)
            else:
                # 尝试搜索最匹配的仓库
                owner, repo = self._search_github_repo(tool_name)

            url = f"{self.sources['github']}/repos/{owner}/{repo}"
            headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN', '')}"}

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            # 获取最新release信息
            release_url = f"{url}/releases/latest"
            release_response = requests.get(release_url, headers=headers)

            release_info = {}
            if release_response.status_code == 200:
                release_data = release_response.json()
                release_info = {
                    "tag_name": release_data.get("tag_name"),
                    "published_at": release_data.get("published_at")
                }

            return {**data, **release_info}

        except Exception as e:
            print(f"Error fetching GitHub info for {tool_name}: {e}")
            return {}

    def _search_github_repo(self, tool_name: str) -> tuple:
        """搜索GitHub仓库"""
        try:
            url = f"{self.sources['github']}/search/repositories"
            params = {
                "q": f"{tool_name} in:name",
                "sort": "stars",
                "order": "desc"
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("items"):
                repo = data["items"][0]
                full_name = repo["full_name"]
                return full_name.split("/", 1)

        except Exception as e:
            print(f"Error searching GitHub for {tool_name}: {e}")

        return "unknown", tool_name

    def _get_contributor_count(self, tool_name: str) -> int:
        """获取贡献者数量"""
        try:
            if "/" in tool_name:
                owner, repo = tool_name.split("/", 1)
            else:
                owner, repo = self._search_github_repo(tool_name)

            url = f"{self.sources['github']}/repos/{owner}/{repo}/contributors"
            params = {"per_page": 1, "anon": "true"}

            response = requests.get(url, params=params)
            if response.status_code == 200:
                # 从Link头获取总数
                link_header = response.headers.get("Link", "")
                if "rel=\"last\"" in link_header:
                    # 解析分页信息
                    import re
                    match = re.search(r'page=(\d+)>; rel="last"', link_header)
                    if match:
                        return int(match.group(1))

            return len(response.json()) if response.status_code == 200 else 0

        except Exception as e:
            print(f"Error fetching contributors for {tool_name}: {e}")
            return 0

    def _get_additional_info(self, tool_name: str) -> Dict[str, Any]:
        """获取额外信息"""
        # 这里可以集成其他API如libraries.io等
        return {}

    def add_review(self, review: ToolReview):
        """添加工具评价"""
        if review.tool_name not in self.reviews:
            self.reviews[review.tool_name] = []

        self.reviews[review.tool_name].append(review)

    def get_tool_reviews(self, tool_name: str) -> List[ToolReview]:
        """获取工具评价"""
        return self.reviews.get(tool_name, [])

    def get_tool_score(self, tool_name: str) -> Dict[str, Any]:
        """计算工具综合评分"""
        reviews = self.get_tool_reviews(tool_name)

        if not reviews:
            return {"average_rating": 0, "review_count": 0}

        total_rating = sum(review.rating for review in reviews)
        average_rating = total_rating / len(reviews)

        return {
            "average_rating": round(average_rating, 2),
            "review_count": len(reviews),
            "rating_distribution": self._get_rating_distribution(reviews)
        }

    def _get_rating_distribution(self, reviews: List[ToolReview]) -> Dict[int, int]:
        """获取评分分布"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            distribution[review.rating] += 1
        return distribution

    def generate_research_report(self, tools: List[str]) -> str:
        """生成调研报告"""

        report = f"""
# 测试工具调研报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 调研工具列表

"""

        for tool_name in tools:
            if tool_name in self.tool_database:
                tool = self.tool_database[tool_name]
                score = self.get_tool_score(tool_name)

                report += f"""
### {tool.name}

**基本信息:**
- 分类: {tool.category}
- 许可证: {tool.license}
- 最新版本: {tool.latest_version}
- 发布时间: {tool.release_date}

**社区指标:**
- Stars: {tool.stars}
- Forks: {tool.forks}
- Issues: {tool.issues}
- Contributors: {tool.contributors}

**用户评价:**
- 平均评分: {score['average_rating']}/5
- 评价数量: {score['review_count']}

**评分分布:**
"""

                for rating, count in score.get('rating_distribution', {}).items():
                    report += f"- {rating}星: {count}人\n"

                # 添加评价摘要
                reviews = self.get_tool_reviews(tool_name)
                if reviews:
                    report += "\n**主要评价:**\n"
                    for review in reviews[:3]:  # 显示前3个评价
                        report += f"- {review.reviewer}: {review.rating}星 - {review.use_case}\n"

        report += """
## 调研建议

1. **优先考虑**: 社区活跃、评价良好的工具
2. **谨慎评估**: 评价较少或版本不稳定的工具
3. **PoC验证**: 选择2-3个候选工具进行概念验证
4. **团队试用**: 让开发团队实际使用一段时间

"""

        return report

# 使用示例
if __name__ == "__main__":
    researcher = ToolResearcher()

    # 调研工具
    tools = ["pytest", "jmeter", "great_expectations", "prometheus"]

    for tool in tools:
        info = researcher.research_tool(tool, "testing")
        print(f"Researched {tool}: {info.stars} stars, {info.contributors} contributors")

    # 添加评价示例
    review1 = ToolReview(
        tool_name="pytest",
        reviewer="测试工程师",
        rating=5,
        pros=["易用性好", "插件丰富", "社区活跃"],
        cons=["学习曲线稍陡"],
        use_case="Python单元测试",
        review_date=datetime.now().isoformat()
    )
    researcher.add_review(review1)

    # 生成报告
    report = researcher.generate_research_report(tools)
    print("调研报告:")
    print(report)
```

### 第三阶段：评估实施

```python
# 工具评估实施框架
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

@dataclass
class EvaluationCriteria:
    """评估准则"""
    name: str
    weight: float
    description: str
    scale_type: str  # 'benefit' or 'cost'
    sub_criteria: List[str]

@dataclass
class ToolScore:
    """工具评分"""
    tool_name: str
    criteria_scores: Dict[str, float]
    weighted_score: float
    rank: int

class ToolEvaluator:
    """工具评估器"""

    def __init__(self):
        self.criteria = self._initialize_criteria()
        self.evaluation_history = []

    def _initialize_criteria(self) -> Dict[str, EvaluationCriteria]:
        """初始化评估准则"""
        return {
            "functionality": EvaluationCriteria(
                name="功能完整性",
                weight=0.25,
                description="工具功能是否满足测试需求",
                scale_type="benefit",
                sub_criteria=["核心功能", "扩展能力", "集成能力", "自动化水平"]
            ),

            "maturity": EvaluationCriteria(
                name="技术成熟度",
                weight=0.20,
                description="工具的技术稳定性和发展状况",
                scale_type="benefit",
                sub_criteria=["版本稳定", "社区活跃", "文档完善", "技术支持"]
            ),

            "integration": EvaluationCriteria(
                name="集成友好性",
                weight=0.15,
                description="工具与其他系统的集成能力",
                scale_type="benefit",
                sub_criteria=["API丰富", "标准支持", "生态兼容", "配置复杂度"]
            ),

            "cost": EvaluationCriteria(
                name="成本效益",
                weight=0.15,
                description="工具的成本和投资回报",
                scale_type="cost",
                sub_criteria=["许可证费", "实施成本", "维护成本", "培训成本"]
            ),

            "support": EvaluationCriteria(
                name="厂商支持",
                weight=0.10,
                description="厂商的技术支持和服务质量",
                scale_type="benefit",
                sub_criteria=["技术支持", "响应时间", "服务水平", "培训资源"]
            ),

            "scalability": EvaluationCriteria(
                name="扩展性",
                weight=0.10,
                description="工具的可扩展性和性能表现",
                scale_type="benefit",
                sub_criteria=["并发能力", "数据规模", "集群部署", "资源效率"]
            ),

            "security": EvaluationCriteria(
                name="安全性",
                weight=0.05,
                description="工具的安全性和合规性",
                scale_type="benefit",
                sub_criteria=["安全认证", "数据保护", "合规性", "漏洞管理"]
            )
        }

    def evaluate_tools(self, tools_data: Dict[str, Dict[str, Any]]) -> List[ToolScore]:
        """评估多个工具"""

        tool_scores = []

        for tool_name, criteria_data in tools_data.items():
            score = self._calculate_tool_score(tool_name, criteria_data)
            tool_scores.append(score)

        # 排序
        tool_scores.sort(key=lambda x: x.weighted_score, reverse=True)

        # 分配排名
        for i, score in enumerate(tool_scores, 1):
            score.rank = i

        # 记录评估历史
        self.evaluation_history.append({
            "timestamp": pd.Timestamp.now(),
            "tools_evaluated": [s.tool_name for s in tool_scores],
            "top_choice": tool_scores[0].tool_name if tool_scores else None
        })

        return tool_scores

    def _calculate_tool_score(self, tool_name: str, criteria_data: Dict[str, Any]) -> ToolScore:
        """计算工具评分"""

        criteria_scores = {}
        weighted_score = 0.0

        for criteria_name, criteria in self.criteria.items():
            if criteria_name in criteria_data:
                raw_score = criteria_data[criteria_name]

                # 归一化处理（假设输入是1-10分）
                if criteria.scale_type == "cost":
                    # 成本型准则：分数越低越好，转换为0-1区间
                    normalized_score = (11 - raw_score) / 10
                else:
                    # 效益型准则：分数越高越好，转换为0-1区间
                    normalized_score = raw_score / 10

                criteria_scores[criteria_name] = normalized_score
                weighted_score += normalized_score * criteria.weight

        return ToolScore(
            tool_name=tool_name,
            criteria_scores=criteria_scores,
            weighted_score=round(weighted_score, 4),
            rank=0
        )

    def create_evaluation_matrix(self, tools_data: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """创建评估矩阵"""

        tools = list(tools_data.keys())
        criteria_names = list(self.criteria.keys())

        # 创建数据矩阵
        matrix_data = {}
        for tool in tools:
            tool_data = tools_data[tool]
            matrix_data[tool] = [tool_data.get(criteria, 0) for criteria in criteria_names]

        df = pd.DataFrame(matrix_data, index=criteria_names).T

        # 添加权重行
        weights = [self.criteria[name].weight for name in criteria_names]
        df.loc['权重'] = weights

        return df

    def create_radar_chart(self, tool_scores: List[ToolScore], top_n: int = 3):
        """创建雷达图"""

        # 选择前N个工具
        top_scores = tool_scores[:top_n]

        # 准备数据
        criteria_names = list(self.criteria.keys())
        criteria_display_names = [self.criteria[name].name for name in criteria_names]

        # 创建雷达图
        angles = np.linspace(0, 2 * np.pi, len(criteria_names), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形

        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))

        for score in top_scores:
            values = [score.criteria_scores.get(c, 0) for c in criteria_names]
            values += values[:1]  # 闭合图形

            ax.plot(angles, values, 'o-', linewidth=2, label=score.tool_name)
            ax.fill(angles, values, alpha=0.25)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(criteria_display_names, fontsize=10)
        ax.set_ylim(0, 1)
        ax.set_title('测试工具评估雷达图', size=16, pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        ax.grid(True)

        plt.tight_layout()
        plt.show()

    def sensitivity_analysis(self, tool_score: ToolScore,
                           sensitivity_range: float = 0.1) -> Dict[str, Any]:
        """敏感性分析"""

        results = {}

        for criteria_name in tool_score.criteria_scores:
            criteria = self.criteria[criteria_name]
            base_score = tool_score.criteria_scores[criteria_name]

            # 测试-10%到+10%的变化
            variations = []
            for change in [-sensitivity_range, 0, sensitivity_range]:
                modified_score = base_score * (1 + change)
                modified_score = max(0, min(1, modified_score))  # 限制在0-1范围内

                # 重新计算加权得分
                new_weighted_score = 0.0
                for c_name, c in self.criteria.items():
                    score = modified_score if c_name == criteria_name else tool_score.criteria_scores.get(c_name, 0)
                    new_weighted_score += score * c.weight

                variations.append({
                    "change": f"{change:+.0%}",
                    "score": round(new_weighted_score, 4)
                })

            results[criteria.name] = variations

        return results

    def generate_evaluation_report(self, tool_scores: List[ToolScore],
                                 tools_data: Dict[str, Dict[str, Any]]) -> str:
        """生成评估报告"""

        report = f"""
# 测试工具选型评估报告

生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## 评估概览

总共评估了 {len(tool_scores)} 个工具。

## 评估准则说明

"""

        for criteria in self.criteria.values():
            report += f"""
### {criteria.name} (权重: {criteria.weight})
- **描述**: {criteria.description}
- **类型**: {'效益型' if criteria.scale_type == 'benefit' else '成本型'}
- **子准则**: {', '.join(criteria.sub_criteria)}
"""

        report += """
## 详细评估结果

"""

        for score in tool_scores:
            report += f"""
### 第{score.rank}名: {score.tool_name}
- **综合得分**: {score.weighted_score:.4f}

**各维度得分:**
"""

            for criteria_name, criteria_score in score.criteria_scores.items():
                criteria = self.criteria[criteria_name]
                raw_score = tools_data[score.tool_name][criteria_name]
                report += f"- {criteria.name}: {criteria_score:.3f} (原始分: {raw_score})\n"

        # 添加评估矩阵
        evaluation_matrix = self.create_evaluation_matrix(tools_data)
        report += f"""
## 评估矩阵

{evaluation_matrix.to_markdown()}

"""

        report += """
## 评估方法说明

### 评分标准
- 各维度采用1-10分制
- 效益型准则：分数越高越好
- 成本型准则：分数越低越好（自动转换）
- 加权计算综合得分

### 评估流程
1. 需求分析：明确项目特点和约束条件
2. 工具调研：收集候选工具信息和用户评价
3. 功能评估：实际测试工具功能和性能
4. 综合评估：基于多维度准则计算得分
5. 决策建议：根据评估结果提供选型建议

### 注意事项
- 评估结果仅供参考，建议结合实际PoC验证
- 不同项目对各维度的重视程度可能不同
- 建议定期review和调整评估准则

"""

        return report

    def export_evaluation_model(self) -> Dict[str, Any]:
        """导出评估模型"""

        return {
            "model_name": "测试工具选型评估模型",
            "version": "1.0",
            "criteria": {
                name: {
                    "name": criteria.name,
                    "weight": criteria.weight,
                    "description": criteria.description,
                    "scale_type": criteria.scale_type,
                    "sub_criteria": criteria.sub_criteria
                }
                for name, criteria in self.criteria.items()
            },
            "evaluation_history": self.evaluation_history,
            "export_timestamp": pd.Timestamp.now().isoformat()
        }

# 使用示例
if __name__ == "__main__":
    evaluator = ToolEvaluator()

    # 示例工具评估数据
    tools_data = {
        "JMeter": {
            "functionality": 8.5,
            "maturity": 9.0,
            "integration": 7.5,
            "cost": 2.0,  # 低成本
            "support": 6.0,
            "scalability": 8.0,
            "security": 7.0
        },

        "LoadRunner": {
            "functionality": 9.0,
            "maturity": 8.5,
            "integration": 8.0,
            "cost": 8.0,  # 高成本
            "support": 9.0,
            "scalability": 9.0,
            "security": 8.5
        },

        "Locust": {
            "functionality": 7.0,
            "maturity": 7.5,
            "integration": 6.5,
            "cost": 1.0,  # 极低成本
            "support": 5.0,
            "scalability": 8.5,
            "security": 6.0
        }
    }

    # 执行评估
    tool_scores = evaluator.evaluate_tools(tools_data)

    print("工具评估结果:")
    for score in tool_scores:
        print(f"{score.rank}. {score.tool_name}: {score.weighted_score:.4f}")

    # 生成评估报告
    report = evaluator.generate_evaluation_report(tool_scores, tools_data)
    print("\n评估报告:")
    print(report)

    # 敏感性分析
    if tool_scores:
        sensitivity = evaluator.sensitivity_analysis(tool_scores[0])
        print("敏感性分析结果:")
        print(json.dumps(sensitivity, indent=2, ensure_ascii=False))

    # 创建雷达图
    evaluator.create_radar_chart(tool_scores)
```

## 决策建议

### 选型策略

1. **匹配度优先**: 选择与项目需求匹配度最高的工具
2. **渐进式引入**: 从核心功能开始，逐步扩展工具链
3. **PoC验证**: 重要工具必须进行概念验证
4. **团队接受度**: 考虑团队的学习成本和接受程度

### 风险控制

1. **技术风险**: 评估工具的稳定性和发展前景
2. **成本风险**: 考虑长期维护和升级成本
3. **集成风险**: 验证工具间的兼容性和集成难度
4. **人员风险**: 评估团队技能匹配度和培训需求

### 实施建议

1. **分阶段实施**: 按优先级分阶段引入工具
2. **培训计划**: 制定详细的团队培训和知识转移计划
3. **文档建设**: 建立工具使用和维护的文档体系
4. **效果跟踪**: 建立工具使用效果的监控和评估机制

### 持续优化

1. **定期review**: 每6-12个月review工具链配置
2. **技术更新**: 关注工具的新版本和功能更新
3. **需求变化**: 根据项目发展调整工具选择
4. **最佳实践**: 总结经验，形成内部最佳实践