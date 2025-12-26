# 云原生测试工具链
# Cloud-Native Testing Toolchain

## 概述 (Overview)
云原生测试工具链提供Kubernetes、Docker、Istio等云原生技术栈的全面测试支持，包括容器化测试、微服务测试、服务网格测试等。

## 核心组件 (Core Components)

### 1. Kubernetes测试框架 (Kubernetes Testing Framework)
```python
# examples/16_tools/kubernetes_test_framework.py
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import subprocess
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class K8sResourceType(Enum):
    """Kubernetes资源类型"""
    POD = "pod"
    SERVICE = "service"
    DEPLOYMENT = "deployment"
    STATEFULSET = "statefulset"
    DAEMONSET = "daemonset"
    JOB = "job"
    CRONJOB = "cronjob"
    CONFIGMAP = "configmap"
    SECRET = "secret"
    INGRESS = "ingress"
    PVC = "persistentvolumeclaim"
    PV = "persistentvolume"

class TestPhase(Enum):
    """测试阶段"""
    SETUP = "setup"
    EXECUTE = "execute"
    VERIFY = "verify"
    CLEANUP = "cleanup"

@dataclass
class K8sTestCase:
    """Kubernetes测试用例"""
    name: str
    namespace: str
    resources: List[Dict[str, Any]]
    test_commands: List[str]
    assertions: List[Dict[str, Any]]
    timeout: int
    retry_count: int

@dataclass
class K8sTestExecution:
    """Kubernetes测试执行"""
    execution_id: str
    test_case: K8sTestCase
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    results: Dict[str, Any]
    logs: List[str]
    resources_created: List[str]

class KubernetesTestFramework:
    """Kubernetes测试框架"""

    def __init__(self, kubeconfig_path: str = None):
        self.kubeconfig = kubeconfig_path or "~/.kube/config"
        self.test_cases: Dict[str, K8sTestCase] = {}
        self.active_executions: Dict[str, K8sTestExecution] = {}
        self.execution_history: List[K8sTestExecution] = []
        self.namespaces_created: List[str] = []

    def register_test_case(self, test_case: K8sTestCase):
        """注册测试用例"""
        self.test_cases[test_case.name] = test_case
        logger.info(f"Registered K8s test case: {test_case.name}")

    def execute_test_case(self, test_case_name: str) -> str:
        """执行测试用例"""
        if test_case_name not in self.test_cases:
            raise ValueError(f"Test case not found: {test_case_name}")

        test_case = self.test_cases[test_case_name]
        execution_id = f"{test_case_name}_{int(time.time())}"

        execution = K8sTestExecution(
            execution_id=execution_id,
            test_case=test_case,
            status='running',
            start_time=datetime.now(),
            results={},
            logs=[],
            resources_created=[]
        )

        self.active_executions[execution_id] = execution

        # 异步执行测试
        import threading
        thread = threading.Thread(target=self._execute_test_async, args=(execution,))
        thread.daemon = True
        thread.start()

        logger.info(f"Started K8s test execution: {execution_id}")
        return execution_id

    def _execute_test_async(self, execution: K8sTestExecution):
        """异步执行测试"""
        try:
            # 创建命名空间
            namespace = self._create_namespace(execution.test_case.namespace)
            execution.resources_created.append(f"namespace/{namespace}")

            # 部署资源
            deployed_resources = self._deploy_resources(
                execution.test_case.resources,
                namespace
            )
            execution.resources_created.extend(deployed_resources)

            # 等待资源就绪
            self._wait_for_resources_ready(deployed_resources, namespace)

            # 执行测试命令
            test_results = self._execute_test_commands(
                execution.test_case.test_commands,
                namespace
            )

            # 执行断言
            assertion_results = self._execute_assertions(
                execution.test_case.assertions,
                namespace
            )

            # 汇总结果
            execution.results = {
                'test_commands': test_results,
                'assertions': assertion_results,
                'resources_deployed': deployed_resources,
                'namespace': namespace
            }

            # 判断测试是否通过
            all_assertions_passed = all(
                assertion.get('passed', False)
                for assertion in assertion_results
            )

            execution.status = 'passed' if all_assertions_passed else 'failed'
            execution.end_time = datetime.now()

        except Exception as e:
            logger.error(f"K8s test execution failed: {str(e)}")
            execution.status = 'failed'
            execution.end_time = datetime.now()
            execution.results = {'error': str(e)}

        finally:
            # 保存到历史记录
            self.execution_history.append(execution)

            # 清理资源
            self._cleanup_resources(execution.resources_created)

    def _create_namespace(self, namespace: str) -> str:
        """创建命名空间"""
        try:
            # 检查命名空间是否已存在
            result = self._run_kubectl_command([
                "get", "namespace", namespace, "--ignore-not-found=true"
            ])

            if not result.strip():
                # 创建命名空间
                self._run_kubectl_command([
                    "create", "namespace", namespace
                ])
                self.namespaces_created.append(namespace)
                logger.info(f"Created namespace: {namespace}")

            return namespace

        except Exception as e:
            logger.error(f"Failed to create namespace {namespace}: {str(e)}")
            raise

    def _deploy_resources(self, resources: List[Dict[str, Any]], namespace: str) -> List[str]:
        """部署资源"""
        deployed_resources = []

        for resource in resources:
            resource_yaml = yaml.dump(resource)
            resource_type = resource.get('kind', 'Unknown').lower()
            resource_name = resource.get('metadata', {}).get('name', 'unnamed')

            try:
                # 应用资源
                self._run_kubectl_command([
                    "apply", "-f", "-", "-n", namespace
                ], input_data=resource_yaml)

                deployed_resources.append(f"{resource_type}/{resource_name}")
                logger.info(f"Deployed resource: {resource_type}/{resource_name}")

            except Exception as e:
                logger.error(f"Failed to deploy resource {resource_name}: {str(e)}")
                raise

        return deployed_resources

    def _wait_for_resources_ready(self, resources: List[str], namespace: str, timeout: int = 300):
        """等待资源就绪"""
        start_time = time.time()

        for resource in resources:
            resource_type, resource_name = resource.split('/', 1)

            while time.time() - start_time < timeout:
                try:
                    if resource_type in ['deployment', 'statefulset', 'daemonset']:
                        # 检查滚动更新状态
                        result = self._run_kubectl_command([
                            "rollout", "status", resource_type, resource_name,
                            "-n", namespace, "--timeout=30s"
                        ])
                        if "successfully rolled out" in result:
                            break
                    elif resource_type == 'pod':
                        # 检查Pod状态
                        result = self._run_kubectl_command([
                            "get", "pod", resource_name, "-n", namespace,
                            "-o", "jsonpath='{.status.phase}'"
                        ])
                        if result.strip("'") == "Running":
                            break
                    elif resource_type == 'job':
                        # 检查Job状态
                        result = self._run_kubectl_command([
                            "get", "job", resource_name, "-n", namespace,
                            "-o", "jsonpath='{.status.conditions[?(@.type==\"Complete\")].status}'"
                        ])
                        if result.strip("'") == "True":
                            break
                    else:
                        # 对于其他资源类型，简单检查是否存在
                        self._run_kubectl_command([
                            "get", resource_type, resource_name, "-n", namespace
                        ])
                        break

                except Exception:
                    pass

                time.sleep(5)

            else:
                raise TimeoutError(f"Resource {resource} failed to become ready within {timeout}s")

    def _execute_test_commands(self, commands: List[str], namespace: str) -> List[Dict[str, Any]]:
        """执行测试命令"""
        results = []

        for command in commands:
            try:
                # 解析命令
                if isinstance(command, str):
                    cmd_parts = command.split()
                else:
                    cmd_parts = command

                # 如果是kubectl命令，添加命名空间
                if cmd_parts[0] == 'kubectl' and '-n' not in cmd_parts:
                    cmd_parts.extend(['-n', namespace])

                result = self._run_command(cmd_parts)
                results.append({
                    'command': command,
                    'output': result,
                    'success': True
                })

            except Exception as e:
                results.append({
                    'command': command,
                    'error': str(e),
                    'success': False
                })

        return results

    def _execute_assertions(self, assertions: List[Dict[str, Any]], namespace: str) -> List[Dict[str, Any]]:
        """执行断言"""
        results = []

        for assertion in assertions:
            assertion_type = assertion.get('type')
            try:
                if assertion_type == 'resource_exists':
                    result = self._assert_resource_exists(assertion, namespace)
                elif assertion_type == 'resource_count':
                    result = self._assert_resource_count(assertion, namespace)
                elif assertion_type == 'pod_status':
                    result = self._assert_pod_status(assertion, namespace)
                elif assertion_type == 'service_endpoint':
                    result = self._assert_service_endpoint(assertion, namespace)
                elif assertion_type == 'metric_value':
                    result = self._assert_metric_value(assertion, namespace)
                else:
                    result = {'passed': False, 'error': f'Unknown assertion type: {assertion_type}'}

                results.append({
                    'assertion': assertion,
                    'result': result,
                    'passed': result.get('passed', False)
                })

            except Exception as e:
                results.append({
                    'assertion': assertion,
                    'error': str(e),
                    'passed': False
                })

        return results

    def _assert_resource_exists(self, assertion: Dict[str, Any], namespace: str) -> Dict[str, Any]:
        """断言资源存在"""
        resource_type = assertion['resource_type']
        resource_name = assertion['resource_name']

        try:
            self._run_kubectl_command([
                "get", resource_type, resource_name, "-n", namespace
            ])
            return {'passed': True}
        except Exception:
            return {'passed': False, 'error': f'Resource {resource_type}/{resource_name} not found'}

    def _assert_resource_count(self, assertion: Dict[str, Any], namespace: str) -> Dict[str, Any]:
        """断言资源数量"""
        resource_type = assertion['resource_type']
        expected_count = assertion['count']
        label_selector = assertion.get('label_selector', '')

        try:
            cmd = ["get", resource_type, "-n", namespace, "--no-headers"]
            if label_selector:
                cmd.extend(["-l", label_selector])

            result = self._run_kubectl_command(cmd)
            actual_count = len(result.strip().split('\n')) if result.strip() else 0

            return {
                'passed': actual_count == expected_count,
                'expected': expected_count,
                'actual': actual_count
            }
        except Exception as e:
            return {'passed': False, 'error': str(e)}

    def _assert_pod_status(self, assertion: Dict[str, Any], namespace: str) -> Dict[str, Any]:
        """断言Pod状态"""
        pod_name = assertion.get('pod_name')
        expected_phase = assertion.get('phase', 'Running')
        label_selector = assertion.get('label_selector')

        try:
            cmd = ["get", "pod", "-n", namespace, "-o", "jsonpath='{.items[*].status.phase}'"]
            if pod_name:
                cmd.append(pod_name)
            elif label_selector:
                cmd.extend(["-l", label_selector])

            result = self._run_kubectl_command(cmd).strip("'")
            phases = result.split() if result else []

            if pod_name:
                actual_phase = phases[0] if phases else 'Unknown'
                passed = actual_phase == expected_phase
            else:
                # 检查所有匹配的Pod
                passed = all(phase == expected_phase for phase in phases)

            return {
                'passed': passed,
                'expected_phase': expected_phase,
                'actual_phases': phases
            }
        except Exception as e:
            return {'passed': False, 'error': str(e)}

    def _assert_service_endpoint(self, assertion: Dict[str, Any], namespace: str) -> Dict[str, Any]:
        """断言服务端点"""
        service_name = assertion['service_name']
        expected_endpoints = assertion.get('expected_endpoints', 1)

        try:
            # 获取端点数量
            result = self._run_kubectl_command([
                "get", "endpoints", service_name, "-n", namespace,
                "-o", "jsonpath='{.subsets[*].addresses[*]}'"
            ])

            actual_endpoints = len(result.strip("'").split()) if result.strip("'") else 0

            return {
                'passed': actual_endpoints >= expected_endpoints,
                'expected_min': expected_endpoints,
                'actual': actual_endpoints
            }
        except Exception as e:
            return {'passed': False, 'error': str(e)}

    def _assert_metric_value(self, assertion: Dict[str, Any], namespace: str) -> Dict[str, Any]:
        """断言指标值"""
        metric_name = assertion['metric_name']
        expected_value = assertion['expected_value']
        operator = assertion.get('operator', '==')

        try:
            # 这里需要集成监控系统，如Prometheus
            # 简化实现，假设通过kubectl获取指标
            actual_value = self._get_metric_value(metric_name, namespace)

            if operator == '==':
                passed = actual_value == expected_value
            elif operator == '>=':
                passed = actual_value >= expected_value
            elif operator == '<=':
                passed = actual_value <= expected_value
            elif operator == '>':
                passed = actual_value > expected_value
            elif operator == '<':
                passed = actual_value < expected_value
            else:
                passed = False

            return {
                'passed': passed,
                'expected': expected_value,
                'actual': actual_value,
                'operator': operator
            }
        except Exception as e:
            return {'passed': False, 'error': str(e)}

    def _get_metric_value(self, metric_name: str, namespace: str) -> float:
        """获取指标值 (简化实现)"""
        # 这里应该集成实际的监控系统
        # 暂时返回模拟值
        return 85.5

    def _cleanup_resources(self, resources: List[str]):
        """清理资源"""
        for resource in reversed(resources):
            try:
                if resource.startswith('namespace/'):
                    namespace = resource.split('/', 1)[1]
                    if namespace in self.namespaces_created:
                        self._run_kubectl_command([
                            "delete", "namespace", namespace, "--ignore-not-found=true"
                        ])
                        self.namespaces_created.remove(namespace)
                        logger.info(f"Deleted namespace: {namespace}")
                else:
                    resource_type, resource_name = resource.split('/', 1)
                    # 注意：这里需要知道命名空间，但简化处理
                    logger.info(f"Would delete resource: {resource}")

            except Exception as e:
                logger.error(f"Failed to cleanup resource {resource}: {str(e)}")

    def _run_kubectl_command(self, args: List[str], input_data: str = None) -> str:
        """运行kubectl命令"""
        cmd = ["kubectl"] + args

        if input_data:
            result = subprocess.run(
                cmd,
                input=input_data,
                text=True,
                capture_output=True,
                check=True
            )
        else:
            result = subprocess.run(
                cmd,
                text=True,
                capture_output=True,
                check=True
            )

        return result.stdout

    def _run_command(self, cmd_parts: List[str]) -> str:
        """运行通用命令"""
        result = subprocess.run(
            cmd_parts,
            text=True,
            capture_output=True,
            check=True
        )
        return result.stdout

    def get_execution_status(self, execution_id: str) -> Optional[K8sTestExecution]:
        """获取执行状态"""
        return self.active_executions.get(execution_id)

    def get_execution_history(self, limit: int = 10) -> List[K8sTestExecution]:
        """获取执行历史"""
        return self.execution_history[-limit:]

    def get_test_summary(self) -> Dict[str, Any]:
        """获取测试汇总"""
        total_tests = len(self.execution_history)
        if total_tests == 0:
            return {'total_tests': 0}

        passed_tests = sum(1 for exec in self.execution_history if exec.status == 'passed')
        failed_tests = total_tests - passed_tests

        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests / total_tests,
            'test_cases_available': len(self.test_cases)
        }
```

