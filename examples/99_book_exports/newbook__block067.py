
# 【章节重点难点总结】

# - 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准
# - 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡

# 【课后思考/练习题】

# 1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
# 2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。


## 自动化故障注入测试框架

# 【阅读提示】本篇聚焦：自动化故障注入测试框架。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

import time
import subprocess
import docker
import random
import threading
from kubernetes import client, config

class FaultInjectionTester:
    def __init__(self, config):
        self.config = config
        self.faults_injected = []
        self.results = []

        # 根据配置初始化相应的客户端
        if config.get('environment') == 'docker':
            self.docker_client = docker.from_env()
        elif config.get('environment') == 'kubernetes':
            config.load_kube_config(config_file=config.get('kube_config'))
            self.k8s_core_v1 = client.CoreV1Api()
            self.k8s_apps_v1 = client.AppsV1Api()

    def inject_network_delay(self, target, delay_ms, duration=60):
        """注入网络延迟"""
        fault_id = f"network_delay_{int(time.time())}"

        try:
            if self.config.get('environment') == 'docker':
                # 使用Docker进行网络延迟注入
                container = self.docker_client.containers.get(target)

                # 使用tc命令添加延迟
                cmd = f"tc qdisc add dev eth0 root netem delay {delay_ms}ms"
                container.exec_run(cmd)

                # 记录故障信息
                self.faults_injected.append({
                    'id': fault_id,
                    'type': 'network_delay',
                    'target': target,
                    'parameters': {'delay_ms': delay_ms},
                    'start_time': time.time()
                })

                # 设置定时器恢复网络
                threading.Timer(duration, self._remove_network_delay, args=[target]).start()

                print(f"已向容器 {target} 注入 {delay_ms}ms 网络延迟，将在 {duration} 秒后恢复")

            elif self.config.get('environment') == 'kubernetes':
                # 在Kubernetes中注入网络延迟
                pod_name = target
                namespace = self.config.get('namespace', 'default')

                # 使用kubectl exec在Pod中执行tc命令
                cmd = [
                    'kubectl', 'exec', pod_name, '-n', namespace, '--',
                    'tc', 'qdisc', 'add', 'dev', 'eth0', 'root', 'netem', 'delay', f'{delay_ms}ms'
                ]
                subprocess.run(cmd, check=True)

                # 记录故障信息
                self.faults_injected.append({
                    'id': fault_id,
                    'type': 'network_delay',
                    'target': target,
                    'parameters': {'delay_ms': delay_ms},
                    'start_time': time.time()
                })

                # 设置定时器恢复网络
                threading.Timer(duration, self._remove_network_delay, args=[target, namespace]).start()

                print(f"已向Pod {namespace}/{pod_name} 注入 {delay_ms}ms 网络延迟，将在 {duration} 秒后恢复")

            return fault_id
        except Exception as e:
            print(f"注入网络延迟失败: {e}")
            return None

    def _remove_network_delay(self, target, namespace=None):
        """移除网络延迟"""
        try:
            if self.config.get('environment') == 'docker':
                container = self.docker_client.containers.get(target)
                cmd = "tc qdisc del dev eth0 root"
                container.exec_run(cmd)
                print(f"已恢复容器 {target} 的网络")
            elif self.config.get('environment') == 'kubernetes':
                pod_name = target
                if not namespace:
                    namespace = self.config.get('namespace', 'default')

                cmd = [
                    'kubectl', 'exec', pod_name, '-n', namespace, '--',
                    'tc', 'qdisc', 'del', 'dev', 'eth0', 'root'
                ]
                subprocess.run(cmd, check=True)
                print(f"已恢复Pod {namespace}/{pod_name} 的网络")
        except Exception as e:
            print(f"恢复网络失败: {e}")

    def inject_container_kill(self, target, restart=True):
        """杀死容器"""
        fault_id = f"container_kill_{int(time.time())}"

        try:
            if self.config.get('environment') == 'docker':
                container = self.docker_client.containers.get(target)
                container.kill()

                if restart:
                    container.start()
                    print(f"已杀死并重启容器 {target}")
                else:
                    print(f"已杀死容器 {target}")

                # 记录故障信息
                self.faults_injected.append({
                    'id': fault_id,
                    'type': 'container_kill',
                    'target': target,
                    'parameters': {'restart': restart},
                    'timestamp': time.time()
                })

            elif self.config.get('environment') == 'kubernetes':
                pod_name = target
                namespace = self.config.get('namespace', 'default')

                # 删除Pod（Kubernetes会自动重启，如果配置了适当的重启策略）
                self.k8s_core_v1.delete_namespaced_pod(pod_name, namespace)
                print(f"已删除Pod {namespace}/{pod_name}")

                # 记录故障信息
                self.faults_injected.append({
                    'id': fault_id,
                    'type': 'pod_kill',
                    'target': target,
                    'parameters': {'namespace': namespace},
                    'timestamp': time.time()
                })

            return fault_id
        except Exception as e:
            print(f"杀死容器失败: {e}")
            return None

    def inject_cpu_stress(self, target, cpu_percent=100, duration=60):
        """注入CPU压力"""
        fault_id = f"cpu_stress_{int(time.time())}"

        try:
            if self.config.get('environment') == 'docker':
                container = self.docker_client.containers.get(target)

                # 在容器中运行stress命令
                stress_cmd = f"stress --cpu {cpu_percent} --timeout {duration}s"
                exec_id = container.exec_run(stress_cmd, detach=True)

                # 记录故障信息
                self.faults_injected.append({
                    'id': fault_id,
                    'type': 'cpu_stress',
                    'target': target,
                    'parameters': {'cpu_percent': cpu_percent, 'duration': duration},
                    'exec_id': exec_id,
                    'start_time': time.time()
                })

                print(f"已向容器 {target} 注入CPU压力 ({cpu_percent}%)，将持续 {duration} 秒")

            elif self.config.get('environment') == 'kubernetes':
                pod_name = target
                namespace = self.config.get('namespace', 'default')

                # 在Pod中运行stress命令
                cmd = [
                    'kubectl', 'exec', pod_name, '-n', namespace, '--',
                    'stress', '--cpu', str(cpu_percent), '--timeout', f'{duration}s'
                ]
                subprocess.Popen(cmd)  # 非阻塞执行

                # 记录故障信息
                self.faults_injected.append({
                    'id': fault_id,
                    'type': 'cpu_stress',
                    'target': target,
                    'parameters': {'cpu_percent': cpu_percent, 'duration': duration, 'namespace': namespace},
                    'start_time': time.time()
                })

                print(f"已向Pod {namespace}/{pod_name} 注入CPU压力 ({cpu_percent}%)，将持续 {duration} 秒")

            return fault_id
        except Exception as e:
            print(f"注入CPU压力失败: {e}")
            return None

    def inject_memory_stress(self, target, memory_mb, duration=60):
        """注入内存压力"""
        fault_id = f"memory_stress_{int(time.time())}"

        try:
            if self.config.get('environment') == 'docker':
                container = self.docker_client.containers.get(target)

                # 在容器中运行stress命令
                stress_cmd = f"stress --vm 1 --vm-bytes {memory_mb}M --timeout {duration}s"
                exec_id = container.exec_run(stress_cmd, detach=True)

                # 记录故障信息
                self.faults_injected.append({
                    'id': fault_id,
                    'type': 'memory_stress',
                    'target': target,
                    'parameters': {'memory_mb': memory_mb, 'duration': duration},
                    'exec_id': exec_id,
                    'start_time': time.time()
                })

                print(f"已向容器 {target} 注入内存压力 ({memory_mb}MB)，将持续 {duration} 秒")

            elif self.config.get('environment') == 'kubernetes':
                pod_name = target
                namespace = self.config.get('namespace', 'default')

                # 在Pod中运行stress命令
                cmd = [
                    'kubectl', 'exec', pod_name, '-n', namespace, '--',
                    'stress', '--vm', '1', '--vm-bytes', f'{memory_mb}M', '--timeout', f'{duration}s'
                ]
                subprocess.Popen(cmd)  # 非阻塞执行

                # 记录故障信息
                self.faults_injected.append({
                    'id': fault_id,
                    'type': 'memory_stress',
                    'target': target,
                    'parameters': {'memory_mb': memory_mb, 'duration': duration, 'namespace': namespace},
                    'start_time': time.time()
                })

                print(f"已向Pod {namespace}/{pod_name} 注入内存压力 ({memory_mb}MB)，将持续 {duration} 秒")

            return fault_id
        except Exception as e:
            print(f"注入内存压力失败: {e}")
            return None

    def run_fault_injection_suite(self, suite_config):
        """运行故障注入测试套件"""
        print(f"开始运行故障注入测试套件: {suite_config.get('name', 'Unnamed Suite')}")

        for fault_config in suite_config.get('faults', []):
            fault_type = fault_config.get('type')
            target = fault_config.get('target')
            params = fault_config.get('parameters', {})
            wait_before_next = fault_config.get('wait_before_next', 30)

            print(f"\n注入故障: {fault_type} 到 {target}")

            # 注入故障
            if fault_type == 'network_delay':
                self.inject_network_delay(
                    target=target,
                    delay_ms=params.get('delay_ms', 1000),
                    duration=params.get('duration', 60)
                )
            elif fault_type == 'container_kill':
                self.inject_container_kill(
                    target=target,
                    restart=params.get('restart', True)
                )
            elif fault_type == 'cpu_stress':
                self.inject_cpu_stress(
                    target=target,
                    cpu_percent=params.get('cpu_percent', 100),
                    duration=params.get('duration', 60)
                )
            elif fault_type == 'memory_stress':
                self.inject_memory_stress(
                    target=target,
                    memory_mb=params.get('memory_mb', 512),
                    duration=params.get('duration', 60)
                )
            else:
                print(f"未知的故障类型: {fault_type}")

            # 等待指定时间再执行下一个故障
            if wait_before_next > 0:
                print(f"等待 {wait_before_next} 秒再执行下一个故障...")
                time.sleep(wait_before_next)

        print("\n故障注入测试套件执行完成")

    def verify_system_recovery(self, verification_func, timeout=300):
        """验证系统恢复情况"""
        print("开始验证系统恢复情况...")

        start_time = time.time()
        max_time = start_time + timeout

        while time.time() < max_time:
            try:
                # 执行验证函数
                is_recovered = verification_func()

                if is_recovered:
                    recovery_time = time.time() - start_time
                    print(f"系统已恢复，恢复时间: {recovery_time:.2f} 秒")

                    # 记录结果
                    self.results.append({
                        'verification_time': time.time(),
                        'is_recovered': True,
                        'recovery_time': recovery_time
                    })

                    return True
            except Exception as e:
                print(f"验证过程中出错: {e}")

            # 等待一段时间再重试
            print("系统尚未恢复，继续等待...")
            time.sleep(10)

        # 超时
        print("系统恢复验证超时")

        # 记录结果
        self.results.append({
            'verification_time': time.time(),
            'is_recovered': False,
            'recovery_time': None
        })

        return False

