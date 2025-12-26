# 智能告警系统设计与实现

## 概述

本文档详细介绍大数据测试系统的智能告警系统，包括告警规则引擎、告警聚合与抑制、自动化响应机制等核心组件。

## 告警规则引擎

### 规则定义结构

```python
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
import time

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    FIRING = "firing"
    RESOLVED = "resolved"
    SILENCED = "silenced"

@dataclass
class AlertRule:
    """告警规则定义"""
    id: str
    name: str
    description: str
    severity: AlertSeverity
    condition: str  # PromQL表达式或自定义条件
    duration: int   # 持续时间（秒）
    labels: Dict[str, str]
    annotations: Dict[str, str]
    enabled: bool = True
    group: str = "default"

@dataclass
class Alert:
    """告警实例"""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    metric: str
    value: float
    threshold: float
    timestamp: float
    labels: Dict[str, str]
    annotations: Dict[str, str]
    resolved_at: Optional[float] = None
    assigned_to: Optional[str] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[float] = None
```

### 规则引擎实现

```python
from prometheus_api_client import PrometheusConnect
from typing import Dict, Any, List, Callable
import logging
import time
import re

logger = logging.getLogger(__name__)

class AlertRuleEngine:
    """告警规则引擎"""

    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.prometheus = PrometheusConnect(url=prometheus_url)
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.evaluation_interval = 60  # 评估间隔（秒）

    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules[rule.id] = rule
        logger.info(f"Added alert rule: {rule.name} ({rule.id})")

    def remove_rule(self, rule_id: str):
        """移除告警规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")

    def evaluate_rules(self) -> List[Alert]:
        """评估所有规则并生成告警"""
        new_alerts = []

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            try:
                alert = self._evaluate_rule(rule)
                if alert:
                    new_alerts.append(alert)
                    self.alerts[alert.id] = alert

            except Exception as e:
                logger.error(f"Error evaluating rule {rule.id}: {e}")

        return new_alerts

    def _evaluate_rule(self, rule: AlertRule) -> Optional[Alert]:
        """评估单个规则"""
        try:
            # 执行PromQL查询
            result = self.prometheus.custom_query(query=rule.condition)

            if not result:
                return None

            # 解析查询结果
            value = float(result[0]['value'][1])
            labels = result[0]['metric']

            # 检查是否超过阈值（简化逻辑，实际需要更复杂的条件解析）
            threshold = self._extract_threshold(rule.condition)
            if threshold is None:
                return None

            is_alerting = self._check_condition(value, threshold, rule.condition)

            if is_alerting:
                # 检查是否已有活跃告警
                existing_alert = self._find_existing_alert(rule.id, labels)
                if existing_alert:
                    # 更新现有告警的时间戳
                    existing_alert.timestamp = time.time()
                    return None

                # 创建新告警
                alert_id = f"{rule.id}_{int(time.time())}_{hash(str(labels))}"

                alert = Alert(
                    id=alert_id,
                    title=rule.annotations.get('title', rule.name),
                    description=rule.annotations.get('description', rule.description),
                    severity=rule.severity,
                    status=AlertStatus.FIRING,
                    source="rule_engine",
                    metric=rule.condition,
                    value=value,
                    threshold=threshold,
                    timestamp=time.time(),
                    labels={**rule.labels, **labels},
                    annotations=rule.annotations
                )

                return alert

        except Exception as e:
            logger.error(f"Error evaluating rule {rule.id}: {e}")

        return None

    def _extract_threshold(self, condition: str) -> Optional[float]:
        """从条件中提取阈值（简化实现）"""
        # 简单的阈值提取逻辑
        match = re.search(r'[<>]=?\s*(\d+(?:\.\d+)?)', condition)
        if match:
            return float(match.group(1))
        return None

    def _check_condition(self, value: float, threshold: float, condition: str) -> bool:
        """检查条件是否满足"""
        if '>' in condition:
            return value > threshold
        elif '>=' in condition:
            return value >= threshold
        elif '<' in condition:
            return value < threshold
        elif '<=' in condition:
            return value <= threshold
        return False

    def _find_existing_alert(self, rule_id: str, labels: Dict[str, str]) -> Optional[Alert]:
        """查找现有的活跃告警"""
        for alert in self.alerts.values():
            if (alert.status == AlertStatus.FIRING and
                alert.labels.get('rule_id') == rule_id and
                alert.labels.get('instance') == labels.get('instance')):
                return alert
        return None

    def resolve_alert(self, alert_id: str):
        """解决告警"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = time.time()
            logger.info(f"Resolved alert: {alert_id}")

    def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        return [alert for alert in self.alerts.values()
                if alert.status == AlertStatus.FIRING]

    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """获取告警历史"""
        cutoff_time = time.time() - (hours * 3600)
        return [alert for alert in self.alerts.values()
                if alert.timestamp >= cutoff_time]
```

