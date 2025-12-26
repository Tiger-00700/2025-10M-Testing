# AI测试成熟度评估模型

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns

class AIMaturityModel:
    """AI测试成熟度评估模型"""

    def __init__(self):
        self.maturity_levels = {
            1: {
                "name": "初始级",
                "description": "开始探索AI测试技术",
                "characteristics": [
                    "了解AI测试基本概念",
                    "有初步的AI工具使用经验",
                    "AI应用限于简单场景"
                ],
                "capabilities": ["basic_ai_tools", "manual_integration"],
                "score_range": (0, 20)
            },
            2: {
                "name": "发展级",
                "description": "建立AI测试基础能力",
                "characteristics": [
                    "有专门的AI测试团队",
                    "实现部分自动化AI流程",
                    "开始数据积累和模型训练"
                ],
                "capabilities": ["dedicated_team", "automated_workflows", "data_collection"],
                "score_range": (21, 40)
            },
            3: {
                "name": "成熟级",
                "description": "AI测试成为核心竞争力",
                "characteristics": [
                    "AI测试融入开发流程",
                    "建立完整的AI模型生态",
                    "实现显著的质量和效率提升"
                ],
                "capabilities": ["process_integration", "model_ecosystem", "quality_improvement"],
                "score_range": (41, 70)
            },
            4: {
                "name": "优化级",
                "description": "持续创新和优化",
                "characteristics": [
                    "领先的AI测试技术应用",
                    "自主的AI模型开发能力",
                    "成为行业AI测试标杆"
                ],
                "capabilities": ["innovation_leadership", "autonomous_development", "industry_benchmark"],
                "score_range": (71, 90)
            },
            5: {
                "name": "卓越级",
                "description": "AI测试技术领导者",
                "characteristics": [
                    "开创性的AI测试方法",
                    "全面的AI测试生态系统",
                    "引领行业技术发展方向"
                ],
                "capabilities": ["pioneering_methods", "comprehensive_ecosystem", "industry_leadership"],
                "score_range": (91, 100)
            }
        }

        self.assessment_criteria = {
            "strategy": {
                "weight": 0.15,
                "sub_criteria": {
                    "ai_vision": 0.4,
                    "roadmap": 0.3,
                    "resource_allocation": 0.3
                }
            },
            "technology": {
                "weight": 0.25,
                "sub_criteria": {
                    "ai_tools_adoption": 0.3,
                    "model_development": 0.3,
                    "infrastructure": 0.4
                }
            },
            "process": {
                "weight": 0.2,
                "sub_criteria": {
                    "integration_level": 0.4,
                    "automation_degree": 0.3,
                    "continuous_improvement": 0.3
                }
            },
            "people": {
                "weight": 0.15,
                "sub_criteria": {
                    "skill_level": 0.4,
                    "training_programs": 0.3,
                    "culture_adoption": 0.3
                }
            },
            "governance": {
                "weight": 0.15,
                "sub_criteria": {
                    "ethics_compliance": 0.3,
                    "risk_management": 0.3,
                    "performance_monitoring": 0.4
                }
            },
            "business_value": {
                "weight": 0.1,
                "sub_criteria": {
                    "roi_measurement": 0.5,
                    "quality_improvement": 0.3,
                    "time_to_market": 0.2
                }
            }
        }

    def assess_maturity(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估AI测试成熟度"""

        # 计算各维度得分
        dimension_scores = {}
        total_weighted_score = 0

        for dimension, config in self.assessment_criteria.items():
            dimension_score = self._calculate_dimension_score(dimension, assessment_data)
            dimension_scores[dimension] = {
                "score": dimension_score,
                "weight": config["weight"],
                "weighted_score": dimension_score * config["weight"]
            }
            total_weighted_score += dimension_score * config["weight"]

        # 确定成熟度等级
        maturity_level = self._determine_maturity_level(total_weighted_score)

        # 生成改进建议
        recommendations = self._generate_recommendations(dimension_scores, maturity_level)

        assessment_result = {
            "overall_score": round(total_weighted_score, 1),
            "maturity_level": maturity_level,
            "level_info": self.maturity_levels[maturity_level],
            "dimension_scores": dimension_scores,
            "strengths": [k for k, v in dimension_scores.items() if v["score"] >= 70],
            "weaknesses": [k for k, v in dimension_scores.items() if v["score"] < 50],
            "recommendations": recommendations,
            "next_level_requirements": self._get_next_level_requirements(maturity_level)
        }

        return assessment_result

    def _calculate_dimension_score(self, dimension: str, data: Dict[str, Any]) -> float:
        """计算维度得分"""
        config = self.assessment_criteria[dimension]
        total_score = 0

        for sub_criterion, weight in config["sub_criteria"].items():
            value = data.get(dimension, {}).get(sub_criterion, 0)
            # 假设输入是0-100的分数
            total_score += value * weight

        return round(total_score, 1)

    def _determine_maturity_level(self, score: float) -> int:
        """确定成熟度等级"""
        for level, info in self.maturity_levels.items():
            min_score, max_score = info["score_range"]
            if min_score <= score <= max_score:
                return level
        return 1  # 默认最低等级

    def _generate_recommendations(self, dimension_scores: Dict[str, Any], current_level: int) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 基于弱项的建议
        weak_dimensions = [k for k, v in dimension_scores.items() if v["score"] < 60]

        for dimension in weak_dimensions:
            if dimension == "strategy":
                recommendations.extend([
                    "制定明确的AI测试战略规划",
                    "建立AI测试路线图和里程碑",
                    "合理分配AI测试资源和预算"
                ])
            elif dimension == "technology":
                recommendations.extend([
                    "评估和采用合适的AI测试工具",
                    "建立AI模型开发和维护能力",
                    "升级基础设施支持AI计算需求"
                ])
            elif dimension == "process":
                recommendations.extend([
                    "将AI测试融入软件开发生命周期",
                    "提高AI测试流程自动化程度",
                    "建立持续改进机制"
                ])
            elif dimension == "people":
                recommendations.extend([
                    "提升团队AI测试技能水平",
                    "建立系统性的培训计划",
                    "培养AI测试文化"
                ])
            elif dimension == "governance":
                recommendations.extend([
                    "建立AI伦理和合规框架",
                    "完善风险管理机制",
                    "加强AI测试效果监控"
                ])

        # 基于当前等级的建议
        if current_level < 3:
            recommendations.append("重点关注AI测试的基础建设")
        elif current_level < 5:
            recommendations.append("推动AI测试的创新应用和生态建设")

        return list(set(recommendations))  # 去重

    def _get_next_level_requirements(self, current_level: int) -> List[str]:
        """获取下一等级的要求"""
        if current_level >= 5:
            return ["保持技术领先地位", "持续创新和突破"]

        next_level = current_level + 1
        next_info = self.maturity_levels[next_level]

        return next_info["characteristics"]

    def create_maturity_radar_chart(self, assessment_result: Dict[str, Any]):
        """创建成熟度雷达图"""
        dimension_scores = assessment_result["dimension_scores"]

        # 准备数据
        categories = list(dimension_scores.keys())
        values = [v["score"] for v in dimension_scores.values()]

        # 重复第一个值以闭合雷达图
        values += values[:1]
        categories += categories[:1]

        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=True)

        # 创建雷达图
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

        # 绘制数据
        ax.plot(angles, values, 'o-', linewidth=2, label='当前得分', color='blue')
        ax.fill(angles, values, alpha=0.25, color='blue')

        # 添加网格线
        ax.set_thetagrids(angles[:-1] * 180/np.pi, categories[:-1])
        ax.set_ylim(0, 100)
        ax.set_title(f'AI测试成熟度评估 - 等级 {assessment_result["maturity_level"]}', size=16, pad=20)

        # 添加参考线
        for level in [20, 40, 60, 80]:
            ax.plot(angles, [level] * len(angles), '--', color='gray', alpha=0.5)

        ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        ax.grid(True)

        plt.tight_layout()
        plt.show()

    def generate_maturity_report(self, assessment_result: Dict[str, Any]) -> str:
        """生成成熟度评估报告"""

        report = f"""
# AI测试成熟度评估报告

## 总体评估
- **综合得分**: {assessment_result["overall_score"]}/100
- **成熟度等级**: {assessment_result["maturity_level"]} - {assessment_result["level_info"]["name"]}
- **等级描述**: {assessment_result["level_info"]["description"]}

## 维度得分详情
"""

        for dimension, scores in assessment_result["dimension_scores"].items():
            report += f"""
### {dimension.title()}
- 原始得分: {scores["score"]}/100
- 权重: {scores["weight"]*100}%
- 加权得分: {scores["weighted_score"]:.1f}
"""

        report += f"""
## 优势领域
{chr(10).join(f"- {strength.title()}" for strength in assessment_result["strengths"])}

## 改进领域
{chr(10).join(f"- {weakness.title()}" for weakness in assessment_result["weaknesses"])}

## 改进建议
{chr(10).join(f"- {rec}" for rec in assessment_result["recommendations"])}

## 下一等级要求
{chr(10).join(f"- {req}" for req in assessment_result["next_level_requirements"])}
"""

        return report

# 使用示例
if __name__ == "__main__":
    model = AIMaturityModel()

    # 模拟评估数据
    assessment_data = {
        "strategy": {
            "ai_vision": 75,
            "roadmap": 70,
            "resource_allocation": 65
        },
        "technology": {
            "ai_tools_adoption": 80,
            "model_development": 60,
            "infrastructure": 70
        },
        "process": {
            "integration_level": 55,
            "automation_degree": 60,
            "continuous_improvement": 50
        },
        "people": {
            "skill_level": 45,
            "training_programs": 50,
            "culture_adoption": 40
        },
        "governance": {
            "ethics_compliance": 65,
            "risk_management": 60,
            "performance_monitoring": 55
        },
        "business_value": {
            "roi_measurement": 70,
            "quality_improvement": 75,
            "time_to_market": 60
        }
    }

    # 执行评估
    result = model.assess_maturity(assessment_data)

    print("AI测试成熟度评估结果:")
    print(json.dumps(result, indent=2, default=str))

    # 生成报告
    report = model.generate_maturity_report(result)
    print("\n成熟度评估报告:")
    print(report)

    # 创建雷达图
    model.create_maturity_radar_chart(result)