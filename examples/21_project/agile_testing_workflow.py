#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敏捷测试流程 - Agile Testing Workflow
大数据测试项目的敏捷开发与DevOps实践框架

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


class SprintStatus(Enum):
    """冲刺状态枚举"""
    PLANNING = "规划中"
    ACTIVE = "进行中"
    REVIEW = "评审中"
    RETROSPECTIVE = "回顾中"
    COMPLETED = "已完成"


class UserStoryStatus(Enum):
    """用户故事状态枚举"""
    BACKLOG = "产品待办"
    READY = "准备就绪"
    IN_PROGRESS = "进行中"
    TESTING = "测试中"
    DONE = "完成"


class TestType(Enum):
    """测试类型枚举"""
    UNIT = "单元测试"
    INTEGRATION = "集成测试"
    SYSTEM = "系统测试"
    ACCEPTANCE = "验收测试"
    PERFORMANCE = "性能测试"
    SECURITY = "安全测试"


@dataclass
class UserStory:
    """用户故事类"""
    id: str
    title: str
    description: str
    acceptance_criteria: List[str] = field(default_factory=list)
    story_points: int = 0
    priority: str = "medium"
    status: UserStoryStatus = UserStoryStatus.BACKLOG
    assignee: Optional[str] = None
    sprint_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def update_status(self, new_status: UserStoryStatus):
        """更新用户故事状态"""
        self.status = new_status
        self.updated_at = datetime.now()

    def add_acceptance_criterion(self, criterion: str):
        """添加验收标准"""
        self.acceptance_criteria.append(criterion)


@dataclass
class Sprint:
    """冲刺类"""
    id: str
    name: str
    goal: str
    start_date: datetime
    end_date: datetime
    status: SprintStatus = SprintStatus.PLANNING
    capacity: int = 0  # 总故事点容量
    committed_points: int = 0  # 已承诺的故事点
    completed_points: int = 0  # 已完成的故事点
    user_stories: List[str] = field(default_factory=list)
    burndown_data: List[Dict] = field(default_factory=list)

    def add_user_story(self, story_id: str, story_points: int):
        """添加用户故事到冲刺"""
        if story_id not in self.user_stories:
            self.user_stories.append(story_id)
            self.committed_points += story_points

    def update_burndown(self, remaining_points: int, date: datetime = None):
        """更新燃尽图数据"""
        if date is None:
            date = datetime.now()

        self.burndown_data.append({
            "date": date.isoformat(),
            "remaining_points": remaining_points,
            "ideal_remaining": self._calculate_ideal_burndown(date)
        })

    def _calculate_ideal_burndown(self, current_date: datetime) -> float:
        """计算理想燃尽曲线"""
        total_days = (self.end_date - self.start_date).days
        elapsed_days = (current_date - self.start_date).days
        if total_days <= 0:
            return 0
        progress_ratio = elapsed_days / total_days
        return max(0, self.committed_points * (1 - progress_ratio))


@dataclass
class TestCase:
    """测试用例类"""
    id: str
    title: str
    description: str
    test_type: TestType
    user_story_id: str
    preconditions: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    expected_results: List[str] = field(default_factory=list)
    actual_results: List[str] = field(default_factory=list)
    status: str = "pending"
    priority: str = "medium"
    automation_status: str = "manual"
    execution_time: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def execute(self, actual_results: List[str], execution_time: float):
        """执行测试用例"""
        self.actual_results = actual_results
        self.execution_time = execution_time
        self.status = "passed" if self._verify_results() else "failed"
        self.updated_at = datetime.now()

    def _verify_results(self) -> bool:
        """验证测试结果"""
        if len(self.actual_results) != len(self.expected_results):
            return False
        return all(actual == expected
                  for actual, expected in zip(self.actual_results, self.expected_results))


@dataclass
class ContinuousIntegration:
    """持续集成配置类"""
    pipeline_name: str
    stages: List[Dict] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    quality_gates: List[Dict] = field(default_factory=list)
    notifications: List[str] = field(default_factory=list)

    def add_stage(self, name: str, jobs: List[str], quality_checks: List[str] = None):
        """添加流水线阶段"""
        stage = {
            "name": name,
            "jobs": jobs,
            "quality_checks": quality_checks or []
        }
        self.stages.append(stage)