## 告警聚合与抑制

### 告警聚合策略

```python
from collections import defaultdict
import time
from typing import List, Dict, Any

class AlertAggregator:
    """告警聚合器"""

    def __init__(self):
        self.aggregation_rules = []
        self.aggregation_windows = {}  # 聚合时间窗口

    def add_aggregation_rule(self, rule: Dict[str, Any]):
        """添加聚合规则"""
        self.aggregation_rules.append(rule)

    def aggregate_alerts(self, alerts: List[Alert]) -> List[Alert]:
        """聚合告警"""
        if not alerts:
            return alerts

        aggregated = []
        grouped_alerts = self._group_alerts(alerts)

        for group_key, group_alerts in grouped_alerts.items():
            if len(group_alerts) > 1:
                # 创建聚合告警
                aggregated_alert = self._create_aggregated_alert(group_key, group_alerts)
                aggregated.append(aggregated_alert)
            else:
                # 单个告警直接保留
                aggregated.extend(group_alerts)

        return aggregated

    def _group_alerts(self, alerts: List[Alert]) -> Dict[str, List[Alert]]:
        """按规则分组告警"""
        groups = defaultdict(list)

        for alert in alerts:
            # 按告警名称和实例分组
            group_key = f"{alert.title}_{alert.labels.get('instance', 'unknown')}"
            groups[group_key].append(alert)

        return groups

    def _create_aggregated_alert(self, group_key: str, alerts: List[Alert]) -> Alert:
        """创建聚合告警"""
        # 取最高严重程度
        max_severity = max(alert.severity for alert in alerts)

        # 计算平均值
        avg_value = sum(alert.value for alert in alerts) / len(alerts)

        # 合并描述
        descriptions = [alert.description for alert in alerts]
        aggregated_description = f"Multiple alerts: {len(alerts)} occurrences. " + \
                                f"Average value: {avg_value:.2f}. " + \
                                f"Details: {'; '.join(descriptions[:3])}"

        return Alert(
            id=f"aggregated_{int(time.time())}_{hash(group_key)}",
            title=f"Aggregated: {alerts[0].title}",
            description=aggregated_description,
            severity=max_severity,
            status=AlertStatus.FIRING,
            source="aggregator",
            metric=f"aggregated_{len(alerts)}_alerts",
            value=avg_value,
            threshold=alerts[0].threshold,
            timestamp=time.time(),
            labels={"aggregated_count": str(len(alerts)), "group_key": group_key},
            annotations={"original_alerts": [alert.id for alert in alerts]}
        )
```

### 告警抑制机制

```python
class AlertInhibitor:
    """告警抑制器"""

    def __init__(self):
        self.inhibition_rules: List[Dict[str, Any]] = []

    def add_inhibition_rule(self, rule: Dict[str, Any]):
        """添加抑制规则"""
        self.inhibition_rules.append(rule)

    def inhibit_alerts(self, alerts: List[Alert]) -> List[Alert]:
        """抑制告警"""
        inhibited_alerts = []

        for alert in alerts:
            if not self._is_inhibited(alert):
                inhibited_alerts.append(alert)

        return inhibited_alerts

    def _is_inhibited(self, alert: Alert) -> bool:
        """检查告警是否被抑制"""
        for rule in self.inhibition_rules:
            if self._matches_inhibition_rule(alert, rule):
                return True
        return False

    def _matches_inhibition_rule(self, alert: Alert, rule: Dict[str, Any]) -> bool:
        """检查告警是否匹配抑制规则"""
        # 检查源告警条件
        source_matchers = rule.get('source_matchers', {})
        for label, pattern in source_matchers.items():
            if not self._matches_pattern(alert.labels.get(label, ''), pattern):
                return False

        # 检查目标告警条件
        target_matchers = rule.get('target_matchers', {})
        for label, pattern in target_matchers.items():
            if not self._matches_pattern(alert.labels.get(label, ''), pattern):
                return False

        # 检查相等条件
        equal_conditions = rule.get('equal', [])
        for label in equal_conditions:
            # 这里需要检查是否存在匹配的源告警
            # 简化实现：假设如果有更高严重程度的活跃告警，则抑制
            if alert.severity.value < rule.get('min_severity', 3):
                return True

        return False

    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """模式匹配"""
        import re
        try:
            return re.match(pattern, value) is not None
        except:
            return value == pattern
```

