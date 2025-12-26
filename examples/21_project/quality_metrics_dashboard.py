#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量度量仪表板 - Quality Metrics Dashboard
大数据测试项目的质量监控和持续改进系统

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
import statistics

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """度量类型枚举"""
    COVERAGE = "覆盖率"
    DEFECT_DENSITY = "缺陷密度"
    RESPONSE_TIME = "响应时间"
    AVAILABILITY = "可用性"
    THROUGHPUT = "吞吐量"
    ERROR_RATE = "错误率"
    TEST_EXECUTION_TIME = "测试执行时间"
    AUTOMATION_RATE = "自动化率"


class MetricStatus(Enum):
    """度量状态枚举"""
    HEALTHY = "健康"
    WARNING = "警告"
    CRITICAL = "严重"
    UNKNOWN = "未知"


@dataclass
class QualityMetric:
    """质量度量类"""
    id: str
    name: str
    type: MetricType
    description: str
    unit: str
    target_value: float
    warning_threshold: float
    critical_threshold: float
    current_value: float = 0.0
    status: MetricStatus = MetricStatus.UNKNOWN
    trend: str = "stable"  # increasing, decreasing, stable
    data_points: List[Dict] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

    def update_value(self, new_value: float, timestamp: datetime = None):
        """更新度量值"""
        if timestamp is None:
            timestamp = datetime.now()

        # 添加数据点
        self.data_points.append({
            "value": new_value,
            "timestamp": timestamp.isoformat()
        })

        # 保持最近30个数据点
        if len(self.data_points) > 30:
            self.data_points = self.data_points[-30:]

        # 更新当前值和状态
        old_value = self.current_value
        self.current_value = new_value
        self.status = self._calculate_status()
        self.trend = self._calculate_trend(old_value)
        self.last_updated = timestamp

    def _calculate_status(self) -> MetricStatus:
        """计算度量状态"""
        if self.type in [MetricType.COVERAGE, MetricType.AVAILABILITY, MetricType.AUTOMATION_RATE]:
            # 越高越好
            if self.current_value >= self.target_value:
                return MetricStatus.HEALTHY
            elif self.current_value >= self.warning_threshold:
                return MetricStatus.WARNING
            else:
                return MetricStatus.CRITICAL
        else:
            # 越低越好
            if self.current_value <= self.target_value:
                return MetricStatus.HEALTHY
            elif self.current_value <= self.warning_threshold:
                return MetricStatus.WARNING
            else:
                return MetricStatus.CRITICAL

    def _calculate_trend(self, old_value: float) -> str:
        """计算趋势"""
        if len(self.data_points) < 2:
            return "stable"

        recent_values = [dp["value"] for dp in self.data_points[-5:]]
        if len(recent_values) < 2:
            return "stable"

        # 计算线性趋势
        try:
            slope = statistics.linear_regression(range(len(recent_values)), recent_values)[0]
            if abs(slope) < 0.01:  # 阈值
                return "stable"
            elif slope > 0:
                return "increasing" if self._is_positive_good() else "worsening"
            else:
                return "decreasing" if self._is_positive_good() else "improving"
        except:
            return "stable"

    def _is_positive_good(self) -> bool:
        """判断正向变化是否良好"""
        return self.type in [MetricType.COVERAGE, MetricType.AVAILABILITY, MetricType.AUTOMATION_RATE]

    def get_summary(self) -> Dict[str, Any]:
        """获取度量摘要"""
        return {
            "id": self.id,
            "name": self.name,
            "current_value": self.current_value,
            "target_value": self.target_value,
            "status": self.status.value,
            "trend": self.trend,
            "last_updated": self.last_updated.isoformat(),
            "data_points_count": len(self.data_points)
        }


