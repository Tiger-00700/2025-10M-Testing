# examples/22_streaming_batch/implementation_steps.py
"""
流批一体实施步骤脚本
用于规划和执行实施步骤，生成实施计划和进度跟踪
"""

import yaml
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StepStatus(Enum):
    """步骤状态"""
    PENDING = "待开始"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    BLOCKED = "受阻"
    CANCELLED = "已取消"

@dataclass
class ImplementationStep:
    """实施步骤"""
    id: str
    name: str
    description: str
    phase: str
    dependencies: List[str]
    estimated_effort: int  # 人天
    actual_effort: Optional[int] = None
    status: StepStatus = StepStatus.PENDING
    assignee: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    deliverables: List[str] = None
    risks: List[str] = None
    mitigation_actions: List[str] = None

@dataclass
class CriticalTechnology:
    """关键技术"""
    name: str
    description: str
    implementation_approach: str
    challenges: List[str]
    solutions: List[str]

@dataclass
class Milestone:
    """里程碑"""
    name: str
    description: str
    target_date: datetime
    deliverables: List[str]
    success_criteria: List[str]

class ImplementationPlanner:
    """实施规划器"""

    def __init__(self, config_file: str = 'implementation_steps.yml'):
        self.config = self._load_config(config_file)
        self.steps: List[ImplementationStep] = []
        self.critical_technologies: List[CriticalTechnology] = []
        self.milestones: List[Milestone] = []

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        config_path = Path(__file__).parent / config_file
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def plan_implementation_steps(self) -> List[ImplementationStep]:
        """规划实施步骤"""
        steps_config = self.config.get('implementation_steps', [])

        for step_data in steps_config:
            step = ImplementationStep(
                id=step_data['id'],
                name=step_data['name'],
                description=step_data['description'],
                phase=step_data['phase'],
                dependencies=step_data.get('dependencies', []),
                estimated_effort=step_data['estimated_effort'],
                actual_effort=step_data.get('actual_effort'),
                status=StepStatus(step_data.get('status', 'PENDING')),
                assignee=step_data.get('assignee'),
                start_date=step_data.get('start_date'),
                end_date=step_data.get('end_date'),
                deliverables=step_data.get('deliverables', []),
                risks=step_data.get('risks', []),
                mitigation_actions=step_data.get('mitigation_actions', [])
            )
            self.steps.append(step)

        return self.steps

    def identify_critical_technologies(self) -> List[CriticalTechnology]:
        """识别关键技术"""
        tech_config = self.config.get('critical_technologies', [])

        for tech_data in tech_config:
            tech = CriticalTechnology(
                name=tech_data['name'],
                description=tech_data['description'],
                implementation_approach=tech_data['implementation_approach'],
                challenges=tech_data['challenges'],
                solutions=tech_data['solutions']
            )
            self.critical_technologies.append(tech)

        return self.critical_technologies

    def define_milestones(self) -> List[Milestone]:
        """定义里程碑"""
        milestones_config = self.config.get('milestones', [])

        for milestone_data in milestones_config:
            milestone = Milestone(
                name=milestone_data['name'],
                description=milestone_data['description'],
                target_date=datetime.fromisoformat(milestone_data['target_date']),
                deliverables=milestone_data['deliverables'],
                success_criteria=milestone_data['success_criteria']
            )
            self.milestones.append(milestone)

        return self.milestones

    def calculate_critical_path(self) -> List[str]:
        """计算关键路径"""
        # 简化的关键路径计算
        step_dict = {step.id: step for step in self.steps}

        # 构建依赖图
        dependency_graph = {}
        for step in self.steps:
            dependency_graph[step.id] = step.dependencies

        # 计算每个步骤的 earliest start time
        earliest_start = {}
        for step in self.steps:
            if not step.dependencies:
                earliest_start[step.id] = 0
            else:
                earliest_start[step.id] = max(
                    earliest_start[dep] + step_dict[dep].estimated_effort
                    for dep in step.dependencies
                )

        # 计算关键路径（简化版：选择耗时最长的路径）
        critical_path = []
        current_max = 0
        current_path = []

        def find_critical_path(current_step, current_time, path):
            nonlocal current_max, current_path

            path = path + [current_step]
            current_time += step_dict[current_step].estimated_effort

            if current_time > current_max:
                current_max = current_time
                current_path = path[:]

            # 递归处理后续步骤
            for step in self.steps:
                if current_step in step.dependencies and step.id not in path:
                    find_critical_path(step.id, current_time, path)

            path.pop()

        # 从没有依赖的步骤开始
        for step in self.steps:
            if not step.dependencies:
                find_critical_path(step.id, 0, [])

        return current_path

    def generate_implementation_plan(self) -> Dict[str, Any]:
        """生成实施计划"""
        logger.info("开始生成实施计划...")

        # 执行各项规划
        steps = self.plan_implementation_steps()
        critical_technologies = self.identify_critical_technologies()
        milestones = self.define_milestones()

        # 计算关键路径
        critical_path = self.calculate_critical_path()

        # 计算项目总工期和总人力
        total_effort = sum(step.estimated_effort for step in steps)
        completed_steps = [step for step in steps if step.status == StepStatus.COMPLETED]
        completed_effort = sum(step.actual_effort or step.estimated_effort for step in completed_steps)
        progress_percentage = completed_effort / total_effort if total_effort > 0 else 0

        # 生成计划
        plan = {
            'summary': {
                'total_steps': len(steps),
                'completed_steps': len(completed_steps),
                'in_progress_steps': len([s for s in steps if s.status == StepStatus.IN_PROGRESS]),
                'blocked_steps': len([s for s in steps if s.status == StepStatus.BLOCKED]),
                'total_effort': total_effort,
                'completed_effort': completed_effort,
                'progress_percentage': progress_percentage,
                'critical_path_length': len(critical_path),
                'critical_technologies_count': len(critical_technologies),
                'milestones_count': len(milestones)
            },
            'implementation_steps': [asdict(step) for step in steps],
            'critical_technologies': [asdict(tech) for tech in critical_technologies],
            'milestones': [asdict(milestone) for milestone in milestones],
            'critical_path': critical_path,
            'phase_breakdown': self._analyze_phases(),
            'risk_assessment': self._assess_risks(),
            'recommendations': [
                "优先执行关键路径上的任务",
                "关注关键技术的攻克",
                "定期review里程碑达成情况",
                "及时识别和处理风险",
                "保持团队沟通和协作"
            ]
        }

        return plan

    def _analyze_phases(self) -> Dict[str, Any]:
        """分析各阶段情况"""
        phases = {}
        for step in self.steps:
            if step.phase not in phases:
                phases[step.phase] = {
                    'total_steps': 0,
                    'completed_steps': 0,
                    'total_effort': 0,
                    'completed_effort': 0
                }

            phases[step.phase]['total_steps'] += 1
            phases[step.phase]['total_effort'] += step.estimated_effort

            if step.status == StepStatus.COMPLETED:
                phases[step.phase]['completed_steps'] += 1
                phases[step.phase]['completed_effort'] += step.actual_effort or step.estimated_effort

        # 计算各阶段进度
        for phase_data in phases.values():
            if phase_data['total_effort'] > 0:
                phase_data['progress_percentage'] = phase_data['completed_effort'] / phase_data['total_effort']
            else:
                phase_data['progress_percentage'] = 0

        return phases

    def _assess_risks(self) -> Dict[str, Any]:
        """风险评估"""
        all_risks = []
        for step in self.steps:
            if step.risks:
                all_risks.extend(step.risks)

        risk_counts = {}
        for risk in all_risks:
            risk_counts[risk] = risk_counts.get(risk, 0) + 1

        return {
            'total_risks': len(all_risks),
            'unique_risks': len(risk_counts),
            'risk_distribution': risk_counts,
            'high_risk_steps': [
                step.id for step in self.steps
                if len(step.risks or []) > 2 or step.status == StepStatus.BLOCKED
            ]
        }