## 自动化响应机制

### 响应动作定义

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)

class ResponseAction(ABC):
    """响应动作基类"""

    @abstractmethod
    def execute(self, alert: Alert, context: Dict[str, Any]) -> bool:
        """执行响应动作"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """动作名称"""
        pass

class ScaleAction(ResponseAction):
    """扩缩容动作"""

    def __init__(self, k8s_client):
        self.k8s_client = k8s_client

    @property
    def name(self) -> str:
        return "scale"

    def execute(self, alert: Alert, context: Dict[str, Any]) -> bool:
        """执行扩缩容"""
        try:
            deployment_name = alert.labels.get('deployment')
            namespace = alert.labels.get('namespace', 'default')
            replicas = context.get('target_replicas', 2)

            # Kubernetes API调用
            self.k8s_client.apps_v1.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace=namespace,
                body={"spec": {"replicas": replicas}}
            )

            logger.info(f"Scaled deployment {deployment_name} to {replicas} replicas")
            return True

        except Exception as e:
            logger.error(f"Scale action failed: {e}")
            return False

class RestartAction(ResponseAction):
    """重启服务动作"""

    def __init__(self, k8s_client):
        self.k8s_client = k8s_client

    @property
    def name(self) -> str:
        return "restart"

    def execute(self, alert: Alert, context: Dict[str, Any]) -> bool:
        """执行重启"""
        try:
            deployment_name = alert.labels.get('deployment')
            namespace = alert.labels.get('namespace', 'default')

            # 重启Pod
            self.k8s_client.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body={
                    "spec": {
                        "template": {
                            "metadata": {
                                "annotations": {
                                    "kubectl.kubernetes.io/restartedAt": str(time.time())
                                }
                            }
                        }
                    }
                }
            )

            logger.info(f"Restarted deployment {deployment_name}")
            return True

        except Exception as e:
            logger.error(f"Restart action failed: {e}")
            return False

class NotificationAction(ResponseAction):
    """通知动作"""

    def __init__(self, notification_service):
        self.notification_service = notification_service

    @property
    def name(self) -> str:
        return "notify"

    def execute(self, alert: Alert, context: Dict[str, Any]) -> bool:
        """发送通知"""
        try:
            channels = context.get('channels', ['email'])
            recipients = context.get('recipients', [])

            message = {
                'title': alert.title,
                'description': alert.description,
                'severity': alert.severity.value,
                'timestamp': alert.timestamp
            }

            for channel in channels:
                self.notification_service.send(channel, recipients, message)

            logger.info(f"Sent notification for alert {alert.id}")
            return True

        except Exception as e:
            logger.error(f"Notification action failed: {e}")
            return False
```

### 自动化响应引擎

```python
class AutoResponseEngine:
    """自动化响应引擎"""

    def __init__(self):
        self.actions: Dict[str, ResponseAction] = {}
        self.response_rules: List[Dict[str, Any]] = []
        self.action_history: List[Dict[str, Any]] = []

    def register_action(self, action: ResponseAction):
        """注册响应动作"""
        self.actions[action.name] = action
        logger.info(f"Registered response action: {action.name}")

    def add_response_rule(self, rule: Dict[str, Any]):
        """添加响应规则"""
        self.response_rules.append(rule)
        logger.info("Added response rule")

    def process_alert(self, alert: Alert) -> List[Dict[str, Any]]:
        """处理告警并执行自动响应"""
        executed_actions = []

        for rule in self.response_rules:
            if self._matches_rule(alert, rule):
                actions = rule.get('actions', [])

                for action_config in actions:
                    action_name = action_config['name']
                    context = action_config.get('context', {})

                    if action_name in self.actions:
                        action = self.actions[action_name]

                        try:
                            success = action.execute(alert, context)

                            result = {
                                'alert_id': alert.id,
                                'action_name': action_name,
                                'success': success,
                                'timestamp': time.time(),
                                'context': context
                            }

                            executed_actions.append(result)
                            self.action_history.append(result)

                            if success:
                                logger.info(f"Successfully executed action {action_name} for alert {alert.id}")
                            else:
                                logger.error(f"Failed to execute action {action_name} for alert {alert.id}")

                        except Exception as e:
                            logger.error(f"Error executing action {action_name}: {e}")

        return executed_actions

    def _matches_rule(self, alert: Alert, rule: Dict[str, Any]) -> bool:
        """检查告警是否匹配响应规则"""
        # 检查告警名称匹配
        alert_matchers = rule.get('alert_matchers', {})
        for field, pattern in alert_matchers.items():
            if field == 'title':
                if not self._matches_pattern(alert.title, pattern):
                    return False
            elif field == 'description':
                if not self._matches_pattern(alert.description, pattern):
                    return False
            elif field == 'severity':
                if alert.severity.value != pattern:
                    return False

        # 检查标签匹配
        label_matchers = rule.get('label_matchers', {})
        for label, pattern in label_matchers.items():
            if not self._matches_pattern(alert.labels.get(label, ''), pattern):
                return False

        return True

    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """模式匹配"""
        import re
        try:
            return re.match(pattern, value) is not None
        except:
            return value == pattern

    def get_action_history(self, alert_id: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
        """获取动作执行历史"""
        cutoff_time = time.time() - (hours * 3600)

        history = [action for action in self.action_history
                  if action['timestamp'] >= cutoff_time]

        if alert_id:
            history = [action for action in history if action['alert_id'] == alert_id]

        return history
```

## 告警管理系统

### 告警生命周期管理

```python
class AlertLifecycleManager:
    """告警生命周期管理器"""

    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.lifecycle_rules: List[Dict[str, Any]] = []

    def add_lifecycle_rule(self, rule: Dict[str, Any]):
        """添加生命周期规则"""
        self.lifecycle_rules.append(rule)

    def process_alert_lifecycle(self, alert: Alert):
        """处理告警生命周期"""
        # 存储告警
        self.alerts[alert.id] = alert

        # 应用生命周期规则
        for rule in self.lifecycle_rules:
            if self._matches_lifecycle_rule(alert, rule):
                self._apply_lifecycle_rule(alert, rule)

    def _matches_lifecycle_rule(self, alert: Alert, rule: Dict[str, Any]) -> bool:
        """检查告警是否匹配生命周期规则"""
        matchers = rule.get('matchers', {})
        for field, pattern in matchers.items():
            if field == 'severity':
                if alert.severity.value != pattern:
                    return False
            elif field == 'source':
                if alert.source != pattern:
                    return False
        return True

    def _apply_lifecycle_rule(self, alert: Alert, rule: Dict[str, Any]):
        """应用生命周期规则"""
        actions = rule.get('actions', [])

        for action in actions:
            action_type = action.get('type')

            if action_type == 'auto_resolve':
                # 自动解决规则
                delay = action.get('delay', 300)  # 默认5分钟
                # 这里可以启动定时器来自动解决告警

            elif action_type == 'escalate':
                # 升级规则
                if alert.severity.value < 4:  # 不是最高级别
                    alert.severity = AlertSeverity.CRITICAL
                    logger.info(f"Escalated alert {alert.id} to CRITICAL")

            elif action_type == 'assign':
                # 分配规则
                assignee = action.get('assignee')
                alert.assigned_to = assignee
                logger.info(f"Assigned alert {alert.id} to {assignee}")

    def acknowledge_alert(self, alert_id: str, user: str):
        """确认告警"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.acknowledged_by = user
            alert.acknowledged_at = time.time()
            logger.info(f"Alert {alert_id} acknowledged by {user}")

    def resolve_alert(self, alert_id: str, user: Optional[str] = None):
        """解决告警"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = time.time()
            logger.info(f"Alert {alert_id} resolved by {user}")

    def get_alert_stats(self) -> Dict[str, Any]:
        """获取告警统计"""
        total_alerts = len(self.alerts)
        active_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.FIRING])
        resolved_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.RESOLVED])

        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len([
                a for a in self.alerts.values()
                if a.severity == severity and a.status == AlertStatus.FIRING
            ])

        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'resolved_alerts': resolved_alerts,
            'severity_distribution': severity_counts
        }
```

## 智能告警配置

### 告警规则配置

```yaml
# examples/28_chapter/alert_rules.yml
groups:
  - name: infrastructure_alerts
    rules:
      - alert: HighCpuUsage
        expr: cpu_usage_percent > 85
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          title: "High CPU Usage"
          description: "CPU usage is {{ $value }}% on {{ $labels.instance }}"
          runbook_url: "https://wiki.company.com/cpu-troubleshooting"

      - alert: LowDiskSpace
        expr: disk_free_percent < 10
        for: 10m
        labels:
          severity: critical
          team: infrastructure
        annotations:
          title: "Low Disk Space"
          description: "Disk space is below 10% on {{ $labels.instance }}"
          runbook_url: "https://wiki.company.com/disk-space"

  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: error_rate_percent > 5
        for: 5m
        labels:
          severity: critical
          team: application
        annotations:
          title: "High Error Rate"
          description: "Error rate is {{ $value }}% for {{ $labels.service }}"
          runbook_url: "https://wiki.company.com/error-handling"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, response_time_seconds) > 2
        for: 5m
        labels:
          severity: warning
          team: application
        annotations:
          title: "Slow Response Time"
          description: "95th percentile response time is {{ $value }}s"
          runbook_url: "https://wiki.company.com/performance-tuning"

  - name: business_alerts
    rules:
      - alert: LowConversionRate
        expr: conversion_rate < 0.02
        for: 15m
        labels:
          severity: warning
          team: business
        annotations:
          title: "Low Conversion Rate"
          description: "Conversion rate dropped to {{ $value }}"
          impact: "Potential revenue impact"

      - alert: DataQualityIssue
        expr: data_quality_score < 0.8
        for: 10m
        labels:
          severity: error
          team: data
        annotations:
          title: "Data Quality Issue"
          description: "Data quality score is {{ $value }} for {{ $labels.dataset }}"
          runbook_url: "https://wiki.company.com/data-quality"
```

### 自动化响应配置

```yaml
# examples/28_chapter/auto_response.yml
response_rules:
  - name: scale_on_high_cpu
    alert_matchers:
      title: "High CPU Usage"
      severity: "warning"
    label_matchers:
      team: "infrastructure"
    actions:
      - name: scale
        context:
          target_replicas: 3
      - name: notify
        context:
          channels: ["slack", "email"]
          recipients: ["devops-team@company.com"]

  - name: restart_on_service_down
    alert_matchers:
      title: "Service Down"
      severity: "critical"
    actions:
      - name: restart
        context:
          wait_time: 30
      - name: notify
        context:
          channels: ["pagerduty", "slack"]
          recipients: ["oncall-engineer@company.com"]

  - name: notify_on_business_impact
    alert_matchers:
      severity: "critical"
    label_matchers:
      business_impact: "high"
    actions:
      - name: notify
        context:
          channels: ["sms", "email", "slack"]
          recipients: ["management@company.com", "oncall-lead@company.com"]

inhibition_rules:
  - source_matchers:
      severity: "critical"
    target_matchers:
      severity: "warning"
    equal:
      - instance
    reason: "Inhibit warnings when critical alerts are firing"

lifecycle_rules:
  - matchers:
      severity: "info"
    actions:
      - type: auto_resolve
        delay: 300  # 5分钟后自动解决

  - matchers:
      severity: "critical"
      source: "business"
    actions:
      - type: escalate
        delay: 600  # 10分钟后升级
      - type: assign
        assignee: "business-lead"
```

## 告警最佳实践

### 规则设计原则
- **精确性**: 避免误报和漏报，合理设置阈值
- **分层告警**: 不同严重程度对应不同响应级别
- **上下文信息**: 提供足够的信息帮助诊断问题
- **动态调整**: 基于历史数据和业务变化调整规则

### 告警管理策略
- **告警分组**: 按服务、团队、环境进行告警分组
- **告警路由**: 基于标签和规则路由到相应团队
- **告警升级**: 未及时处理的告警自动升级
- **告警抑制**: 避免告警风暴和重复告警

### 自动化响应准则
- **安全第一**: 自动化动作不能影响系统稳定性
- **渐进式**: 从简单通知开始，逐步增加自动化程度
- **可回滚**: 自动化动作要有相应的回滚机制
- **监控效果**: 监控自动化响应的效果和成功率

### 持续改进机制
- **告警评估**: 定期评估告警的有效性和准确性
- **误报分析**: 分析误报原因并优化规则
- **响应时间**: 监控告警发现到解决的平均时间
- **用户反馈**: 收集处理人员的反馈并改进系统