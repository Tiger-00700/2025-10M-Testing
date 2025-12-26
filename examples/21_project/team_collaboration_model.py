#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
团队协作模型 - Team Collaboration Model
大数据测试项目团队协作与沟通管理框架

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


class CommunicationType(Enum):
    """沟通类型枚举"""
    SYNC = "同步沟通"
    ASYNC = "异步沟通"
    FORMAL = "正式沟通"
    INFORMAL = "非正式沟通"


class TeamRole(Enum):
    """团队角色枚举"""
    PROJECT_MANAGER = "项目经理"
    SCRUM_MASTER = "Scrum Master"
    TEST_ARCHITECT = "测试架构师"
    SENIOR_TEST_ENGINEER = "高级测试工程师"
    TEST_ENGINEER = "测试工程师"
    DEVOPS_ENGINEER = "DevOps工程师"
    BUSINESS_ANALYST = "业务分析师"
    DEVELOPER = "开发工程师"


@dataclass
class TeamMember:
    """团队成员类"""
    id: str
    name: str
    role: TeamRole
    skills: List[str] = field(default_factory=list)
    availability: float = 1.0  # 可用性百分比
    communication_style: str = "协作型"
    timezone: str = "UTC+8"

    def is_available(self, hours: int = 8) -> bool:
        """检查成员是否可用"""
        return self.availability >= (hours / 8.0)


@dataclass
class CommunicationChannel:
    """沟通渠道类"""
    name: str
    type: CommunicationType
    purpose: str
    participants: List[str] = field(default_factory=list)
    frequency: str = "daily"
    tools: List[str] = field(default_factory=list)

    def add_participant(self, member_id: str):
        """添加参与者"""
        if member_id not in self.participants:
            self.participants.append(member_id)

    def remove_participant(self, member_id: str):
        """移除参与者"""
        if member_id in self.participants:
            self.participants.remove(member_id)


@dataclass
class Meeting:
    """会议类"""
    id: str
    title: str
    type: str
    facilitator: str
    participants: List[str] = field(default_factory=list)
    scheduled_time: datetime = field(default_factory=datetime.now)
    duration_minutes: int = 60
    agenda: List[str] = field(default_factory=list)
    action_items: List[Dict] = field(default_factory=list)
    status: str = "scheduled"

    def add_agenda_item(self, item: str):
        """添加议程项"""
        self.agenda.append(item)

    def add_action_item(self, description: str, assignee: str, due_date: datetime):
        """添加行动项"""
        self.action_items.append({
            "description": description,
            "assignee": assignee,
            "due_date": due_date.isoformat(),
            "status": "pending"
        })


class WorkflowStage(Enum):
    """工作流阶段枚举"""
    PLANNING = "规划阶段"
    DEVELOPMENT = "开发阶段"
    TESTING = "测试阶段"
    DEPLOYMENT = "部署阶段"
    MAINTENANCE = "维护阶段"


@dataclass
class WorkflowTask:
    """工作流任务类"""
    id: str
    title: str
    description: str
    stage: WorkflowStage
    assignee: str
    priority: str = "medium"
    status: str = "todo"
    dependencies: List[str] = field(default_factory=list)
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def update_status(self, new_status: str):
        """更新任务状态"""
        self.status = new_status
        self.updated_at = datetime.now()

    def add_dependency(self, task_id: str):
        """添加依赖任务"""
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)