class AgileTestingWorkflow:
    """敏捷测试流程主类"""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.product_backlog: Dict[str, UserStory] = {}
        self.sprints: Dict[str, Sprint] = {}
        self.test_cases: Dict[str, TestCase] = {}
        self.ci_pipelines: Dict[str, ContinuousIntegration] = {}
        self.metrics: Dict[str, Any] = {}

        # 初始化默认CI流水线
        self._initialize_default_pipeline()

    def _initialize_default_pipeline(self):
        """初始化默认CI流水线"""
        pipeline = ContinuousIntegration("大数据测试CI流水线")

        # 提交阶段
        pipeline.add_stage(
            "commit",
            ["代码检查", "单元测试", "静态分析"],
            ["代码覆盖率 > 80%", "无严重缺陷"]
        )

        # 构建阶段
        pipeline.add_stage(
            "build",
            ["编译构建", "集成测试", "容器构建"],
            ["构建成功", "集成测试通过"]
        )

        # 测试阶段
        pipeline.add_stage(
            "test",
            ["系统测试", "性能测试", "安全测试"],
            ["测试通过率 > 95%", "性能基准达标"]
        )

        # 部署阶段
        pipeline.add_stage(
            "deploy",
            ["部署到测试环境", "冒烟测试", "验收测试"],
            ["部署成功", "验收测试通过"]
        )

        self.ci_pipelines[pipeline.pipeline_name] = pipeline

    def create_user_story(self, story: UserStory):
        """创建用户故事"""
        self.product_backlog[story.id] = story
        logger.info(f"创建用户故事: {story.title}")

    def create_sprint(self, sprint: Sprint):
        """创建冲刺"""
        self.sprints[sprint.id] = sprint
        logger.info(f"创建冲刺: {sprint.name}")

    def create_test_case(self, test_case: TestCase):
        """创建测试用例"""
        self.test_cases[test_case.id] = test_case
        logger.info(f"创建测试用例: {test_case.title}")

    def start_sprint(self, sprint_id: str):
        """开始冲刺"""
        if sprint_id in self.sprints:
            sprint = self.sprints[sprint_id]
            sprint.status = SprintStatus.ACTIVE
            sprint.update_burndown(sprint.committed_points)
            logger.info(f"开始冲刺: {sprint.name}")

    def complete_user_story(self, story_id: str):
        """完成用户故事"""
        if story_id in self.product_backlog:
            story = self.product_backlog[story_id]
            story.update_status(UserStoryStatus.DONE)

            # 更新相关冲刺的燃尽图
            if story.sprint_id and story.sprint_id in self.sprints:
                sprint = self.sprints[story.sprint_id]
                sprint.completed_points += story.story_points
                remaining = sprint.committed_points - sprint.completed_points
                sprint.update_burndown(remaining)

            logger.info(f"完成用户故事: {story.title}")

    def run_ci_pipeline(self, pipeline_name: str) -> Dict[str, Any]:
        """运行CI流水线"""
        if pipeline_name not in self.ci_pipelines:
            raise ValueError(f"流水线不存在: {pipeline_name}")

        pipeline = self.ci_pipelines[pipeline_name]
        results = {
            "pipeline": pipeline_name,
            "start_time": datetime.now().isoformat(),
            "stages": [],
            "overall_status": "success"
        }

        for stage in pipeline.stages:
            stage_result = {
                "name": stage["name"],
                "status": "success",
                "jobs": [],
                "quality_checks": []
            }

            # 模拟执行作业
            for job in stage["jobs"]:
                job_result = self._execute_job(job)
                stage_result["jobs"].append(job_result)
                if job_result["status"] == "failed":
                    stage_result["status"] = "failed"
                    results["overall_status"] = "failed"

            # 执行质量检查
            for check in stage["quality_checks"]:
                check_result = self._execute_quality_check(check)
                stage_result["quality_checks"].append(check_result)
                if not check_result["passed"]:
                    stage_result["status"] = "failed"
                    results["overall_status"] = "failed"

            results["stages"].append(stage_result)

        results["end_time"] = datetime.now().isoformat()
        logger.info(f"CI流水线执行完成: {pipeline_name} - {results['overall_status']}")
        return results

    def _execute_job(self, job_name: str) -> Dict[str, Any]:
        """执行作业（模拟）"""
        # 模拟作业执行结果
        success_rate = 0.95  # 95% 成功率
        import random
        status = "success" if random.random() < success_rate else "failed"

        return {
            "name": job_name,
            "status": status,
            "duration": random.uniform(1, 10),
            "output": f"作业 {job_name} 执行完成"
        }

    def _execute_quality_check(self, check_name: str) -> Dict[str, Any]:
        """执行质量检查（模拟）"""
        # 解析检查条件
        if ">" in check_name:
            metric, threshold = check_name.split(">")
            metric = metric.strip()
            threshold = float(threshold.strip().rstrip("%")) / 100 if "%" in threshold else float(threshold.strip())
            # 模拟度量值
            actual_value = 0.85 if "覆盖率" in metric else 0.95
            passed = actual_value >= threshold
        else:
            passed = True  # 默认通过

        return {
            "name": check_name,
            "passed": passed,
            "actual_value": actual_value if ">" in check_name else None
        }

    def get_sprint_metrics(self, sprint_id: str) -> Dict[str, Any]:
        """获取冲刺度量"""
        if sprint_id not in self.sprints:
            raise ValueError(f"冲刺不存在: {sprint_id}")

        sprint = self.sprints[sprint_id]
        stories = [self.product_backlog[sid] for sid in sprint.user_stories if sid in self.product_backlog]

        return {
            "sprint_id": sprint_id,
            "total_stories": len(stories),
            "completed_stories": len([s for s in stories if s.status == UserStoryStatus.DONE]),
            "committed_points": sprint.committed_points,
            "completed_points": sprint.completed_points,
            "velocity": sprint.completed_points,
            "burndown_efficiency": self._calculate_burndown_efficiency(sprint)
        }

    def _calculate_burndown_efficiency(self, sprint: Sprint) -> float:
        """计算燃尽效率"""
        if not sprint.burndown_data:
            return 0.0

        # 计算实际燃尽与理想燃尽的差异
        latest_data = sprint.burndown_data[-1]
        ideal_remaining = latest_data.get("ideal_remaining", 0)
        actual_remaining = latest_data.get("remaining_points", 0)

        if ideal_remaining == 0:
            return 1.0 if actual_remaining == 0 else 0.0

        return 1.0 - (actual_remaining - ideal_remaining) / sprint.committed_points

    def generate_sprint_report(self, sprint_id: str) -> str:
        """生成冲刺报告"""
        metrics = self.get_sprint_metrics(sprint_id)
        sprint = self.sprints[sprint_id]

        report = f"""
# 冲刺报告 - {sprint.name}
项目: {self.project_name}
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 冲刺概况
- 状态: {sprint.status.value}
- 周期: {sprint.start_date.strftime('%Y-%m-%d')} 至 {sprint.end_date.strftime('%Y-%m-%d')}
- 目标: {sprint.goal}

## 进度指标
- 用户故事: {metrics['completed_stories']}/{metrics['total_stories']}
- 故事点: {metrics['completed_points']}/{metrics['committed_points']}
- 速度: {metrics['velocity']} 故事点/冲刺
- 燃尽效率: {metrics['burndown_efficiency']:.1%}

## 用户故事状态
{self._format_stories_status(sprint_id)}

## 测试执行情况
{self._format_test_execution_status(sprint_id)}
        """
        return report

    def _format_stories_status(self, sprint_id: str) -> str:
        """格式化用户故事状态"""
        sprint = self.sprints[sprint_id]
        status_counts = {}
        for story_id in sprint.user_stories:
            if story_id in self.product_backlog:
                status = self.product_backlog[story_id].status.value
                status_counts[status] = status_counts.get(status, 0) + 1

        lines = []
        for status, count in status_counts.items():
            lines.append(f"- {status}: {count} 个")
        return "\n".join(lines) if lines else "- 无用户故事"

    def _format_test_execution_status(self, sprint_id: str) -> str:
        """格式化测试执行状态"""
        sprint = self.sprints[sprint_id]
        related_tests = [tc for tc in self.test_cases.values()
                        if tc.user_story_id in sprint.user_stories]

        if not related_tests:
            return "- 无相关测试用例"

        status_counts = {}
        for test in related_tests:
            status_counts[test.status] = status_counts.get(test.status, 0) + 1

        lines = []
        for status, count in status_counts.items():
            lines.append(f"- {status}: {count} 个")
        return "\n".join(lines)

    def export_configuration(self) -> Dict[str, Any]:
        """导出配置"""
        return {
            "project_name": self.project_name,
            "product_backlog": [vars(story) for story in self.product_backlog.values()],
            "sprints": [vars(sprint) for sprint in self.sprints.values()],
            "test_cases": [vars(tc) for tc in self.test_cases.values()],
            "ci_pipelines": [vars(pipeline) for pipeline in self.ci_pipelines.values()],
            "exported_at": datetime.now().isoformat()
        }


