# examples/14_monitoring/monitoring_pipeline.py
# 测试环境监控数据管道
# Monitoring Data Pipeline for Test Environments

import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram
import psutil
import requests

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MonitoringConfig:
    """监控配置"""
    environment: str
    service_name: str
    metrics_endpoint: str
    alert_webhook: Optional[str] = None
    scrape_interval: int = 15

@dataclass
class SLIMetrics:
    """SLI 指标数据"""
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str]

class TestEnvironmentMonitor:
    """测试环境监控器"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.registry = CollectorRegistry()

        # 初始化 Prometheus 指标
        self.cpu_usage = Gauge('test_env_cpu_usage_percent',
                              'CPU 使用率百分比',
                              ['environment', 'service'],
                              registry=self.registry)

        self.memory_usage = Gauge('test_env_memory_usage_percent',
                                 '内存使用率百分比',
                                 ['environment', 'service'],
                                 registry=self.registry)

        self.disk_usage = Gauge('test_env_disk_usage_percent',
                               '磁盘使用率百分比',
                               ['environment', 'service'],
                               registry=self.registry)

        self.response_time = Histogram('test_env_response_time_seconds',
                                      '响应时间直方图',
                                      ['environment', 'service', 'endpoint'],
                                      registry=self.registry)

        self.error_count = Counter('test_env_error_total',
                                  '错误总数',
                                  ['environment', 'service', 'error_type'],
                                  registry=self.registry)

        # SLO 跟踪器
        self.slo_violations = Counter('test_env_slo_violations_total',
                                     'SLO 违反总数',
                                     ['environment', 'service', 'slo_name'],
                                     registry=self.registry)

    def collect_system_metrics(self) -> List[SLIMetrics]:
        """收集系统指标"""
        metrics = []

        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_usage.labels(
            environment=self.config.environment,
            service=self.config.service_name
        ).set(cpu_percent)

        metrics.append(SLIMetrics(
            name='cpu_usage',
            value=cpu_percent,
            timestamp=time.time(),
            labels={'environment': self.config.environment, 'service': self.config.service_name}
        ))

        # 内存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        self.memory_usage.labels(
            environment=self.config.environment,
            service=self.config.service_name
        ).set(memory_percent)

        metrics.append(SLIMetrics(
            name='memory_usage',
            value=memory_percent,
            timestamp=time.time(),
            labels={'environment': self.config.environment, 'service': self.config.service_name}
        ))

        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        self.disk_usage.labels(
            environment=self.config.environment,
            service=self.config.service_name
        ).set(disk_percent)

        metrics.append(SLIMetrics(
            name='disk_usage',
            value=disk_percent,
            timestamp=time.time(),
            labels={'environment': self.config.environment, 'service': self.config.service_name}
        ))

        return metrics

    def collect_application_metrics(self) -> List[SLIMetrics]:
        """收集应用指标"""
        metrics = []

        try:
            # 模拟应用健康检查
            response = requests.get(f"http://localhost:8080/health", timeout=5)
            response_time = response.elapsed.total_seconds()

            # 记录响应时间
            self.response_time.labels(
                environment=self.config.environment,
                service=self.config.service_name,
                endpoint='/health'
            ).observe(response_time)

            metrics.append(SLIMetrics(
                name='response_time',
                value=response_time,
                timestamp=time.time(),
                labels={
                    'environment': self.config.environment,
                    'service': self.config.service_name,
                    'endpoint': '/health'
                }
            ))

            # 检查状态码
            if response.status_code >= 400:
                self.error_count.labels(
                    environment=self.config.environment,
                    service=self.config.service_name,
                    error_type='http_error'
                ).inc()

        except Exception as e:
            logger.error(f"应用指标收集失败: {e}")
            self.error_count.labels(
                environment=self.config.environment,
                service=self.config.service_name,
                error_type='connection_error'
            ).inc()

        return metrics

    def check_slo_compliance(self, metrics: List[SLIMetrics]) -> List[str]:
        """检查 SLO 合规性"""
        violations = []

        # CPU SLO: 使用率不超过 80%
        cpu_metrics = [m for m in metrics if m.name == 'cpu_usage']
        if cpu_metrics and cpu_metrics[0].value > 80:
            violations.append('cpu_slo_violation')
            self.slo_violations.labels(
                environment=self.config.environment,
                service=self.config.service_name,
                slo_name='cpu_usage_slo'
            ).inc()

        # 内存 SLO: 使用率不超过 85%
        memory_metrics = [m for m in metrics if m.name == 'memory_usage']
        if memory_metrics and memory_metrics[0].value > 85:
            violations.append('memory_slo_violation')
            self.slo_violations.labels(
                environment=self.config.environment,
                service=self.config.service_name,
                slo_name='memory_usage_slo'
            ).inc()

        # 响应时间 SLO: P95 不超过 2 秒
        response_metrics = [m for m in metrics if m.name == 'response_time']
        if response_metrics and response_metrics[0].value > 2:
            violations.append('response_time_slo_violation')
            self.slo_violations.labels(
                environment=self.config.environment,
                service=self.config.service_name,
                slo_name='response_time_slo'
            ).inc()

        return violations

    def send_alert(self, violations: List[str]):
        """发送告警"""
        if not self.config.alert_webhook or not violations:
            return

        alert_data = {
            'environment': self.config.environment,
            'service': self.config.service_name,
            'violations': violations,
            'timestamp': time.time(),
            'severity': 'warning' if len(violations) < 3 else 'critical'
        }

        try:
            response = requests.post(self.config.alert_webhook, json=alert_data, timeout=5)
            if response.status_code == 200:
                logger.info(f"告警发送成功: {violations}")
            else:
                logger.error(f"告警发送失败: {response.status_code}")
        except Exception as e:
            logger.error(f"告警发送异常: {e}")

    def run_monitoring_loop(self):
        """运行监控循环"""
        logger.info(f"启动监控: {self.config.environment} - {self.config.service_name}")

        while True:
            try:
                # 收集系统指标
                system_metrics = self.collect_system_metrics()

                # 收集应用指标
                app_metrics = self.collect_application_metrics()

                all_metrics = system_metrics + app_metrics

                # 检查 SLO 合规性
                violations = self.check_slo_compliance(all_metrics)

                # 发送告警
                if violations:
                    self.send_alert(violations)

                # 记录指标
                logger.info(f"收集到 {len(all_metrics)} 个指标, {len(violations)} 个违反")

            except Exception as e:
                logger.error(f"监控循环异常: {e}")

            time.sleep(self.config.scrape_interval)

# 使用示例
if __name__ == "__main__":
    config = MonitoringConfig(
        environment="test",
        service_name="web_app",
        metrics_endpoint="http://localhost:9090",
        alert_webhook="http://alertmanager:9093/api/v2/alerts",
        scrape_interval=15
    )

    monitor = TestEnvironmentMonitor(config)
    monitor.run_monitoring_loop()