# 默认配置
DEFAULT_CONFIG = {
    'implementation_steps': [
        {
            'id': 'ENV_SETUP',
            'name': '环境搭建',
            'description': '搭建开发、测试和生产环境',
            'phase': '准备阶段',
            'dependencies': [],
            'estimated_effort': 5,
            'status': 'COMPLETED',
            'deliverables': ['开发环境', '测试环境', 'CI/CD流水线'],
            'risks': ['环境配置复杂', '资源不足'],
            'mitigation_actions': ['提前规划资源', '使用自动化部署']
        },
        {
            'id': 'DATA_INTEGRATION',
            'name': '数据集成',
            'description': '实现数据源接入和数据管道',
            'phase': '开发阶段',
            'dependencies': ['ENV_SETUP'],
            'estimated_effort': 10,
            'status': 'IN_PROGRESS',
            'deliverables': ['数据采集组件', '数据管道', '数据质量检查'],
            'risks': ['数据源多样性', '数据质量问题'],
            'mitigation_actions': ['统一数据格式', '实施数据治理']
        },
        {
            'id': 'STREAM_PROCESSING',
            'name': '流处理功能开发',
            'description': '开发实时流数据处理功能',
            'phase': '开发阶段',
            'dependencies': ['DATA_INTEGRATION'],
            'estimated_effort': 15,
            'deliverables': ['流处理作业', '状态管理', '容错机制'],
            'risks': ['状态一致性', '性能瓶颈'],
            'mitigation_actions': ['使用Exactly-Once语义', '性能优化和测试']
        },
        {
            'id': 'BATCH_PROCESSING',
            'name': '批处理功能开发',
            'description': '开发批量数据处理功能',
            'phase': '开发阶段',
            'dependencies': ['DATA_INTEGRATION'],
            'estimated_effort': 12,
            'deliverables': ['批处理作业', '数据转换', '结果存储'],
            'risks': ['数据倾斜', '处理时间过长'],
            'mitigation_actions': ['优化数据分布', '并行处理优化']
        },
        {
            'id': 'UNIFIED_API',
            'name': '统一API开发',
            'description': '开发统一的数据访问API',
            'phase': '开发阶段',
            'dependencies': ['STREAM_PROCESSING', 'BATCH_PROCESSING'],
            'estimated_effort': 8,
            'deliverables': ['REST API', '查询接口', '数据服务'],
            'risks': ['接口设计复杂', '性能要求高'],
            'mitigation_actions': ['遵循RESTful设计', '实施缓存策略']
        },
        {
            'id': 'TESTING_VALIDATION',
            'name': '测试验证',
            'description': '进行全面的功能和性能测试',
            'phase': '测试阶段',
            'dependencies': ['UNIFIED_API'],
            'estimated_effort': 10,
            'deliverables': ['测试报告', '性能基准', '质量评估'],
            'risks': ['测试覆盖不足', '性能不达标'],
            'mitigation_actions': ['制定测试策略', '性能调优']
        },
        {
            'id': 'DEPLOYMENT',
            'name': '部署上线',
            'description': '将系统部署到生产环境',
            'phase': '部署阶段',
            'dependencies': ['TESTING_VALIDATION'],
            'estimated_effort': 5,
            'deliverables': ['生产部署', '监控配置', '运维文档'],
            'risks': ['部署失败', '生产问题'],
            'mitigation_actions': ['灰度发布', '回滚计划']
        }
    ],
    'critical_technologies': [
        {
            'name': '流批统一处理',
            'description': '实现流处理和批处理的数据一致性和统一接口',
            'implementation_approach': '基于Flink的流批一体架构，抽象统一的数据处理接口',
            'challenges': ['状态管理复杂', '数据一致性保证', '性能平衡'],
            'solutions': ['使用Flink状态管理', '实现Exactly-Once语义', '动态资源分配']
        },
        {
            'name': '实时数据质量监控',
            'description': '实时监控数据质量和处理效果',
            'implementation_approach': '构建数据质量监控框架，集成到数据管道中',
            'challenges': ['实时性要求', '准确性验证', '告警机制'],
            'solutions': ['流式质量检查', '统计采样验证', '多级告警体系']
        }
    ],
    'milestones': [
        {
            'name': '环境就绪',
            'description': '开发和测试环境搭建完成',
            'target_date': '2024-01-15',
            'deliverables': ['开发环境', '测试环境', 'CI/CD流水线'],
            'success_criteria': ['环境可正常使用', '自动化部署成功']
        },
        {
            'name': '核心功能完成',
            'description': '流处理和批处理核心功能开发完成',
            'target_date': '2024-02-28',
            'deliverables': ['流处理作业', '批处理作业', '数据管道'],
            'success_criteria': ['功能测试通过', '性能测试达标']
        },
        {
            'name': '系统集成完成',
            'description': '系统集成测试和API开发完成',
            'target_date': '2024-03-15',
            'deliverables': ['统一API', '集成测试报告'],
            'success_criteria': ['接口测试通过', '集成测试通过']
        },
        {
            'name': '生产就绪',
            'description': '系统测试完成，准备生产部署',
            'target_date': '2024-03-30',
            'deliverables': ['测试报告', '部署文档', '运维手册'],
            'success_criteria': ['所有测试通过', '性能达标', '文档完整']
        }
    ]
}

# 使用示例
if __name__ == "__main__":
    # 创建默认配置文件
    config_path = Path(__file__).parent / 'implementation_steps.yml'
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True)

    # 创建规划器并生成计划
    planner = ImplementationPlanner()

    # 生成实施计划
    plan = planner.generate_implementation_plan()

    # 输出结果
    print("实施计划:")
    print(json.dumps(plan['summary'], indent=2, ensure_ascii=False))

    print(f"\n关键路径: {' -> '.join(plan['critical_path'])}")

    print(f"\n项目进度: {plan['summary']['progress_percentage']:.1%}")

    print("实施规划完成")