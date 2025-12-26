"""
流程韧性与风险控制 (Process Resilience and Risk Control)

此脚本用于评估和提升软件开发流程的韧性，建立风险控制体系。
基于混沌工程和容灾设计原则，提供流程恢复能力和风险管理机制。
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import random
import json
from datetime import datetime, timedelta


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResilienceStrategy(Enum):
    REDUNDANCY = "redundancy"          # 冗余设计
    CIRCUIT_BREAKER = "circuit_breaker" # 断路器模式
    GRACEFUL_DEGRADATION = "graceful_degradation"  # 优雅降级
    AUTO_RECOVERY = "auto_recovery"    # 自动恢复
    MANUAL_INTERVENTION = "manual_intervention"  # 人工干预


@dataclass
class RiskEvent:
    """风险事件"""
    event_id: str
    description: str
    probability: float  # 发生概率（0-1）
    impact: float       # 影响程度（0-1）
    risk_level: RiskLevel
    affected_processes: List[str]
    detection_time: Optional[datetime]
    mitigation_strategy: ResilienceStrategy
    status: str  # identified, mitigated, resolved


@dataclass
class ResilienceMetrics:
    """韧性指标"""
    mean_time_between_failures: float  # 平均故障间隔时间（小时）
    mean_time_to_recovery: float       # 平均恢复时间（分钟）
    service_availability: float        # 服务可用性（%）
    failure_impact_score: float        # 故障影响得分（0-100）
    recovery_success_rate: float       # 恢复成功率（%）


@dataclass
class ResilienceAssessment:
    """韧性评估结果"""
    overall_resilience_score: float
    metrics: ResilienceMetrics
    identified_risks: List[RiskEvent]
    recommended_strategies: List[ResilienceStrategy]
    improvement_actions: List[str]
    resilience_gaps: List[str]


class ResilienceManager:
    """韧性管理器"""

    def __init__(self):
        self.risk_events: List[RiskEvent] = []
        self.resilience_strategies: Dict[str, ResilienceStrategy] = {}
        self.monitoring_data: List[Dict[str, Any]] = []

    def assess_resilience(self, process_data: Dict[str, Any]) -> ResilienceAssessment:
        """评估流程韧性"""
        # 计算韧性指标
        metrics = self._calculate_resilience_metrics(process_data)

        # 识别风险
        risks = self._identify_risks(process_data)

        # 评估整体韧性得分
        overall_score = self._calculate_overall_resilience_score(metrics, risks)

        # 生成建议
        strategies = self._recommend_resilience_strategies(metrics, risks)
        actions = self._generate_improvement_actions(metrics, risks)
        gaps = self._identify_resilience_gaps(metrics, risks)

        return ResilienceAssessment(
            overall_resilience_score=overall_score,
            metrics=metrics,
            identified_risks=risks,
            recommended_strategies=strategies,
            improvement_actions=actions,
            resilience_gaps=gaps
        )

    def _calculate_resilience_metrics(self, process_data: Dict[str, Any]) -> ResilienceMetrics:
        """计算韧性指标"""
        # 从process_data中提取相关信息，默认为模拟数据
        mtbf = process_data.get("mtbf_hours", 168.0)  # 默认一周
        mttr = process_data.get("mttr_minutes", 45.0)  # 默认45分钟
        availability = process_data.get("availability_percent", 99.5)
        failure_impact = process_data.get("failure_impact_score", 25.0)
        recovery_rate = process_data.get("recovery_success_rate", 95.0)

        return ResilienceMetrics(
            mean_time_between_failures=mtbf,
            mean_time_to_recovery=mttr,
            service_availability=availability,
            failure_impact_score=failure_impact,
            recovery_success_rate=recovery_rate
        )

    def _identify_risks(self, process_data: Dict[str, Any]) -> List[RiskEvent]:
        """识别风险事件"""
        risks = []

        # 基于流程数据的常见风险识别
        risk_scenarios = [
            {
                "description": "关键人员离职导致知识丢失",
                "probability": 0.3,
                "impact": 0.7,
                "affected_processes": ["需求分析", "架构设计", "代码审查"],
                "strategy": ResilienceStrategy.REDUNDANCY
            },
            {
                "description": "第三方服务中断",
                "probability": 0.2,
                "impact": 0.8,
                "affected_processes": ["CI/CD部署", "外部集成"],
                "strategy": ResilienceStrategy.CIRCUIT_BREAKER
            },
            {
                "description": "网络故障导致协作中断",
                "probability": 0.4,
                "impact": 0.5,
                "affected_processes": ["团队协作", "代码提交"],
                "strategy": ResilienceStrategy.GRACEFUL_DEGRADATION
            },
            {
                "description": "生产环境配置错误",
                "probability": 0.1,
                "impact": 0.9,
                "affected_processes": ["生产部署", "配置管理"],
                "strategy": ResilienceStrategy.AUTO_RECOVERY
            },
            {
                "description": "需求变更过于频繁",
                "probability": 0.6,
                "impact": 0.4,
                "affected_processes": ["需求管理", "迭代规划"],
                "strategy": ResilienceStrategy.MANUAL_INTERVENTION
            }
        ]

        for i, scenario in enumerate(risk_scenarios):
            risk_score = scenario["probability"] * scenario["impact"]
            if risk_score > 0.2:  # 只包含高风险事件
                risk_level = self._calculate_risk_level(risk_score)

                risk = RiskEvent(
                    event_id=f"RISK_{i+1:03d}",
                    description=scenario["description"],
                    probability=scenario["probability"],
                    impact=scenario["impact"],
                    risk_level=risk_level,
                    affected_processes=scenario["affected_processes"],
                    detection_time=None,
                    mitigation_strategy=scenario["strategy"],
                    status="identified"
                )
                risks.append(risk)

        return risks

    def _calculate_risk_level(self, risk_score: float) -> RiskLevel:
        """计算风险等级"""
        if risk_score >= 0.7:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.4:
            return RiskLevel.HIGH
        elif risk_score >= 0.2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _calculate_overall_resilience_score(self, metrics: ResilienceMetrics, risks: List[RiskEvent]) -> float:
        """计算整体韧性得分"""
        # 基于指标的得分
        availability_score = metrics.service_availability
        recovery_score = min(100, 100 - (metrics.mean_time_to_recovery / 60) * 100)  # 1小时内恢复为满分
        mtbf_score = min(100, (metrics.mean_time_between_failures / 24) * 10)  # 按天计算
        impact_score = 100 - metrics.failure_impact_score
        success_score = metrics.recovery_success_rate

        metric_score = statistics.mean([availability_score, recovery_score, mtbf_score, impact_score, success_score])

        # 风险调整因子
        high_risk_count = len([r for r in risks if r.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]])
        risk_penalty = high_risk_count * 5  # 每个高风险扣5分

        final_score = max(0, min(100, metric_score - risk_penalty))

        return final_score

    def _recommend_resilience_strategies(self, metrics: ResilienceMetrics, risks: List[RiskEvent]) -> List[ResilienceStrategy]:
        """推荐韧性策略"""
        strategies = set()

        # 基于指标推荐
        if metrics.mean_time_to_recovery > 60:
            strategies.add(ResilienceStrategy.AUTO_RECOVERY)

        if metrics.service_availability < 99.9:
            strategies.add(ResilienceStrategy.REDUNDANCY)

        if metrics.failure_impact_score > 50:
            strategies.add(ResilienceStrategy.CIRCUIT_BREAKER)

        # 基于风险推荐
        for risk in risks:
            strategies.add(risk.mitigation_strategy)

        return list(strategies)

    def _generate_improvement_actions(self, metrics: ResilienceMetrics, risks: List[RiskEvent]) -> List[str]:
        """生成改进行动"""
        actions = []

        if metrics.mean_time_to_recovery > 30:
            actions.append("实施自动化故障检测和恢复机制")

        if metrics.service_availability < 99.5:
            actions.append("建立多区域部署和自动故障转移")

        if len(risks) > 3:
            actions.append("完善风险识别和监控体系")

        if metrics.recovery_success_rate < 95:
            actions.append("建立故障演练和恢复预案")

        actions.extend([
            "实施混沌工程实践",
            "建立应急响应团队",
            "完善监控和告警系统"
        ])

        return actions

    def _identify_resilience_gaps(self, metrics: ResilienceMetrics, risks: List[RiskEvent]) -> List[str]:
        """识别韧性差距"""
        gaps = []

        if metrics.mean_time_between_failures < 100:
            gaps.append("故障间隔时间过短，需要提升系统稳定性")

        if metrics.mean_time_to_recovery > 60:
            gaps.append("恢复时间过长，需要优化应急响应流程")

        if metrics.service_availability < 99:
            gaps.append("可用性不足，需要实施高可用架构")

        if len([r for r in risks if r.mitigation_strategy == ResilienceStrategy.MANUAL_INTERVENTION]) > 2:
            gaps.append("依赖人工干预过多，需要增加自动化程度")

        return gaps

    def simulate_failure_scenario(self, scenario_type: str) -> Dict[str, Any]:
        """模拟故障场景"""
        scenarios = {
            "network_failure": {
                "description": "网络连接中断",
                "impact_processes": ["代码提交", "CI/CD部署", "团队协作"],
                "expected_duration": 30,  # 分钟
                "recovery_strategy": ResilienceStrategy.GRACEFUL_DEGRADATION
            },
            "server_crash": {
                "description": "应用服务器崩溃",
                "impact_processes": ["生产部署", "用户访问"],
                "expected_duration": 15,
                "recovery_strategy": ResilienceStrategy.AUTO_RECOVERY
            },
            "data_corruption": {
                "description": "数据损坏",
                "impact_processes": ["数据处理", "备份恢复"],
                "expected_duration": 120,
                "recovery_strategy": ResilienceStrategy.REDUNDANCY
            },
            "security_breach": {
                "description": "安全漏洞攻击",
                "impact_processes": ["访问控制", "数据保护"],
                "expected_duration": 60,
                "recovery_strategy": ResilienceStrategy.CIRCUIT_BREAKER
            }
        }

        scenario = scenarios.get(scenario_type, scenarios["network_failure"])

        # 模拟故障影响
        impact_score = random.uniform(0.3, 0.9)
        detection_time = random.uniform(5, 30)  # 检测时间
        recovery_time = scenario["expected_duration"] * random.uniform(0.8, 1.5)

        result = {
            "scenario": scenario_type,
            "description": scenario["description"],
            "impact_score": impact_score,
            "affected_processes": scenario["impact_processes"],
            "detection_time_minutes": detection_time,
            "recovery_time_minutes": recovery_time,
            "total_downtime": detection_time + recovery_time,
            "recovery_success": random.random() > 0.1,  # 90%成功率
            "lessons_learned": self._generate_lesson_learned(scenario_type)
        }

        return result

    def _generate_lesson_learned(self, scenario_type: str) -> List[str]:
        """生成经验教训"""
        lessons = {
            "network_failure": [
                "建立网络连接的健康检查",
                "实施异步通信模式",
                "准备离线工作能力"
            ],
            "server_crash": [
                "实施容器化和自动扩缩容",
                "建立多实例冗余部署",
                "完善日志和监控体系"
            ],
            "data_corruption": [
                "加强数据备份和验证",
                "实施数据冗余存储",
                "建立数据恢复演练"
            ],
            "security_breach": [
                "实施零信任安全模型",
                "建立安全监控和响应",
                "定期进行安全评估"
            ]
        }

        return lessons.get(scenario_type, ["完善故障处理流程", "加强监控能力"])

    def run_chaos_experiment(self, experiment_config: Dict[str, Any]) -> Dict[str, Any]:
        """运行混沌实验"""
        experiment = {
            "experiment_id": f"CHAOS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now(),
            "config": experiment_config,
            "results": {},
            "status": "running"
        }

        # 模拟实验执行
        import time
        time.sleep(2)  # 模拟实验时间

        # 生成实验结果
        experiment["results"] = {
            "system_stability": random.uniform(85, 98),
            "recovery_time": random.uniform(10, 45),
            "impact_scope": random.choice(["局部", "中等", "广泛"]),
            "auto_recovery_success": random.random() > 0.2,
            "monitoring_effectiveness": random.uniform(75, 95)
        }

        experiment["end_time"] = datetime.now()
        experiment["status"] = "completed"

        return experiment


def main():
    """主函数：演示韧性管理"""
    # 创建韧性管理器
    manager = ResilienceManager()

    # 示例流程数据
    process_data = {
        "mtbf_hours": 120.0,      # 平均故障间隔5天
        "mttr_minutes": 35.0,     # 平均恢复时间35分钟
        "availability_percent": 99.7,
        "failure_impact_score": 20.0,
        "recovery_success_rate": 96.0
    }

    # 评估韧性
    assessment = manager.assess_resilience(process_data)

    # 输出评估报告
    print("=== 流程韧性评估报告 ===")
    print(".1f"
    print("\n韧性指标:")
    print(".1f"    print(".1f"    print(".1f"    print(".1f"    print(".1f"
    print("\n识别的风险事件:")
    for risk in assessment.identified_risks:
        print(f"  {risk.event_id}: {risk.description}")
        print(".2f"        print(f"    等级: {risk.risk_level.value}")
        print(f"    影响流程: {', '.join(risk.affected_processes)}")
        print(f"    缓解策略: {risk.mitigation_strategy.value}")

    print("
推荐的韧性策略:"    for strategy in assessment.recommended_strategies:
        print(f"  • {strategy.value}")

    print("
改进行动:"    for action in assessment.improvement_actions:
        print(f"  • {action}")

    print("
韧性差距:"    for gap in assessment.resilience_gaps:
        print(f"  • {gap}")

    # 模拟故障场景
    print("
=== 故障场景模拟 ===")
    failure_scenarios = ["network_failure", "server_crash", "data_corruption", "security_breach"]

    for scenario in failure_scenarios:
        result = manager.simulate_failure_scenario(scenario)
        print(f"\n场景: {scenario}")
        print(f"  描述: {result['description']}")
        print(".2f"        print(".1f"        print(f"  恢复成功: {result['recovery_success']}")
        print("  经验教训:"
        for lesson in result['lessons_learned'][:2]:  # 只显示前2个
            print(f"    • {lesson}")

    # 运行混沌实验
    print("
=== 混沌实验演示 ===")
    chaos_config = {
        "target_service": "user_authentication",
        "failure_type": "latency_injection",
        "duration_minutes": 10,
        "intensity": "medium"
    }

    experiment = manager.run_chaos_experiment(chaos_config)
    print(f"实验ID: {experiment['experiment_id']}")
    print(f"状态: {experiment['status']}")
    print("结果:"
    for key, value in experiment['results'].items():
        if isinstance(value, float):
            print(".2f"        else:
            print(f"    {key}: {value}")


if __name__ == "__main__":
    main()