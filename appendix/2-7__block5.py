# 大数据安全测试工具集成框架
import os
import sys
import json
import subprocess
import time
import logging
import yaml
import paramiko
import requests
import concurrent.futures
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bigdata_security_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BigDataSecurityToolkit")

class ToolExecutor:
    """安全测试工具执行器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def execute(self) -> Dict[str, Any]:
        """执行安全测试"""
        raise NotImplementedError("子类必须实现execute方法")
    
    def parse_results(self, raw_output: str) -> Dict[str, Any]:
        """解析测试结果"""
        raise NotImplementedError("子类必须实现parse_results方法")
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试结果摘要"""
        raise NotImplementedError("子类必须实现get_summary方法")
    
    def save_results(self, output_dir: str) -> str:
        """保存测试结果到文件"""
        output_path = os.path.join(output_dir, f"{self.__class__.__name__}_results.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        return output_path
    
    def _run_command(self, command: List[str], timeout: int = 3600) -> str:
        """运行命令并返回输出"""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=timeout)
            
            if process.returncode != 0:
                logger.error(f"命令执行失败: {' '.join(command)}")
                logger.error(f"错误输出: {stderr}")
                raise Exception(f"命令执行失败，返回码: {process.returncode}")
            
            return stdout
        except subprocess.TimeoutExpired:
            process.kill()
            raise Exception(f"命令执行超时: {' '.join(command)}")
        except Exception as e:
            logger.error(f"执行命令时出错: {str(e)}")
            raise

class LocalToolExecutor(ToolExecutor):
    """本地安全测试工具执行器"""
    
    def execute(self) -> Dict[str, Any]:
        """执行本地安全测试工具"""
        self.start_time = datetime.now().isoformat()
        
        try:
            # 检查工具是否安装
            if not os.path.exists(self.config['tool_path']):
                raise Exception(f"工具未找到: {self.config['tool_path']}")
            
            # 构建命令
            command = [self.config['tool_path']]
            if 'arguments' in self.config:
                command.extend(self.config['arguments'])
            
            logger.info(f"执行本地工具: {' '.join(command)}")
            
            # 执行命令
            raw_output = self._run_command(command, self.config.get('timeout', 3600))
            
            # 解析结果
            self.results = self.parse_results(raw_output)
            
            # 添加元数据
            self.results['metadata'] = {
                'tool': self.config.get('name', self.__class__.__name__),
                'tool_path': self.config['tool_path'],
                'start_time': self.start_time,
                'end_time': datetime.now().isoformat(),
                'command': ' '.join(command)
            }
            
            return self.results
            
        except Exception as e:
            logger.error(f"执行本地工具时出错: {str(e)}")
            self.results['error'] = str(e)
            return self.results

