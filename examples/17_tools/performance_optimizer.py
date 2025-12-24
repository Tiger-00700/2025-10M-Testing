# examples/17_tools/performance_optimizer.py
import psutil
import time
from typing import Dict, List
from dataclasses import dataclass
from prometheus_client import Gauge, Counter, Histogram
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
cpu_usage = Gauge('tool_cpu_usage_percent', 'CPU usage percentage', ['tool_name'])
memory_usage = Gauge('tool_memory_usage_mb', 'Memory usage in MB', ['tool_name'])
disk_io = Counter('tool_disk_io_bytes', 'Disk I/O bytes', ['tool_name', 'operation'])
network_io = Counter('tool_network_io_bytes', 'Network I/O bytes', ['tool_name', 'direction'])
test_execution_time = Histogram('test_execution_duration_seconds', 'Test execution time', ['test_type'])

@dataclass
class PerformanceMetrics:
    cpu_percent: float
    memory_mb: float
    disk_read_mb: float
    disk_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    timestamp: float

class ToolPerformanceMonitor:
    """Monitor performance of testing tools"""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.process = None
        self.baseline_metrics = None
        self.monitoring_active = False

    def find_process(self) -> bool:
        """Find the tool process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if self.tool_name.lower() in ' '.join(proc.info['cmdline'] or []).lower():
                    self.process = psutil.Process(proc.info['pid'])
                    logger.info(f"Found {self.tool_name} process: PID {proc.info['pid']}")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        if not self.process:
            return None

        try:
            cpu_percent = self.process.cpu_percent(interval=1)
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            # Disk I/O
            io_counters = self.process.io_counters()
            disk_read_mb = io_counters.read_bytes / 1024 / 1024 if io_counters else 0
            disk_write_mb = io_counters.write_bytes / 1024 / 1024 if io_counters else 0

            # Network I/O (system-wide for simplicity)
            net_counters = psutil.net_io_counters()
            network_sent_mb = net_counters.bytes_sent / 1024 / 1024
            network_recv_mb = net_counters.bytes_recv / 1024 / 1024

            return PerformanceMetrics(
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                disk_read_mb=disk_read_mb,
                disk_write_mb=disk_write_mb,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                timestamp=time.time()
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error collecting metrics for {self.tool_name}: {e}")
            return None

    def establish_baseline(self, duration_seconds: int = 60):
        """Establish performance baseline"""
        logger.info(f"Establishing baseline for {self.tool_name}...")
        metrics_list = []

        for _ in range(duration_seconds // 5):
            metrics = self.collect_metrics()
            if metrics:
                metrics_list.append(metrics)
            time.sleep(5)

        if metrics_list:
            self.baseline_metrics = PerformanceMetrics(
                cpu_percent=sum(m.cpu_percent for m in metrics_list) / len(metrics_list),
                memory_mb=sum(m.memory_mb for m in metrics_list) / len(metrics_list),
                disk_read_mb=max(m.disk_read_mb for m in metrics_list),
                disk_write_mb=max(m.disk_write_mb for m in metrics_list),
                network_sent_mb=max(m.network_sent_mb for m in metrics_list),
                network_recv_mb=max(m.network_recv_mb for m in metrics_list),
                timestamp=time.time()
            )
            logger.info(f"Baseline established for {self.tool_name}")

    def monitor_continuous(self, interval_seconds: int = 30):
        """Continuously monitor performance"""
        self.monitoring_active = True
        logger.info(f"Starting continuous monitoring for {self.tool_name}")

        while self.monitoring_active:
            metrics = self.collect_metrics()
            if metrics:
                self._update_prometheus_metrics(metrics)
                self._check_thresholds(metrics)
                self._log_metrics(metrics)

            time.sleep(interval_seconds)

    def _update_prometheus_metrics(self, metrics: PerformanceMetrics):
        """Update Prometheus metrics"""
        cpu_usage.labels(tool_name=self.tool_name).set(metrics.cpu_percent)
        memory_usage.labels(tool_name=self.tool_name).set(metrics.memory_mb)
        disk_io.labels(tool_name=self.tool_name, operation='read').inc(metrics.disk_read_mb)
        disk_io.labels(tool_name=self.tool_name, operation='write').inc(metrics.disk_write_mb)
        network_io.labels(tool_name=self.tool_name, direction='sent').inc(metrics.network_sent_mb)
        network_io.labels(tool_name=self.tool_name, direction='recv').inc(metrics.network_recv_mb)

    def _check_thresholds(self, metrics: PerformanceMetrics):
        """Check if metrics exceed thresholds"""
        alerts = []

        if self.baseline_metrics:
            cpu_threshold = self.baseline_metrics.cpu_percent * 2
            memory_threshold = self.baseline_metrics.memory_mb * 1.5

            if metrics.cpu_percent > cpu_threshold:
                alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}% (baseline: {self.baseline_metrics.cpu_percent:.1f}%)")

            if metrics.memory_mb > memory_threshold:
                alerts.append(f"High memory usage: {metrics.memory_mb:.1f}MB (baseline: {self.baseline_metrics.memory_mb:.1f}MB)")

        if alerts:
            logger.warning(f"Performance alerts for {self.tool_name}: {', '.join(alerts)}")

    def _log_metrics(self, metrics: PerformanceMetrics):
        """Log current metrics"""
        logger.info(f"{self.tool_name} metrics - CPU: {metrics.cpu_percent:.1f}%, "
                   f"Memory: {metrics.memory_mb:.1f}MB, "
                   f"Disk R/W: {metrics.disk_read_mb:.1f}/{metrics.disk_write_mb:.1f}MB")

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        logger.info(f"Stopped monitoring for {self.tool_name}")

class JMeterPerformanceMonitor(ToolPerformanceMonitor):
    """JMeter specific performance monitor"""

    def __init__(self):
        super().__init__("jmeter")

    def monitor_test_execution(self, test_plan_path: str):
        """Monitor JMeter test execution"""
        with test_execution_time.labels(test_type='jmeter').time():
            # Execute JMeter test and monitor performance
            start_time = time.time()

            # Here would be the JMeter execution logic
            # For now, simulate monitoring
            self.monitor_continuous(interval_seconds=10)

            execution_time = time.time() - start_time
            logger.info(f"JMeter test completed in {execution_time:.2f} seconds")

class SparkPerformanceMonitor(ToolPerformanceMonitor):
    """Spark specific performance monitor"""

    def __init__(self):
        super().__init__("spark")

    def monitor_job_execution(self, job_name: str):
        """Monitor Spark job execution"""
        with test_execution_time.labels(test_type='spark').time():
            logger.info(f"Monitoring Spark job: {job_name}")
            self.monitor_continuous(interval_seconds=15)

# Usage example
if __name__ == "__main__":
    # Monitor JMeter performance
    jmeter_monitor = JMeterPerformanceMonitor()
    if jmeter_monitor.find_process():
        jmeter_monitor.establish_baseline()
        jmeter_monitor.monitor_continuous(interval_seconds=30)

    # Monitor Spark performance
    spark_monitor = SparkPerformanceMonitor()
    if spark_monitor.find_process():
        spark_monitor.establish_baseline()
        spark_monitor.monitor_continuous(interval_seconds=60)