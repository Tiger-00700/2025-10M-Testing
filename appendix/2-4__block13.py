#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
import logging
import statistics
from datetime import datetime

def setup_logging():
    """设置日志"""
    log_dir = '/logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'backup_restore_performance_test.log')
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 同时输出到控制台
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

class BackupRestorePerformanceTester:
    """备份恢复性能测试器"""
    
    def __init__(self, config):
        """初始化测试器"""
        self.config = config
        self.results = {
            'backup_times': [],
            'restore_times': [],
            'backup_sizes': [],
            'resource_usage': []
        }
    
    def execute_command(self, command):
        """执行命令并返回结果"""
        try:
            logging.info(f"执行命令: {command}")
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            logging.error(f"命令执行失败: {command}")
            logging.error(f"错误输出: {e.stderr}")
            return False, e.stderr
    
    def generate_test_data(self, size_gb):
        """生成指定大小的测试数据"""
        logging.info(f"生成{size_gb}GB的测试数据...")
        
        # 确保测试数据目录存在
        test_data_dir = self.config['test_data_dir']
        os.makedirs(test_data_dir, exist_ok=True)
        
        # 生成测试文件（每个100MB）
        files_to_create = size_gb * 10  # 10个100MB文件 = 1GB
        chunk_size_mb = 100
        chunk_count = 0
        
        start_time = time.time()
        
        for i in range(files_to_create):
            file_path = os.path.join(test_data_dir, f"test_file_{i:04d}.dat")
            
            # 使用dd命令生成文件
            dd_command = f"dd if=/dev/urandom of={file_path} bs=1M count={chunk_size_mb} status=none"
            success, _ = self.execute_command(dd_command)
            
            if not success:
                logging.error(f"无法生成测试文件 {file_path}")
                return False
            
            chunk_count += 1
            if chunk_count % 10 == 0:
                logging.info(f"已生成 {chunk_count} 个文件（{chunk_count * chunk_size_mb}MB）")
        
        duration = time.time() - start_time
        logging.info(f"测试数据生成完成，耗时: {duration:.2f} 秒")
        
        # 验证生成的数据大小
        du_command = f"du -sh {test_data_dir}"
        success, output = self.execute_command(du_command)
        if success:
            actual_size = output.split()[0]
            logging.info(f"实际生成的数据大小: {actual_size}")
        
        return True
    
    def measure_resource_usage(self, pid, duration):
        """测量指定进程的资源使用情况"""
        try:
            # 使用ps命令获取CPU和内存使用率
            ps_command = f"ps -p {pid} -o %cpu,%mem"
            success, output = self.execute_command(ps_command)
            if success and len(output.strip().split('\n')) > 1:
                # 解析第二行（第一行是标题）
                usage_data = output.strip().split('\n')[1].strip().split()
                cpu_usage = float(usage_data[0])
                mem_usage = float(usage_data[1])
                
                return {
                    'cpu_percent': cpu_usage,
                    'memory_percent': mem_usage,
                    'duration': duration
                }
        except Exception as e:
            logging.error(f"无法测量资源使用情况: {str(e)}")
        
        return None
    
    def run_backup_test(self, test_id):
        """运行备份测试"""
        logging.info(f"开始备份测试 #{test_id}...")
        
        # 确保备份目录存在
        backup_dir = self.config['backup_dir']
        os.makedirs(backup_dir, exist_ok=True)
        
        # 备份目标路径
        backup_path = os.path.join(backup_dir, f"backup_{test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz")
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行备份（使用tar命令作为示例）
        tar_command = f"tar -czf {backup_path} -C {os.path.dirname(self.config['test_data_dir'])} {os.path.basename(self.config['test_data_dir'])}"
        success, _ = self.execute_command(tar_command)
        
        # 计算备份时间
        backup_time = time.time() - start_time
        
        if success:
            # 获取备份文件大小
            du_command = f"du -h {backup_path}"
            _, size_output = self.execute_command(du_command)
            backup_size = size_output.split()[0]
            
            logging.info(f"备份测试 #{test_id} 完成，耗时: {backup_time:.2f} 秒，备份大小: {backup_size}")
            
            # 记录结果
            self.results['backup_times'].append(backup_time)
            self.results['backup_sizes'].append(backup_size)
            
            return backup_path
        else:
            logging.error(f"备份测试 #{test_id} 失败")
            return None
    
    def run_restore_test(self, test_id, backup_path):
        """运行恢复测试"""
        logging.info(f"开始恢复测试 #{test_id}...")
        
        # 确保恢复目录存在
        restore_dir = os.path.join(self.config['restore_dir'], f"restore_{test_id}")
        os.makedirs(restore_dir, exist_ok=True)
        
        # 记录开始时间
        start_time = time.time()
        
        # 执行恢复
        tar_command = f"tar -xzf {backup_path} -C {restore_dir}"
        success, _ = self.execute_command(tar_command)
        
        # 计算恢复时间
        restore_time = time.time() - start_time
        
        if success:
            logging.info(f"恢复测试 #{test_id} 完成，耗时: {restore_time:.2f} 秒")
            
            # 验证恢复的数据
            original_data_dir = os.path.basename(self.config['test_data_dir'])
            restored_data_dir = os.path.join(restore_dir, original_data_dir)
            
            if os.path.exists(restored_data_dir):
                # 比较文件数量
                original_file_count = len(os.listdir(self.config['test_data_dir']))
                restored_file_count = len(os.listdir(restored_data_dir))
                
                if original_file_count == restored_file_count:
                    logging.info(f"恢复验证成功：文件数量匹配 ({restored_file_count} 个文件)")
                    
                    # 记录结果
                    self.results['restore_times'].append(restore_time)
                    
                    return True
                else:
                    logging.error(f"恢复验证失败：文件数量不匹配 - 原始: {original_file_count}, 恢复: {restored_file_count}")
                    return False
            else:
                logging.error(f"恢复验证失败：恢复目录不存在: {restored_data_dir}")
                return False
        else:
            logging.error(f"恢复测试 #{test_id} 失败")
            return False
    
    def run_performance_test(self, iterations=3):
        """运行完整的性能测试"""
        logging.info("开始备份恢复性能测试")
        
        # 1. 生成测试数据
        if not self.generate_test_data(self.config['test_data_size_gb']):
            return False
        
        # 2. 运行多次测试以获得统计数据
        for i in range(1, iterations + 1):
            logging.info(f"执行测试迭代 #{i}/{iterations}")
            
            # 执行备份测试
            backup_path = self.run_backup_test(i)
            if not backup_path:
                logging.error(f"迭代 #{i} 的备份测试失败，跳过后续步骤")
                continue
            
            # 执行恢复测试
            self.run_restore_test(i, backup_path)
        
        # 3. 生成性能报告
        self.generate_performance_report()
        
        return True
    
    def generate_performance_report(self):
        """生成性能测试报告"""
        logging.info("生成备份恢复性能测试报告")
        
        report = {
            'test_configuration': self.config,
            'test_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'metrics': {}
        }
        
        # 计算备份时间统计
        if self.results['backup_times']:
            backup_mean = statistics.mean(self.results['backup_times'])
            backup_std = statistics.stdev(self.results['backup_times']) if len(self.results['backup_times']) > 1 else 0
            backup_min = min(self.results['backup_times'])
            backup_max = max(self.results['backup_times'])
            
            report['metrics']['backup'] = {
                'mean_time_seconds': backup_mean,
                'std_time_seconds': backup_std,
                'min_time_seconds': backup_min,
                'max_time_seconds': backup_max,
                'iterations': len(self.results['backup_times']),
                'backup_sizes': self.results['backup_sizes']
            }
            
            # 计算备份吞吐量（MB/秒）
            data_size_mb = self.config['test_data_size_gb'] * 1024
            backup_throughput = data_size_mb / backup_mean
            report['metrics']['backup']['throughput_mb_per_sec'] = backup_throughput
        
        # 计算恢复时间统计
        if self.results['restore_times']:
            restore_mean = statistics.mean(self.results['restore_times'])
            restore_std = statistics.stdev(self.results['restore_times']) if len(self.results['restore_times']) > 1 else 0
            restore_min = min(self.results['restore_times'])
            restore_max = max(self.results['restore_times'])
            
            report['metrics']['restore'] = {
                'mean_time_seconds': restore_mean,
                'std_time_seconds': restore_std,
                'min_time_seconds': restore_min,
                'max_time_seconds': restore_max,
                'iterations': len(self.results['restore_times'])
            }
            
            # 计算恢复吞吐量（MB/秒）
            data_size_mb = self.config['test_data_size_gb'] * 1024
            restore_throughput = data_size_mb / restore_mean
            report['metrics']['restore']['throughput_mb_per_sec'] = restore_throughput
        
        # 打印性能报告
        logging.info("===== 备份恢复性能测试报告 =====")
        logging.info(f"测试配置: {self.config}")
        
        if 'backup' in report['metrics']:
            backup_metrics = report['metrics']['backup']
            logging.info("\n备份性能:")
            logging.info(f"  平均备份时间: {backup_metrics['mean_time_seconds']:.2f} 秒")
            logging.info(f"  备份时间标准差: {backup_metrics['std_time_seconds']:.2f} 秒")
            logging.info(f"  最短备份时间: {backup_metrics['min_time_seconds']:.2f} 秒")
            logging.info(f"  最长备份时间: {backup_metrics['max_time_seconds']:.2f} 秒")
            logging.info(f"  备份吞吐量: {backup_metrics['throughput_mb_per_sec']:.2f} MB/秒")
            logging.info(f"  备份文件大小: {', '.join(backup_metrics['backup_sizes'])}")
        
        if 'restore' in report['metrics']:
            restore_metrics = report['metrics']['restore']
            logging.info("\n恢复性能:")
            logging.info(f"  平均恢复时间: {restore_metrics['mean_time_seconds']:.2f} 秒")
            logging.info(f"  恢复时间标准差: {restore_metrics['std_time_seconds']:.2f} 秒")
            logging.info(f"  最短恢复时间: {restore_metrics['min_time_seconds']:.2f} 秒")
            logging.info(f"  最长恢复时间: {restore_metrics['max_time_seconds']:.2f} 秒")
            logging.info(f"  恢复吞吐量: {restore_metrics['throughput_mb_per_sec']:.2f} MB/秒")
        
        # 保存报告到文件
        report_file = os.path.join('/logs', f'backup_restore_performance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        with open(report_file, 'w') as f:
            f.write("===== 备份恢复性能测试报告 =====\n")
            f.write(f"测试时间: {report['test_time']}\n\n")
            f.write("测试配置:\n")
            for key, value in report['test_configuration'].items():
                f.write(f"  {key}: {value}\n")
            
            if 'backup' in report['metrics']:
                backup_metrics = report['metrics']['backup']
                f.write("\n备份性能:\n")
                f.write(f"  平均备份时间: {backup_metrics['mean_time_seconds']:.2f} 秒\n")
                f.write(f"  备份时间标准差: {backup_metrics['std_time_seconds']:.2f} 秒\n")
                f.write(f"  最短备份时间: {backup_metrics['min_time_seconds']:.2f} 秒\n")
                f.write(f"  最长备份时间: {backup_metrics['max_time_seconds']:.2f} 秒\n")
                f.write(f"  备份吞吐量: {backup_metrics['throughput_mb_per_sec']:.2f} MB/秒\n")
                f.write(f"  备份文件大小: {', '.join(backup_metrics['backup_sizes'])}\n")
            
            if 'restore' in report['metrics']:
                restore_metrics = report['metrics']['restore']
                f.write("\n恢复性能:\n")
                f.write(f"  平均恢复时间: {restore_metrics['mean_time_seconds']:.2f} 秒\n")
                f.write(f"  恢复时间标准差: {restore_metrics['std_time_seconds']:.2f} 秒\n")
                f.write(f"  最短恢复时间: {restore_metrics['min_time_seconds']:.2f} 秒\n")
                f.write(f"  最长恢复时间: {restore_metrics['max_time_seconds']:.2f} 秒\n")
                f.write(f"  恢复吞吐量: {restore_metrics['throughput_mb_per_sec']:.2f} MB/秒\n")
        
        logging.info(f"性能测试报告已保存到: {report_file}")

def main():
    """主函数"""
    setup_logging()
    
    # 测试配置
    config = {
        'test_data_dir': '/data/test_backup_data',
        'test_data_size_gb': 1,  # 测试数据大小（GB）
        'backup_dir': '/backup/performance_tests',
        'restore_dir': '/restore/performance_tests',
        'iterations': 3  # 测试迭代次数
    }
    
    # 创建测试器并运行测试
    tester = BackupRestorePerformanceTester(config)
    tester.run_performance_test(iterations=config['iterations'])

if __name__ == "__main__":
    main()
