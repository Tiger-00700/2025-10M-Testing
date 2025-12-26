#!/usr/bin/env python3
"""
大数据测试项目管理框架
Big Data Testing Project Management Framework

提供完整的项目管理生命周期管理，包括规划、执行、监控和收尾。
"""

import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ProjectStatus(Enum):
    """项目状态枚举"""
    PLANNING = "planning"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SustainabilityMetric(Enum):
    """可持续性指标枚举"""
    ENERGY_CONSUMPTION = "energy_consumption"
    CARBON_FOOTPRINT = "carbon_footprint"
    RESOURCE_UTILIZATION = "resource_utilization"
    GREEN_TESTING_RATIO = "green_testing_ratio"


@dataclass
class TeamMember:
    """团队成员"""
    name: str
    role: str
    skills: List[str]
    availability: float = 1.0  # 可用性百分比


@dataclass
class ProjectTask:
    """项目任务"""
    id: str
    name: str
    description: str
    assignee: str
    estimated_hours: float
    actual_hours: float = 0.0
    status: str = "todo"
    dependencies: List[str] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class ProjectMilestone:
    """项目里程碑"""
    id: str
    name: str
    description: str
    target_date: datetime
    completed_date: Optional[datetime] = None
    deliverables: List[str] = field(default_factory=list)


@dataclass
class ProjectRisk:
    """项目风险"""
    id: str
    description: str
    probability: float  # 0-1
    impact: float  # 0-1
    level: RiskLevel
    mitigation_plan: str
    owner: str
    status: str = "open"


@dataclass
class QualityMetric:
    """质量指标"""
    name: str
    target_value: float
    current_value: float = 0.0
    unit: str = "%"
    trend: str = "stable"  # improving, stable, declining