### 2. Docker容器测试框架 (Docker Container Testing Framework)
```python
# Docker容器测试框架
class DockerTestFramework:
    """Docker容器测试框架"""

    def __init__(self):
        self.containers_created: List[str] = []
        self.networks_created: List[str] = []
        self.volumes_created: List[str] = []

    def create_test_environment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建测试环境"""
        environment = {
            'containers': [],
            'networks': [],
            'volumes': [],
            'created_at': datetime.now().isoformat()
        }

        try:
            # 创建网络
            if 'networks' in config:
                for network_config in config['networks']:
                    network_id = self._create_network(network_config)
                    environment['networks'].append(network_id)
                    self.networks_created.append(network_id)

            # 创建卷
            if 'volumes' in config:
                for volume_config in config['volumes']:
                    volume_name = self._create_volume(volume_config)
                    environment['volumes'].append(volume_name)
                    self.volumes_created.append(volume_name)

            # 创建容器
            if 'containers' in config:
                for container_config in config['containers']:
                    container_id = self._create_container(container_config)
                    environment['containers'].append(container_id)
                    self.containers_created.append(container_id)

                    # 启动容器
                    self._start_container(container_id)

            # 等待容器就绪
            self._wait_for_containers_ready(environment['containers'])

            environment['status'] = 'ready'

        except Exception as e:
            logger.error(f"Failed to create test environment: {str(e)}")
            environment['status'] = 'failed'
            environment['error'] = str(e)
            # 清理已创建的资源
            self._cleanup_environment(environment)

        return environment

    def _create_network(self, config: Dict[str, Any]) -> str:
        """创建Docker网络"""
        network_name = config.get('name', f"test-network-{int(time.time())}")
        driver = config.get('driver', 'bridge')

        cmd = [
            "docker", "network", "create",
            "--driver", driver,
            network_name
        ]

        if 'options' in config:
            for key, value in config['options'].items():
                cmd.extend(["--opt", f"{key}={value}"])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        network_id = result.stdout.strip()

        logger.info(f"Created Docker network: {network_name} ({network_id})")
        return network_id

    def _create_volume(self, config: Dict[str, Any]) -> str:
        """创建Docker卷"""
        volume_name = config.get('name', f"test-volume-{int(time.time())}")
        driver = config.get('driver', 'local')

        cmd = [
            "docker", "volume", "create",
            "--driver", driver,
            volume_name
        ]

        if 'options' in config:
            for key, value in config['options'].items():
                cmd.extend(["--opt", f"{key}={value}"])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Created Docker volume: {volume_name}")
        return volume_name

    def _create_container(self, config: Dict[str, Any]) -> str:
        """创建Docker容器"""
        image = config['image']
        container_name = config.get('name', f"test-container-{int(time.time())}")

        cmd = [
            "docker", "run",
            "-d",
            "--name", container_name
        ]

        # 添加端口映射
        if 'ports' in config:
            for port_mapping in config['ports']:
                cmd.extend(["-p", port_mapping])

        # 添加环境变量
        if 'environment' in config:
            for env_var in config['environment']:
                cmd.extend(["-e", env_var])

        # 添加卷挂载
        if 'volumes' in config:
            for volume_mount in config['volumes']:
                cmd.extend(["-v", volume_mount])

        # 添加网络
        if 'network' in config:
            cmd.extend(["--network", config['network']])

        # 添加其他选项
        if 'options' in config:
            cmd.extend(config['options'])

        # 添加镜像
        cmd.append(image)

        # 添加命令
        if 'command' in config:
            if isinstance(config['command'], list):
                cmd.extend(config['command'])
            else:
                cmd.extend(config['command'].split())

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        container_id = result.stdout.strip()

        logger.info(f"Created Docker container: {container_name} ({container_id})")
        return container_id

    def _start_container(self, container_id: str):
        """启动容器"""
        subprocess.run([
            "docker", "start", container_id
        ], capture_output=True, text=True, check=True)

        logger.info(f"Started container: {container_id}")

    def _wait_for_containers_ready(self, container_ids: List[str], timeout: int = 60):
        """等待容器就绪"""
        start_time = time.time()

        for container_id in container_ids:
            while time.time() - start_time < timeout:
                try:
                    # 检查容器状态
                    result = subprocess.run([
                        "docker", "inspect", container_id,
                        "--format", "{{.State.Status}}"
                    ], capture_output=True, text=True, check=True)

                    status = result.stdout.strip()
                    if status == "running":
                        # 检查容器健康状态（如果有健康检查）
                        health_result = subprocess.run([
                            "docker", "inspect", container_id,
                            "--format", "{{.State.Health.Status}}"
                        ], capture_output=True, text=True)

                        if health_result.returncode == 0:
                            health_status = health_result.stdout.strip()
                            if health_status in ["healthy", ""]:
                                break
                        else:
                            # 没有健康检查，认为运行中即就绪
                            break

                except Exception:
                    pass

                time.sleep(2)

            else:
                raise TimeoutError(f"Container {container_id} failed to become ready within {timeout}s")

    def execute_container_test(self, container_id: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """在容器中执行测试"""
        test_result = {
            'container_id': container_id,
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }

        try:
            # 执行测试命令
            if 'commands' in test_config:
                command_results = []
                for command in test_config['commands']:
                    result = self._execute_in_container(container_id, command)
                    command_results.append(result)

                test_result['command_results'] = command_results

            # 执行断言
            if 'assertions' in test_config:
                assertion_results = []
                for assertion in test_config['assertions']:
                    result = self._execute_container_assertion(container_id, assertion)
                    assertion_results.append(result)

                test_result['assertion_results'] = assertion_results

            # 判断测试是否通过
            all_assertions_passed = all(
                assertion.get('passed', False)
                for assertion in assertion_results
            )

            test_result['status'] = 'passed' if all_assertions_passed else 'failed'
            test_result['end_time'] = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Container test failed: {str(e)}")
            test_result['status'] = 'failed'
            test_result['error'] = str(e)
            test_result['end_time'] = datetime.now().isoformat()

        return test_result

    def _execute_in_container(self, container_id: str, command: str) -> Dict[str, Any]:
        """在容器中执行命令"""
        try:
            result = subprocess.run([
                "docker", "exec", container_id
            ] + command.split(), capture_output=True, text=True, check=True)

            return {
                'command': command,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'success': True
            }

        except subprocess.CalledProcessError as e:
            return {
                'command': command,
                'stdout': e.stdout,
                'stderr': e.stderr,
                'return_code': e.returncode,
                'success': False,
                'error': str(e)
            }

    def _execute_container_assertion(self, container_id: str, assertion: Dict[str, Any]) -> Dict[str, Any]:
        """执行容器断言"""
        assertion_type = assertion.get('type')

        try:
            if assertion_type == 'command_exit_code':
                result = self._assert_command_exit_code(container_id, assertion)
            elif assertion_type == 'output_contains':
                result = self._assert_output_contains(container_id, assertion)
            elif assertion_type == 'file_exists':
                result = self._assert_file_exists(container_id, assertion)
            elif assertion_type == 'port_listening':
                result = self._assert_port_listening(container_id, assertion)
            else:
                result = {'passed': False, 'error': f'Unknown assertion type: {assertion_type}'}

            return {
                'assertion': assertion,
                'result': result,
                'passed': result.get('passed', False)
            }

        except Exception as e:
            return {
                'assertion': assertion,
                'error': str(e),
                'passed': False
            }

    def _assert_command_exit_code(self, container_id: str, assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言命令退出码"""
        command = assertion['command']
        expected_code = assertion.get('expected_code', 0)

        result = self._execute_in_container(container_id, command)
        actual_code = result.get('return_code', -1)

        return {
            'passed': actual_code == expected_code,
            'expected': expected_code,
            'actual': actual_code
        }

    def _assert_output_contains(self, container_id: str, assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言输出包含文本"""
        command = assertion['command']
        expected_text = assertion['expected_text']

        result = self._execute_in_container(container_id, command)
        output = result.get('stdout', '') + result.get('stderr', '')

        return {
            'passed': expected_text in output,
            'expected_text': expected_text,
            'output': output
        }

    def _assert_file_exists(self, container_id: str, assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言文件存在"""
        file_path = assertion['file_path']

        result = self._execute_in_container(container_id, f"test -f {file_path}")
        exists = result.get('return_code', -1) == 0

        return {
            'passed': exists,
            'file_path': file_path,
            'exists': exists
        }

    def _assert_port_listening(self, container_id: str, assertion: Dict[str, Any]) -> Dict[str, Any]:
        """断言端口监听"""
        port = assertion['port']

        result = self._execute_in_container(container_id, f"netstat -tln | grep :{port}")
        is_listening = result.get('return_code', -1) == 0

        return {
            'passed': is_listening,
            'port': port,
            'is_listening': is_listening
        }

    def _cleanup_environment(self, environment: Dict[str, Any]):
        """清理测试环境"""
        # 停止并删除容器
        for container_id in environment.get('containers', []):
            try:
                subprocess.run([
                    "docker", "stop", container_id
                ], capture_output=True, text=True)
                subprocess.run([
                    "docker", "rm", container_id
                ], capture_output=True, text=True)
                logger.info(f"Cleaned up container: {container_id}")
            except Exception as e:
                logger.error(f"Failed to cleanup container {container_id}: {str(e)}")

        # 删除网络
        for network_id in environment.get('networks', []):
            try:
                subprocess.run([
                    "docker", "network", "rm", network_id
                ], capture_output=True, text=True)
                logger.info(f"Cleaned up network: {network_id}")
            except Exception as e:
                logger.error(f"Failed to cleanup network {network_id}: {str(e)}")

        # 删除卷
        for volume_name in environment.get('volumes', []):
            try:
                subprocess.run([
                    "docker", "volume", "rm", volume_name
                ], capture_output=True, text=True)
                logger.info(f"Cleaned up volume: {volume_name}")
            except Exception as e:
                logger.error(f"Failed to cleanup volume {volume_name}: {str(e)}")

    def cleanup_all(self):
        """清理所有资源"""
        # 清理容器
        for container_id in self.containers_created:
            try:
                subprocess.run([
                    "docker", "stop", container_id
                ], capture_output=True, text=True)
                subprocess.run([
                    "docker", "rm", container_id
                ], capture_output=True, text=True)
            except Exception as e:
                logger.error(f"Failed to cleanup container {container_id}: {str(e)}")

        # 清理网络
        for network_id in self.networks_created:
            try:
                subprocess.run([
                    "docker", "network", "rm", network_id
                ], capture_output=True, text=True)
            except Exception as e:
                logger.error(f"Failed to cleanup network {network_id}: {str(e)}")

        # 清理卷
        for volume_name in self.volumes_created:
            try:
                subprocess.run([
                    "docker", "volume", "rm", volume_name
                ], capture_output=True, text=True)
            except Exception as e:
                logger.error(f"Failed to cleanup volume {volume_name}: {str(e)}")

        # 清空列表
        self.containers_created.clear()
        self.networks_created.clear()
        self.volumes_created.clear()

        logger.info("Cleaned up all Docker test resources")
```

