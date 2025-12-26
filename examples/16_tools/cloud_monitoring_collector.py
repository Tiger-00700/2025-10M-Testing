# 云服务监控和告警系统
# Cloud Service Monitoring and Alerting System

## 概述 (Overview)
本系统提供统一的云服务监控和智能告警解决方案，支持多云环境的实时监控、异常检测和自动化响应。

## 核心组件 (Core Components)

### 1. 多云监控收集器 (Multi-Cloud Monitoring Collector)
```python
# examples/16_tools/cloud_monitoring_collector.py
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """指标类型枚举"""
    GAUGE = "gauge"        # 瞬时值
    COUNTER = "counter"    # 累积值
    HISTOGRAM = "histogram"  # 分布统计
    SUMMARY = "summary"    # 分位数统计

class AlertSeverity(Enum):
    """告警严重程度枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class MetricDefinition:
    """指标定义"""
    name: str
    type: MetricType
    description: str
    unit: str
    labels: List[str] = None
    buckets: List[float] = None  # for histogram

@dataclass
class AlertRule:
    """告警规则"""
    name: str
    description: str
    condition: str
    severity: AlertSeverity
    labels: Dict[str, str] = None
    annotations: Dict[str, str] = None
    for_duration: str = "5m"  # 持续时间
    evaluation_interval: str = "1m"

@dataclass
class AlertInstance:
    """告警实例"""
    alert_name: str
    severity: AlertSeverity
    description: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    starts_at: datetime
    ends_at: Optional[datetime] = None
    generator_url: str = ""

class CloudMonitoringCollector:
    """多云监控收集器"""

    def __init__(self):
        self.providers: Dict[str, Any] = {}
        self.metrics_definitions: Dict[str, MetricDefinition] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, AlertInstance] = {}
        self.metric_data: Dict[str, List[Dict[str, Any]]] = {}
        self.event_listeners: List[Callable] = []
        self.collection_interval = 60  # seconds

    def register_provider(self, name: str, provider_client: Any):
        """注册云服务提供商"""
        self.providers[name] = provider_client
        logger.info(f"Registered monitoring provider: {name}")

    def define_metric(self, metric_def: MetricDefinition):
        """定义指标"""
        self.metrics_definitions[metric_def.name] = metric_def
        self.metric_data[metric_def.name] = []
        logger.info(f"Defined metric: {metric_def.name}")

    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_rules[rule.name] = rule
        logger.info(f"Added alert rule: {rule.name}")

    def start_collection(self):
        """启动监控收集"""
        logger.info("Starting monitoring collection")
        self.collection_thread = threading.Thread(target=self._collection_loop)
        self.collection_thread.daemon = True
        self.collection_thread.start()

    def _collection_loop(self):
        """监控收集循环"""
        while True:
            try:
                self._collect_all_metrics()
                self._evaluate_alert_rules()
                self._cleanup_old_data()
            except Exception as e:
                logger.error(f"Collection cycle failed: {str(e)}")

            time.sleep(self.collection_interval)

    def _collect_all_metrics(self):
        """收集所有指标"""
        for provider_name, provider in self.providers.items():
            try:
                metrics = self._collect_provider_metrics(provider_name, provider)
                self._store_metrics(metrics)
            except Exception as e:
                logger.error(f"Failed to collect metrics from {provider_name}: {str(e)}")

    def _collect_provider_metrics(self, provider_name: str, provider: Any) -> Dict[str, Any]:
        """收集特定提供商的指标"""
        metrics = {}

        # CPU使用率
        if hasattr(provider, 'get_cpu_utilization'):
            metrics['cpu_utilization'] = provider.get_cpu_utilization()

        # 内存使用率
        if hasattr(provider, 'get_memory_utilization'):
            metrics['memory_utilization'] = provider.get_memory_utilization()

        # 磁盘使用率
        if hasattr(provider, 'get_disk_utilization'):
            metrics['disk_utilization'] = provider.get_disk_utilization()

        # 网络流量
        if hasattr(provider, 'get_network_traffic'):
            network_data = provider.get_network_traffic()
            metrics['network_bytes_in'] = network_data.get('bytes_in', 0)
            metrics['network_bytes_out'] = network_data.get('bytes_out', 0)

        # 请求延迟
        if hasattr(provider, 'get_request_latency'):
            metrics['request_latency'] = provider.get_request_latency()

        # 错误率
        if hasattr(provider, 'get_error_rate'):
            metrics['error_rate'] = provider.get_error_rate()

        # 添加提供商标签
        for metric_name, value in metrics.items():
            if isinstance(value, dict):
                value['provider'] = provider_name
            else:
                metrics[metric_name] = {'value': value, 'provider': provider_name}

        return metrics

    def _store_metrics(self, metrics: Dict[str, Any]):
        """存储指标数据"""
        timestamp = datetime.now()

        for metric_name, metric_data in metrics.items():
            if metric_name in self.metrics_definitions:
                data_point = {
                    'timestamp': timestamp,
                    'value': metric_data.get('value', metric_data) if isinstance(metric_data, dict) else metric_data,
                    'labels': metric_data.get('labels', {}) if isinstance(metric_data, dict) else {'provider': metric_data.get('provider', 'unknown')}
                }

                self.metric_data[metric_name].append(data_point)

                # 限制数据点数量
                if len(self.metric_data[metric_name]) > 1000:
                    self.metric_data[metric_name] = self.metric_data[metric_name][-1000:]

    def _evaluate_alert_rules(self):
        """评估告警规则"""
        for rule_name, rule in self.alert_rules.items():
            try:
                self._evaluate_single_rule(rule)
            except Exception as e:
                logger.error(f"Failed to evaluate rule {rule_name}: {str(e)}")

    def _evaluate_single_rule(self, rule: AlertRule):
        """评估单个告警规则"""
        # 简化的规则评估逻辑
        # 实际实现需要解析PromQL风格的表达式

        alert_key = rule.name
        should_alert = self._check_condition(rule.condition)

        if should_alert:
            if alert_key not in self.active_alerts:
                # 创建新告警
                alert = AlertInstance(
                    alert_name=rule.name,
                    severity=rule.severity,
                    description=rule.description,
                    labels=rule.labels or {},
                    annotations=rule.annotations or {},
                    starts_at=datetime.now()
                )
                self.active_alerts[alert_key] = alert
                self._notify_alert('firing', alert)
                logger.warning(f"Alert firing: {rule.name}")
        else:
            if alert_key in self.active_alerts:
                # 解决告警
                alert = self.active_alerts[alert_key]
                alert.ends_at = datetime.now()
                self._notify_alert('resolved', alert)
                del self.active_alerts[alert_key]
                logger.info(f"Alert resolved: {rule.name}")

    def _check_condition(self, condition: str) -> bool:
        """检查告警条件"""
        # 简化的条件检查逻辑
        # 实际实现需要解析复杂的表达式

        if 'cpu_utilization > 0.8' in condition:
            cpu_metric = self.metric_data.get('cpu_utilization', [])
            if cpu_metric:
                latest_value = cpu_metric[-1]['value']
                return latest_value > 0.8

        elif 'memory_utilization > 0.9' in condition:
            memory_metric = self.metric_data.get('memory_utilization', [])
            if memory_metric:
                latest_value = memory_metric[-1]['value']
                return latest_value > 0.9

        elif 'error_rate > 0.05' in condition:
            error_metric = self.metric_data.get('error_rate', [])
            if error_metric:
                latest_value = error_metric[-1]['value']
                return latest_value > 0.05

        return False

    def _notify_alert(self, state: str, alert: AlertInstance):
        """通知告警"""
        for listener in self.event_listeners:
            try:
                listener(state, alert)
            except Exception as e:
                logger.error(f"Alert notification failed: {str(e)}")

    def _cleanup_old_data(self):
        """清理旧数据"""
        cutoff_time = datetime.now() - timedelta(hours=24)

        for metric_name in self.metric_data:
            self.metric_data[metric_name] = [
                point for point in self.metric_data[metric_name]
                if point['timestamp'] > cutoff_time
            ]

    def add_event_listener(self, listener: Callable):
        """添加事件监听器"""
        self.event_listeners.append(listener)

    def get_metric_data(self, metric_name: str, hours: int = 1) -> List[Dict[str, Any]]:
        """获取指标数据"""
        if metric_name not in self.metric_data:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            point for point in self.metric_data[metric_name]
            if point['timestamp'] > cutoff_time
        ]

    def get_active_alerts(self) -> Dict[str, AlertInstance]:
        """获取活跃告警"""
        return self.active_alerts.copy()

    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取告警历史"""
        # 简化的历史记录实现
        # 实际应该从持久化存储中获取
        return []
```