@dataclass
class QualityDashboard:
    """质量仪表板类"""
    name: str
    description: str
    metrics: Dict[str, QualityMetric] = field(default_factory=dict)
    alerts: List[Dict] = field(default_factory=list)
    reports: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_metric(self, metric: QualityMetric):
        """添加度量"""
        self.metrics[metric.id] = metric
        self.updated_at = datetime.now()
        logger.info(f"添加质量度量: {metric.name}")

    def update_metric(self, metric_id: str, value: float):
        """更新度量值"""
        if metric_id in self.metrics:
            self.metrics[metric_id].update_value(value)
            self._check_alerts(metric_id)
            self.updated_at = datetime.now()

    def _check_alerts(self, metric_id: str):
        """检查告警"""
        metric = self.metrics[metric_id]
        if metric.status in [MetricStatus.WARNING, MetricStatus.CRITICAL]:
            alert = {
                "metric_id": metric_id,
                "metric_name": metric.name,
                "status": metric.status.value,
                "current_value": metric.current_value,
                "target_value": metric.target_value,
                "timestamp": datetime.now().isoformat(),
                "message": self._generate_alert_message(metric)
            }
            self.alerts.append(alert)
            logger.warning(f"质量告警: {alert['message']}")

    def _generate_alert_message(self, metric: QualityMetric) -> str:
        """生成告警消息"""
        if metric.status == MetricStatus.CRITICAL:
            return f"严重告警: {metric.name} 当前值 {metric.current_value}{metric.unit}, 远低于目标 {metric.target_value}{metric.unit}"
        else:
            return f"警告: {metric.name} 当前值 {metric.current_value}{metric.unit}, 接近阈值 {metric.warning_threshold}{metric.unit}"

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """获取仪表板摘要"""
        total_metrics = len(self.metrics)
        healthy_count = len([m for m in self.metrics.values() if m.status == MetricStatus.HEALTHY])
        warning_count = len([m for m in self.metrics.values() if m.status == MetricStatus.WARNING])
        critical_count = len([m for m in self.metrics.values() if m.status == MetricStatus.CRITICAL])

        return {
            "name": self.name,
            "total_metrics": total_metrics,
            "healthy_metrics": healthy_count,
            "warning_metrics": warning_count,
            "critical_metrics": critical_count,
            "overall_health": self._calculate_overall_health(healthy_count, warning_count, critical_count),
            "last_updated": self.updated_at.isoformat(),
            "active_alerts": len([a for a in self.alerts if not a.get("resolved", False)])
        }

    def _calculate_overall_health(self, healthy: int, warning: int, critical: int) -> str:
        """计算整体健康状态"""
        total = healthy + warning + critical
        if total == 0:
            return "unknown"

        health_score = (healthy * 1.0 + warning * 0.5 + critical * 0.0) / total

        if health_score >= 0.8:
            return "excellent"
        elif health_score >= 0.6:
            return "good"
        elif health_score >= 0.4:
            return "fair"
        else:
            return "poor"

    def generate_quality_report(self, period_days: int = 7) -> str:
        """生成质量报告"""
        summary = self.get_dashboard_summary()
        recent_alerts = [a for a in self.alerts
                        if (datetime.now() - datetime.fromisoformat(a["timestamp"])).days <= period_days]

        report = f"""
# 质量度量报告 - {self.name}
报告周期: 最近{period_days}天
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 整体健康状态
- 总度量数: {summary['total_metrics']}
- 健康度量: {summary['healthy_metrics']}
- 警告度量: {summary['warning_metrics']}
- 严重度量: {summary['critical_metrics']}
- 整体健康度: {summary['overall_health'].upper()}
- 活跃告警: {summary['active_alerts']}

## 度量详情
{self._format_metrics_details()}

## 近期告警
{self._format_recent_alerts(recent_alerts)}

## 改进建议
{self._generate_improvement_suggestions()}
        """
        return report

    def _format_metrics_details(self) -> str:
        """格式化度量详情"""
        lines = []
        for metric in self.metrics.values():
            summary = metric.get_summary()
            status_icon = "✅" if summary["status"] == "健康" else "⚠️" if summary["status"] == "警告" else "❌"
            trend_icon = "📈" if summary["trend"] == "increasing" else "📉" if summary["trend"] == "decreasing" else "➡️"

            lines.append(f"- {status_icon}{trend_icon} {summary['name']}: {summary['current_value']:.2f}{metric.unit} "
                        f"(目标: {summary['target_value']:.2f}, 状态: {summary['status']})")

        return "\n".join(lines) if lines else "- 无度量数据"

    def _format_recent_alerts(self, alerts: List[Dict]) -> str:
        """格式化近期告警"""
        if not alerts:
            return "- 无近期告警"

        lines = []
        for alert in alerts[-10:]:  # 显示最近10个告警
            lines.append(f"- {alert['timestamp'][:10]}: {alert['message']}")

        return "\n".join(lines)

    def _generate_improvement_suggestions(self) -> str:
        """生成改进建议"""
        suggestions = []

        # 分析严重度量
        critical_metrics = [m for m in self.metrics.values() if m.status == MetricStatus.CRITICAL]
        if critical_metrics:
            suggestions.append(f"- 优先解决 {len(critical_metrics)} 个严重问题:")
            for metric in critical_metrics:
                suggestions.append(f"  - {metric.name}: 当前值 {metric.current_value:.2f}{metric.unit}, 需要达到 {metric.target_value:.2f}{metric.unit}")

        # 分析趋势恶化的度量
        worsening_metrics = [m for m in self.metrics.values() if m.trend in ["worsening", "decreasing"] and m._is_positive_good() == False]
        if worsening_metrics:
            suggestions.append(f"- 关注趋势恶化的 {len(worsening_metrics)} 个度量，采取纠正措施")

        # 一般建议
        if not suggestions:
            suggestions.append("- 继续保持当前质量水平，定期review度量目标")
            suggestions.append("- 考虑提升自动化测试覆盖率和执行效率")

        return "\n".join(suggestions)

    def export_configuration(self) -> Dict[str, Any]:
        """导出配置"""
        return {
            "name": self.name,
            "description": self.description,
            "metrics": [vars(metric) for metric in self.metrics.values()],
            "alerts": self.alerts,
            "reports": self.reports,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


def create_sample_dashboard() -> QualityDashboard:
    """创建示例质量仪表板"""
    dashboard = QualityDashboard(
        name="大数据测试质量仪表板",
        description="电商大数据测试项目的质量监控和度量系统"
    )

    # 定义质量度量
    metrics_data = [
        {
            "id": "coverage_unit",
            "name": "单元测试覆盖率",
            "type": MetricType.COVERAGE,
            "description": "代码单元测试覆盖率",
            "unit": "%",
            "target_value": 85.0,
            "warning_threshold": 75.0,
            "critical_threshold": 65.0,
            "current_value": 82.5
        },
        {
            "id": "defect_density",
            "name": "缺陷密度",
            "type": MetricType.DEFECT_DENSITY,
            "description": "每千行代码缺陷数",
            "unit": "个/KLOC",
            "target_value": 2.0,
            "warning_threshold": 3.0,
            "critical_threshold": 5.0,
            "current_value": 2.8
        },
        {
            "id": "response_time",
            "name": "API响应时间",
            "type": MetricType.RESPONSE_TIME,
            "description": "API接口平均响应时间",
            "unit": "ms",
            "target_value": 200.0,
            "warning_threshold": 500.0,
            "critical_threshold": 1000.0,
            "current_value": 180.0
        },
        {
            "id": "availability",
            "name": "系统可用性",
            "type": MetricType.AVAILABILITY,
            "description": "系统可用性百分比",
            "unit": "%",
            "target_value": 99.9,
            "warning_threshold": 99.5,
            "critical_threshold": 99.0,
            "current_value": 99.8
        },
        {
            "id": "automation_rate",
            "name": "测试自动化率",
            "type": MetricType.AUTOMATION_RATE,
            "description": "自动化测试用例占比",
            "unit": "%",
            "target_value": 70.0,
            "warning_threshold": 50.0,
            "critical_threshold": 30.0,
            "current_value": 65.0
        }
    ]

    for metric_data in metrics_data:
        metric = QualityMetric(**metric_data)
        dashboard.add_metric(metric)

        # 添加一些历史数据点
        import random
        base_value = metric_data["current_value"]
        for i in range(10):
            variation = random.uniform(-0.05, 0.05)  # ±5% 变化
            historical_value = base_value * (1 + variation)
            timestamp = datetime.now() - timedelta(days=9-i)
            metric.update_value(historical_value, timestamp)

    return dashboard


if __name__ == "__main__":
    # 创建示例质量仪表板
    dashboard = create_sample_dashboard()

    # 更新一些度量值
    dashboard.update_metric("coverage_unit", 87.3)
    dashboard.update_metric("defect_density", 2.1)

    # 生成质量报告
    report = dashboard.generate_quality_report()
    print(report)

    # 获取仪表板摘要
    summary = dashboard.get_dashboard_summary()
    print(f"\n仪表板摘要: {summary['overall_health'].upper()} ({summary['healthy_metrics']}/{summary['total_metrics']} 健康)")

    # 导出配置
    config = dashboard.export_configuration()
    with open("quality_metrics_dashboard_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("\n质量度量仪表板配置已导出到 quality_metrics_dashboard_config.json")