# ## 使用示例 （来自：第5篇-第17章-大数据测试自动化【进阶】）

# 【阅读提示】本篇聚焦：使用示例 （来自：第5篇-第17章-大数据测试自动化【进阶】）。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

def run_fault_injection_demo():
    # 配置故障注入测试器
    config = {
        'environment': 'docker',  # 或 'kubernetes'
        'namespace': 'default',  # 仅用于Kubernetes
        'kube_config': '~/.kube/config'  # 仅用于Kubernetes
    }

    # 初始化测试器
    tester = FaultInjectionTester(config)

    # 定义系统恢复验证函数
    def verify_hdfs_recovery():
        # 示例：检查HDFS是否恢复
        # 实际实现中可能需要调用HDFS API或执行命令来检查
        try:
            # 这里应该是实际的验证逻辑
            # 例如：检查NameNode状态、执行简单的HDFS操作等
            print("执行HDFS恢复验证...")
            # 模拟恢复成功
            return True
        except Exception:
            return False

    # 定义故障注入套件
    fault_suite = {
        'name': 'HDFS高可用测试套件',
        'faults': [
            {
                'type': 'network_delay',
                'target': 'namenode1',  # 目标容器或Pod名称
                'parameters': {
                    'delay_ms': 5000,  # 5秒延迟
                    'duration': 60      # 持续60秒
                },
                'wait_before_next': 30  # 等待30秒再执行下一个故障
            },
            {
                'type': 'container_kill',
                'target': 'namenode1',
                'parameters': {
                    'restart': True
                },
                'wait_before_next': 60
            },
            {
                'type': 'cpu_stress',
                'target': 'datanode1',
                'parameters': {
                    'cpu_percent': 100,
                    'duration': 120
                },
                'wait_before_next': 30
            },
            {
                'type': 'memory_stress',
                'target': 'datanode2',
                'parameters': {
                    'memory_mb': 1024,
                    'duration': 120
                },
                'wait_before_next': 0
            }
        ]
    }

    # 运行故障注入测试套件
    tester.run_fault_injection_suite(fault_suite)

    # 验证系统恢复
    tester.verify_system_recovery(verify_hdfs_recovery, timeout=600)

    # 输出测试结果
    print("\n故障注入测试结果:")
    for fault in tester.faults_injected:
        print(f"- {fault['type']} 到 {fault['target']}: {fault['parameters']}")

    for result in tester.results:
        status = "成功恢复" if result['is_recovered'] else "未恢复"
        recovery_time = result['recovery_time'] if result['is_recovered'] else "N/A"
        print(f"- 系统状态: {status}, 恢复时间: {recovery_time}秒")