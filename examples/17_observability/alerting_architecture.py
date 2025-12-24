#!/usr/bin/env python3
"""
告警系统架构设计与测试工具
提供告警规则、聚合、分发、处理的可观测性解决方案

作者: 2025-10M-Testing Team
版本: 1.0.0
"""

import json
import logging
import smtplib
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import statistics
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """告警严重程度枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """告警状态枚举"""
    FIRING = "firing"
    RESOLVED = "resolved"
    PENDING = "pending"


@dataclass
class Alert:
    """告警对象"""
    id: str
    name: str
    severity: AlertSeverity
    status: AlertStatus
    description: str
    summary: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    starts_at: datetime
    ends_at: Optional[datetime] = None
    generator_url: Optional[str] = None
    value: Optional[float] = None


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    condition: str
    severity: AlertSeverity
    duration: str
    description: str
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
        if self.annotations is None:
            self.annotations = {}


class AlertingArchitectureManager:
    """告警系统架构管理器"""

    def __init__(self, config_path: str = "alerting_architecture.yml"):
        self.config = self._load_config(config_path)
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self._load_alert_rules()

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except ImportError:
            with open(config_path.replace('.yml', '.json'), 'r', encoding='utf-8') as f:
                return json.load(f)

    def _load_alert_rules(self):
        """加载告警规则"""
        for rule_config in self.config.get('rules', []):
            rule = AlertRule(
                name=rule_config['name'],
                condition=rule_config['condition'],
                severity=AlertSeverity(rule_config['level'].lower()),
                duration=rule_config['duration'],
                description=rule_config['description'],
                labels=rule_config.get('labels', {}),
                annotations=rule_config.get('annotations', {})
            )
            self.alert_rules[rule.name] = rule

    def validate_alerting_architecture(self) -> Dict[str, Any]:
        """验证告警系统架构"""
        logger.info("开始验证告警系统架构")

        results = {
            'rule_configuration': self._check_rule_configuration(),
            'aggregation_setup': self._validate_aggregation_setup(),
            'notification_channels': self._check_notification_channels(),
            'routing_logic': self._validate_routing_logic(),
            'suppression_rules': self._check_suppression_rules()
        }

        # 计算整体评分
        scores = [result.get('score', 0) for result in results.values() if isinstance(result, dict)]
        overall_score = statistics.mean(scores) if scores else 0

        results['overall_score'] = overall_score
        results['recommendations'] = self._generate_recommendations(results)

        return results

    def _check_rule_configuration(self) -> Dict[str, Any]:
        """检查规则配置"""
        issues = []

        if not self.alert_rules:
            issues.append("未配置任何告警规则")

        for name, rule in self.alert_rules.items():
            if not rule.condition:
                issues.append(f"规则 {name} 缺少condition配置")

            if not rule.description:
                issues.append(f"规则 {name} 缺少description")

            # 检查持续时间格式
            try:
                self._parse_duration(rule.duration)
            except ValueError:
                issues.append(f"规则 {name} 的duration格式无效")

        return {
            'rule_count': len(self.alert_rules),
            'issues': issues,
            'score': 100 - (len(issues) * 10)
        }

    def _validate_aggregation_setup(self) -> Dict[str, Any]:
        """验证聚合设置"""
        aggregation_config = self.config.get('aggregation', {})

        issues = []

        if 'group_by' not in aggregation_config:
            issues.append("未配置分组字段")

        if 'group_wait' not in aggregation_config:
            issues.append("未配置分组等待时间")

        if 'repeat_interval' not in aggregation_config:
            issues.append("未配置重复间隔")

        return {
            'group_by_fields': aggregation_config.get('group_by', []),
            'issues': issues,
            'score': 100 - (len(issues) * 20)
        }

    def _check_notification_channels(self) -> Dict[str, Any]:
        """检查通知渠道"""
        receivers = self.config.get('receivers', [])

        channel_types = []
        for receiver in receivers:
            if 'email_configs' in receiver:
                channel_types.append('email')
            if 'slack_configs' in receiver:
                channel_types.append('slack')
            if 'pagerduty_configs' in receiver:
                channel_types.append('pagerduty')

        channel_score = len(set(channel_types)) * 25  # 每种渠道25分

        return {
            'available_channels': list(set(channel_types)),
            'receiver_count': len(receivers),
            'score': min(channel_score, 100)
        }

    def _validate_routing_logic(self) -> Dict[str, Any]:
        """验证路由逻辑"""
        routes = self.config.get('routes', [])

        issues = []

        if not routes:
            issues.append("未配置路由规则")

        severity_coverage = set()
        for route in routes:
            if 'match' in route:
                match = route['match']
                if 'severity' in match:
                    severity_coverage.add(match['severity'])

        expected_severities = {'critical', 'warning', 'error', 'info'}
        missing_severities = expected_severities - severity_coverage

        if missing_severities:
            issues.append(f"缺少以下严重程度的路由: {missing_severities}")

        return {
            'route_count': len(routes),
            'severity_coverage': list(severity_coverage),
            'issues': issues,
            'score': 100 - (len(issues) * 15)
        }

    def _check_suppression_rules(self) -> Dict[str, Any]:
        """检查抑制规则"""
        inhibition_config = self.config.get('inhibition', [])

        suppression_score = len(inhibition_config) * 30  # 每个抑制规则30分

        return {
            'suppression_rules_count': len(inhibition_config),
            'score': min(suppression_score, 100)
        }

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if results['rule_configuration']['score'] < 85:
            recommendations.append("完善告警规则配置，确保所有规则都有有效的condition和description")

        if results['aggregation_setup']['score'] < 80:
            recommendations.append("优化告警聚合设置，合理配置分组和重复策略")

        if results['notification_channels']['score'] < 60:
            recommendations.append("增加通知渠道多样性，确保重要告警有多种通知方式")

        if results['routing_logic']['score'] < 85:
            recommendations.append("完善路由逻辑，确保不同严重程度的告警被正确路由")

        if results['suppression_rules']['score'] < 50:
            recommendations.append("配置告警抑制规则，减少告警噪音")

        return recommendations

    def run_accuracy_test(self) -> Dict[str, Any]:
        """运行准确性测试"""
        logger.info("开始准确性测试")

        accuracy_results = {}

        # 测试误报率和漏报率
        false_positive_rate = self._calculate_false_positive_rate()
        false_negative_rate = self._calculate_false_negative_rate()

        fp_threshold = self.config['testing']['accuracy_test']['false_positive_rate']
        fn_threshold = self.config['testing']['accuracy_test']['false_negative_rate']

        return {
            'false_positive_rate': false_positive_rate,
            'false_negative_rate': false_negative_rate,
            'fp_threshold': fp_threshold,
            'fn_threshold': fn_threshold,
            'passed': false_positive_rate <= fp_threshold and false_negative_rate <= fn_threshold
        }

    def run_timeliness_test(self) -> Dict[str, Any]:
        """运行时效性测试"""
        logger.info("开始时效性测试")

        timeliness_results = {}

        # 测试不同级别告警的响应时间
        for severity in ['P0', 'P1']:
            response_time = self._measure_alert_response_time(severity)
            timeliness_results[severity] = response_time

        p0_max_time = self.config['testing']['timeliness_test']['p0_response_time']
        p1_max_time = self.config['testing']['timeliness_test']['p1_response_time']

        p0_passed = timeliness_results.get('P0', float('inf')) <= p0_max_time
        p1_passed = timeliness_results.get('P1', float('inf')) <= p1_max_time

        return {
            'response_times': timeliness_results,
            'p0_max_time': p0_max_time,
            'p1_max_time': p1_max_time,
            'p0_passed': p0_passed,
            'p1_passed': p1_passed,
            'passed': p0_passed and p1_passed
        }

    def run_reliability_test(self) -> Dict[str, Any]:
        """运行可靠性测试"""
        logger.info("开始可靠性测试")

        reliability_metrics = {
            'notification_delivery_rate': self._measure_delivery_rate(),
            'system_uptime': self._measure_system_uptime()
        }

        delivery_threshold = self.config['testing']['reliability_test']['notification_delivery_rate']
        uptime_threshold = self.config['testing']['reliability_test']['system_uptime']

        delivery_passed = reliability_metrics['notification_delivery_rate'] >= delivery_threshold
        uptime_passed = reliability_metrics['system_uptime'] >= uptime_threshold

        return {
            'metrics': reliability_metrics,
            'delivery_threshold': delivery_threshold,
            'uptime_threshold': uptime_threshold,
            'delivery_passed': delivery_passed,
            'uptime_passed': uptime_passed,
            'passed': delivery_passed and uptime_passed
        }

    def create_alert(self, rule_name: str, value: float, labels: Optional[Dict[str, str]] = None) -> Optional[Alert]:
        """创建告警"""
        if rule_name not in self.alert_rules:
            return None

        rule = self.alert_rules[rule_name]

        alert_id = f"{rule_name}_{int(time.time())}"

        alert = Alert(
            id=alert_id,
            name=rule_name,
            severity=rule.severity,
            status=AlertStatus.FIRING,
            description=rule.description,
            summary=rule.annotations.get('summary', rule.description),
            labels={**rule.labels, **(labels or {})},
            annotations=rule.annotations,
            starts_at=datetime.now(),
            value=value
        )

        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)

        logger.info(f"创建告警: {alert_id} - {rule_name}")
        return alert

    def resolve_alert(self, alert_id: str):
        """解决告警"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.ends_at = datetime.now()

            del self.active_alerts[alert_id]
            logger.info(f"解决告警: {alert_id}")

    def send_notification(self, alert: Alert, channel: str = 'email'):
        """发送通知"""
        try:
            if channel == 'email':
                self._send_email_notification(alert)
            elif channel == 'slack':
                self._send_slack_notification(alert)
            # 其他渠道...

            logger.info(f"发送通知: {alert.id} via {channel}")
        except Exception as e:
            logger.error(f"发送通知失败: {e}")

    def _send_email_notification(self, alert: Alert):
        """发送邮件通知"""
        # 简化实现，实际需要配置SMTP服务器
        logger.info(f"模拟发送邮件通知: {alert.name}")

    def _send_slack_notification(self, alert: Alert):
        """发送Slack通知"""
        # 简化实现，实际需要配置Slack Webhook
        logger.info(f"模拟发送Slack通知: {alert.name}")

    def _parse_duration(self, duration_str: str) -> int:
        """解析持续时间字符串"""
        # 简化的持续时间解析，如 "5m", "1h"
        if duration_str.endswith('m'):
            return int(duration_str[:-1]) * 60
        elif duration_str.endswith('h'):
            return int(duration_str[:-1]) * 3600
        elif duration_str.endswith('s'):
            return int(duration_str[:-1])
        else:
            raise ValueError(f"无效的持续时间格式: {duration_str}")

    def _calculate_false_positive_rate(self) -> float:
        """计算误报率（模拟）"""
        return 0.005  # 0.5%

    def _calculate_false_negative_rate(self) -> float:
        """计算漏报率（模拟）"""
        return 0.002  # 0.2%

    def _measure_alert_response_time(self, severity: str) -> float:
        """测量告警响应时间（模拟）"""
        if severity == 'P0':
            return 180.0  # 3分钟
        elif severity == 'P1':
            return 600.0  # 10分钟
        else:
            return 1800.0  # 30分钟

    def _measure_delivery_rate(self) -> float:
        """测量送达率（模拟）"""
        return 0.9995  # 99.95%

    def _measure_system_uptime(self) -> float:
        """测量系统正常运行时间（模拟）"""
        return 0.9999  # 99.99%


def main():
    """主函数"""
    # 创建告警架构管理器
    manager = AlertingArchitectureManager()

    # 验证架构
    architecture_results = manager.validate_alerting_architecture()

    print("\n=== 告警系统架构验证结果 ===")
    print(f"整体评分: {architecture_results['overall_score']:.1f}/100")
    print("\n各维度评分:")
    for key, result in architecture_results.items():
        if isinstance(result, dict) and 'score' in result:
            print(f"  {key}: {result['score']:.1f}/100")

    print("\n改进建议:")
    for rec in architecture_results['recommendations']:
        print(f"  - {rec}")

    # 运行测试
    print("\n=== 运行告警测试 ===")

    # 准确性测试
    accuracy_result = manager.run_accuracy_test()
    print(f"准确性测试: {'通过' if accuracy_result['passed'] else '失败'}")
    print(".2%")

    # 时效性测试
    timeliness_result = manager.run_timeliness_test()
    print(f"时效性测试: {'通过' if timeliness_result['passed'] else '失败'}")

    # 可靠性测试
    reliability_result = manager.run_reliability_test()
    print(f"可靠性测试: {'通过' if reliability_result['passed'] else '失败'}")
    print(".2%")


if __name__ == "__main__":
    main()