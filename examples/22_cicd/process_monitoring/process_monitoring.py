"""
监控与持续改进 (Process Monitoring and Continuous Improvement)

此脚本用于监控软件开发流程的性能指标，实现持续改进循环。
基于指标监控和趋势分析，提供流程优化建议和改进跟踪。
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics
import json
from datetime import datetime, timedelta
from collections import defaultdict


class MetricType(Enum):
    CYCLE_TIME = "cycle_time"          # 周期时间
    THROUGHPUT = "throughput"          # 吞吐量
    QUALITY = "quality"               # 质量指标
    EFFICIENCY = "efficiency"          # 效率指标
    SATISFACTION = "satisfaction"      # 满意度


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class MetricData:
    """指标数据"""
    timestamp: datetime
    value: float
    metric_type: MetricType
    context: Dict[str, Any]


@dataclass
class ProcessAlert:
    """流程告警"""
    level: AlertLevel
    metric_type: MetricType
    message: str
    threshold: float
    current_value: float
    timestamp: datetime
    recommendations: List[str]


@dataclass
class ImprovementAction:
    """改进行动"""
    action_id: str
    description: str
    metric_target: MetricType
    expected_improvement: float
    status: str  # planned, in_progress, completed, cancelled
    start_date: Optional[datetime]
    completion_date: Optional[datetime]
    actual_improvement: Optional[float]


@dataclass
class MonitoringDashboard:
    """监控仪表板"""
    current_metrics: Dict[MetricType, float]
    trend_analysis: Dict[MetricType, Dict[str, float]]
    alerts: List[ProcessAlert]
    improvement_actions: List[ImprovementAction]
    overall_health_score: float
    recommendations: List[str]


class ProcessMonitor:
    """流程监控器"""

    def __init__(self):
        self.metric_history: Dict[MetricType, List[MetricData]] = defaultdict(list)
        self.alert_thresholds = {
            MetricType.CYCLE_TIME: {"warning": 14.0, "critical": 21.0},  # 天
            MetricType.THROUGHPUT: {"warning": 15.0, "critical": 10.0},  # 故事点/周
            MetricType.QUALITY: {"warning": 90.0, "critical": 80.0},    # 成功率%
            MetricType.EFFICIENCY: {"warning": 70.0, "critical": 50.0}, # 效率%
            MetricType.SATISFACTION: {"warning": 75.0, "critical": 60.0} # 满意度%
        }
        self.improvement_actions: List[ImprovementAction] = []

    def record_metric(self, metric_type: MetricType, value: float, context: Optional[Dict[str, Any]] = None):
        """记录指标数据"""
        data = MetricData(
            timestamp=datetime.now(),
            value=value,
            metric_type=metric_type,
            context=context or {}
        )
        self.metric_history[metric_type].append(data)

    def get_current_metrics(self) -> Dict[MetricType, float]:
        """获取当前指标值"""
        current = {}
        for metric_type in MetricType:
            history = self.metric_history[metric_type]
            if history:
                # 获取最近7天的平均值作为当前值
                recent_data = [d for d in history if d.timestamp > datetime.now() - timedelta(days=7)]
                if recent_data:
                    current[metric_type] = statistics.mean(d.value for d in recent_data)
                else:
                    current[metric_type] = history[-1].value
        return current

    def analyze_trends(self, days: int = 30) -> Dict[MetricType, Dict[str, float]]:
        """分析指标趋势"""
        trends = {}
        cutoff_date = datetime.now() - timedelta(days=days)

        for metric_type in MetricType:
            history = [d for d in self.metric_history[metric_type] if d.timestamp > cutoff_date]
            if len(history) < 2:
                continue

            values = [d.value for d in history]
            trend_data = {
                "current": values[-1],
                "average": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "volatility": statistics.stdev(values) if len(values) > 1 else 0,
                "trend_direction": self._calculate_trend_direction(values),
                "change_percentage": self._calculate_change_percentage(values)
            }
            trends[metric_type] = trend_data

        return trends

    def _calculate_trend_direction(self, values: List[float]) -> str:
        """计算趋势方向"""
        if len(values) < 3:
            return "insufficient_data"

        # 使用简单线性回归计算趋势
        n = len(values)
        x = list(range(n))
        slope = statistics.linear_regression(x, values)[0]

        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "declining"
        else:
            return "stable"

    def _calculate_change_percentage(self, values: List[float]) -> float:
        """计算变化百分比"""
        if len(values) < 2:
            return 0.0

        recent_avg = statistics.mean(values[-7:]) if len(values) >= 7 else values[-1]
        older_avg = statistics.mean(values[:-7]) if len(values) > 7 else values[0]

        if older_avg == 0:
            return 0.0

        return ((recent_avg - older_avg) / older_avg) * 100

    def check_alerts(self) -> List[ProcessAlert]:
        """检查告警"""
        alerts = []
        current_metrics = self.get_current_metrics()

        for metric_type, value in current_metrics.items():
            thresholds = self.alert_thresholds.get(metric_type, {})

            if value <= thresholds.get("critical", float('-inf')):
                level = AlertLevel.CRITICAL
            elif value <= thresholds.get("warning", float('-inf')):
                level = AlertLevel.WARNING
            else:
                continue  # 正常，无需告警

            alert = ProcessAlert(
                level=level,
                metric_type=metric_type,
                message=self._generate_alert_message(metric_type, level, value),
                threshold=thresholds.get(level.value, 0),
                current_value=value,
                timestamp=datetime.now(),
                recommendations=self._generate_alert_recommendations(metric_type, level)
            )
            alerts.append(alert)

        return alerts

    def _generate_alert_message(self, metric_type: MetricType, level: AlertLevel, value: float) -> str:
        """生成告警消息"""
        metric_names = {
            MetricType.CYCLE_TIME: "周期时间",
            MetricType.THROUGHPUT: "吞吐量",
            MetricType.QUALITY: "质量指标",
            MetricType.EFFICIENCY: "效率指标",
            MetricType.SATISFACTION: "满意度"
        }

        level_names = {
            AlertLevel.WARNING: "警告",
            AlertLevel.CRITICAL: "严重"
        }

        return f"{level_names[level]}: {metric_names[metric_type]}为{value:.2f}，超出阈值"

    def _generate_alert_recommendations(self, metric_type: MetricType, level: AlertLevel) -> List[str]:
        """生成告警建议"""
        recommendations = {
            MetricType.CYCLE_TIME: [
                "优化需求管理流程",
                "减少不必要的审批环节",
                "实施并行开发模式"
            ],
            MetricType.THROUGHPUT: [
                "增加团队资源配置",
                "优化任务分配策略",
                "减少上下文切换"
            ],
            MetricType.QUALITY: [
                "加强自动化测试",
                "实施代码审查制度",
                "完善质量门控"
            ],
            MetricType.EFFICIENCY: [
                "识别和消除瓶颈",
                "优化工具和流程",
                "提供技能培训"
            ],
            MetricType.SATISFACTION: [
                "改善沟通机制",
                "关注团队福祉",
                "收集反馈并改进"
            ]
        }

        return recommendations.get(metric_type, ["进行深入分析以确定根本原因"])

    def add_improvement_action(self, description: str, metric_target: MetricType, expected_improvement: float) -> str:
        """添加改进行动"""
        action_id = f"IMP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        action = ImprovementAction(
            action_id=action_id,
            description=description,
            metric_target=metric_target,
            expected_improvement=expected_improvement,
            status="planned",
            start_date=None,
            completion_date=None,
            actual_improvement=None
        )

        self.improvement_actions.append(action)
        return action_id

    def update_improvement_action(self, action_id: str, status: str, actual_improvement: Optional[float] = None):
        """更新改进行动状态"""
        for action in self.improvement_actions:
            if action.action_id == action_id:
                action.status = status
                if actual_improvement is not None:
                    action.actual_improvement = actual_improvement
                if status == "in_progress" and not action.start_date:
                    action.start_date = datetime.now()
                elif status in ["completed", "cancelled"] and not action.completion_date:
                    action.completion_date = datetime.now()
                break

    def generate_dashboard(self) -> MonitoringDashboard:
        """生成监控仪表板"""
        current_metrics = self.get_current_metrics()
        trend_analysis = self.analyze_trends()
        alerts = self.check_alerts()

        # 计算整体健康得分
        health_score = self._calculate_health_score(current_metrics, trend_analysis)

        # 生成建议
        recommendations = self._generate_dashboard_recommendations(current_metrics, trend_analysis, alerts)

        return MonitoringDashboard(
            current_metrics=current_metrics,
            trend_analysis=trend_analysis,
            alerts=alerts,
            improvement_actions=self.improvement_actions,
            overall_health_score=health_score,
            recommendations=recommendations
        )

    def _calculate_health_score(self, current_metrics: Dict[MetricType, float], trends: Dict[MetricType, Dict[str, float]]) -> float:
        """计算整体健康得分"""
        if not current_metrics:
            return 50.0  # 默认中等

        scores = []

        for metric_type, value in current_metrics.items():
            thresholds = self.alert_thresholds.get(metric_type, {})
            max_threshold = max(thresholds.values()) if thresholds else 100

            # 对于越低越好的指标（如周期时间），得分计算不同
            if metric_type in [MetricType.CYCLE_TIME]:
                score = max(0, 100 - (value / max_threshold) * 100)
            else:
                score = min(100, (value / max_threshold) * 100)

            scores.append(score)

            # 趋势加成
            trend = trends.get(metric_type, {})
            if trend.get("trend_direction") == "improving":
                score += 10
            elif trend.get("trend_direction") == "declining":
                score -= 10

            scores.append(min(100, max(0, score)))

        return statistics.mean(scores) if scores else 50.0

    def _generate_dashboard_recommendations(self, current_metrics: Dict[MetricType, float],
                                          trends: Dict[MetricType, Dict[str, float]],
                                          alerts: List[ProcessAlert]) -> List[str]:
        """生成仪表板建议"""
        recommendations = []

        # 基于告警的建议
        if alerts:
            critical_count = len([a for a in alerts if a.level == AlertLevel.CRITICAL])
            if critical_count > 0:
                recommendations.append(f"优先处理 {critical_count} 个严重告警")

        # 基于趋势的建议
        declining_metrics = [mt for mt, trend in trends.items() if trend.get("trend_direction") == "declining"]
        if declining_metrics:
            metric_names = [mt.value for mt in declining_metrics]
            recommendations.append(f"关注下降趋势指标: {', '.join(metric_names)}")

        # 基于当前值的建议
        low_metrics = []
        for metric_type, value in current_metrics.items():
            thresholds = self.alert_thresholds.get(metric_type, {})
            if value <= thresholds.get("warning", float('inf')):
                low_metrics.append(metric_type.value)

        if low_metrics:
            recommendations.append(f"改进表现不佳的指标: {', '.join(low_metrics)}")

        # 改进行动建议
        active_actions = [a for a in self.improvement_actions if a.status == "in_progress"]
        if len(active_actions) < 3:
            recommendations.append("考虑启动更多改进行动以提升整体表现")

        return recommendations or ["继续监控各项指标，保持当前良好表现"]


def main():
    """主函数：演示流程监控"""
    # 创建监控器
    monitor = ProcessMonitor()

    # 模拟记录一些指标数据
    import random

    # 生成30天的模拟数据
    base_date = datetime.now() - timedelta(days=30)
    for i in range(30):
        date = base_date + timedelta(days=i)

        # 模拟指标数据（添加一些趋势和波动）
        cycle_time = 14 + random.uniform(-3, 3) - i * 0.1  # 逐渐改善
        throughput = 18 + random.uniform(-2, 2) + i * 0.05  # 逐渐提升
        quality = 88 + random.uniform(-5, 5) + i * 0.1      # 逐渐改善
        efficiency = 75 + random.uniform(-8, 8)             # 相对稳定
        satisfaction = 80 + random.uniform(-10, 10)         # 有波动

        # 记录指标（模拟过去数据）
        monitor.metric_history[MetricType.CYCLE_TIME].append(
            MetricData(date, cycle_time, MetricType.CYCLE_TIME, {}))
        monitor.metric_history[MetricType.THROUGHPUT].append(
            MetricData(date, throughput, MetricType.THROUGHPUT, {}))
        monitor.metric_history[MetricType.QUALITY].append(
            MetricData(date, quality, MetricType.QUALITY, {}))
        monitor.metric_history[MetricType.EFFICIENCY].append(
            MetricData(date, efficiency, MetricType.EFFICIENCY, {}))
        monitor.metric_history[MetricType.SATISFACTION].append(
            MetricData(date, satisfaction, MetricType.SATISFACTION, {}))

    # 添加一些改进行动
    action1_id = monitor.add_improvement_action(
        "优化代码审查流程以减少周期时间",
        MetricType.CYCLE_TIME,
        15.0
    )
    monitor.update_improvement_action(action1_id, "completed", 12.0)

    action2_id = monitor.add_improvement_action(
        "扩展自动化测试覆盖率",
        MetricType.QUALITY,
        10.0
    )
    monitor.update_improvement_action(action2_id, "in_progress")

    # 生成仪表板
    dashboard = monitor.generate_dashboard()

    # 输出监控报告
    print("=== 流程监控仪表板 ===")
    print(".1f"
    print("\n当前指标:")
    for metric_type, value in dashboard.current_metrics.items():
        print(".2f"
    print("\n趋势分析:")
    for metric_type, trend in dashboard.trend_analysis.items():
        print(f"  {metric_type.value}:")
        print(f"    当前值: {trend['current']:.2f}")
        print(f"    平均值: {trend['average']:.2f}")
        print(f"    趋势: {trend['trend_direction']}")
        print(".2f"
    print("\n活跃告警:")
    for alert in dashboard.alerts:
        print(f"  [{alert.level.value.upper()}] {alert.message}")
        print(f"    当前值: {alert.current_value:.2f}, 阈值: {alert.threshold:.2f}")

    print("
改进行动:"    for action in dashboard.improvement_actions:
        status_icon = {"planned": "📋", "in_progress": "🔄", "completed": "✅", "cancelled": "❌"}
        print(f"  {status_icon.get(action.status, '❓')} {action.description}")
        print(f"    目标指标: {action.metric_target.value}")
        print(".1f"        if action.actual_improvement:
            print(".1f"
    print("\n关键建议:")
    for rec in dashboard.recommendations:
        print(f"  • {rec}")


if __name__ == "__main__":
    main()