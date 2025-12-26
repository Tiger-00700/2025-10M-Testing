# 测试生态系统运营管理器

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json

@dataclass
class EcosystemParticipant:
    """生态参与者"""
    id: str
    name: str
    type: str  # developer, partner, contributor, user
    join_date: datetime
    status: str  # active, inactive, suspended
    contributions: List[Dict[str, Any]]
    engagement_metrics: Dict[str, float]

@dataclass
class EcosystemAsset:
    """生态资产"""
    id: str
    name: str
    type: str  # plugin, template, documentation, tool
    creator: str
    created_date: datetime
    downloads: int
    ratings: float
    revenue: float

class TestingEcosystemManager:
    """测试生态系统运营管理器"""

    def __init__(self):
        self.participants = {}
        self.assets = {}
        self.metrics = {}
        self.strategies = self._initialize_strategies()

    def _initialize_strategies(self) -> Dict[str, Dict[str, Any]]:
        """初始化运营策略"""
        return {
            "developer_engagement": {
                "name": "开发者参与策略",
                "objectives": ["增加开发者数量", "提升贡献质量", "建立社区文化"],
                "tactics": [
                    "提供完善的技术文档和示例",
                    "举办黑客马拉松和编程大赛",
                    "建立贡献者认可和奖励机制",
                    "创建开发者大使计划"
                ],
                "metrics": ["developer_growth", "contribution_quality", "community_satisfaction"]
            },

            "partner_ecosystem": {
                "name": "合作伙伴生态策略",
                "objectives": ["拓展市场覆盖", "增强产品能力", "创造互补价值"],
                "tactics": [
                    "建立合作伙伴认证体系",
                    "提供联合营销支持",
                    "开展技术合作项目",
                    "共享销售渠道和客户资源"
                ],
                "metrics": ["partner_recruitment", "joint_revenue", "market_expansion"]
            },

            "open_source_growth": {
                "name": "开源增长策略",
                "objectives": ["扩大社区规模", "提升代码质量", "增强品牌影响力"],
                "tactics": [
                    "维护高质量的开源代码库",
                    "举办社区会议和线上活动",
                    "提供技术支持和培训",
                    "建立贡献者入门指南"
                ],
                "metrics": ["community_size", "code_contributions", "brand_awareness"]
            },

            "marketplace_monetization": {
                "name": "市场货币化策略",
                "objectives": ["创造收入来源", "激励高质量贡献", "可持续运营"],
                "tactics": [
                    "实施插件收费模式",
                    "提供高级服务订阅",
                    "建立收益分享机制",
                    "开展企业级定制服务"
                ],
                "metrics": ["revenue_growth", "plugin_quality", "user_satisfaction"]
            },

            "education_certification": {
                "name": "教育认证策略",
                "objectives": ["培养专业人才", "提升行业标准", "建立信任机制"],
                "tactics": [
                    "开发系统化的培训课程",
                    "建立多级认证体系",
                    "提供继续教育服务",
                    "与高校建立合作关系"
                ],
                "metrics": ["certification_numbers", "skill_improvement", "industry_recognition"]
            }
        }

    def register_participant(self, participant_data: Dict[str, Any]) -> str:
        """注册生态参与者"""
        participant_id = f"participant_{len(self.participants) + 1}"

        participant = EcosystemParticipant(
            id=participant_id,
            name=participant_data["name"],
            type=participant_data["type"],
            join_date=datetime.now(),
            status="active",
            contributions=[],
            engagement_metrics={
                "activity_score": 0.0,
                "contribution_score": 0.0,
                "network_score": 0.0
            }
        )

        self.participants[participant_id] = participant
        return participant_id

    def publish_asset(self, asset_data: Dict[str, Any]) -> str:
        """发布生态资产"""
        asset_id = f"asset_{len(self.assets) + 1}"

        asset = EcosystemAsset(
            id=asset_id,
            name=asset_data["name"],
            type=asset_data["type"],
            creator=asset_data["creator"],
            created_date=datetime.now(),
            downloads=0,
            ratings=0.0,
            revenue=0.0
        )

        self.assets[asset_id] = asset
        return asset_id

    def calculate_engagement_metrics(self, participant_id: str) -> Dict[str, float]:
        """计算参与者参与度指标"""
        if participant_id not in self.participants:
            return {}

        participant = self.participants[participant_id]

        # 计算活动得分（基于贡献频率和质量）
        recent_contributions = [
            c for c in participant.contributions
            if (datetime.now() - c["date"]).days <= 90
        ]

        activity_score = min(len(recent_contributions) * 10, 100)

        # 计算贡献得分（基于贡献影响力和认可度）
        contribution_score = sum(c.get("impact_score", 0) for c in participant.contributions)
        contribution_score = min(contribution_score, 100)

        # 计算网络得分（基于与其他参与者的互动）
        network_score = len(set(c.get("collaborators", []) for c in participant.contributions))
        network_score = min(network_score * 5, 100)

        metrics = {
            "activity_score": activity_score,
            "contribution_score": contribution_score,
            "network_score": network_score,
            "overall_engagement": (activity_score + contribution_score + network_score) / 3
        }

        participant.engagement_metrics = metrics
        return metrics

    def generate_ecosystem_report(self) -> Dict[str, Any]:
        """生成生态系统报告"""
        total_participants = len(self.participants)
        active_participants = len([p for p in self.participants.values() if p.status == "active"])

        total_assets = len(self.assets)
        total_downloads = sum(a.downloads for a in self.assets.values())
        total_revenue = sum(a.revenue for a in self.assets.values())

        # 参与者类型分布
        type_distribution = {}
        for participant in self.participants.values():
            type_distribution[participant.type] = type_distribution.get(participant.type, 0) + 1

        # 资产类型分布
        asset_distribution = {}
        for asset in self.assets.values():
            asset_distribution[asset.type] = asset_distribution.get(asset.type, 0) + 1

        # 参与度分析
        engagement_levels = {
            "high": len([p for p in self.participants.values() if p.engagement_metrics.get("overall_engagement", 0) >= 70]),
            "medium": len([p for p in self.participants.values() if 40 <= p.engagement_metrics.get("overall_engagement", 0) < 70]),
            "low": len([p for p in self.participants.values() if p.engagement_metrics.get("overall_engagement", 0) < 40])
        }

        # 增长趋势（模拟）
        growth_trends = {
            "participants": [total_participants * (0.8 + i * 0.1) for i in range(12)],
            "assets": [total_assets * (0.7 + i * 0.15) for i in range(12)],
            "downloads": [total_downloads * (0.6 + i * 0.2) for i in range(12)]
        }

        return {
            "overview": {
                "total_participants": total_participants,
                "active_participants": active_participants,
                "total_assets": total_assets,
                "total_downloads": total_downloads,
                "total_revenue": total_revenue,
                "activity_rate": active_participants / total_participants if total_participants > 0 else 0
            },
            "distributions": {
                "participant_types": type_distribution,
                "asset_types": asset_distribution,
                "engagement_levels": engagement_levels
            },
            "trends": growth_trends,
            "top_contributors": self._get_top_contributors(10),
            "top_assets": self._get_top_assets(10),
            "health_score": self._calculate_ecosystem_health()
        }

    def _get_top_contributors(self, limit: int) -> List[Dict[str, Any]]:
        """获取顶级贡献者"""
        contributors = []
        for participant in self.participants.values():
            engagement = participant.engagement_metrics.get("overall_engagement", 0)
            contributors.append({
                "id": participant.id,
                "name": participant.name,
                "type": participant.type,
                "engagement_score": engagement,
                "contributions_count": len(participant.contributions)
            })

        contributors.sort(key=lambda x: x["engagement_score"], reverse=True)
        return contributors[:limit]

    def _get_top_assets(self, limit: int) -> List[Dict[str, Any]]:
        """获取热门资产"""
        asset_list = []
        for asset in self.assets.values():
            asset_list.append({
                "id": asset.id,
                "name": asset.name,
                "type": asset.type,
                "downloads": asset.downloads,
                "ratings": asset.ratings,
                "revenue": asset.revenue
            })

        asset_list.sort(key=lambda x: x["downloads"], reverse=True)
        return asset_list[:limit]

    def _calculate_ecosystem_health(self) -> float:
        """计算生态系统健康度"""
        if not self.participants:
            return 0.0

        # 基于多个维度的健康度计算
        activity_rate = len([p for p in self.participants.values() if p.status == "active"]) / len(self.participants)

        avg_engagement = sum(p.engagement_metrics.get("overall_engagement", 0) for p in self.participants.values()) / len(self.participants)

        asset_utilization = sum(a.downloads for a in self.assets.values()) / max(len(self.assets), 1)

        # 归一化计算
        health_score = (activity_rate * 0.3 + avg_engagement / 100 * 0.4 + min(asset_utilization / 100, 1) * 0.3) * 100

        return round(health_score, 1)

    def optimize_ecosystem_strategy(self) -> Dict[str, Any]:
        """优化生态策略"""
        current_metrics = self.generate_ecosystem_report()

        recommendations = []

        # 基于健康度提出建议
        health_score = current_metrics["health_score"]
        if health_score < 50:
            recommendations.extend([
                "加强社区运营，提高参与者活跃度",
                "改善用户体验，降低参与门槛",
                "增加优质内容和资源投入"
            ])
        elif health_score < 70:
            recommendations.extend([
                "深化参与者互动，建立合作机制",
                "完善激励体系，鼓励高质量贡献",
                "拓展生态覆盖范围，吸引更多参与者"
            ])
        else:
            recommendations.extend([
                "维持当前良好势头",
                "探索新的增长点和创新模式",
                "建立可持续的生态运营机制"
            ])

        # 基于分布情况提出建议
        type_distribution = current_metrics["distributions"]["participant_types"]
        if type_distribution.get("developer", 0) < type_distribution.get("user", 0) * 0.5:
            recommendations.append("增加开发者招募和培养活动")

        if type_distribution.get("partner", 0) < 10:
            recommendations.append("加强合作伙伴体系建设")

        return {
            "current_health": health_score,
            "strategy_effectiveness": self._assess_strategy_effectiveness(),
            "recommendations": recommendations,
            "action_plan": self._generate_action_plan(recommendations)
        }

    def _assess_strategy_effectiveness(self) -> Dict[str, float]:
        """评估策略有效性"""
        # 简化的策略评估逻辑
        return {
            "developer_engagement": 75.0,
            "partner_ecosystem": 68.0,
            "open_source_growth": 82.0,
            "marketplace_monetization": 65.0,
            "education_certification": 71.0
        }

    def _generate_action_plan(self, recommendations: List[str]) -> List[Dict[str, Any]]:
        """生成行动计划"""
        action_plan = []

        for rec in recommendations:
            action = {
                "recommendation": rec,
                "priority": "high" if "加强" in rec or "增加" in rec else "medium",
                "timeline": "1-3个月",
                "owner": "生态运营团队",
                "resources_needed": ["人力", "预算", "技术支持"],
                "success_metrics": ["参与度提升", "数量增长", "质量改善"]
            }
            action_plan.append(action)

        return action_plan

# 使用示例
if __name__ == "__main__":
    manager = TestingEcosystemManager()

    # 注册参与者
    dev1 = manager.register_participant({
        "name": "张三",
        "type": "developer"
    })

    partner1 = manager.register_participant({
        "name": "ABC公司",
        "type": "partner"
    })

    # 发布资产
    plugin1 = manager.publish_asset({
        "name": "数据质量检查插件",
        "type": "plugin",
        "creator": dev1
    })

    # 计算参与度
    engagement = manager.calculate_engagement_metrics(dev1)
    print(f"开发者参与度: {engagement}")

    # 生成生态报告
    report = manager.generate_ecosystem_report()
    print("生态系统报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # 优化策略
    optimization = manager.optimize_ecosystem_strategy()
    print("策略优化建议:")
    print(json.dumps(optimization, indent=2, ensure_ascii=False))