class RemoteToolExecutor(ToolExecutor):
    """远程安全测试工具执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    def connect(self):
        """建立SSH连接"""
        try:
            logger.info(f"连接到远程主机: {self.config['hostname']}")
            
            if 'key_file' in self.config:
                self.ssh_client.connect(
                    hostname=self.config['hostname'],
                    port=self.config.get('port', 22),
                    username=self.config['username'],
                    key_filename=self.config['key_file']
                )
            else:
                self.ssh_client.connect(
                    hostname=self.config['hostname'],
                    port=self.config.get('port', 22),
                    username=self.config['username'],
                    password=self.config.get('password')
                )
            
            logger.info(f"成功连接到远程主机: {self.config['hostname']}")
        except Exception as e:
            logger.error(f"连接远程主机失败: {str(e)}")
            raise
    
    def disconnect(self):
        """关闭SSH连接"""
        if self.ssh_client:
            self.ssh_client.close()
            logger.info(f"已断开与远程主机的连接: {self.config['hostname']}")
    
    def execute(self) -> Dict[str, Any]:
        """执行远程安全测试工具"""
        self.start_time = datetime.now().isoformat()
        
        try:
            # 建立SSH连接
            self.connect()
            
            # 构建命令
            command = self.config['remote_command']
            logger.info(f"在远程主机执行命令: {command}")
            
            # 执行远程命令
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=self.config.get('timeout', 3600))
            
            # 获取输出
            raw_output = stdout.read().decode('utf-8')
            error_output = stderr.read().decode('utf-8')
            
            # 检查执行状态
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                logger.error(f"远程命令执行失败，返回码: {exit_status}")
                logger.error(f"错误输出: {error_output}")
                raise Exception(f"远程命令执行失败: {error_output}")
            
            # 解析结果
            self.results = self.parse_results(raw_output)
            
            # 添加元数据
            self.results['metadata'] = {
                'tool': self.config.get('name', self.__class__.__name__),
                'hostname': self.config['hostname'],
                'start_time': self.start_time,
                'end_time': datetime.now().isoformat(),
                'command': command
            }
            
            return self.results
            
        except Exception as e:
            logger.error(f"执行远程工具时出错: {str(e)}")
            self.results['error'] = str(e)
            return self.results
        finally:
            # 断开连接
            self.disconnect()

class APIToolExecutor(ToolExecutor):
    """API安全测试工具执行器"""
    
    def execute(self) -> Dict[str, Any]:
        """执行API安全测试工具"""
        self.start_time = datetime.now().isoformat()
        
        try:
            # 准备请求参数
            url = self.config['url']
            method = self.config.get('method', 'GET').upper()
            headers = self.config.get('headers', {})
            params = self.config.get('params', {})
            data = self.config.get('data', None)
            json_data = self.config.get('json', None)
            timeout = self.config.get('timeout', 30)
            
            logger.info(f"发送API请求: {method} {url}")
            
            # 发送请求
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                if json_data:
                    response = requests.post(url, headers=headers, json=json_data, timeout=timeout)
                else:
                    response = requests.post(url, headers=headers, data=data, timeout=timeout)
            elif method == 'PUT':
                if json_data:
                    response = requests.put(url, headers=headers, json=json_data, timeout=timeout)
                else:
                    response = requests.put(url, headers=headers, data=data, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=timeout)
            else:
                raise Exception(f"不支持的HTTP方法: {method}")
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析结果
            try:
                raw_output = response.json()
            except ValueError:
                raw_output = response.text
            
            self.results = self.parse_results(raw_output)
            
            # 添加元数据
            self.results['metadata'] = {
                'tool': self.config.get('name', self.__class__.__name__),
                'url': url,
                'method': method,
                'start_time': self.start_time,
                'end_time': datetime.now().isoformat(),
                'status_code': response.status_code
            }
            
            return self.results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            self.results['error'] = str(e)
            return self.results
        except Exception as e:
            logger.error(f"执行API工具时出错: {str(e)}")
            self.results['error'] = str(e)
            return self.results

# 具体工具实现类
class NessusExecutor(APIToolExecutor):
    """Nessus漏洞扫描器执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = None
        self.session = requests.Session()
    
    def login(self):
        """登录Nessus API"""
        try:
            login_url = f"{self.config['url']}/session"
            login_data = {
                "username": self.config['username'],
                "password": self.config['password']
            }
            
            logger.info("登录Nessus API")
            response = self.session.post(login_url, json=login_data, verify=self.config.get('verify_ssl', True))
            response.raise_for_status()
            
            # 获取API密钥
            data = response.json()
            self.api_key = data['token']
            
            # 设置认证头
            self.session.headers.update({
                "X-Cookie": f"token={self.api_key}",
                "Content-Type": "application/json"
            })
            
            logger.info("成功登录Nessus API")
        except Exception as e:
            logger.error(f"Nessus API登录失败: {str(e)}")
            raise
    
    def logout(self):
        """登出Nessus API"""
        try:
            if self.api_key:
                logout_url = f"{self.config['url']}/session"
                self.session.delete(logout_url)
                logger.info("已登出Nessus API")
        except Exception as e:
            logger.error(f"Nessus API登出失败: {str(e)}")
    
    def create_scan(self, targets: List[str], policy_id: int = None) -> int:
        """创建扫描任务"""
        try:
            scan_url = f"{self.config['url']}/scans"
            
            # 准备扫描配置
            scan_config = {
                "uuid": self.config.get('scan_template_uuid', "ad625c5e-099a-ba69-5309-8d72de958600"),  # 高级扫描模板
                "settings": {
                    "name": f"BigData Security Scan - {datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "description": "自动创建的大数据环境安全扫描",
                    "text_targets": ",".join(targets),
                    "enabled": True
                }
            }
            
            # 如果指定了策略ID，使用现有策略
            if policy_id:
                scan_config['settings']['policy_id'] = policy_id
            
            logger.info(f"创建Nessus扫描任务: {scan_config['settings']['name']}")
            response = self.session.post(scan_url, json=scan_config)
            response.raise_for_status()
            
            # 获取扫描ID
            data = response.json()
            scan_id = data['scan']['id']
            
            logger.info(f"成功创建扫描任务，ID: {scan_id}")
            return scan_id
            
        except Exception as e:
            logger.error(f"创建Nessus扫描任务失败: {str(e)}")
            raise
    
    def start_scan(self, scan_id: int):
        """启动扫描任务"""
        try:
            start_url = f"{self.config['url']}/scans/{scan_id}/launch"
            
            logger.info(f"启动Nessus扫描任务，ID: {scan_id}")
            response = self.session.post(start_url, json={})
            response.raise_for_status()
            
            logger.info(f"成功启动扫描任务，ID: {scan_id}")
        except Exception as e:
            logger.error(f"启动Nessus扫描任务失败: {str(e)}")
            raise
    
    def get_scan_status(self, scan_id: int) -> Dict[str, Any]:
        """获取扫描状态"""
        try:
            status_url = f"{self.config['url']}/scans/{scan_id}"
            
            response = self.session.get(status_url)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"获取Nessus扫描状态失败: {str(e)}")
            raise
    
    def wait_for_scan_completion(self, scan_id: int, check_interval: int = 300) -> Dict[str, Any]:
        """等待扫描完成"""
        logger.info(f"等待Nessus扫描任务完成，ID: {scan_id}")
        
        while True:
            status = self.get_scan_status(scan_id)
            scan_status = status['info']['status']
            
            logger.info(f"扫描状态: {scan_status}, 进度: {status['info'].get('progress', 0)}%")
            
            if scan_status == 'completed':
                logger.info(f"扫描任务完成，ID: {scan_id}")
                return status
            elif scan_status in ['canceled', 'error', 'paused']:
                logger.error(f"扫描任务异常: {scan_status}")
                raise Exception(f"扫描任务异常: {scan_status}")
            
            # 等待指定时间后再次检查
            time.sleep(check_interval)
    
    def download_scan_results(self, scan_id: int, format_type: str = 'json') -> str:
        """下载扫描结果"""
        try:
            # 获取结果文件ID
            download_url = f"{self.config['url']}/scans/{scan_id}/export"
            export_data = {
                "format": format_type,
                "reportContents": {
                    "hostSections": ["host_information", "scan_information"],
                    "vulnerabilitySections": [
                        "synopsis", "description", "see_also", "solution",
                        "risk_factor", "cvss3_base_score", "cvss3_vector",
                        "cvss_base_score", "cvss_vector", "exploit_available",
                        "plugin_information"
                    ]
                }
            }
            
            logger.info(f"请求导出扫描结果，扫描ID: {scan_id}")
            response = self.session.post(download_url, json=export_data)
            response.raise_for_status()
            
            # 获取文件ID
            file_id = response.json()['file']
            
            # 等待导出完成
            logger.info(f"等待扫描结果导出完成，文件ID: {file_id}")
            
            while True:
                status_url = f"{self.config['url']}/scans/{scan_id}/export/{file_id}/status"
                status_response = self.session.get(status_url)
                status_response.raise_for_status()
                
                status_data = status_response.json()
                if status_data['status'] == 'ready':
                    break
                
                time.sleep(10)
            
            # 下载结果
            final_url = f"{self.config['url']}/scans/{scan_id}/export/{file_id}/download"
            logger.info(f"下载扫描结果，文件ID: {file_id}")
            
            download_response = self.session.get(final_url)
            download_response.raise_for_status()
            
            return download_response.text
            
        except Exception as e:
            logger.error(f"下载Nessus扫描结果失败: {str(e)}")
            raise
    
    def execute(self) -> Dict[str, Any]:
        """执行Nessus扫描"""
        self.start_time = datetime.now().isoformat()
        
        try:
            # 登录Nessus API
            self.login()
            
            # 创建并启动扫描
            scan_id = self.create_scan(self.config['targets'], self.config.get('policy_id'))
            self.start_scan(scan_id)
            
            # 等待扫描完成
            scan_status = self.wait_for_scan_completion(
                scan_id, 
                self.config.get('check_interval', 300)
            )
            
            # 下载扫描结果
            raw_results = self.download_scan_results(scan_id, 'json')
            
            # 解析结果
            self.results = self.parse_results(raw_results)
            
            # 添加元数据
            self.results['metadata'] = {
                'tool': 'Nessus',
                'url': self.config['url'],
                'scan_id': scan_id,
                'targets': self.config['targets'],
                'start_time': self.start_time,
                'end_time': datetime.now().isoformat()
            }
            
            return self.results
            
        except Exception as e:
            logger.error(f"执行Nessus扫描时出错: {str(e)}")
            self.results['error'] = str(e)
            return self.results
        finally:
            # 登出
            self.logout()
    
    def parse_results(self, raw_output: str) -> Dict[str, Any]:
        """解析Nessus扫描结果"""
        try:
            results = json.loads(raw_output)
            
            # 提取关键信息
            parsed_results = {
                'scan_info': results.get('scan', {}).get('info', {}),
                'hosts': [],
                'vulnerabilities': {},
                'summary': {
                    'total_hosts': 0,
                    'total_vulnerabilities': 0,
                    'by_severity': {
                        'critical': 0,
                        'high': 0,
                        'medium': 0,
                        'low': 0,
                        'info': 0
                    }
                }
            }
            
            # 处理主机和漏洞信息
            for host in results.get('scan', {}).get('hosts', []):
                host_data = {
                    'hostname': host.get('hostname'),
                    'ip': host.get('ip'),
                    'os': host.get('operating-system'),
                    'critical': host.get('critical', 0),
                    'high': host.get('high', 0),
                    'medium': host.get('medium', 0),
                    'low': host.get('low', 0),
                    'info': host.get('info', 0),
                    'vulnerabilities': []
                }
                
                # 更新摘要统计
                parsed_results['summary']['total_hosts'] += 1
                parsed_results['summary']['by_severity']['critical'] += host_data['critical']
                parsed_results['summary']['by_severity']['high'] += host_data['high']
                parsed_results['summary']['by_severity']['medium'] += host_data['medium']
                parsed_results['summary']['by_severity']['low'] += host_data['low']
                parsed_results['summary']['by_severity']['info'] += host_data['info']
                
                # 获取主机的详细漏洞信息
                host_details = self.get_host_details(host.get('host_id'))
                if host_details:
                    host_data['vulnerabilities'] = host_details
                
                parsed_results['hosts'].append(host_data)
                
                # 收集所有漏洞信息
                for vuln in host_data['vulnerabilities']:
                    plugin_id = vuln.get('plugin_id')
                    if plugin_id not in parsed_results['vulnerabilities']:
                        parsed_results['vulnerabilities'][plugin_id] = {
                            'name': vuln.get('plugin_name'),
                            'severity': vuln.get('severity'),
                            'synopsis': vuln.get('synopsis'),
                            'solution': vuln.get('solution'),
                            'affected_hosts': [host.get('ip')]
                        }
                    else:
                        parsed_results['vulnerabilities'][plugin_id]['affected_hosts'].append(host.get('ip'))
            
            # 计算总漏洞数
            parsed_results['summary']['total_vulnerabilities'] = sum(parsed_results['summary']['by_severity'].values())
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"解析Nessus扫描结果失败: {str(e)}")
            return {"error": str(e), "raw_output": raw_output}
    
    def get_host_details(self, host_id: int) -> List[Dict[str, Any]]:
        """获取主机的详细漏洞信息"""
        try:
            details_url = f"{self.config['url']}/hosts/{host_id}/plugins"
            response = self.session.get(details_url)
            response.raise_for_status()
            
            data = response.json()
            vulnerabilities = []
            
            for plugin in data.get('plugins', []):
                vuln = {
                    'plugin_id': plugin.get('plugin_id'),
                    'plugin_name': plugin.get('plugin_name'),
                    'severity': plugin.get('severity'),
                    'synopsis': plugin.get('synopsis'),
                    'description': plugin.get('description'),
                    'solution': plugin.get('solution'),
                    'see_also': plugin.get('see_also', []),
                    'cvss3_base_score': plugin.get('cvss3_base_score'),
                    'cvss_base_score': plugin.get('cvss_base_score')
                }
                vulnerabilities.append(vuln)
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"获取主机详细信息失败: {str(e)}")
            return []
    
    def get_summary(self) -> Dict[str, Any]:
        """获取Nessus扫描结果摘要"""
        return self.results.get('summary', {})