### 2. 智能告警管理器 (Intelligent Alert Manager)
```python
# 智能告警管理器
class IntelligentAlertManager:
    """智能告警管理器"""

    def __init__(self, collector: CloudMonitoringCollector):
        self.collector = collector
        self.alert_templates: Dict[str, Dict[str, Any]] = {}
        self.escalation_policies: Dict[str, List[Dict[str, Any]]] = {}
        self.auto_remediation_rules: Dict[str, Callable] = {}
        self.alert_correlation_rules: Dict[str, Dict[str, Any]] = {}

    def define_alert_template(self, name: str, template: Dict[str, Any]):
        """定义告警模板"""
        self.alert_templates[name] = template

    def set_escalation_policy(self, alert_type: str, policy: List[Dict[str, Any]]):
        """设置升级策略"""
        self.escalation_policies[alert_type] = policy

    def add_auto_remediation_rule(self, alert_name: str, remediation_function: Callable):
        """添加自动修复规则"""
        self.auto_remediation_rules[alert_name] = remediation_function

    def add_correlation_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """添加告警关联规则"""
        self.alert_correlation_rules[rule_name] = rule_config

    def process_alert(self, alert_state: str, alert: AlertInstance):
        """处理告警"""
        if alert_state == 'firing':
            self._handle_alert_firing(alert)
        elif alert_state == 'resolved':
            self._handle_alert_resolution(alert)

    def _handle_alert_firing(self, alert: AlertInstance):
        """处理告警触发"""
        logger.info(f"Processing alert firing: {alert.alert_name}")

        # 应用关联规则
        correlated_alerts = self._find_correlated_alerts(alert)
        if correlated_alerts:
            self._create_correlated_alert(alert, correlated_alerts)

        # 检查是否需要自动修复
        if alert.alert_name in self.auto_remediation_rules:
            self._execute_auto_remediation(alert)

        # 应用升级策略
        self._apply_escalation_policy(alert)

        # 发送通知
        self._send_alert_notifications(alert)

    def _handle_alert_resolution(self, alert: AlertInstance):
        """处理告警解决"""
        logger.info(f"Processing alert resolution: {alert.alert_name}")

        # 清理关联告警
        self._cleanup_correlated_alerts(alert)

        # 发送恢复通知
        self._send_resolution_notifications(alert)

    def _find_correlated_alerts(self, alert: AlertInstance) -> List[AlertInstance]:
        """查找关联告警"""
        correlated = []

        for rule_name, rule_config in self.alert_correlation_rules.items():
            if self._matches_correlation_rule(alert, rule_config):
                # 查找匹配的活跃告警
                for active_alert in self.collector.get_active_alerts().values():
                    if self._matches_correlation_criteria(active_alert, rule_config):
                        correlated.append(active_alert)

        return correlated

    def _matches_correlation_rule(self, alert: AlertInstance, rule_config: Dict[str, Any]) -> bool:
        """检查是否匹配关联规则"""
        # 简化的匹配逻辑
        alert_patterns = rule_config.get('alert_patterns', [])
        for pattern in alert_patterns:
            if pattern in alert.alert_name:
                return True
        return False

    def _matches_correlation_criteria(self, alert: AlertInstance, rule_config: Dict[str, Any]) -> bool:
        """检查是否匹配关联条件"""
        # 简化的匹配逻辑
        time_window = rule_config.get('time_window', 300)  # 5分钟
        if alert.starts_at and (datetime.now() - alert.starts_at).total_seconds() <= time_window:
            return True
        return False

    def _create_correlated_alert(self, trigger_alert: AlertInstance, correlated_alerts: List[AlertInstance]):
        """创建关联告警"""
        correlated_names = [alert.alert_name for alert in correlated_alerts]

        correlated_alert = AlertInstance(
            alert_name=f"correlated_{trigger_alert.alert_name}",
            severity=AlertSeverity.WARNING,  # 关联告警通常是警告级别
            description=f"Multiple related alerts detected: {trigger_alert.alert_name} + {', '.join(correlated_names)}",
            labels={'correlation_type': 'multiple_alerts'},
            annotations={
                'trigger_alert': trigger_alert.alert_name,
                'correlated_alerts': json.dumps(correlated_names),
                'recommendation': 'Investigate root cause affecting multiple components'
            },
            starts_at=datetime.now()
        )

        # 添加到活跃告警
        self.collector.active_alerts[correlated_alert.alert_name] = correlated_alert

    def _execute_auto_remediation(self, alert: AlertInstance):
        """执行自动修复"""
        remediation_function = self.auto_remediation_rules[alert.alert_name]

        try:
            logger.info(f"Executing auto-remediation for alert: {alert.alert_name}")
            result = remediation_function(alert)

            if result.get('success', False):
                logger.info(f"Auto-remediation successful for {alert.alert_name}")
                # 可以选择自动解决告警
            else:
                logger.warning(f"Auto-remediation failed for {alert.alert_name}")

        except Exception as e:
            logger.error(f"Auto-remediation error for {alert.alert_name}: {str(e)}")

    def _apply_escalation_policy(self, alert: AlertInstance):
        """应用升级策略"""
        alert_type = self._classify_alert_type(alert)
        policy = self.escalation_policies.get(alert_type, [])

        for escalation_step in policy:
            delay = escalation_step.get('delay', 0)
            if delay > 0:
                # 延迟执行升级
                threading.Timer(delay, self._execute_escalation_step, args=[alert, escalation_step]).start()
            else:
                self._execute_escalation_step(alert, escalation_step)

    def _execute_escalation_step(self, alert: AlertInstance, step: Dict[str, Any]):
        """执行升级步骤"""
        action = step.get('action')
        if action == 'notify':
            self._send_escalation_notification(alert, step)
        elif action == 'page':
            self._send_page_notification(alert, step)
        elif action == 'create_ticket':
            self._create_support_ticket(alert, step)

    def _classify_alert_type(self, alert: AlertInstance) -> str:
        """分类告警类型"""
        if 'cpu' in alert.alert_name.lower():
            return 'infrastructure'
        elif 'error' in alert.alert_name.lower():
            return 'application'
        elif 'latency' in alert.alert_name.lower():
            return 'performance'
        else:
            return 'general'

    def _send_alert_notifications(self, alert: AlertInstance):
        """发送告警通知"""
        # 实现具体的通知逻辑 (邮件、Slack、短信等)
        logger.info(f"Sending alert notification for: {alert.alert_name}")

    def _send_resolution_notifications(self, alert: AlertInstance):
        """发送恢复通知"""
        logger.info(f"Sending resolution notification for: {alert.alert_name}")

    def _send_escalation_notification(self, alert: AlertInstance, step: Dict[str, Any]):
        """发送升级通知"""
        logger.info(f"Sending escalation notification for: {alert.alert_name}")

    def _send_page_notification(self, alert: AlertInstance, step: Dict[str, Any]):
        """发送寻呼通知"""
        logger.warning(f"Sending page notification for: {alert.alert_name}")

    def _create_support_ticket(self, alert: AlertInstance, step: Dict[str, Any]):
        """创建支持工单"""
        logger.info(f"Creating support ticket for: {alert.alert_name}")

    def _cleanup_correlated_alerts(self, resolved_alert: AlertInstance):
        """清理关联告警"""
        # 查找并解决相关的关联告警
        correlated_keys = [
            key for key in self.collector.active_alerts.keys()
            if key.startswith('correlated_') and resolved_alert.alert_name in key
        ]

        for key in correlated_keys:
            if key in self.collector.active_alerts:
                correlated_alert = self.collector.active_alerts[key]
                correlated_alert.ends_at = datetime.now()
                logger.info(f"Resolved correlated alert: {key}")
                del self.collector.active_alerts[key]
```

