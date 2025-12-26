#!/usr/bin/env python3
"""
大数据测试环境健康检查脚本

用于检查测试环境的各项指标，确保环境稳定性和可靠性。
支持容器化环境、本地环境和云环境的健康检查。
"""

import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
import psutil
import requests
from dataclasses import dataclass

@dataclass
class HealthCheckResult:
    """健康检查结果数据类"""
    component: str
    status: str  # 'healthy', 'warning', 'critical'
    message: str
    timestamp: datetime
    metrics: Dict[str, float]

class BigDataTestEnvironmentChecker:
    """大数据测试环境健康检查器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.results: List[HealthCheckResult] = []

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        default_config = {
            "checks": {
                "cpu_usage": {"threshold": 80.0, "enabled": True},
                "memory_usage": {"threshold": 85.0, "enabled": True},
                "disk_usage": {"threshold": 90.0, "enabled": True},
                "network_connectivity": {"enabled": True},
                "database_connectivity": {"enabled": True},
                "message_queue": {"enabled": True},
                "container_health": {"enabled": True}
            },
            "services": {
                "spark_master": "spark://localhost:7077",
                "hadoop_namenode": "hdfs://localhost:9000",
                "kafka_brokers": ["localhost:9092"],
                "elasticsearch": "http://localhost:9200"
            }
        }

        if config_path:
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Failed to load config {config_path}: {e}")

        return default_config

    def run_all_checks(self) -> List[HealthCheckResult]:
        """运行所有健康检查"""
        print("Starting comprehensive health check...")

        # 系统资源检查
        self._check_system_resources()

        # 网络连接检查
        self._check_network_connectivity()

        # 服务可用性检查
        self._check_service_availability()

        # 容器健康检查
        self._check_container_health()

        # 数据存储检查
        self._check_data_storage()

        print(f"Health check completed. {len(self.results)} checks performed.")
        return self.results

    def _check_system_resources(self):
        """检查系统资源使用情况"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        status = 'healthy' if cpu_percent < self.config['checks']['cpu_usage']['threshold'] else 'warning'
        if cpu_percent >= 95:
            status = 'critical'

        self.results.append(HealthCheckResult(
            component="CPU Usage",
            status=status,
            message=f"CPU usage: {cpu_percent:.1f}%",
            timestamp=datetime.now(),
            metrics={"cpu_percent": cpu_percent}
        ))

        # 内存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        status = 'healthy' if memory_percent < self.config['checks']['memory_usage']['threshold'] else 'warning'
        if memory_percent >= 95:
            status = 'critical'

        self.results.append(HealthCheckResult(
            component="Memory Usage",
            status=status,
            message=f"Memory usage: {memory_percent:.1f}% ({memory.used/1024/1024/1024:.1f}GB used)",
            timestamp=datetime.now(),
            metrics={"memory_percent": memory_percent, "memory_used_gb": memory.used/1024/1024/1024}
        ))

        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        status = 'healthy' if disk_percent < self.config['checks']['disk_usage']['threshold'] else 'warning'
        if disk_percent >= 95:
            status = 'critical'

        self.results.append(HealthCheckResult(
            component="Disk Usage",
            status=status,
            message=f"Disk usage: {disk_percent:.1f}% ({disk.used/1024/1024/1024:.1f}GB used)",
            timestamp=datetime.now(),
            metrics={"disk_percent": disk_percent, "disk_used_gb": disk.used/1024/1024/1024}
        ))

    def _check_network_connectivity(self):
        """检查网络连接"""
        test_urls = [
            "https://www.google.com",
            "https://httpbin.org/status/200"
        ]

        success_count = 0
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    success_count += 1
            except Exception as e:
                print(f"Network check failed for {url}: {e}")

        status = 'healthy' if success_count >= len(test_urls) * 0.8 else 'warning'
        if success_count == 0:
            status = 'critical'

        self.results.append(HealthCheckResult(
            component="Network Connectivity",
            status=status,
            message=f"Network connectivity: {success_count}/{len(test_urls)} endpoints reachable",
            timestamp=datetime.now(),
            metrics={"reachable_endpoints": success_count, "total_endpoints": len(test_urls)}
        ))

    def _check_service_availability(self):
        """检查大数据服务可用性"""
        services = self.config.get('services', {})

        # Spark Master
        if 'spark_master' in services:
            self._check_spark_master(services['spark_master'])

        # Hadoop NameNode
        if 'hadoop_namenode' in services:
            self._check_hadoop_namenode(services['hadoop_namenode'])

        # Kafka Brokers
        if 'kafka_brokers' in services:
            self._check_kafka_brokers(services['kafka_brokers'])

        # Elasticsearch
        if 'elasticsearch' in services:
            self._check_elasticsearch(services['elasticsearch'])

    def _check_spark_master(self, master_url: str):
        """检查Spark Master状态"""
        try:
            # 这里应该使用Spark REST API
            # 简化版本：检查端口是否可达
            import socket
            host, port = master_url.replace('spark://', '').split(':')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, int(port)))
            sock.close()

            status = 'healthy' if result == 0 else 'critical'
            message = "Spark Master is accessible" if result == 0 else "Spark Master is not accessible"

            self.results.append(HealthCheckResult(
                component="Spark Master",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={"port_accessible": 1 if result == 0 else 0}
            ))
        except Exception as e:
            self.results.append(HealthCheckResult(
                component="Spark Master",
                status='critical',
                message=f"Spark Master check failed: {e}",
                timestamp=datetime.now(),
                metrics={"error": 1}
            ))

    def _check_hadoop_namenode(self, namenode_url: str):
        """检查Hadoop NameNode状态"""
        try:
            # 简化检查：尝试连接NameNode端口
            import socket
            host, port = namenode_url.replace('hdfs://', '').split(':')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, int(port)))
            sock.close()

            status = 'healthy' if result == 0 else 'critical'
            message = "Hadoop NameNode is accessible" if result == 0 else "Hadoop NameNode is not accessible"

            self.results.append(HealthCheckResult(
                component="Hadoop NameNode",
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={"port_accessible": 1 if result == 0 else 0}
            ))
        except Exception as e:
            self.results.append(HealthCheckResult(
                component="Hadoop NameNode",
                status='critical',
                message=f"Hadoop NameNode check failed: {e}",
                timestamp=datetime.now(),
                metrics={"error": 1}
            ))

    def _check_kafka_brokers(self, brokers: List[str]):
        """检查Kafka Brokers状态"""
        healthy_brokers = 0
        for broker in brokers:
            try:
                host, port = broker.split(':')
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, int(port)))
                sock.close()
                if result == 0:
                    healthy_brokers += 1
            except:
                pass

        status = 'healthy' if healthy_brokers >= len(brokers) * 0.5 else 'warning'
        if healthy_brokers == 0:
            status = 'critical'

        self.results.append(HealthCheckResult(
            component="Kafka Brokers",
            status=status,
            message=f"Kafka brokers: {healthy_brokers}/{len(brokers)} healthy",
            timestamp=datetime.now(),
            metrics={"healthy_brokers": healthy_brokers, "total_brokers": len(brokers)}
        ))

    def _check_elasticsearch(self, es_url: str):
        """检查Elasticsearch状态"""
        try:
            response = requests.get(f"{es_url}/_cluster/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                cluster_status = health_data.get('status', 'unknown')
                status_map = {'green': 'healthy', 'yellow': 'warning', 'red': 'critical'}
                status = status_map.get(cluster_status, 'warning')

                self.results.append(HealthCheckResult(
                    component="Elasticsearch",
                    status=status,
                    message=f"Elasticsearch cluster status: {cluster_status}",
                    timestamp=datetime.now(),
                    metrics={"cluster_status": cluster_status}
                ))
            else:
                self.results.append(HealthCheckResult(
                    component="Elasticsearch",
                    status='critical',
                    message=f"Elasticsearch API returned status {response.status_code}",
                    timestamp=datetime.now(),
                    metrics={"http_status": response.status_code}
                ))
        except Exception as e:
            self.results.append(HealthCheckResult(
                component="Elasticsearch",
                status='critical',
                message=f"Elasticsearch check failed: {e}",
                timestamp=datetime.now(),
                metrics={"error": 1}
            ))

    def _check_container_health(self):
        """检查容器健康状态"""
        try:
            # 检查Docker是否运行
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # 解析容器数量
                lines = result.stdout.strip().split('\n')
                container_count = len(lines) - 1  # 减去表头

                self.results.append(HealthCheckResult(
                    component="Docker Containers",
                    status='healthy',
                    message=f"Docker is running with {container_count} containers",
                    timestamp=datetime.now(),
                    metrics={"container_count": container_count}
                ))
            else:
                self.results.append(HealthCheckResult(
                    component="Docker Containers",
                    status='critical',
                    message="Docker is not running or accessible",
                    timestamp=datetime.now(),
                    metrics={"docker_running": 0}
                ))
        except Exception as e:
            self.results.append(HealthCheckResult(
                component="Docker Containers",
                status='critical',
                message=f"Container check failed: {e}",
                timestamp=datetime.now(),
                metrics={"error": 1}
            ))

    def _check_data_storage(self):
        """检查数据存储状态"""
        # 这里可以添加对HDFS、S3等存储的检查
        # 简化版本：检查本地数据目录
        import os
        data_dirs = ['/tmp/test_data', './test_data', '/data']

        accessible_dirs = 0
        for data_dir in data_dirs:
            if os.path.exists(data_dir) and os.access(data_dir, os.R_OK):
                accessible_dirs += 1

        status = 'healthy' if accessible_dirs > 0 else 'warning'

        self.results.append(HealthCheckResult(
            component="Data Storage",
            status=status,
            message=f"Data directories: {accessible_dirs}/{len(data_dirs)} accessible",
            timestamp=datetime.now(),
            metrics={"accessible_dirs": accessible_dirs, "total_dirs": len(data_dirs)}
        ))

    def generate_report(self) -> str:
        """生成健康检查报告"""
        report = []
        report.append("# 大数据测试环境健康检查报告")
        report.append(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # 统计信息
        total_checks = len(self.results)
        healthy_count = sum(1 for r in self.results if r.status == 'healthy')
        warning_count = sum(1 for r in self.results if r.status == 'warning')
        critical_count = sum(1 for r in self.results if r.status == 'critical')

        report.append("## 检查统计")
        report.append(f"- 总检查项: {total_checks}")
        report.append(f"- 健康: {healthy_count}")
        report.append(f"- 警告: {warning_count}")
        report.append(f"- 严重: {critical_count}")
        report.append("")

        # 详细结果
        report.append("## 详细结果")
        for result in self.results:
            status_icon = {
                'healthy': '✅',
                'warning': '⚠️',
                'critical': '❌'
            }.get(result.status, '❓')

            report.append(f"### {status_icon} {result.component}")
            report.append(f"- 状态: {result.status}")
            report.append(f"- 消息: {result.message}")
            report.append(f"- 时间: {result.timestamp.strftime('%H:%M:%S')}")

            if result.metrics:
                report.append("- 指标:")
                for key, value in result.metrics.items():
                    if isinstance(value, float):
                        report.append(f"  - {key}: {value:.2f}")
                    else:
                        report.append(f"  - {key}: {value}")
            report.append("")

        # 建议
        report.append("## 建议")
        if critical_count > 0:
            report.append("⚠️ 发现严重问题，请立即处理！")
        elif warning_count > 0:
            report.append("⚠️ 发现警告问题，建议及时处理。")
        else:
            report.append("✅ 所有检查通过，环境运行正常。")

        return "\n".join(report)

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='大数据测试环境健康检查')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--output', help='输出报告文件路径')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')

    args = parser.parse_args()

    checker = BigDataTestEnvironmentChecker(args.config)
    results = checker.run_all_checks()

    if args.json:
        # JSON输出
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'results': [
                {
                    'component': r.component,
                    'status': r.status,
                    'message': r.message,
                    'timestamp': r.timestamp.isoformat(),
                    'metrics': r.metrics
                } for r in results
            ]
        }
        output = json.dumps(output_data, indent=2, ensure_ascii=False)
    else:
        # Markdown报告
        output = checker.generate_report()

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()</content>
<parameter name="filePath">e:\DONT_TOUCH\10M-2025-Testing\examples\31_chapter\env_health_check.py