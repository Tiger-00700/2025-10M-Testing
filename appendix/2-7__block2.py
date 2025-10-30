# 大数据集群安全配置扫描器
import os
import re
import json
import subprocess
import paramiko
import yaml
from datetime import datetime

class BigDataSecurityScanner:
    def __init__(self, config_file='scanner_config.yaml'):
        """初始化安全扫描器"""
        # 加载配置文件
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化结果存储
        self.scan_results = {
            'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'nodes': {},
            'summary': {
                'high_risks': 0,
                'medium_risks': 0,
                'low_risks': 0,
                'passed_checks': 0
            }
        }
    
    def scan_local_node(self):
        """扫描本地节点"""
        hostname = os.uname().nodename if hasattr(os, 'uname') else 'localhost'
        self.scan_results['nodes'][hostname] = []
        
        # 执行本地安全检查
        self._check_host_security()
        self._check_hadoop_config()
        self._check_spark_config()
        
        return self.scan_results['nodes'][hostname]
    
    def scan_remote_nodes(self):
        """扫描远程节点"""
        for node in self.config.get('remote_nodes', []):
            hostname = node['hostname']
            self.scan_results['nodes'][hostname] = []
            
            try:
                # 建立SSH连接
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    hostname=hostname,
                    username=node.get('username', 'hadoop'),
                    key_filename=node.get('key_file'),
                    password=node.get('password')
                )
                
                # 执行远程安全检查
                self._check_remote_host_security(client, hostname)
                self._check_remote_hadoop_config(client, hostname)
                self._check_remote_spark_config(client, hostname)
                
                client.close()
            except Exception as e:
                self._add_scan_result(hostname, 'critical', 'SSH连接失败', f'无法连接到节点 {hostname}: {str(e)}')
        
    def _check_host_security(self):
        """检查本地主机安全配置"""
        hostname = os.uname().nodename if hasattr(os, 'uname') else 'localhost'
        
        # 检查SSH配置
        if os.path.exists('/etc/ssh/sshd_config'):
            with open('/etc/ssh/sshd_config', 'r') as f:
                ssh_config = f.read()
                
                # 检查是否禁用了root登录
                if not re.search(r'^\s*PermitRootLogin\s+no', ssh_config, re.MULTILINE):
                    self._add_scan_result(hostname, 'high', 'SSH允许root登录', 'SSH配置允许root直接登录，建议禁用')
                else:
                    self._add_scan_result(hostname, 'passed', 'SSH禁用root登录', 'SSH配置正确禁用了root直接登录')
                
                # 检查密码认证
                if re.search(r'^\s*PasswordAuthentication\s+yes', ssh_config, re.MULTILINE):
                    self._add_scan_result(hostname, 'medium', 'SSH启用密码认证', 'SSH配置启用了密码认证，建议仅使用密钥认证')
                else:
                    self._add_scan_result(hostname, 'passed', 'SSH禁用密码认证', 'SSH配置正确禁用了密码认证')
        
        # 检查防火墙状态
        try:
            result = subprocess.run(['firewall-cmd', '--state'], capture_output=True, text=True)
            if result.returncode != 0:
                self._add_scan_result(hostname, 'high', '防火墙未运行', '系统防火墙未运行，建议启用')
            else:
                self._add_scan_result(hostname, 'passed', '防火墙正常运行', '系统防火墙正在运行')
        except FileNotFoundError:
            try:
                result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
                if 'inactive' in result.stdout:
                    self._add_scan_result(hostname, 'high', '防火墙未运行', '系统防火墙未运行，建议启用')
                else:
                    self._add_scan_result(hostname, 'passed', '防火墙正常运行', '系统防火墙正在运行')
            except FileNotFoundError:
                self._add_scan_result(hostname, 'low', '无法检测防火墙状态', '未找到防火墙管理工具')
    
    def _check_hadoop_config(self):
        """检查Hadoop安全配置"""
        hostname = os.uname().nodename if hasattr(os, 'uname') else 'localhost'
        hadoop_conf_dir = os.environ.get('HADOOP_CONF_DIR', '/etc/hadoop/conf')
        
        # 检查core-site.xml中的安全配置
        core_site_path = os.path.join(hadoop_conf_dir, 'core-site.xml')
        if os.path.exists(core_site_path):
            with open(core_site_path, 'r') as f:
                content = f.read()
                
                # 检查是否启用了安全认证
                if 'hadoop.security.authentication' in content and 'kerberos' in content:
                    self._add_scan_result(hostname, 'passed', 'Hadoop启用Kerberos认证', 'Hadoop正确配置了Kerberos认证')
                else:
                    self._add_scan_result(hostname, 'high', 'Hadoop未启用Kerberos认证', 'Hadoop未配置Kerberos认证，存在安全风险')
                
                # 检查是否启用了授权
                if 'hadoop.security.authorization' in content and 'true' in content:
                    self._add_scan_result(hostname, 'passed', 'Hadoop启用授权检查', 'Hadoop正确配置了授权检查')
                else:
                    self._add_scan_result(hostname, 'high', 'Hadoop未启用授权检查', 'Hadoop未启用授权检查，存在安全风险')
    
    def _check_spark_config(self):
        """检查Spark安全配置"""
        hostname = os.uname().nodename if hasattr(os, 'uname') else 'localhost'
        spark_conf_dir = os.environ.get('SPARK_CONF_DIR', '/etc/spark/conf')
        
        # 检查spark-defaults.conf中的安全配置
        spark_defaults_path = os.path.join(spark_conf_dir, 'spark-defaults.conf')
        if os.path.exists(spark_defaults_path):
            with open(spark_defaults_path, 'r') as f:
                content = f.read()
                
                # 检查是否启用了身份验证
                if 'spark.authenticate' in content and 'true' in content:
                    self._add_scan_result(hostname, 'passed', 'Spark启用身份验证', 'Spark正确配置了身份验证')
                else:
                    self._add_scan_result(hostname, 'medium', 'Spark未启用身份验证', 'Spark未启用身份验证，存在安全风险')
    
    def _check_remote_host_security(self, client, hostname):
        """检查远程主机安全配置"""
        # 检查SSH配置
        stdin, stdout, stderr = client.exec_command('cat /etc/ssh/sshd_config')
        ssh_config = stdout.read().decode('utf-8')
        
        if not re.search(r'^\s*PermitRootLogin\s+no', ssh_config, re.MULTILINE):
            self._add_scan_result(hostname, 'high', 'SSH允许root登录', 'SSH配置允许root直接登录，建议禁用')
        else:
            self._add_scan_result(hostname, 'passed', 'SSH禁用root登录', 'SSH配置正确禁用了root直接登录')
        
        # 检查防火墙状态
        stdin, stdout, stderr = client.exec_command('systemctl is-active firewalld || ufw status')
        firewall_status = stdout.read().decode('utf-8').strip()
        
        if firewall_status in ['inactive', 'inactive\nStatus: inactive']:
            self._add_scan_result(hostname, 'high', '防火墙未运行', '系统防火墙未运行，建议启用')
        elif 'active' in firewall_status or 'Status: active' in firewall_status:
            self._add_scan_result(hostname, 'passed', '防火墙正常运行', '系统防火墙正在运行')
        else:
            self._add_scan_result(hostname, 'low', '无法检测防火墙状态', f'防火墙状态未知: {firewall_status}')
    
    def _check_remote_hadoop_config(self, client, hostname):
        """检查远程Hadoop安全配置"""
        stdin, stdout, stderr = client.exec_command('echo $HADOOP_CONF_DIR || echo /etc/hadoop/conf')
        hadoop_conf_dir = stdout.read().decode('utf-8').strip()
        
        stdin, stdout, stderr = client.exec_command(f'cat {hadoop_conf_dir}/core-site.xml 2>/dev/null || echo "文件不存在"')
        content = stdout.read().decode('utf-8')
        
        if '文件不存在' not in content:
            if 'hadoop.security.authentication' in content and 'kerberos' in content:
                self._add_scan_result(hostname, 'passed', 'Hadoop启用Kerberos认证', 'Hadoop正确配置了Kerberos认证')
            else:
                self._add_scan_result(hostname, 'high', 'Hadoop未启用Kerberos认证', 'Hadoop未配置Kerberos认证，存在安全风险')
    
    def _check_remote_spark_config(self, client, hostname):
        """检查远程Spark安全配置"""
        stdin, stdout, stderr = client.exec_command('echo $SPARK_CONF_DIR || echo /etc/spark/conf')
        spark_conf_dir = stdout.read().decode('utf-8').strip()
        
        stdin, stdout, stderr = client.exec_command(f'cat {spark_conf_dir}/spark-defaults.conf 2>/dev/null || echo "文件不存在"')
        content = stdout.read().decode('utf-8')
        
        if '文件不存在' not in content:
            if 'spark.authenticate' in content and 'true' in content:
                self._add_scan_result(hostname, 'passed', 'Spark启用身份验证', 'Spark正确配置了身份验证')
            else:
                self._add_scan_result(hostname, 'medium', 'Spark未启用身份验证', 'Spark未启用身份验证，存在安全风险')
    
    def _add_scan_result(self, hostname, severity, title, description):
        """添加扫描结果"""
        result = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'severity': severity,
            'title': title,
            'description': description
        }
        
        self.scan_results['nodes'][hostname].append(result)
        
        # 更新摘要统计
        if severity == 'high' or severity == 'critical':
            self.scan_results['summary']['high_risks'] += 1
        elif severity == 'medium':
            self.scan_results['summary']['medium_risks'] += 1
        elif severity == 'low':
            self.scan_results['summary']['low_risks'] += 1
        elif severity == 'passed':
            self.scan_results['summary']['passed_checks'] += 1
    
    def generate_report(self, output_file='security_scan_report.json'):
        """生成安全扫描报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False)
        
        print(f"安全扫描报告已生成: {output_file}")
        print(f"\n扫描摘要:")
        print(f"- 高危风险: {self.scan_results['summary']['high_risks']}")
        print(f"- 中危风险: {self.scan_results['summary']['medium_risks']}")
        print(f"- 低危风险: {self.scan_results['summary']['low_risks']}")
        print(f"- 通过检查: {self.scan_results['summary']['passed_checks']}")

# 主函数
def main():
    # 创建配置文件示例
    config_content = """
remote_nodes:
  - hostname: "datanode1"
    username: "hadoop"
    key_file: "/path/to/key.pem"
  - hostname: "datanode2"
    username: "hadoop"
    password: "your_password"  # 不推荐在生产环境中使用密码
"""
    
    with open('scanner_config.yaml', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("配置文件已创建: scanner_config.yaml")
    print("请根据实际环境修改配置文件中的节点信息")
    
    # 初始化并运行扫描器
    scanner = BigDataSecurityScanner()
    print("\n开始扫描本地节点...")
    scanner.scan_local_node()
    
    print("\n开始扫描远程节点...")
    scanner.scan_remote_nodes()
    
    # 生成报告
    scanner.generate_report()

if __name__ == "__main__":
    main()