### 3. Istio服务网格测试框架 (Istio Service Mesh Testing Framework)
```python
# Istio服务网格测试框架
class IstioTestFramework:
    """Istio服务网格测试框架"""

    def __init__(self, istioctl_path: str = "istioctl"):
        self.istioctl = istioctl_path
        self.virtual_services_created: List[str] = []
        self.destination_rules_created: List[str] = []
        self.gateway_created: List[str] = []
        self.peer_authentications_created: List[str] = []

    def deploy_service_mesh_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """部署服务网格配置"""
        deployment_result = {
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'resources_created': []
        }

        try:
            # 部署网关
            if 'gateways' in config:
                for gateway_config in config['gateways']:
                    gateway_name = self._create_gateway(gateway_config)
                    deployment_result['resources_created'].append(f"gateway/{gateway_name}")
                    self.gateway_created.append(gateway_name)

            # 部署虚拟服务
            if 'virtual_services' in config:
                for vs_config in config['virtual_services']:
                    vs_name = self._create_virtual_service(vs_config)
                    deployment_result['resources_created'].append(f"virtualservice/{vs_name}")
                    self.virtual_services_created.append(vs_name)

            # 部署目标规则
            if 'destination_rules' in config:
                for dr_config in config['destination_rules']:
                    dr_name = self._create_destination_rule(dr_config)
                    deployment_result['resources_created'].append(f"destinationrule/{dr_name}")
                    self.destination_rules_created.append(dr_name)

            # 部署对等认证
            if 'peer_authentications' in config:
                for pa_config in config['peer_authentications']:
                    pa_name = self._create_peer_authentication(pa_config)
                    deployment_result['resources_created'].append(f"peerauthentication/{pa_name}")
                    self.peer_authentications_created.append(pa_name)

            # 等待配置生效
            time.sleep(10)

            deployment_result['status'] = 'completed'
            deployment_result['end_time'] = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Failed to deploy service mesh config: {str(e)}")
            deployment_result['status'] = 'failed'
            deployment_result['error'] = str(e)
            deployment_result['end_time'] = datetime.now().isoformat()

        return deployment_result

    def _create_gateway(self, config: Dict[str, Any]) -> str:
        """创建Istio网关"""
        gateway_yaml = yaml.dump(config)
        gateway_name = config.get('metadata', {}).get('name', 'unnamed-gateway')

        cmd = [self.istioctl, "create", "-f", "-"]
        result = subprocess.run(
            cmd,
            input=gateway_yaml,
            text=True,
            capture_output=True,
            check=True
        )

        logger.info(f"Created Istio gateway: {gateway_name}")
        return gateway_name

    def _create_virtual_service(self, config: Dict[str, Any]) -> str:
        """创建虚拟服务"""
        vs_yaml = yaml.dump(config)
        vs_name = config.get('metadata', {}).get('name', 'unnamed-vs')

        cmd = [self.istioctl, "create", "-f", "-"]
        result = subprocess.run(
            cmd,
            input=vs_yaml,
            text=True,
            capture_output=True,
            check=True
        )

        logger.info(f"Created virtual service: {vs_name}")
        return vs_name

    def _create_destination_rule(self, config: Dict[str, Any]) -> str:
        """创建目标规则"""
        dr_yaml = yaml.dump(config)
        dr_name = config.get('metadata', {}).get('name', 'unnamed-dr')

        cmd = [self.istioctl, "create", "-f", "-"]
        result = subprocess.run(
            cmd,
            input=dr_yaml,
            text=True,
            capture_output=True,
            check=True
        )

        logger.info(f"Created destination rule: {dr_name}")
        return dr_name

    def _create_peer_authentication(self, config: Dict[str, Any]) -> str:
        """创建对等认证"""
        pa_yaml = yaml.dump(config)
        pa_name = config.get('metadata', {}).get('name', 'unnamed-pa')

        cmd = [self.istioctl, "create", "-f", "-"]
        result = subprocess.run(
            cmd,
            input=pa_yaml,
            text=True,
            capture_output=True,
            check=True
        )

        logger.info(f"Created peer authentication: {pa_name}")
        return pa_name

    def execute_mesh_test(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """执行服务网格测试"""
        test_result = {
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'test_type': test_config.get('type', 'unknown')
        }

        try:
            if test_config['type'] == 'traffic_routing':
                result = self._test_traffic_routing(test_config)
            elif test_config['type'] == 'fault_injection':
                result = self._test_fault_injection(test_config)
            elif test_config['type'] == 'circuit_breaking':
                result = self._test_circuit_breaking(test_config)
            elif test_config['type'] == 'authentication':
                result = self._test_authentication(test_config)
            else:
                result = {'passed': False, 'error': f"Unknown test type: {test_config['type']}"}

            test_result.update(result)
            test_result['status'] = 'passed' if result.get('passed', False) else 'failed'
            test_result['end_time'] = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Service mesh test failed: {str(e)}")
            test_result['status'] = 'failed'
            test_result['error'] = str(e)
            test_result['end_time'] = datetime.now().isoformat()

        return test_result

    def _test_traffic_routing(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """测试流量路由"""
        source_url = config['source_url']
        expected_routes = config['expected_routes']
        request_count = config.get('request_count', 10)

        route_counts = {}

        for _ in range(request_count):
            try:
                # 发送请求并记录路由
                result = subprocess.run([
                    "curl", "-s", "-w", "%{http_code}", source_url
                ], capture_output=True, text=True, check=True)

                # 解析响应头中的路由信息 (简化实现)
                route = "v1"  # 应该从响应头解析实际路由
                route_counts[route] = route_counts.get(route, 0) + 1

            except Exception as e:
                logger.error(f"Traffic routing test request failed: {str(e)}")

        # 验证路由分布
        total_requests = sum(route_counts.values())
        route_percentages = {
            route: count / total_requests
            for route, count in route_counts.items()
        }

        passed = True
        for expected_route, expected_percentage in expected_routes.items():
            actual_percentage = route_percentages.get(expected_route, 0)
            if abs(actual_percentage - expected_percentage) > 0.1:  # 10% 容差
                passed = False
                break

        return {
            'passed': passed,
            'route_counts': route_counts,
            'route_percentages': route_percentages,
            'expected_routes': expected_routes
        }

    def _test_fault_injection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """测试故障注入"""
        target_url = config['target_url']
        fault_type = config['fault_type']
        expected_behavior = config['expected_behavior']

        try:
            # 发送测试请求
            result = subprocess.run([
                "curl", "-s", "-w", "%{http_code}\n%{time_total}",
                target_url
            ], capture_output=True, text=True, check=True)

            response_lines = result.stdout.strip().split('\n')
            status_code = int(response_lines[0])
            response_time = float(response_lines[1])

            # 根据故障类型验证行为
            if fault_type == 'delay':
                expected_delay = expected_behavior.get('delay_seconds', 0)
                passed = response_time >= expected_delay
            elif fault_type == 'abort':
                expected_status = expected_behavior.get('status_code', 200)
                passed = status_code == expected_status
            else:
                passed = False

            return {
                'passed': passed,
                'fault_type': fault_type,
                'status_code': status_code,
                'response_time': response_time,
                'expected_behavior': expected_behavior
            }

        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'fault_type': fault_type
            }

    def _test_circuit_breaking(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """测试熔断器"""
        target_url = config['target_url']
        request_count = config.get('request_count', 20)
        expected_failure_rate = config.get('expected_failure_rate', 0.5)

        success_count = 0
        failure_count = 0

        for _ in range(request_count):
            try:
                result = subprocess.run([
                    "curl", "-s", "--max-time", "5", target_url
                ], capture_output=True, text=True, check=True)

                success_count += 1
            except subprocess.CalledProcessError:
                failure_count += 1

        actual_failure_rate = failure_count / request_count

        passed = abs(actual_failure_rate - expected_failure_rate) <= 0.1  # 10% 容差

        return {
            'passed': passed,
            'success_count': success_count,
            'failure_count': failure_count,
            'actual_failure_rate': actual_failure_rate,
            'expected_failure_rate': expected_failure_rate
        }

    def _test_authentication(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """测试认证"""
        target_url = config['target_url']
        auth_config = config['auth_config']
        expected_result = config['expected_result']

        try:
            cmd = ["curl", "-s", "-w", "%{http_code}"]

            # 添加认证头
            if 'token' in auth_config:
                cmd.extend(["-H", f"Authorization: Bearer {auth_config['token']}"])
            elif 'certificate' in auth_config:
                cmd.extend([
                    "--cert", auth_config['certificate']['cert_file'],
                    "--key", auth_config['certificate']['key_file']
                ])

            cmd.append(target_url)

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            status_code = int(result.stdout.strip())

            passed = status_code == expected_result.get('status_code', 200)

            return {
                'passed': passed,
                'status_code': status_code,
                'expected_status': expected_result.get('status_code', 200),
                'auth_type': list(auth_config.keys())[0]
            }

        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'auth_type': list(auth_config.keys())[0] if auth_config else 'unknown'
            }

    def cleanup_mesh_resources(self):
        """清理服务网格资源"""
        # 清理虚拟服务
        for vs_name in self.virtual_services_created:
            try:
                subprocess.run([
                    self.istioctl, "delete", "virtualservice", vs_name
                ], capture_output=True, text=True)
            except Exception as e:
                logger.error(f"Failed to cleanup virtual service {vs_name}: {str(e)}")

        # 清理目标规则
        for dr_name in self.destination_rules_created:
            try:
                subprocess.run([
                    self.istioctl, "delete", "destinationrule", dr_name
                ], capture_output=True, text=True)
            except Exception as e:
                logger.error(f"Failed to cleanup destination rule {dr_name}: {str(e)}")

        # 清理网关
        for gateway_name in self.gateway_created:
            try:
                subprocess.run([
                    self.istioctl, "delete", "gateway", gateway_name
                ], capture_output=True, text=True)
            except Exception as e:
                logger.error(f"Failed to cleanup gateway {gateway_name}: {str(e)}")

        # 清理对等认证
        for pa_name in self.peer_authentications_created:
            try:
                subprocess.run([
                    self.istioctl, "delete", "peerauthentication", pa_name
                ], capture_output=True, text=True)
            except Exception as e:
                logger.error(f"Failed to cleanup peer authentication {pa_name}: {str(e)}")

        # 清空列表
        self.virtual_services_created.clear()
        self.destination_rules_created.clear()
        self.gateway_created.clear()
        self.peer_authentications_created.clear()

        logger.info("Cleaned up all Istio service mesh resources")
```