class MetasploitExecutor(RemoteToolExecutor):
    """Metasploit渗透测试框架执行器"""
    
    def parse_results(self, raw_output: str) -> Dict[str, Any]:
        """解析Metasploit执行结果"""
        # 这是一个简化的解析器，实际使用时需要根据具体的Metasploit输出格式进行调整
        parsed_results = {
            'raw_output': raw_output,
            'exploits': [],
            'vulnerabilities': []
        }
        
        # 提取关键信息（示例）
        if "[+]" in raw_output:
            # 提取成功的漏洞利用
            exploits = [line.strip() for line in raw_output.split('\n') if "[+]" in line]
            parsed_results['exploits'] = exploits
        
        if "[*]" in raw_output:
            # 提取发现的漏洞
            vulnerabilities = [line.strip() for line in raw_output.split('\n') if "[*]" in line]
            parsed_results['vulnerabilities'] = vulnerabilities
        
        return parsed_results
    
    def get_summary(self) -> Dict[str, Any]:
        """获取Metasploit执行结果摘要"""
        return {
            'total_exploits': len(self.results.get('exploits', [])),
            'total_vulnerabilities': len(self.results.get('vulnerabilities', []))
        }

class ELKSecurityAnalyzer(APIToolExecutor):
    """ELK Stack安全日志分析器"""
    
    def parse_results(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """解析ELK查询结果"""
        parsed_results = {
            'raw_response': raw_output,
            'alerts': [],
            'anomalies': [],
            'aggregations': {}
        }
        
        # 提取告警信息
        if 'hits' in raw_output and 'hits' in raw_output['hits']:
            for hit in raw_output['hits']['hits']:
                source = hit.get('_source', {})
                
                # 判断是否为告警
                if source.get('event', {}).get('category') == 'alert' or source.get('alert', {}).get('status') == 'firing':
                    alert = {
                        'timestamp': source.get('@timestamp'),
                        'severity': source.get('severity', 'unknown'),
                        'message': source.get('message', ''),
                        'source': source
                    }
                    parsed_results['alerts'].append(alert)
                
                # 判断是否为异常行为
                elif source.get('event', {}).get('outcome') == 'failure' or source.get('tags', []) == 'suspicious':
                    anomaly = {
                        'timestamp': source.get('@timestamp'),
                        'event_type': source.get('event', {}).get('type', 'unknown'),
                        'source_ip': source.get('source', {}).get('ip', 'unknown'),
                        'destination_ip': source.get('destination', {}).get('ip', 'unknown'),
                        'message': source.get('message', ''),
                        'source': source
                    }
                    parsed_results['anomalies'].append(anomaly)
        
        # 提取聚合信息
        if 'aggregations' in raw_output:
            parsed_results['aggregations'] = raw_output['aggregations']
        
        return parsed_results
    
    def get_summary(self) -> Dict[str, Any]:
        """获取ELK分析结果摘要"""
        return {
            'total_alerts': len(self.results.get('alerts', [])),
            'total_anomalies': len(self.results.get('anomalies', [])),
            'aggregation_results': self.results.get('aggregations', {})
        }

class SecurityToolkit:
    """大数据安全测试工具包"""
    
    def __init__(self, config_path: str):
        """初始化安全工具包"""
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 创建输出目录
        self.output_dir = os.path.join(
            self.config.get('output_dir', 'security_test_results'),
            datetime.now().strftime('%Y%m%d_%H%M%S')
        )
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"安全工具包初始化完成，输出目录: {self.output_dir}")
    
    def _create_executor(self, tool_config: Dict[str, Any]) -> ToolExecutor:
        """根据工具配置创建执行器"""
        tool_type = tool_config.get('type', 'unknown')
        
        if tool_type == 'local':
            return LocalToolExecutor(tool_config)
        elif tool_type == 'remote':
            return RemoteToolExecutor(tool_config)
        elif tool_type == 'api':
            return APIToolExecutor(tool_config)
        elif tool_type == 'nessus':
            return NessusExecutor(tool_config)
        elif tool_type == 'metasploit':
            return MetasploitExecutor(tool_config)
        elif tool_type == 'elk':
            return ELKSecurityAnalyzer(tool_config)
        else:
            raise Exception(f"不支持的工具类型: {tool_type}")
    
    def run_tool(self, tool_name: str) -> Dict[str, Any]:
        """运行单个安全测试工具"""
        logger.info(f"开始运行工具: {tool_name}")
        
        # 检查工具配置是否存在
        if tool_name not in self.config.get('tools', {}):
            raise Exception(f"未找到工具配置: {tool_name}")
        
        tool_config = self.config['tools'][tool_name]
        
        # 创建执行器
        executor = self._create_executor(tool_config)
        
        # 执行工具
        results = executor.execute()
        
        # 保存结果
        output_path = executor.save_results(self.output_dir)
        logger.info(f"工具执行完成: {tool_name}，结果保存到: {output_path}")
        
        # 返回摘要
        return {
            'tool': tool_name,
            'results_path': output_path,
            'summary': executor.get_summary()
        }
    
    def run_all_tools(self, parallel: bool = False, max_workers: int = 4) -> List[Dict[str, Any]]:
        """运行所有配置的安全测试工具"""
        logger.info("开始运行所有安全测试工具")
        
        results = []
        
        if parallel:
            # 并行执行
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_tool = {
                    executor.submit(self.run_tool, tool_name): tool_name 
                    for tool_name in self.config.get('tools', {})
                }
                
                for future in concurrent.futures.as_completed(future_to_tool):
                    tool_name = future_to_tool[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"工具执行异常: {tool_name}, 错误: {str(e)}")
                        results.append({
                            'tool': tool_name,
                            'error': str(e)
                        })
        else:
            # 串行执行
            for tool_name in self.config.get('tools', {}):
                try:
                    result = self.run_tool(tool_name)
                    results.append(result)
                except Exception as e:
                    logger.error(f"工具执行异常: {tool_name}, 错误: {str(e)}")
                    results.append({
                        'tool': tool_name,
                        'error': str(e)
                    })
        
        # 生成综合报告
        self.generate_comprehensive_report(results)
        
        logger.info("所有安全测试工具执行完成")
        return results
    
    def generate_comprehensive_report(self, results: List[Dict[str, Any]]):
        """生成综合测试报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'tools': results,
            'summary': self._generate_report_summary(results)
        }
        
        # 保存报告
        report_path = os.path.join(self.output_dir, 'comprehensive_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"综合安全测试报告已生成: {report_path}")
        
        # 生成HTML报告
        self._generate_html_report(report)
    
    def _generate_report_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成报告摘要"""
        summary = {
            'total_tools': len(results),
            'successful_tools': sum(1 for r in results if 'error' not in r),
            'failed_tools': sum(1 for r in results if 'error' in r),
            'security_summary': {
                'total_vulnerabilities': 0,
                'by_severity': {
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'info': 0
                },
                'recommendations': []
            }
        }
        
        # 汇总各工具的安全发现
        for result in results:
            if 'summary' in result:
                tool_summary = result['summary']
                
                # 处理Nessus结果
                if 'total_vulnerabilities' in tool_summary:
                    summary['security_summary']['total_vulnerabilities'] += tool_summary.get('total_vulnerabilities', 0)
                    
                    # 按严重程度汇总
                    if 'by_severity' in tool_summary:
                        for severity in ['critical', 'high', 'medium', 'low', 'info']:
                            summary['security_summary']['by_severity'][severity] += \
                                tool_summary['by_severity'].get(severity, 0)
                
                # 处理Metasploit结果
                if 'total_exploits' in tool_summary:
                    # 添加发现可利用漏洞的警告
                    if tool_summary.get('total_exploits', 0) > 0:
                        summary['security_summary']['recommendations'].append(
                            f"{result['tool']}发现{tool_summary['total_exploits']}个可利用漏洞，请立即修复。"
                        )
        
        # 生成总体建议
        if summary['security_summary']['by_severity']['critical'] > 0:
            summary['security_summary']['recommendations'].insert(0, 
                f"发现{summary['security_summary']['by_severity']['critical']}个严重漏洞，请优先处理。"
            )
        
        if summary['security_summary']['by_severity']['high'] > 0:
            summary['security_summary']['recommendations'].append(
                f"发现{summary['security_summary']['by_severity']['high']}个高危漏洞，建议在短期内修复。"
            )
        
        return summary
    
    def _generate_html_report(self, report: Dict[str, Any]):
        """生成HTML格式的报告"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>大数据安全测试综合报告</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333366; }}
                h2 {{ color: #333366; border-bottom: 1px solid #cccccc; padding-bottom: 5px; }}
                .summary {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .severity-critical {{ color: #cc0000; }}
                .severity-high {{ color: #ff6600; }}
                .severity-medium {{ color: #ffcc00; }}
                .severity-low {{ color: #009900; }}
                .severity-info {{ color: #0066cc; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .tool-result {{ margin-bottom: 20px; }}
                .error {{ color: #cc0000; }}
                .recommendation {{ background-color: #e6f2ff; padding: 10px; margin-top: 10px; border-left: 4px solid #0066cc; }}
            </style>
        </head>
        <body>
            <h1>大数据安全测试综合报告</h1>
            <p>生成时间: {timestamp}</p>
            
            <div class="summary">
                <h2>测试摘要</h2>
                <p><strong>测试工具总数:</strong> {total_tools}</p>
                <p><strong>成功执行工具:</strong> {successful_tools}</p>
                <p><strong>失败执行工具:</strong> {failed_tools}</p>
            </div>
            
            <h2>安全发现摘要</h2>
            <p><strong>总漏洞数:</strong> {total_vulnerabilities}</p>
            
            <table>
                <tr>
                    <th>严重程度</th>
                    <th>数量</th>
                </tr>
                <tr>
                    <td class="severity-critical"><strong>严重</strong></td>
                    <td>{severity_critical}</td>
                </tr>
                <tr>
                    <td class="severity-high"><strong>高危</strong></td>
                    <td>{severity_high}</td>
                </tr>
                <tr>
                    <td class="severity-medium"><strong>中危</strong></td>
                    <td>{severity_medium}</td>
                </tr>
                <tr>
                    <td class="severity-low"><strong>低危</strong></td>
                    <td>{severity_low}</td>
                </tr>
                <tr>
                    <td class="severity-info"><strong>信息</strong></td>
                    <td>{severity_info}</td>
                </tr>
            </table>
            
            <h2>安全建议</h2>
            {recommendations}
            
            <h2>工具执行详情</h2>
            {tool_details}
        </body>
        </html>
        """
        
        # 准备模板数据
        timestamp = report['timestamp']
        summary = report['summary']
        
        # 生成建议列表
        recommendations_html = ""
        for rec in summary['security_summary']['recommendations']:
            recommendations_html += f"<div class='recommendation'>{rec}</div>\n"
        
        # 生成工具详情
        tool_details_html = ""
        for tool in report['tools']:
            tool_details_html += f"<div class='tool-result'>\n"
            tool_details_html += f"<h3>{tool['tool']}</h3>\n"
            
            if 'error' in tool:
                tool_details_html += f"<p class='error'>执行失败: {tool['error']}</p>\n"
            else:
                tool_details_html += f"<p><strong>结果文件:</strong> <a href='{os.path.basename(tool['results_path'])}'>{os.path.basename(tool['results_path'])}</a></p>\n"
                
                # 显示工具摘要
                if 'summary' in tool:
                    tool_details_html += "<h4>工具摘要:</h4>\n"
                    tool_details_html += "<pre>" + json.dumps(tool['summary'], indent=2, ensure_ascii=False) + "</pre>\n"
            
            tool_details_html += "</div>\n"
        
        # 填充模板
        html_content = html_template.format(
            timestamp=timestamp,
            total_tools=summary['total_tools'],
            successful_tools=summary['successful_tools'],
            failed_tools=summary['failed_tools'],
            total_vulnerabilities=summary['security_summary']['total_vulnerabilities'],
            severity_critical=summary['security_summary']['by_severity']['critical'],
            severity_high=summary['security_summary']['by_severity']['high'],
            severity_medium=summary['security_summary']['by_severity']['medium'],
            severity_low=summary['security_summary']['by_severity']['low'],
            severity_info=summary['security_summary']['by_severity']['info'],
            recommendations=recommendations_html,
            tool_details=tool_details_html
        )
        
        # 保存HTML报告
        html_path = os.path.join(self.output_dir, 'comprehensive_report.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML格式安全测试报告已生成: {html_path}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python bigdata_security_toolkit.py <配置文件路径>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    try:
        # 初始化安全工具包
        toolkit = SecurityToolkit(config_path)
        
        # 运行所有工具
        results = toolkit.run_all_tools(
            parallel=toolkit.config.get('parallel_execution', False),
            max_workers=toolkit.config.get('max_workers', 4)
        )
        
        print("\n安全测试完成！")
        print(f"结果保存在: {toolkit.output_dir}")
        
        # 显示摘要
        for result in results:
            if 'error' in result:
                print(f"{result['tool']}: 执行失败 - {result['error']}")
            else:
                print(f"{result['tool']}: 执行成功")
                if 'summary' in result:
                    print(f"  摘要: {json.dumps(result['summary'], indent=2, ensure_ascii=False)}")
                    
    except Exception as e:
        logger.error(f"程序执行异常: {str(e)}")
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
