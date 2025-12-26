#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运维监控测试指标仪表板
examples/23_chapter/monitoring_dashboard.py

该脚本提供了一个完整的运维监控仪表板实现，
包含实时指标收集、告警管理和趋势分析功能。
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

import psutil
import requests
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, generate_latest
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, jsonify, render_template_string

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MetricConfig:
    """指标配置类"""
    name: str
    description: str
    unit: str
    collection_interval: int  # 秒
    warning_threshold: float
    critical_threshold: float
    aggregation_method: str

@dataclass
class AlertRule:
    """告警规则类"""
    name: str
    condition: str
    severity: str
    channels: List[str]
    cooldown_period: int  # 秒

class MonitoringDashboard:
    """运维监控仪表板主类"""

    def __init__(self):
        self.metrics_config = self._load_metrics_config()
        self.alert_rules = self._load_alert_rules()
        self.metrics_history = defaultdict(list)
        self.active_alerts = {}
        self.registry = CollectorRegistry()

        # 初始化Prometheus指标
        self._init_prometheus_metrics()

        # 启动监控循环
        self.running = True

    def _load_metrics_config(self) -> Dict[str, MetricConfig]:
        """加载指标配置"""
        return {
            'cpu_usage': MetricConfig(
                name='cpu_usage_percent',
                description='CPU使用率百分比',
                unit='%',
                collection_interval=30,
                warning_threshold=75.0,
                critical_threshold=90.0,
                aggregation_method='average'
            ),
            'memory_usage': MetricConfig(
                name='memory_usage_percent',
                description='内存使用率百分比',
                unit='%',
                collection_interval=30,
                warning_threshold=80.0,
                critical_threshold=95.0,
                aggregation_method='average'
            ),
            'disk_usage': MetricConfig(
                name='disk_usage_percent',
                description='磁盘使用率百分比',
                unit='%',
                collection_interval=300,
                warning_threshold=85.0,
                critical_threshold=95.0,
                aggregation_method='max'
            ),
            'network_traffic': MetricConfig(
                name='network_bandwidth_percent',
                description='网络带宽使用率',
                unit='%',
                collection_interval=60,
                warning_threshold=70.0,
                critical_threshold=90.0,
                aggregation_method='95th_percentile'
            )
        }

    def _load_alert_rules(self) -> List[AlertRule]:
        """加载告警规则"""
        return [
            AlertRule(
                name='high_cpu_usage',
                condition='cpu_usage > 90',
                severity='critical',
                channels=['email', 'sms', 'slack'],
                cooldown_period=300
            ),
            AlertRule(
                name='high_memory_usage',
                condition='memory_usage > 95',
                severity='critical',
                channels=['email', 'sms', 'slack'],
                cooldown_period=300
            ),
            AlertRule(
                name='disk_space_critical',
                condition='disk_usage > 95',
                severity='critical',
                channels=['email', 'slack'],
                cooldown_period=600
            ),
            AlertRule(
                name='network_congestion',
                condition='network_traffic > 90',
                severity='warning',
                channels=['slack'],
                cooldown_period=1800
            )
        ]

    def _init_prometheus_metrics(self):
        """初始化Prometheus指标"""
        self.prometheus_metrics = {}

        for metric_name, config in self.metrics_config.items():
            if config.unit == '%':
                self.prometheus_metrics[metric_name] = Gauge(
                    f'system_{metric_name}',
                    config.description,
                    registry=self.registry
                )
            elif 'response_time' in metric_name:
                self.prometheus_metrics[metric_name] = Histogram(
                    f'app_{metric_name}',
                    config.description,
                    registry=self.registry
                )
            else:
                self.prometheus_metrics[metric_name] = Gauge(
                    f'system_{metric_name}',
                    config.description,
                    registry=self.registry
                )

    def collect_system_metrics(self) -> Dict[str, float]:
        """收集系统指标"""
        metrics = {}

        # CPU使用率
        metrics['cpu_usage'] = psutil.cpu_percent(interval=1)

        # 内存使用率
        memory = psutil.virtual_memory()
        metrics['memory_usage'] = memory.percent

        # 磁盘使用率
        disk = psutil.disk_usage('/')
        metrics['disk_usage'] = disk.percent

        # 网络流量（简化实现）
        net = psutil.net_io_counters()
        # 这里应该计算实际的带宽使用率，这里用占位符
        metrics['network_traffic'] = 45.0  # 模拟值

        return metrics

    def collect_application_metrics(self) -> Dict[str, float]:
        """收集应用指标"""
        # 这里应该从应用监控接口收集数据
        # 暂时返回模拟数据
        return {
            'api_response_time': 1250.0,  # ms
            'error_rate': 0.8,  # %
            'throughput': 150.0  # req/sec
        }

    def check_alerts(self, metrics: Dict[str, float]):
        """检查告警条件"""
        current_time = time.time()

        for rule in self.alert_rules:
            metric_name = rule.condition.split()[0]
            operator = rule.condition.split()[1]
            threshold = float(rule.condition.split()[2])

            if metric_name in metrics:
                value = metrics[metric_name]
                condition_met = self._evaluate_condition(value, operator, threshold)

                if condition_met:
                    alert_key = f"{rule.name}_{metric_name}"

                    # 检查冷却期
                    if alert_key not in self.active_alerts or \
                       current_time - self.active_alerts[alert_key] > rule.cooldown_period:

                        self.active_alerts[alert_key] = current_time
                        self._trigger_alert(rule, metric_name, value, threshold)
                else:
                    # 清除已解决的告警
                    alert_key = f"{rule.name}_{metric_name}"
                    if alert_key in self.active_alerts:
                        del self.active_alerts[alert_key]
                        logger.info(f"Alert resolved: {rule.name}")

    def _evaluate_condition(self, value: float, operator: str, threshold: float) -> bool:
        """评估告警条件"""
        if operator == '>':
            return value > threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<':
            return value < threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return abs(value - threshold) < 0.001
        else:
            return False

    def _trigger_alert(self, rule: AlertRule, metric_name: str, value: float, threshold: float):
        """触发告警"""
        alert_message = f"""
告警触发: {rule.name}
指标: {metric_name}
当前值: {value:.2f}
阈值: {threshold}
严重程度: {rule.severity}
时间: {datetime.now().isoformat()}
        """.strip()

        logger.warning(alert_message)

        # 发送告警通知（这里是模拟实现）
        for channel in rule.channels:
            self._send_notification(channel, alert_message)

    def _send_notification(self, channel: str, message: str):
        """发送通知（模拟实现）"""
        logger.info(f"Sending {channel} notification: {message[:100]}...")

        # 这里应该实现实际的通知逻辑
        # 例如：发送邮件、Slack消息、短信等

    def update_metrics_history(self, metrics: Dict[str, float]):
        """更新指标历史数据"""
        timestamp = datetime.now()

        for metric_name, value in metrics.items():
            self.metrics_history[metric_name].append({
                'timestamp': timestamp,
                'value': value
            })

            # 保持历史数据在合理范围内（最近24小时）
            cutoff_time = timestamp - timedelta(hours=24)
            self.metrics_history[metric_name] = [
                entry for entry in self.metrics_history[metric_name]
                if entry['timestamp'] > cutoff_time
            ]

    def generate_trend_analysis(self, metric_name: str, hours: int = 24) -> Dict[str, Any]:
        """生成趋势分析"""
        if metric_name not in self.metrics_history:
            return {}

        # 获取指定时间范围的数据
        cutoff_time = datetime.now() - timedelta(hours=hours)
        data = [
            entry for entry in self.metrics_history[metric_name]
            if entry['timestamp'] > cutoff_time
        ]

        if not data:
            return {}

        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)

        analysis = {
            'current_value': data[-1]['value'] if data else None,
            'average': df['value'].mean(),
            'min': df['value'].min(),
            'max': df['value'].max(),
            'trend': self._calculate_trend(df['value']),
            'volatility': df['value'].std(),
            'data_points': len(data)
        }

        return analysis

    def _calculate_trend(self, series: pd.Series) -> str:
        """计算趋势"""
        if len(series) < 2:
            return 'insufficient_data'

        # 简单的线性回归趋势
        x = range(len(series))
        slope = pd.Series(x).corr(series)

        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表板数据"""
        current_metrics = self.collect_system_metrics()
        current_metrics.update(self.collect_application_metrics())

        # 更新Prometheus指标
        for metric_name, value in current_metrics.items():
            if metric_name in self.prometheus_metrics:
                self.prometheus_metrics[metric_name].set(value)

        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'current_metrics': current_metrics,
            'alerts': list(self.active_alerts.keys()),
            'trends': {}
        }

        # 添加趋势分析
        for metric_name in self.metrics_config.keys():
            dashboard_data['trends'][metric_name] = self.generate_trend_analysis(metric_name)

        return dashboard_data

    def run_monitoring_loop(self):
        """运行监控循环"""
        logger.info("Starting monitoring dashboard...")

        while self.running:
            try:
                # 收集指标
                system_metrics = self.collect_system_metrics()
                app_metrics = self.collect_application_metrics()
                all_metrics = {**system_metrics, **app_metrics}

                # 检查告警
                self.check_alerts(all_metrics)

                # 更新历史数据
                self.update_metrics_history(all_metrics)

                # 等待下一个收集周期
                time.sleep(30)  # 30秒间隔

            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(60)  # 出错时等待更长时间

    def stop(self):
        """停止监控"""
        self.running = False
        logger.info("Monitoring dashboard stopped")

# Flask Web应用
app = Flask(__name__)
dashboard = MonitoringDashboard()

@app.route('/')
def index():
    """仪表板主页"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>运维监控仪表板</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .metric { background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .alert { background: #ffcccc; border: 1px solid #ff0000; padding: 10px; margin: 10px 0; }
            .trend { background: #ccffcc; border: 1px solid #00ff00; padding: 10px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>运维监控仪表板</h1>
        <div id="dashboard"></div>

        <script>
            function updateDashboard() {
                fetch('/api/metrics')
                    .then(response => response.json())
                    .then(data => {
                        let html = '<h2>当前指标</h2>';
                        for (const [key, value] of Object.entries(data.current_metrics)) {
                            html += `<div class="metric">${key}: ${value.toFixed(2)}</div>`;
                        }

                        if (data.alerts.length > 0) {
                            html += '<h2>活跃告警</h2>';
                            data.alerts.forEach(alert => {
                                html += `<div class="alert">${alert}</div>`;
                            });
                        }

                        html += '<h2>趋势分析</h2>';
                        for (const [key, trend] of Object.entries(data.trends)) {
                            if (trend.current_value !== null) {
                                html += `<div class="trend">${key}: ${trend.trend} (当前: ${trend.current_value.toFixed(2)})</div>`;
                            }
                        }

                        document.getElementById('dashboard').innerHTML = html;
                    });
            }

            updateDashboard();
            setInterval(updateDashboard, 30000);  // 30秒更新一次
        </script>
    </body>
    </html>
    """)

@app.route('/api/metrics')
def get_metrics():
    """获取指标API"""
    return jsonify(dashboard.get_dashboard_data())

@app.route('/metrics')
def prometheus_metrics():
    """Prometheus指标端点"""
    return generate_latest(dashboard.registry)

if __name__ == '__main__':
    # 启动监控线程
    import threading
    monitoring_thread = threading.Thread(target=dashboard.run_monitoring_loop, daemon=True)
    monitoring_thread.start()

    # 启动Web服务器
    app.run(host='0.0.0.0', port=8080, debug=False)