### 3. 监控配置模板 (Monitoring Configuration Template)
```yaml
# 多云监控和告警配置
cloud_monitoring_config:
  providers:
    - name: aws
      type: AWSProvider
      regions: ["us-east-1", "eu-west-1"]
      services: ["EC2", "RDS", "ELB", "CloudWatch"]

    - name: azure
      type: AzureProvider
      subscription_id: "${AZURE_SUBSCRIPTION_ID}"
      resource_groups: ["prod-rg", "staging-rg"]

    - name: gcp
      type: GCPProvider
      project_id: "${GCP_PROJECT_ID}"
      zones: ["us-central1-a", "europe-west1-b"]

  metrics:
    - name: cpu_utilization
      type: gauge
      description: "CPU utilization percentage"
      unit: percent
      collection_interval: 60s

    - name: memory_utilization
      type: gauge
      description: "Memory utilization percentage"
      unit: percent
      collection_interval: 60s

    - name: disk_utilization
      type: gauge
      description: "Disk utilization percentage"
      unit: percent
      collection_interval: 300s

    - name: network_traffic
      type: counter
      description: "Network traffic in bytes"
      unit: bytes
      labels: ["direction"]
      collection_interval: 60s

    - name: request_latency
      type: histogram
      description: "Request latency distribution"
      unit: seconds
      buckets: [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
      collection_interval: 60s

    - name: error_rate
      type: gauge
      description: "Error rate percentage"
      unit: percent
      collection_interval: 60s

  alert_rules:
    - name: high_cpu_utilization
      description: "CPU utilization is too high"
      condition: cpu_utilization > 0.8
      severity: warning
      for_duration: 5m
      labels:
        team: infrastructure
      annotations:
        summary: "High CPU utilization detected"
        description: "CPU utilization is above 80% for 5 minutes"
        runbook_url: "https://wiki.company.com/cpu-troubleshooting"

    - name: high_memory_utilization
      description: "Memory utilization is too high"
      condition: memory_utilization > 0.9
      severity: error
      for_duration: 3m
      labels:
        team: infrastructure
      annotations:
        summary: "High memory utilization detected"
        description: "Memory utilization is above 90% for 3 minutes"

    - name: high_error_rate
      description: "Error rate is too high"
      condition: error_rate > 0.05
      severity: critical
      for_duration: 2m
      labels:
        team: application
      annotations:
        summary: "High error rate detected"
        description: "Error rate is above 5% for 2 minutes"
        impact: "Service degradation possible"

    - name: high_request_latency
      description: "Request latency is too high"
      condition: histogram_quantile(0.95, request_latency) > 5.0
      severity: warning
      for_duration: 5m
      labels:
        team: application
      annotations:
        summary: "High request latency detected"
        description: "95th percentile request latency is above 5 seconds"

  escalation_policies:
    infrastructure:
      - delay: 0
        action: notify
        channels: ["slack", "email"]
        recipients: ["infra-team@company.com"]
      - delay: 1800  # 30 minutes
        action: page
        channels: ["pagerduty"]
        recipients: ["infra-oncall@company.com"]
      - delay: 3600  # 1 hour
        action: create_ticket
        system: "jira"
        priority: high

    application:
      - delay: 0
        action: notify
        channels: ["slack", "email"]
        recipients: ["app-team@company.com"]
      - delay: 900   # 15 minutes
        action: page
        channels: ["pagerduty"]
        recipients: ["app-oncall@company.com"]
      - delay: 1800  # 30 minutes
        action: create_ticket
        system: "jira"
        priority: critical

  auto_remediation:
    - alert_name: high_cpu_utilization
      action: scale_out
      parameters:
        service: web-app
        max_instances: 10
        cooldown: 300

    - alert_name: high_memory_utilization
      action: restart_service
      parameters:
        service: memory-intensive-app
        graceful_shutdown: true
        restart_delay: 30

  correlation_rules:
    - name: infrastructure_correlation
      alert_patterns: ["high_cpu", "high_memory", "disk_full"]
      time_window: 300
      min_alerts: 2
      action: create_incident
      description: "Multiple infrastructure alerts detected"

    - name: application_correlation
      alert_patterns: ["high_error_rate", "high_latency", "timeout_errors"]
      time_window: 600
      min_alerts: 3
      action: create_incident
      description: "Multiple application performance alerts detected"

  notification_channels:
    slack:
      webhook_url: "${SLACK_WEBHOOK_URL}"
      channel: "#alerts"
      username: "Cloud Monitor"

    email:
      smtp_server: "smtp.company.com"
      smtp_port: 587
      username: "${EMAIL_USER}"
      password: "${EMAIL_PASSWORD}"
      from_address: "alerts@company.com"

    pagerduty:
      integration_key: "${PAGERDUTY_INTEGRATION_KEY}"
      service_name: "Cloud Infrastructure"

    webhook:
      url: "${WEBHOOK_URL}"
      headers:
        Authorization: "Bearer ${WEBHOOK_TOKEN}"
        Content-Type: "application/json"
```

