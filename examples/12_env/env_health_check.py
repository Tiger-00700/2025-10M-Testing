#!/usr/bin/env python3
"""
环境健康检查脚本
Environment Health Check Script

用于检查大数据测试环境的整体健康状态，包括基础设施、依赖服务和测试资源。
"""

import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    component: str
    status: str  # 'healthy', 'warning', 'critical'
    message: str
    details: Dict[str, Any]
    timestamp: datetime


class EnvironmentHealthChecker:
    """环境健康检查器"""

    def __init__(self):
        self.results: List[HealthCheckResult] = []
        self.checks = {
            'infrastructure': self._check_infrastructure,
            'dependencies': self._check_dependencies,
            'storage': self._check_storage,
            'network': self._check_network,
            'security': self._check_security
        }

    def run_all_checks(self) -> List[HealthCheckResult]:
        """运行所有健康检查"""
        print("开始环境健康检查...")

        for check_name, check_func in self.checks.items():
            print(f"检查 {check_name}...")
            try:
                result = check_func()
                self.results.append(result)
                status_icon = "✅" if result.status == "healthy" else "⚠️" if result.status == "warning" else "❌"
                print(f"  {status_icon} {result.component}: {result.message}")
            except Exception as e:
                error_result = HealthCheckResult(
                    component=check_name,
                    status="critical",
                    message=f"检查失败: {str(e)}",
                    details={"error": str(e)},
                    timestamp=datetime.now()
                )
                self.results.append(error_result)
                print(f"  ❌ {check_name}: 检查失败 - {str(e)}")

        return self.results

    def _check_infrastructure(self) -> HealthCheckResult:
        """检查基础设施"""
        details = {}

        # 检查CPU使用率
        try:
            result = subprocess.run(['wmic', 'cpu', 'get', 'loadpercentage'],
                                  capture_output=True, text=True, timeout=10)
            cpu_usage = result.stdout.strip().split('\n')[-1]
            details['cpu_usage'] = f"{cpu_usage}%"
        except:
            details['cpu_usage'] = "unknown"

        # 检查内存使用率
        try:
            result = subprocess.run(['wmic', 'os', 'get', 'freephysicalmemory,totalvisiblememorysize'],
                                  capture_output=True, text=True, timeout=10)
            mem_info = result.stdout.strip().split('\n')[-1].split()
            if len(mem_info) >= 2:
                free_mem = int(mem_info[0])
                total_mem = int(mem_info[1])
                mem_usage = ((total_mem - free_mem) / total_mem) * 100
                details['memory_usage'] = ".1f"
        except:
            details['memory_usage'] = "unknown"

        # 检查磁盘空间
        try:
            result = subprocess.run(['wmic', 'logicaldisk', 'get', 'size,freespace,caption'],
                                  capture_output=True, text=True, timeout=10)
            disk_info = result.stdout.strip().split('\n')[1:]  # 跳过标题行
            disk_usage = []
            for line in disk_info:
                parts = line.split()
                if len(parts) >= 3:
                    drive = parts[0]
                    free = int(parts[1])
                    total = int(parts[2])
                    usage = ((total - free) / total) * 100
                    disk_usage.append(f"{drive}: {usage:.1f}%")
            details['disk_usage'] = disk_usage
        except:
            details['disk_usage'] = "unknown"

        # 判断整体状态
        status = "healthy"
        message = "基础设施运行正常"

        # 检查是否有高负载
        if details.get('cpu_usage', '0').replace('%', '').isdigit():
            cpu_val = float(details['cpu_usage'].replace('%', ''))
            if cpu_val > 90:
                status = "critical"
                message = f"CPU使用率过高: {cpu_val}%"
            elif cpu_val > 70:
                status = "warning"
                message = f"CPU使用率较高: {cpu_val}%"

        return HealthCheckResult(
            component="基础设施",
            status=status,
            message=message,
            details=details,
            timestamp=datetime.now()
        )

    def _check_dependencies(self) -> HealthCheckResult:
        """检查依赖服务"""
        details = {}

        # 检查Python版本
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        details['python_version'] = python_version

        # 检查关键模块
        required_modules = ['pytest', 'docker', 'kubernetes', 'requests', 'pandas', 'numpy']
        missing_modules = []

        for module in required_modules:
            try:
                __import__(module)
                details[f'{module}_available'] = True
            except ImportError:
                details[f'{module}_available'] = False
                missing_modules.append(module)

        # 检查Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=5)
            details['docker_version'] = result.stdout.strip()
            details['docker_available'] = True
        except:
            details['docker_available'] = False
            details['docker_version'] = "not found"

        # 判断状态
        if missing_modules:
            status = "warning"
            message = f"缺少关键模块: {', '.join(missing_modules)}"
        elif not details.get('docker_available', False):
            status = "warning"
            message = "Docker不可用，可能影响容器化测试"
        else:
            status = "healthy"
            message = "所有依赖服务正常"

        return HealthCheckResult(
            component="依赖服务",
            status=status,
            message=message,
            details=details,
            timestamp=datetime.now()
        )

    def _check_storage(self) -> HealthCheckResult:
        """检查存储系统"""
        details = {}

        # 检查测试数据目录
        test_dirs = ['test_data', 'examples', 'chapter']
        missing_dirs = []

        for dir_name in test_dirs:
            if not os.path.exists(dir_name):
                missing_dirs.append(dir_name)
            else:
                # 检查目录大小
                try:
                    result = subprocess.run(['du', '-sh', dir_name],
                                          capture_output=True, text=True, timeout=10)
                    size = result.stdout.strip().split()[0]
                    details[f'{dir_name}_size'] = size
                except:
                    details[f'{dir_name}_size'] = "unknown"

        details['missing_dirs'] = missing_dirs

        # 判断状态
        if missing_dirs:
            status = "warning"
            message = f"缺少测试目录: {', '.join(missing_dirs)}"
        else:
            status = "healthy"
            message = "存储系统正常"

        return HealthCheckResult(
            component="存储系统",
            status=status,
            message=message,
            details=details,
            timestamp=datetime.now()
        )

    def _check_network(self) -> HealthCheckResult:
        """检查网络连接"""
        details = {}

        # 检查网络连接
        test_urls = ['https://www.google.com', 'https://github.com', 'https://pypi.org']
        connectivity = {}

        for url in test_urls:
            try:
                import requests
                response = requests.get(url, timeout=5)
                connectivity[url] = response.status_code == 200
            except:
                connectivity[url] = False

        details['connectivity'] = connectivity

        # 检查DNS解析
        try:
            import socket
            test_domains = ['github.com', 'pypi.org', 'docker.io']
            dns_resolution = {}
            for domain in test_domains:
                try:
                    socket.gethostbyname(domain)
                    dns_resolution[domain] = True
                except:
                    dns_resolution[domain] = False
            details['dns_resolution'] = dns_resolution
        except:
            details['dns_resolution'] = "check failed"

        # 判断状态
        failed_connections = [url for url, status in connectivity.items() if not status]
        if failed_connections:
            status = "warning"
            message = f"网络连接问题: {len(failed_connections)} 个服务不可达"
        else:
            status = "healthy"
            message = "网络连接正常"

        return HealthCheckResult(
            component="网络连接",
            status=status,
            message=message,
            details=details,
            timestamp=datetime.now()
        )

    def _check_security(self) -> HealthCheckResult:
        """检查安全配置"""
        details = {}

        # 检查文件权限
        sensitive_files = ['config.yml', 'secrets.json', '.env']
        permission_issues = []

        for file_path in sensitive_files:
            if os.path.exists(file_path):
                # 检查文件权限 (Windows)
                try:
                    import stat
                    file_stat = os.stat(file_path)
                    mode = file_stat.st_mode
                    if mode & stat.S_IRGRP or mode & stat.S_IROTH:
                        permission_issues.append(f"{file_path}: 可被其他用户读取")
                except:
                    pass

        details['permission_issues'] = permission_issues

        # 检查敏感信息泄露
        leak_patterns = ['password', 'secret', 'key', 'token']
        potential_leaks = []

        # 简单的文件扫描 (仅检查配置文件)
        config_files = ['config.yml', 'settings.json', '.env']
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        for pattern in leak_patterns:
                            if pattern in content:
                                potential_leaks.append(f"{config_file}: 可能包含{pattern}")
                                break
                except:
                    pass

        details['potential_leaks'] = potential_leaks

        # 判断状态
        if permission_issues or potential_leaks:
            status = "warning"
            issues = len(permission_issues) + len(potential_leaks)
            message = f"发现 {issues} 个安全问题"
        else:
            status = "healthy"
            message = "安全配置正常"

        return HealthCheckResult(
            component="安全配置",
            status=status,
            message=message,
            details=details,
            timestamp=datetime.now()
        )

    def generate_report(self) -> str:
        """生成健康检查报告"""
        report = []
        report.append("# 环境健康检查报告")
        report.append(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # 汇总状态
        healthy_count = sum(1 for r in self.results if r.status == "healthy")
        warning_count = sum(1 for r in self.results if r.status == "warning")
        critical_count = sum(1 for r in self.results if r.status == "critical")

        report.append("## 检查汇总")
        report.append(f"- 健康组件: {healthy_count}")
        report.append(f"- 警告组件: {warning_count}")
        report.append(f"- 严重问题: {critical_count}")
        report.append("")

        # 详细结果
        report.append("## 详细结果")
        for result in self.results:
            status_icon = "✅" if result.status == "healthy" else "⚠️" if result.status == "warning" else "❌"
            report.append(f"### {status_icon} {result.component}")
            report.append(f"状态: {result.status}")
            report.append(f"信息: {result.message}")
            report.append("详情:"            report.append("```json")
            report.append(json.dumps(result.details, indent=2, ensure_ascii=False))
            report.append("```")
            report.append("")

        return "\n".join(report)


def main():
    """主函数"""
    checker = EnvironmentHealthChecker()
    results = checker.run_all_checks()

    # 输出到控制台
    print("\n" + "="*50)
    print("环境健康检查完成")
    print("="*50)

    # 生成报告
    report = checker.generate_report()
    print(report)

    # 保存报告
    report_file = f"health_check_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n报告已保存到: {report_file}")

    # 返回退出码
    critical_count = sum(1 for r in results if r.status == "critical")
    return 1 if critical_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())