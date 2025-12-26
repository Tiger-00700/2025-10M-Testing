#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险管理系统 - Risk Management System
大数据测试项目的风险识别、评估和应急响应框架

作者: 2025测试团队
版本: 1.0
更新日期: 2025-01-23
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskCategory(Enum):
    """风险类别枚举"""
    TECHNICAL = "技术风险"
    RESOURCE = "资源风险"
    SCHEDULE = "进度风险"
    QUALITY = "质量风险"
    BUSINESS = "业务风险"
    COMPLIANCE = "合规风险"
    SECURITY = "安全风险"


class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    CRITICAL = "严重"


class RiskStatus(Enum):
    """风险状态枚举"""
    IDENTIFIED = "已识别"
    ASSESSING = "评估中"
    MITIGATED = "已缓解"
    MONITORING = "监控中"
    TRIGGERED = "已触发"
    CLOSED = "已关闭"


@dataclass
class Risk:
    """风险类"""
    id: str
    title: str
    description: str
    category: RiskCategory
    probability: float  # 0-1 之间
    impact: float  # 0-1 之间
    level: RiskLevel = field(init=False)
    status: RiskStatus = RiskStatus.IDENTIFIED
    owner: str = ""
    identified_by: str = ""
    identified_date: datetime = field(default_factory=datetime.now)
    mitigation_plan: str = ""
    contingency_plan: str = ""
    trigger_conditions: List[str] = field(default_factory=list)
    monitoring_frequency: str = "weekly"
    last_reviewed: datetime = field(default_factory=datetime.now)
    resolution_date: Optional[datetime] = None
    actual_impact: str = ""
    lessons_learned: str = ""

    def __post_init__(self):
        """自动计算风险等级"""
        risk_score = self.probability * self.impact
        if risk_score >= 0.7:
            self.level = RiskLevel.CRITICAL
        elif risk_score >= 0.4:
            self.level = RiskLevel.HIGH
        elif risk_score >= 0.15:
            self.level = RiskLevel.MEDIUM
        else:
            self.level = RiskLevel.LOW

    def update_status(self, new_status: RiskStatus, notes: str = ""):
        """更新风险状态"""
        old_status = self.status
        self.status = new_status
        self.last_reviewed = datetime.now()

        if new_status == RiskStatus.CLOSED:
            self.resolution_date = datetime.now()

        logger.info(f"风险状态更新: {self.title} 从 {old_status.value} 到 {new_status.value}")
        if notes:
            logger.info(f"更新说明: {notes}")

    def trigger_risk(self, actual_impact: str):
        """触发风险"""
        self.status = RiskStatus.TRIGGERED
        self.actual_impact = actual_impact
        self.last_reviewed = datetime.now()
        logger.warning(f"风险已触发: {self.title} - {actual_impact}")

    def add_trigger_condition(self, condition: str):
        """添加触发条件"""
        self.trigger_conditions.append(condition)

    def get_risk_score(self) -> float:
        """获取风险评分"""
        return self.probability * self.impact

    def get_summary(self) -> Dict[str, Any]:
        """获取风险摘要"""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category.value,
            "level": self.level.value,
            "status": self.status.value,
            "probability": self.probability,
            "impact": self.impact,
            "risk_score": self.get_risk_score(),
            "owner": self.owner,
            "last_reviewed": self.last_reviewed.isoformat()
        }


