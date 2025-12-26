"""
瓶颈识别与优化策略 (Bottleneck Identification and Optimization Strategies)

此脚本用于识别软件开发流程中的瓶颈点，分析根本原因，并提供优化策略建议。
基于流程分析和性能监控数据，帮助团队定位和解决流程效率问题。
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics
import json


class BottleneckType(Enum):
    RESOURCE = "resource"          # 资源瓶颈
    PROCESS = "process"           # 流程瓶颈
    TOOL = "tool"                # 工具瓶颈
    SKILL = "skill"              # 技能瓶颈
    COMMUNICATION = "communication"  # 沟通瓶颈
    QUALITY = "quality"           # 质量瓶颈


@dataclass
class ProcessStep:
    """流程步骤数据类"""
    name: str
    duration_hours: float
    resource_utilization: float  # 资源利用率（%）
    wait_time_hours: float
    error_rate: float  # 错误率（%）
    throughput_items: int  # 吞吐量（项/周期）


@dataclass
class BottleneckAnalysis:
    """瓶颈分析结果"""
    bottleneck_type: BottleneckType
    severity_score: float  # 严重程度得分（0-100）
    affected_steps: List[str]
    root_causes: List[str]
    impact_assessment: Dict[str, float]
    optimization_strategies: List[str]
    expected_improvement: Dict[str, float]


class BottleneckAnalyzer:
    """瓶颈分析器"""

    def __init__(self):
        self.bottleneck_thresholds = {
            "duration_ratio": 2.0,      # 持续时间比例阈值
            "utilization_threshold": 85.0,  # 利用率阈值
            "wait_time_ratio": 0.3,     # 等待时间比例阈值
            "error_rate_threshold": 10.0   # 错误率阈值
        }

    def analyze_bottlenecks(self, process_steps: List[ProcessStep]) -> List[BottleneckAnalysis]:
        """分析流程瓶颈"""
        bottlenecks = []

        # 计算统计指标
        stats = self._calculate_process_stats(process_steps)

        # 识别不同类型的瓶颈
        bottlenecks.extend(self._identify_resource_bottlenecks(process_steps, stats))
        bottlenecks.extend(self._identify_process_bottlenecks(process_steps, stats))
        bottlenecks.extend(self._identify_tool_bottlenecks(process_steps, stats))
        bottlenecks.extend(self._identify_skill_bottlenecks(process_steps, stats))
        bottlenecks.extend(self._identify_communication_bottlenecks(process_steps, stats))
        bottlenecks.extend(self._identify_quality_bottlenecks(process_steps, stats))

        # 按严重程度排序
        bottlenecks.sort(key=lambda x: x.severity_score, reverse=True)

        return bottlenecks

    def _calculate_process_stats(self, steps: List[ProcessStep]) -> Dict[str, float]:
        """计算流程统计指标"""
        if not steps:
            return {}

        durations = [s.duration_hours for s in steps]
        utilizations = [s.resource_utilization for s in steps]
        wait_times = [s.wait_time_hours for s in steps]
        error_rates = [s.error_rate for s in steps]
        throughputs = [s.throughput_items for s in steps]

        return {
            "avg_duration": statistics.mean(durations),
            "max_duration": max(durations),
            "avg_utilization": statistics.mean(utilizations),
            "max_utilization": max(utilizations),
            "total_wait_time": sum(wait_times),
            "avg_error_rate": statistics.mean(error_rates),
            "total_throughput": sum(throughputs),
            "throughput_variance": statistics.variance(throughputs) if len(throughputs) > 1 else 0
        }

    def _identify_resource_bottlenecks(self, steps: List[ProcessStep], stats: Dict[str, float]) -> List[BottleneckAnalysis]:
        """识别资源瓶颈"""
        bottlenecks = []

        for step in steps:
            if step.resource_utilization > self.bottleneck_thresholds["utilization_threshold"]:
                severity = min(100, (step.resource_utilization - 80) * 5)

                analysis = BottleneckAnalysis(
                    bottleneck_type=BottleneckType.RESOURCE,
                    severity_score=severity,
                    affected_steps=[step.name],
                    root_causes=self._analyze_resource_root_causes(step),
                    impact_assessment={
                        "throughput_reduction": severity * 0.3,
                        "quality_degradation": severity * 0.2,
                        "cost_increase": severity * 0.4
                    },
                    optimization_strategies=self._generate_resource_strategies(step),
                    expected_improvement={
                        "utilization_reduction": 15.0,
                        "throughput_increase": 20.0,
                        "cost_savings": 25.0
                    }
                )
                bottlenecks.append(analysis)

        return bottlenecks

    def _identify_process_bottlenecks(self, steps: List[ProcessStep], stats: Dict[str, float]) -> List[BottleneckAnalysis]:
        """识别流程瓶颈"""
        bottlenecks = []

        max_duration = stats.get("max_duration", 0)
        avg_duration = stats.get("avg_duration", 1)

        for step in steps:
            duration_ratio = step.duration_hours / avg_duration if avg_duration > 0 else 1

            if duration_ratio > self.bottleneck_thresholds["duration_ratio"]:
                severity = min(100, (duration_ratio - 1) * 25)

                analysis = BottleneckAnalysis(
                    bottleneck_type=BottleneckType.PROCESS,
                    severity_score=severity,
                    affected_steps=[step.name],
                    root_causes=self._analyze_process_root_causes(step),
                    impact_assessment={
                        "cycle_time_increase": severity * 0.5,
                        "efficiency_reduction": severity * 0.3,
                        "bottleneck_propagation": severity * 0.2
                    },
                    optimization_strategies=self._generate_process_strategies(step),
                    expected_improvement={
                        "duration_reduction": 30.0,
                        "efficiency_improvement": 25.0,
                        "flow_optimization": 35.0
                    }
                )
                bottlenecks.append(analysis)

        return bottlenecks

    def _identify_tool_bottlenecks(self, steps: List[ProcessStep], stats: Dict[str, float]) -> List[BottleneckAnalysis]:
        """识别工具瓶颈"""
        # 基于等待时间和错误率识别工具问题
        bottlenecks = []

        for step in steps:
            wait_ratio = step.wait_time_hours / (step.duration_hours + step.wait_time_hours) if (step.duration_hours + step.wait_time_hours) > 0 else 0

            if wait_ratio > self.bottleneck_thresholds["wait_time_ratio"] or step.error_rate > self.bottleneck_thresholds["error_rate_threshold"]:
                severity = min(100, (wait_ratio * 100) + step.error_rate)

                analysis = BottleneckAnalysis(
                    bottleneck_type=BottleneckType.TOOL,
                    severity_score=severity,
                    affected_steps=[step.name],
                    root_causes=["工具集成不足", "自动化程度低", "工具配置不当"],
                    impact_assessment={
                        "manual_effort_increase": severity * 0.4,
                        "error_introduction": severity * 0.3,
                        "velocity_reduction": severity * 0.3
                    },
                    optimization_strategies=[
                        "升级自动化工具链",
                        "实施工具集成平台",
                        "优化工具配置和使用流程"
                    ],
                    expected_improvement={
                        "automation_increase": 40.0,
                        "error_reduction": 50.0,
                        "efficiency_gain": 35.0
                    }
                )
                bottlenecks.append(analysis)

        return bottlenecks

    def _identify_skill_bottlenecks(self, steps: List[ProcessStep], stats: Dict[str, float]) -> List[BottleneckAnalysis]:
        """识别技能瓶颈"""
        # 基于错误率和吞吐量变化识别技能问题
        bottlenecks = []

        if stats.get("throughput_variance", 0) > 100:  # 高方差表示技能不稳定
            severity = min(100, stats["throughput_variance"] / 10)

            analysis = BottleneckAnalysis(
                bottleneck_type=BottleneckType.SKILL,
                severity_score=severity,
                affected_steps=[s.name for s in steps],
                root_causes=["技能水平不均衡", "培训不足", "知识传递不畅"],
                impact_assessment={
                    "quality_variability": severity * 0.4,
                    "delivery_consistency": severity * 0.3,
                    "team_morale_impact": severity * 0.3
                },
                optimization_strategies=[
                    "实施技能评估和培训计划",
                    "建立导师制度",
                    "引入标准化操作流程"
                ],
                expected_improvement={
                    "skill_improvement": 30.0,
                    "consistency_increase": 40.0,
                    "error_reduction": 35.0
                }
            )
            bottlenecks.append(analysis)

        return bottlenecks

    def _identify_communication_bottlenecks(self, steps: List[ProcessStep], stats: Dict[str, float]) -> List[BottleneckAnalysis]:
        """识别沟通瓶颈"""
        # 基于等待时间和跨步骤依赖识别沟通问题
        bottlenecks = []

        total_wait = stats.get("total_wait_time", 0)
        total_duration = sum(s.duration_hours for s in steps)

        if total_wait > total_duration * 0.5:  # 等待时间过长
            severity = min(100, (total_wait / total_duration) * 100)

            analysis = BottleneckAnalysis(
                bottleneck_type=BottleneckType.COMMUNICATION,
                severity_score=severity,
                affected_steps=[s.name for s in steps if s.wait_time_hours > 0],
                root_causes=["信息传递不畅", "跨团队协调困难", "需求澄清不足"],
                impact_assessment={
                    "delay_accumulation": severity * 0.4,
                    "context_switching": severity * 0.3,
                    "rework_increase": severity * 0.3
                },
                optimization_strategies=[
                    "建立敏捷沟通机制",
                    "实施每日站会和回顾",
                    "使用协作工具改善信息流"
                ],
                expected_improvement={
                    "communication_efficiency": 40.0,
                    "delay_reduction": 50.0,
                    "collaboration_improvement": 35.0
                }
            )
            bottlenecks.append(analysis)

        return bottlenecks

    def _identify_quality_bottlenecks(self, steps: List[ProcessStep], stats: Dict[str, float]) -> List[BottleneckAnalysis]:
        """识别质量瓶颈"""
        bottlenecks = []

        avg_error_rate = stats.get("avg_error_rate", 0)

        if avg_error_rate > self.bottleneck_thresholds["error_rate_threshold"]:
            severity = min(100, avg_error_rate * 2)

            analysis = BottleneckAnalysis(
                bottleneck_type=BottleneckType.QUALITY,
                severity_score=severity,
                affected_steps=[s.name for s in steps if s.error_rate > avg_error_rate],
                root_causes=["测试覆盖不足", "代码审查不严", "质量门控缺失"],
                impact_assessment={
                    "defect_leakage": severity * 0.4,
                    "customer_satisfaction": severity * 0.3,
                    "maintenance_cost": severity * 0.3
                },
                optimization_strategies=[
                    "加强自动化测试",
                    "实施代码审查制度",
                    "建立质量门控机制"
                ],
                expected_improvement={
                    "defect_reduction": 60.0,
                    "quality_improvement": 45.0,
                    "customer_satisfaction": 30.0
                }
            )
            bottlenecks.append(analysis)

        return bottlenecks

    def _analyze_resource_root_causes(self, step: ProcessStep) -> List[str]:
        """分析资源瓶颈根本原因"""
        causes = []
        if step.resource_utilization > 95:
            causes.append("资源分配不足")
        if step.duration_hours > 40:  # 单步持续时间过长
            causes.append("任务粒度过大")
        causes.append("并发处理能力有限")
        return causes

    def _analyze_process_root_causes(self, step: ProcessStep) -> List[str]:
        """分析流程瓶颈根本原因"""
        causes = []
        if step.wait_time_hours > step.duration_hours:
            causes.append("依赖关系复杂")
        if step.error_rate > 15:
            causes.append("流程步骤不稳定")
        causes.append("缺乏标准化流程")
        return causes

    def _generate_resource_strategies(self, step: ProcessStep) -> List[str]:
        """生成资源优化策略"""
        return [
            "增加资源分配或扩展容量",
            "实施负载均衡和资源池化",
            "优化资源调度算法",
            "引入云计算弹性伸缩"
        ]

    def _generate_process_strategies(self, step: ProcessStep) -> List[str]:
        """生成流程优化策略"""
        return [
            "流程再造和简化",
            "并行处理和异步化",
            "自动化重复性任务",
            "实施持续改进机制"
        ]


def main():
    """主函数：演示瓶颈分析"""
    # 示例流程步骤数据
    sample_steps = [
        ProcessStep("需求分析", 16.0, 75.0, 8.0, 5.0, 45),
        ProcessStep("设计阶段", 24.0, 80.0, 12.0, 8.0, 38),
        ProcessStep("编码开发", 40.0, 95.0, 6.0, 12.0, 52),  # 资源瓶颈
        ProcessStep("测试验证", 20.0, 70.0, 15.0, 3.0, 48),
        ProcessStep("部署发布", 8.0, 60.0, 4.0, 2.0, 55)
    ]

    # 创建分析器
    analyzer = BottleneckAnalyzer()

    # 执行瓶颈分析
    bottlenecks = analyzer.analyze_bottlenecks(sample_steps)

    # 输出结果
    print("=== 流程瓶颈分析报告 ===")
    print(f"发现 {len(bottlenecks)} 个瓶颈点")

    for i, bottleneck in enumerate(bottlenecks, 1):
        print(f"\n--- 瓶颈 {i} ---")
        print(f"类型: {bottleneck.bottleneck_type.value}")
        print(".1f"        print(f"影响步骤: {', '.join(bottleneck.affected_steps)}")
        print(f"根本原因: {', '.join(bottleneck.root_causes)}")

        print("影响评估:")
        for key, value in bottleneck.impact_assessment.items():
            print(".1f"
        print("优化策略:")
        for strategy in bottleneck.optimization_strategies:
            print(f"  • {strategy}")

        print("预期改进:")
        for key, value in bottleneck.expected_improvement.items():
            print(".1f"
if __name__ == "__main__":
    main()