class ProjectManagementFramework:
    """项目管理框架"""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.status = ProjectStatus.PLANNING
        self.start_date = datetime.now()
        self.end_date: Optional[datetime] = None

        # 团队管理
        self.team_members: List[TeamMember] = []
        self.team_roles = {
            "项目经理": 1,
            "测试架构师": 1,
            "高级测试工程师": 3,
            "测试工程师": 8,
            "DevOps工程师": 2
        }

        # 任务管理
        self.tasks: List[ProjectTask] = []
        self.task_counter = 0

        # 里程碑管理
        self.milestones: List[ProjectMilestone] = []

        # 风险管理
        self.risks: List[ProjectRisk] = []

        # 质量管理
        self.quality_metrics: List[QualityMetric] = [
            QualityMetric("测试覆盖率", 85.0, unit="%"),
            QualityMetric("缺陷逃逸率", 5.0, unit="%"),
            QualityMetric("自动化率", 70.0, unit="%"),
            QualityMetric("上线成功率", 95.0, unit="%")
        ]

        # 可持续性管理
        self.sustainability_metrics: Dict[str, float] = {
            "energy_consumption": 0.0,  # kWh
            "carbon_footprint": 0.0,    # kg CO2
            "resource_utilization": 0.0,  # %
            "green_testing_ratio": 0.0   # %
        }

        # 项目配置
        self.config = {
            "methodology": "Scrum",
            "sprint_duration": 14,  # 天
            "communication_tools": ["Jira", "Confluence", "Slack", "GitLab"],
            "quality_gates": ["代码审查", "测试覆盖", "性能基准", "安全扫描"]
        }

    def add_team_member(self, member: TeamMember):
        """添加团队成员"""
        self.team_members.append(member)

    def create_task(self, name: str, description: str, assignee: str,
                   estimated_hours: float, dependencies: List[str] = None) -> str:
        """创建任务"""
        self.task_counter += 1
        task_id = f"TASK-{self.task_counter:03d}"

        task = ProjectTask(
            id=task_id,
            name=name,
            description=description,
            assignee=assignee,
            estimated_hours=estimated_hours,
            dependencies=dependencies or []
        )

        self.tasks.append(task)
        return task_id

    def add_milestone(self, name: str, description: str, target_date: datetime,
                     deliverables: List[str] = None):
        """添加里程碑"""
        milestone_id = f"MILE-{len(self.milestones) + 1:02d}"

        milestone = ProjectMilestone(
            id=milestone_id,
            name=name,
            description=description,
            target_date=target_date,
            deliverables=deliverables or []
        )

        self.milestones.append(milestone)
        return milestone_id

    def add_risk(self, description: str, probability: float, impact: float,
                mitigation_plan: str, owner: str):
        """添加风险"""
        risk_id = f"RISK-{len(self.risks) + 1:03d}"

        # 计算风险等级
        risk_score = probability * impact
        if risk_score >= 0.7:
            level = RiskLevel.CRITICAL
        elif risk_score >= 0.4:
            level = RiskLevel.HIGH
        elif risk_score >= 0.2:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        risk = ProjectRisk(
            id=risk_id,
            description=description,
            probability=probability,
            impact=impact,
            level=level,
            mitigation_plan=mitigation_plan,
            owner=owner
        )

        self.risks.append(risk)
        return risk_id

    def update_task_status(self, task_id: str, status: str, actual_hours: float = None):
        """更新任务状态"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = status
                if actual_hours is not None:
                    task.actual_hours = actual_hours
                break

    def update_quality_metric(self, name: str, current_value: float):
        """更新质量指标"""
        for metric in self.quality_metrics:
            if metric.name == name:
                old_value = metric.current_value
                metric.current_value = current_value

                # 判断趋势
                if current_value > old_value:
                    metric.trend = "improving"
                elif current_value < old_value:
                    metric.trend = "declining"
                else:
                    metric.trend = "stable"
                break

    def get_project_status_report(self) -> Dict[str, Any]:
        """生成项目状态报告"""
        completed_tasks = len([t for t in self.tasks if t.status == "completed"])
        total_tasks = len(self.tasks)

        completed_milestones = len([m for m in self.milestones if m.completed_date])
        total_milestones = len(self.milestones)

        open_risks = len([r for r in self.risks if r.status == "open"])

        # 计算质量指标达成率
        quality_score = sum(
            min(100, (metric.current_value / metric.target_value) * 100)
            for metric in self.quality_metrics
        ) / len(self.quality_metrics)

        return {
            "project_name": self.project_name,
            "status": self.status.value,
            "progress": {
                "tasks": f"{completed_tasks}/{total_tasks}",
                "milestones": f"{completed_milestones}/{total_milestones}",
                "task_completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0
            },
            "risks": {
                "open_count": open_risks,
                "critical_count": len([r for r in self.risks if r.level == RiskLevel.CRITICAL])
            },
            "quality": {
                "overall_score": quality_score,
                "metrics": [
                    {
                        "name": m.name,
                        "target": m.target_value,
                        "current": m.current_value,
                        "trend": m.trend
                    } for m in self.quality_metrics
                ]
            },
            "team": {
                "total_members": len(self.team_members),
                "roles_filled": len(set(m.role for m in self.team_members))
            },
            "sustainability": {
                "energy_consumption": f"{self.sustainability_metrics['energy_consumption']:.1f} kWh",
                "carbon_footprint": f"{self.sustainability_metrics['carbon_footprint']:.1f} kg CO2",
                "resource_utilization": f"{self.sustainability_metrics['resource_utilization']:.1f}%",
                "green_testing_ratio": f"{self.sustainability_metrics['green_testing_ratio']:.1f}%",
                "sustainability_score": self._calculate_sustainability_score()
            }
        }

    def _calculate_sustainability_score(self) -> float:
        """计算可持续性评分"""
        # 基于绿色测试比例和资源利用率计算综合评分
        green_ratio = self.sustainability_metrics['green_testing_ratio']
        resource_util = self.sustainability_metrics['resource_utilization']

        # 理想情况下，绿色测试比例越高、资源利用率越合理，分数越高
        if green_ratio >= 80 and 60 <= resource_util <= 85:
            return 95.0
        elif green_ratio >= 60 and 50 <= resource_util <= 90:
            return 85.0
        elif green_ratio >= 40 and 40 <= resource_util <= 95:
            return 75.0
        else:
            return 60.0

    def update_sustainability_metric(self, metric: str, value: float):
        """更新可持续性指标"""
        if metric in self.sustainability_metrics:
            self.sustainability_metrics[metric] = value

    def export_project_plan(self, format: str = "yaml") -> str:
        """导出项目计划"""
        plan = {
            "project": {
                "name": self.project_name,
                "status": self.status.value,
                "start_date": self.start_date.isoformat(),
                "config": self.config
            },
            "team": {
                "members": [
                    {
                        "name": m.name,
                        "role": m.role,
                        "skills": m.skills,
                        "availability": m.availability
                    } for m in self.team_members
                ],
                "roles_required": self.team_roles
            },
            "tasks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "assignee": t.assignee,
                    "estimated_hours": t.estimated_hours,
                    "status": t.status,
                    "dependencies": t.dependencies
                } for t in self.tasks
            ],
            "milestones": [
                {
                    "id": m.id,
                    "name": m.name,
                    "target_date": m.target_date.isoformat(),
                    "deliverables": m.deliverables
                } for m in self.milestones
            ],
            "risks": [
                {
                    "id": r.id,
                    "description": r.description,
                    "level": r.level.value,
                    "mitigation_plan": r.mitigation_plan,
                    "owner": r.owner
                } for r in self.risks
            ],
            "quality_metrics": [
                {
                    "name": m.name,
                    "target": m.target_value,
                    "unit": m.unit
                } for m in self.quality_metrics
            ]
        }

        if format == "yaml":
            return yaml.dump(plan, default_flow_style=False, allow_unicode=True)
        elif format == "json":
            return json.dumps(plan, indent=2, ensure_ascii=False, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")


def create_sample_project():
    """创建示例项目"""
    pm = ProjectManagementFramework("电商大数据测试项目")

    # 添加团队成员
    pm.add_team_member(TeamMember("张三", "项目经理", ["项目管理", "风险控制"]))
    pm.add_team_member(TeamMember("李四", "测试架构师", ["测试架构", "技术方案"]))
    pm.add_team_member(TeamMember("王五", "高级测试工程师", ["自动化测试", "性能测试"]))

    # 创建任务
    pm.create_task("需求分析", "分析项目需求和范围", "张三", 40)
    pm.create_task("测试环境搭建", "搭建测试环境", "李四", 80)
    pm.create_task("测试用例设计", "设计测试用例", "王五", 120)

    # 添加里程碑
    pm.add_milestone("需求确认", "完成需求分析和确认", datetime.now() + timedelta(days=30))
    pm.add_milestone("环境就绪", "测试环境搭建完成", datetime.now() + timedelta(days=60))

    # 添加风险
    pm.add_risk("技术难度超出预期", 0.3, 0.8, "技术预研和原型验证", "李四")
    pm.add_risk("团队成员离职", 0.2, 0.6, "备份人员和知识转移", "张三")

    # 设置可持续性指标
    pm.update_sustainability_metric("energy_consumption", 1250.5)  # kWh
    pm.update_sustainability_metric("carbon_footprint", 450.2)     # kg CO2
    pm.update_sustainability_metric("resource_utilization", 78.5)  # %
    pm.update_sustainability_metric("green_testing_ratio", 65.0)   # %

    return pm


def main():
    """主函数"""
    # 创建示例项目
    project = create_sample_project()

    # 更新一些状态
    project.update_task_status("TASK-001", "completed", 45)
    project.update_quality_metric("测试覆盖率", 78.5)

    # 生成报告
    report = project.get_project_status_report()
    print("项目状态报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # 导出项目计划
    plan_yaml = project.export_project_plan("yaml")
    print("\n项目计划 (YAML):")
    print(plan_yaml)


if __name__ == "__main__":
    main()