class TeamCollaborationModel:
    """团队协作模型主类"""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.team_members: Dict[str, TeamMember] = {}
        self.communication_channels: Dict[str, CommunicationChannel] = {}
        self.meetings: Dict[str, Meeting] = {}
        self.workflow_tasks: Dict[str, WorkflowTask] = {}
        self.collaboration_metrics: Dict[str, Any] = {}

        # 初始化默认沟通渠道
        self._initialize_default_channels()

    def _initialize_default_channels(self):
        """初始化默认沟通渠道"""
        channels = [
            {
                "name": "每日站会",
                "type": CommunicationType.SYNC,
                "purpose": "同步项目进展，识别障碍",
                "frequency": "daily",
                "tools": ["Zoom", "Microsoft Teams"]
            },
            {
                "name": "周报沟通",
                "type": CommunicationType.ASYNC,
                "purpose": "分享周工作总结和下周计划",
                "frequency": "weekly",
                "tools": ["Confluence", "Email"]
            },
            {
                "name": "技术讨论",
                "type": CommunicationType.SYNC,
                "purpose": "讨论技术方案和架构设计",
                "frequency": "as_needed",
                "tools": ["Slack", "GitLab"]
            },
            {
                "name": "项目评审",
                "type": CommunicationType.FORMAL,
                "purpose": "评审项目里程碑和交付物",
                "frequency": "biweekly",
                "tools": ["Jira", "Confluence"]
            }
        ]

        for channel_data in channels:
            channel = CommunicationChannel(**channel_data)
            self.communication_channels[channel.name] = channel

    def add_team_member(self, member: TeamMember):
        """添加团队成员"""
        self.team_members[member.id] = member
        logger.info(f"添加团队成员: {member.name} ({member.role.value})")

    def create_meeting(self, meeting: Meeting):
        """创建会议"""
        self.meetings[meeting.id] = meeting
        logger.info(f"创建会议: {meeting.title}")

    def assign_task(self, task: WorkflowTask):
        """分配任务"""
        self.workflow_tasks[task.id] = task
        logger.info(f"分配任务: {task.title} -> {task.assignee}")

    def get_team_utilization(self) -> Dict[str, float]:
        """获取团队利用率"""
        utilization = {}
        for member_id, member in self.team_members.items():
            # 计算当前分配的任务工作量
            assigned_hours = sum(
                task.estimated_hours for task in self.workflow_tasks.values()
                if task.assignee == member_id and task.status != "completed"
            )
            utilization[member.name] = min(assigned_hours / (member.availability * 40), 1.0)
        return utilization

    def get_communication_effectiveness(self) -> Dict[str, Any]:
        """评估沟通效果"""
        effectiveness = {
            "channel_usage": {},
            "meeting_attendance": {},
            "response_times": {},
            "feedback_scores": {}
        }

        # 分析沟通渠道使用情况
        for channel_name, channel in self.communication_channels.items():
            effectiveness["channel_usage"][channel_name] = len(channel.participants)

        # 分析会议出席情况
        for meeting in self.meetings.values():
            if meeting.status == "completed":
                effectiveness["meeting_attendance"][meeting.id] = len(meeting.participants)

        return effectiveness

    def generate_collaboration_report(self) -> str:
        """生成协作报告"""
        report = f"""
# 团队协作报告 - {self.project_name}
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 团队概况
- 团队成员数量: {len(self.team_members)}
- 活跃任务数量: {len([t for t in self.workflow_tasks.values() if t.status != 'completed'])}
- 计划会议数量: {len([m for m in self.meetings.values() if m.status == 'scheduled'])}

## 团队利用率
{self._format_utilization_report()}

## 沟通渠道状态
{self._format_communication_report()}

## 待跟进行动项
{self._format_action_items_report()}
        """
        return report

    def _format_utilization_report(self) -> str:
        """格式化利用率报告"""
        utilization = self.get_team_utilization()
        lines = []
        for member, rate in utilization.items():
            status = "正常" if rate <= 0.8 else "高负载" if rate <= 1.0 else "超载"
            lines.append(f"- {member}: {rate:.1%} ({status})")
        return "\n".join(lines)

    def _format_communication_report(self) -> str:
        """格式化沟通报告"""
        lines = []
        for channel_name, channel in self.communication_channels.items():
            lines.append(f"- {channel_name}: {len(channel.participants)} 参与者")
        return "\n".join(lines)

    def _format_action_items_report(self) -> str:
        """格式化行动项报告"""
        action_items = []
        for meeting in self.meetings.values():
            for item in meeting.action_items:
                if item["status"] == "pending":
                    action_items.append(f"- {item['description']} ({item['assignee']})")

        if not action_items:
            return "- 无待跟进行动项"
        return "\n".join(action_items)

    def export_configuration(self) -> Dict[str, Any]:
        """导出配置"""
        return {
            "project_name": self.project_name,
            "team_members": [vars(member) for member in self.team_members.values()],
            "communication_channels": [vars(channel) for channel in self.communication_channels.values()],
            "meetings": [vars(meeting) for meeting in self.meetings.values()],
            "workflow_tasks": [vars(task) for task in self.workflow_tasks.values()],
            "exported_at": datetime.now().isoformat()
        }

    def import_configuration(self, config: Dict[str, Any]):
        """导入配置"""
        self.project_name = config.get("project_name", self.project_name)

        # 导入团队成员
        for member_data in config.get("team_members", []):
            role = TeamRole(member_data["role"])
            member = TeamMember(
                id=member_data["id"],
                name=member_data["name"],
                role=role,
                skills=member_data.get("skills", []),
                availability=member_data.get("availability", 1.0),
                communication_style=member_data.get("communication_style", "协作型"),
                timezone=member_data.get("timezone", "UTC+8")
            )
            self.team_members[member.id] = member

        logger.info(f"成功导入团队协作模型配置: {self.project_name}")