## 使用示例 (Usage Examples)

### 基本监控设置
```python
from cloud_monitoring_collector import CloudMonitoringCollector, MetricDefinition, MetricType, AlertRule, AlertSeverity
from intelligent_alert_manager import IntelligentAlertManager
import yaml

# 初始化监控收集器
collector = CloudMonitoringCollector()

# 加载配置
with open('cloud_monitoring_config.yml', 'r') as f:
    config = yaml.safe_load(f)

# 注册云提供商 (这里使用模拟提供商)
class MockAWSProvider:
    def get_cpu_utilization(self): return 0.65
    def get_memory_utilization(self): return 0.72
    def get_error_rate(self): return 0.02

class MockAzureProvider:
    def get_cpu_utilization(self): return 0.58
    def get_memory_utilization(self): return 0.68
    def get_error_rate(self): return 0.015

collector.register_provider('aws', MockAWSProvider())
collector.register_provider('azure', MockAzureProvider())

# 定义指标
for metric_config in config['metrics']:
    metric = MetricDefinition(
        name=metric_config['name'],
        type=MetricType(metric_config['type']),
        description=metric_config['description'],
        unit=metric_config['unit'],
        labels=metric_config.get('labels', []),
        buckets=metric_config.get('buckets')
    )
    collector.define_metric(metric)

# 添加告警规则
for rule_config in config['alert_rules']:
    rule = AlertRule(
        name=rule_config['name'],
        description=rule_config['description'],
        condition=rule_config['condition'],
        severity=AlertSeverity(rule_config['severity']),
        labels=rule_config.get('labels', {}),
        annotations=rule_config.get('annotations', {}),
        for_duration=rule_config.get('for_duration', '5m')
    )
    collector.add_alert_rule(rule)

# 初始化智能告警管理器
alert_manager = IntelligentAlertManager(collector)

# 设置升级策略
for alert_type, policy in config.get('escalation_policies', {}).items():
    alert_manager.set_escalation_policy(alert_type, policy)

# 添加关联规则
for rule_config in config.get('correlation_rules', []):
    alert_manager.add_correlation_rule(rule_config['name'], rule_config)

# 连接告警处理器
collector.add_event_listener(alert_manager.process_alert)

# 启动监控
collector.start_collection()

print("Cloud monitoring system started")
```