def create_sample_workflow() -> AgileTestingWorkflow:
    """创建示例敏捷测试流程"""
    workflow = AgileTestingWorkflow("电商大数据测试项目")

    # 创建用户故事
    stories_data = [
        {
            "id": "US001",
            "title": "用户登录功能",
            "description": "作为用户，我想要能够登录系统，以便访问我的账户",
            "story_points": 5,
            "acceptance_criteria": [
                "用户可以使用用户名和密码登录",
                "登录失败时显示错误信息",
                "成功登录后跳转到首页"
            ]
        },
        {
            "id": "US002",
            "title": "商品搜索功能",
            "description": "作为用户，我想要能够搜索商品，以便找到需要的商品",
            "story_points": 8,
            "acceptance_criteria": [
                "支持关键词搜索",
                "支持分类筛选",
                "显示搜索结果列表"
            ]
        }
    ]

    for story_data in stories_data:
        story = UserStory(**story_data)
        workflow.create_user_story(story)

    # 创建冲刺
    sprint = Sprint(
        id="SPRINT_001",
        name="Sprint 1",
        goal="实现用户登录和商品搜索核心功能",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=14),
        capacity=20
    )
    workflow.create_sprint(sprint)

    # 将用户故事添加到冲刺
    for story in workflow.product_backlog.values():
        sprint.add_user_story(story.id, story.story_points)

    # 创建测试用例
    test_cases_data = [
        {
            "id": "TC001",
            "title": "验证用户登录功能",
            "description": "测试用户使用有效凭据登录",
            "test_type": TestType.SYSTEM,
            "user_story_id": "US001",
            "steps": ["访问登录页面", "输入用户名和密码", "点击登录按钮"],
            "expected_results": ["成功登录", "跳转到首页"]
        },
        {
            "id": "TC002",
            "title": "验证商品搜索功能",
            "description": "测试商品关键词搜索",
            "test_type": TestType.SYSTEM,
            "user_story_id": "US002",
            "steps": ["访问搜索页面", "输入搜索关键词", "点击搜索按钮"],
            "expected_results": ["显示搜索结果", "结果包含相关商品"]
        }
    ]

    for tc_data in test_cases_data:
        test_case = TestCase(**tc_data)
        workflow.create_test_case(test_case)

    return workflow


if __name__ == "__main__":
    # 创建示例敏捷测试流程
    workflow = create_sample_workflow()

    # 开始冲刺
    workflow.start_sprint("SPRINT_001")

    # 完成一个用户故事
    workflow.complete_user_story("US001")

    # 运行CI流水线
    ci_result = workflow.run_ci_pipeline("大数据测试CI流水线")
    print(f"CI流水线状态: {ci_result['overall_status']}")

    # 生成冲刺报告
    report = workflow.generate_sprint_report("SPRINT_001")
    print(report)

    # 导出配置
    config = workflow.export_configuration()
    with open("agile_testing_workflow_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("\n敏捷测试流程配置已导出到 agile_testing_workflow_config.json")