def create_sample_team() -> TeamCollaborationModel:
    """创建示例团队"""
    model = TeamCollaborationModel("电商大数据测试项目")

    # 添加团队成员
    members_data = [
        {"id": "PM001", "name": "张经理", "role": TeamRole.PROJECT_MANAGER,
         "skills": ["项目管理", "风险管理", "团队建设"]},
        {"id": "SM001", "name": "林敏捷教练", "role": TeamRole.SCRUM_MASTER,
         "skills": ["敏捷教练", "流程优化", "团队辅导", "障碍移除"]},
        {"id": "TA001", "name": "李架构师", "role": TeamRole.TEST_ARCHITECT,
         "skills": ["测试架构", "性能测试", "自动化测试"]},
        {"id": "STE001", "name": "王高级", "role": TeamRole.SENIOR_TEST_ENGINEER,
         "skills": ["接口测试", "数据库测试", "Linux"]},
        {"id": "STE002", "name": "赵高级", "role": TeamRole.SENIOR_TEST_ENGINEER,
         "skills": ["UI测试", "移动测试", "Python"]},
        {"id": "TE001", "name": "刘工程师", "role": TeamRole.TEST_ENGINEER,
         "skills": ["功能测试", "回归测试", "SQL"]},
        {"id": "DE001", "name": "陈工程师", "role": TeamRole.DEVOPS_ENGINEER,
         "skills": ["Docker", "Kubernetes", "Jenkins"]}
    ]

    for member_data in members_data:
        member = TeamMember(**member_data)
        model.add_team_member(member)

    # 创建示例会议
    meeting = Meeting(
        id="STANDUP_001",
        title="每日站会 - 2025-01-23",
        type="每日站会",
        facilitator="SM001",  # Scrum Master主持站会
        participants=["PM001", "SM001", "TA001", "STE001", "STE002", "TE001", "DE001"],
        duration_minutes=15
    )
    meeting.add_agenda_item("昨日完成工作总结")
    meeting.add_agenda_item("今日计划工作")
    meeting.add_agenda_item("遇到的问题和障碍")
    model.create_meeting(meeting)

    # 创建示例任务
    task = WorkflowTask(
        id="TASK_001",
        title="设计用户登录接口测试用例",
        description="为电商平台的用户登录接口设计完整的测试用例集",
        stage=WorkflowStage.TESTING,
        assignee="STE001",
        priority="high",
        estimated_hours=16.0
    )
    model.assign_task(task)

    return model


if __name__ == "__main__":
    # 创建示例团队协作模型
    team_model = create_sample_team()

    # 生成协作报告
    report = team_model.generate_collaboration_report()
    print(report)

    # 导出配置
    config = team_model.export_configuration()
    with open("team_collaboration_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("\n团队协作模型配置已导出到 team_collaboration_config.json")