### 告警查询和分析
```python
# 查询指标数据
cpu_data = collector.get_metric_data('cpu_utilization', hours=1)
print(f"CPU utilization data points: {len(cpu_data)}")

for point in cpu_data[-5:]:  # 最近5个数据点
    print(f"Time: {point['timestamp']}, Value: {point['value']:.2%}, Provider: {point['labels']['provider']}")

# 查询活跃告警
active_alerts = collector.get_active_alerts()
print(f"Active alerts: {len(active_alerts)}")

for alert_name, alert in active_alerts.items():
    print(f"Alert: {alert_name}, Severity: {alert.severity.value}, Started: {alert.starts_at}")

# 生成监控报告
report = {
    'timestamp': datetime.now().isoformat(),
    'metrics_collected': len(collector.metric_data),
    'active_alerts': len(active_alerts),
    'total_alert_rules': len(collector.alert_rules),
    'providers_monitored': len(collector.providers)
}

print("Monitoring report:", json.dumps(report, indent=2, default=str))
```

## 最佳实践 (Best Practices)

1. **分层监控**: 基础设施层、平台层、应用层分别监控，避免信息过载
2. **智能告警**: 避免告警疲劳，通过关联分析减少重复告警
3. **自动化响应**: 实施自动修复机制，减少人工干预
4. **渐进式升级**: 告警升级策略避免在非工作时间过度打扰
5. **持续优化**: 定期review告警规则的有效性和准确性
6. **跨团队协作**: 建立明确的告警响应流程和责任划分
7. **历史分析**: 保留告警历史，用于趋势分析和容量规划
8. **成本意识**: 监控云资源使用情况，避免不必要的支出