## 配置模板 (Configuration Templates)

### Kubernetes测试配置
```yaml
# k8s_test_config.yml
apiVersion: v1
kind: TestSuite
metadata:
  name: microservices-integration-test
spec:
  namespace: test-namespace
  resources:
    - apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: test-app
      spec:
        replicas: 2
        selector:
          matchLabels:
            app: test-app
        template:
          metadata:
            labels:
              app: test-app
          spec:
            containers:
            - name: app
              image: nginx:1.20
              ports:
              - containerPort: 80
    - apiVersion: v1
      kind: Service
      metadata:
        name: test-service
      spec:
        selector:
          app: test-app
        ports:
        - port: 80
          targetPort: 80
  test_commands:
    - kubectl get pods -l app=test-app
    - kubectl get services test-service
  assertions:
    - type: resource_count
      resource_type: pod
      label_selector: app=test-app
      count: 2
    - type: service_endpoint
      service_name: test-service
      expected_endpoints: 2
    - type: pod_status
      label_selector: app=test-app
      phase: Running
```

### Docker测试配置
```yaml
# docker_test_config.yml
test_environment:
  networks:
    - name: test-network
      driver: bridge
  volumes:
    - name: test-data
      driver: local
  containers:
    - name: web-server
      image: nginx:1.20
      ports:
        - "8080:80"
      volumes:
        - test-data:/usr/share/nginx/html
      network: test-network
    - name: database
      image: mysql:8.0
      environment:
        - MYSQL_ROOT_PASSWORD=test123
        - MYSQL_DATABASE=testdb
      network: test-network

test_cases:
  - name: web_server_test
    container: web-server
    commands:
      - curl -f http://localhost/
    assertions:
      - type: command_exit_code
        command: curl -f http://localhost/
        expected_code: 0
      - type: file_exists
        file_path: /usr/share/nginx/html/index.html
      - type: port_listening
        port: 80
```