@dataclass
class RiskRegister:
    """风险登记册类"""
    project_name: str
    risks: Dict[str, Risk] = field(default_factory=dict)
    risk_matrix: Dict[str, List[Risk]] = field(default_factory=dict)
    mitigation_actions: List[Dict] = field(default_factory=list)
    review_schedule: str = "weekly"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """初始化风险矩阵"""
        for category in RiskCategory:
            self.risk_matrix[category.value] = []

    def add_risk(self, risk: Risk):
        """添加风险"""
        self.risks[risk.id] = risk
        self.risk_matrix[risk.category.value].append(risk)
        self.updated_at = datetime.now()
        logger.info(f"添加风险: {risk.title} ({risk.level.value})")

    def update_risk(self, risk_id: str, **updates):
        """更新风险"""
        if risk_id in self.risks:
            risk = self.risks[risk_id]
            for key, value in updates.items():
                if hasattr(risk, key):
                    setattr(risk, key, value)
            risk.last_reviewed = datetime.now()
            self.updated_at = datetime.now()
            logger.info(f"更新风险: {risk_id}")

    def get_risks_by_level(self, level: RiskLevel) -> List[Risk]:
        """按等级获取风险"""
        return [risk for risk in self.risks.values() if risk.level == level]

    def get_risks_by_category(self, category: RiskCategory) -> List[Risk]:
        """按类别获取风险"""
        return self.risk_matrix.get(category.value, [])

    def get_risks_by_status(self, status: RiskStatus) -> List[Risk]:
        """按状态获取风险"""
        return [risk for risk in self.risks.values() if risk.status == status]

    def get_top_risks(self, limit: int = 10) -> List[Risk]:
        """获取最高风险"""
        sorted_risks = sorted(self.risks.values(),
                            key=lambda r: r.get_risk_score(),
                            reverse=True)
        return sorted_risks[:limit]

    def generate_risk_report(self) -> str:
        """生成风险报告"""
        total_risks = len(self.risks)
        open_risks = len([r for r in self.risks.values() if r.status != RiskStatus.CLOSED])
        critical_risks = len(self.get_risks_by_level(RiskLevel.CRITICAL))
        triggered_risks = len(self.get_risks_by_status(RiskStatus.TRIGGERED))

        report = f"""
# 风险管理报告 - {self.project_name}
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 风险概况
- 总风险数: {total_risks}
- 未关闭风险: {open_risks}
- 严重风险: {critical_risks}
- 已触发风险: {triggered_risks}

## 风险分布
{self._format_risk_distribution()}

## 最高风险清单
{self._format_top_risks()}

## 近期活动
{self._format_recent_activities()}

## 风险趋势
{self._format_risk_trends()}
        """
        return report

    def _format_risk_distribution(self) -> str:
        """格式化风险分布"""
        lines = []

        # 按等级分布
        for level in RiskLevel:
            count = len(self.get_risks_by_level(level))
            if count > 0:
                lines.append(f"- {level.value}风险: {count} 个")

        # 按类别分布
        lines.append("\n按类别分布:")
        for category in RiskCategory:
            risks = self.get_risks_by_category(category)
            if risks:
                lines.append(f"- {category.value}: {len(risks)} 个")

        return "\n".join(lines) if lines else "- 无风险数据"

    def _format_top_risks(self) -> str:
        """格式化最高风险"""
        top_risks = self.get_top_risks(5)
        if not top_risks:
            return "- 无风险数据"

        lines = []
        for i, risk in enumerate(top_risks, 1):
            lines.append(f"{i}. {risk.title} (等级: {risk.level.value}, 评分: {risk.get_risk_score():.2f})")
            lines.append(f"   状态: {risk.status.value}, 负责人: {risk.owner}")

        return "\n".join(lines)

    def _format_recent_activities(self) -> str:
        """格式化近期活动"""
        recent_activities = []
        cutoff_date = datetime.now() - timedelta(days=7)

        for risk in self.risks.values():
            if risk.last_reviewed >= cutoff_date:
                recent_activities.append(f"- {risk.last_reviewed.strftime('%m-%d')}: {risk.title} 状态更新为 {risk.status.value}")

        if not recent_activities:
            return "- 无近期活动"

        return "\n".join(recent_activities[:10])  # 最多显示10条

    def _format_risk_trends(self) -> str:
        """格式化风险趋势"""
        # 计算趋势（简化版）
        total_risks = len(self.risks)
        if total_risks == 0:
            return "- 无风险数据"

        mitigated_count = len([r for r in self.risks.values() if r.status == RiskStatus.MITIGATED])
        mitigation_rate = mitigated_count / total_risks

        if mitigation_rate >= 0.8:
            trend = "风险控制良好"
        elif mitigation_rate >= 0.6:
            trend = "风险控制一般"
        else:
            trend = "需要加强风险控制"

        return f"- 风险缓解率: {mitigation_rate:.1%} ({trend})"

    def conduct_risk_assessment(self):
        """进行风险评估"""
        logger.info("开始风险评估...")

        for risk in self.risks.values():
            if risk.status == RiskStatus.IDENTIFIED:
                # 重新评估风险等级
                old_level = risk.level
                risk.__post_init__()  # 重新计算等级

                if risk.level != old_level:
                    logger.info(f"风险等级变更: {risk.title} 从 {old_level.value} 到 {risk.level.value}")

                # 检查触发条件
                self._check_trigger_conditions(risk)

        self.updated_at = datetime.now()
        logger.info("风险评估完成")

    def _check_trigger_conditions(self, risk: Risk):
        """检查风险触发条件"""
        # 这里可以实现更复杂的触发条件检查逻辑
        # 简化版：如果风险评分很高且没有缓解计划，则标记为需要关注
        if risk.get_risk_score() > 0.5 and not risk.mitigation_plan:
            logger.warning(f"高风险未缓解: {risk.title}")

    def create_mitigation_action(self, risk_id: str, action: str, owner: str, due_date: datetime):
        """创建缓解行动"""
        mitigation = {
            "id": f"MA_{len(self.mitigation_actions) + 1:03d}",
            "risk_id": risk_id,
            "action": action,
            "owner": owner,
            "due_date": due_date.isoformat(),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

        self.mitigation_actions.append(mitigation)
        logger.info(f"创建缓解行动: {action} (风险: {risk_id})")

    def export_configuration(self) -> Dict[str, Any]:
        """导出配置"""
        return {
            "project_name": self.project_name,
            "risks": [vars(risk) for risk in self.risks.values()],
            "mitigation_actions": self.mitigation_actions,
            "review_schedule": self.review_schedule,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


def create_sample_risk_register() -> RiskRegister:
    """创建示例风险登记册"""
    register = RiskRegister("电商大数据测试项目")

    # 定义示例风险
    risks_data = [
        {
            "id": "RISK_001",
            "title": "关键测试人员离职",
            "description": "项目关键测试人员突然离职，导致测试进度延误",
            "category": RiskCategory.RESOURCE,
            "probability": 0.3,
            "impact": 0.8,
            "owner": "项目经理",
            "identified_by": "HR部门",
            "mitigation_plan": "建立人员备份计划，开展知识转移培训",
            "contingency_plan": "启动应急招聘，调整项目计划"
        },
        {
            "id": "RISK_002",
            "title": "测试环境不稳定",
            "description": "测试环境频繁宕机，影响测试执行效率",
            "category": RiskCategory.TECHNICAL,
            "probability": 0.6,
            "impact": 0.6,
            "owner": "DevOps工程师",
            "identified_by": "测试团队",
            "mitigation_plan": "加强环境监控，实施自动化部署",
            "contingency_plan": "准备备用测试环境"
        },
        {
            "id": "RISK_003",
            "title": "需求变更频繁",
            "description": "业务需求频繁变更，导致测试范围扩大",
            "category": RiskCategory.BUSINESS,
            "probability": 0.7,
            "impact": 0.5,
            "owner": "业务分析师",
            "identified_by": "产品经理",
            "mitigation_plan": "实施变更控制流程，加强需求评审",
            "contingency_plan": "预留20%缓冲时间"
        },
        {
            "id": "RISK_004",
            "title": "第三方接口不稳定",
            "description": "依赖的第三方服务接口响应不稳定",
            "category": RiskCategory.TECHNICAL,
            "probability": 0.4,
            "impact": 0.7,
            "owner": "测试架构师",
            "identified_by": "开发团队",
            "mitigation_plan": "实施接口监控，开发Mock服务",
            "contingency_plan": "准备降级方案"
        },
        {
            "id": "RISK_005",
            "title": "数据隐私合规风险",
            "description": "测试数据可能涉及用户隐私，合规风险",
            "category": RiskCategory.COMPLIANCE,
            "probability": 0.2,
            "impact": 0.9,
            "owner": "合规官",
            "identified_by": "法律顾问",
            "mitigation_plan": "实施数据脱敏，签订保密协议",
            "contingency_plan": "停止相关测试，寻求法律意见"
        }
    ]

    for risk_data in risks_data:
        risk = Risk(**risk_data)
        register.add_risk(risk)

    # 创建缓解行动
    register.create_mitigation_action(
        "RISK_001",
        "为关键人员安排导师，开展知识文档整理",
        "项目经理",
        datetime.now() + timedelta(days=30)
    )

    register.create_mitigation_action(
        "RISK_002",
        "部署环境监控工具，设置自动告警",
        "DevOps工程师",
        datetime.now() + timedelta(days=14)
    )

    return register


if __name__ == "__main__":
    # 创建示例风险管理系统
    risk_register = create_sample_risk_register()

    # 进行风险评估
    risk_register.conduct_risk_assessment()

    # 生成风险报告
    report = risk_register.generate_risk_report()
    print(report)

    # 获取最高风险
    top_risks = risk_register.get_top_risks(3)
    print(f"\n最高风险:")
    for risk in top_risks:
        print(f"- {risk.title} (评分: {risk.get_risk_score():.2f})")

    # 导出配置
    config = risk_register.export_configuration()
    with open("risk_management_system_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("\n风险管理系统配置已导出到 risk_management_system_config.json")