### Istio测试配置
```yaml
# istio_test_config.yml
service_mesh_config:
  gateways:
    - apiVersion: networking.istio.io/v1beta1
      kind: Gateway
      metadata:
        name: test-gateway
      spec:
        selector:
          istio: ingressgateway
        servers:
        - port:
            number: 80
            name: http
            protocol: HTTP
          hosts:
          - "*"
  virtual_services:
    - apiVersion: networking.istio.io/v1beta1
      kind: VirtualService
      metadata:
        name: test-routing
      spec:
        hosts:
        - test-app
        http:
        - route:
          - destination:
              host: test-app
              subset: v1
            weight: 80
          - destination:
              host: test-app
              subset: v2
            weight: 20
  destination_rules:
    - apiVersion: networking.istio.io/v1beta1
      kind: DestinationRule
      metadata:
        name: test-app-dr
      spec:
        host: test-app
        subsets:
        - name: v1
          labels:
            version: v1
        - name: v2
          labels:
            version: v2

test_cases:
  - type: traffic_routing
    source_url: http://test-app/
    expected_routes:
      v1: 0.8
      v2: 0.2
    request_count: 100
  - type: fault_injection
    target_url: http://test-app/
    fault_type: delay
    expected_behavior:
      delay_seconds: 2
  - type: circuit_breaking
    target_url: http://test-app/
    request_count: 20
    expected_failure_rate: 0.5
```

## 使用示例 (Usage Examples)

### Kubernetes测试
```python
from kubernetes_test_framework import KubernetesTestFramework
import yaml

# 初始化框架
k8s_framework = KubernetesTestFramework()

# 加载测试配置
with open('k8s_test_config.yml', 'r') as f:
    test_config = yaml.safe_load(f)

# 创建测试用例
test_case = K8sTestCase(
    name=test_config['metadata']['name'],
    namespace=test_config['spec']['namespace'],
    resources=test_config['spec']['resources'],
    test_commands=test_config['spec']['test_commands'],
    assertions=test_config['spec']['assertions'],
    timeout=300,
    retry_count=1
)

k8s_framework.register_test_case(test_case)

# 执行测试
execution_id = k8s_framework.execute_test_case(test_case.name)

# 等待测试完成并获取结果
import time
while True:
    execution = k8s_framework.get_execution_status(execution_id)
    if execution and execution.status in ['passed', 'failed']:
        print(f"Test result: {execution.status}")
        print(f"Results: {execution.results}")
        break
    time.sleep(5)
```

### Docker测试
```python
from docker_test_framework import DockerTestFramework
import yaml

# 初始化框架
docker_framework = DockerTestFramework()

# 加载测试配置
with open('docker_test_config.yml', 'r') as f:
    config = yaml.safe_load(f)

# 创建测试环境
environment = docker_framework.create_test_environment(config['test_environment'])
print(f"Environment created: {environment['status']}")

if environment['status'] == 'ready':
    # 执行测试
    for test_case_config in config['test_cases']:
        container_id = None
        for container in environment['containers']:
            # 查找容器ID (简化实现)
            if test_case_config['container'] in container:
                container_id = container
                break
        
        if container_id:
            result = docker_framework.execute_container_test(container_id, test_case_config)
            print(f"Test {test_case_config['name']}: {result['status']}")

# 清理资源
docker_framework.cleanup_all()
```

### Istio测试
```python
from istio_test_framework import IstioTestFramework
import yaml

# 初始化框架
istio_framework = IstioTestFramework()

# 加载测试配置
with open('istio_test_config.yml', 'r') as f:
    config = yaml.safe_load(f)

# 部署服务网格配置
deployment = istio_framework.deploy_service_mesh_config(config['service_mesh_config'])
print(f"Service mesh deployed: {deployment['status']}")

if deployment['status'] == 'completed':
    # 执行测试
    for test_case_config in config['test_cases']:
        result = istio_framework.execute_mesh_test(test_case_config)
        print(f"Test {test_case_config['type']}: {result['status']}")

# 清理资源
istio_framework.cleanup_mesh_resources()
```

## 最佳实践 (Best Practices)

1. **环境隔离**: 为不同测试类型创建独立的命名空间和网络
2. **资源管理**: 实施自动清理机制，避免资源泄漏
3. **配置管理**: 使用GitOps管理测试配置和资源模板
4. **监控集成**: 集成Prometheus和Grafana进行测试指标监控
5. **CI/CD集成**: 将测试框架集成到CI/CD流水线中
6. **性能优化**: 使用并行测试执行和资源池化提高效率
7. **安全性**: 实施最小权限原则和安全扫描
8. **可观测性**: 添加详细日志记录和测试结果分析