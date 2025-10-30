#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
import logging
import json
from datetime import datetime

# 配置日志
logging.basicConfig(
    filename='/logs/disaster_recovery_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 测试配置
CONFIG = {
    'primary_db': {
        'host': 'primary-db.example.com',
        'port': 5432,
        'user': 'postgres',
        'password': 'secure_password',
        'dbname': 'production_db'
    },
    'backup_server': {
        'host': 'backup-server.example.com',
        'backup_dir': '/backup/production'
    },
    'dr_site': {
        'host': 'dr-db.example.com',
        'port': 5432,
        'user': 'postgres',
        'password': 'secure_password',
        'dbname': 'production_db'
    },
    'test': {
        'rto_target': 3600,  # 恢复时间目标（秒）
        'rpo_target': 300    # 恢复点目标（秒）
    }
}

def execute_remote_command(host, command):
    """在远程主机上执行命令"""
    ssh_command = f"ssh -o StrictHostKeyChecking=no {host} '{command}'"
    try:
        logging.info(f"在 {host} 上执行: {command}")
        result = subprocess.run(
            ssh_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"命令执行失败: {ssh_command}")
        logging.error(f"错误输出: {e.stderr}")
        return False, e.stderr

def verify_data_integrity(source, target):
    """验证源数据库和目标数据库的数据完整性"""
    logging.info("验证数据完整性...")
    
    # 获取源数据库的表列表
    source_tables_cmd = f"PGPASSWORD={source['password']} psql -h {source['host']} -p {source['port']} -U {source['user']} -d {source['dbname']} -t -c \"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';\""
    success, source_tables = execute_remote_command(source['host'], source_tables_cmd)
    if not success:
        return False
    
    tables = [table.strip() for table in source_tables.strip().split('\n') if table.strip()]
    verification_results = {}
    
    all_valid = True
    
    for table in tables:
        # 获取源表行数
        source_count_cmd = f"PGPASSWORD={source['password']} psql -h {source['host']} -p {source['port']} -U {source['user']} -d {source['dbname']} -t -c \"SELECT COUNT(*) FROM {table};\""
        success, source_count = execute_remote_command(source['host'], source_count_cmd)
        if not success:
            all_valid = False
            verification_results[table] = {'status': 'error', 'message': '无法获取源表行数'}
            continue
        
        # 获取目标表行数
        target_count_cmd = f"PGPASSWORD={target['password']} psql -h {target['host']} -p {target['port']} -U {target['user']} -d {target['dbname']} -t -c \"SELECT COUNT(*) FROM {table};\""
        success, target_count = execute_remote_command(target['host'], target_count_cmd)
        if not success:
            all_valid = False
            verification_results[table] = {'status': 'error', 'message': '无法获取目标表行数'}
            continue
        
        # 比较行数
        source_count = source_count.strip()
        target_count = target_count.strip()
        
        if source_count == target_count:
            verification_results[table] = {
                'status': 'success',
                'source_count': source_count,
                'target_count': target_count,
                'message': '行数匹配'
            }
        else:
            all_valid = False
            verification_results[table] = {
                'status': 'failed',
                'source_count': source_count,
                'target_count': target_count,
                'message': '行数不匹配'
            }
    
    # 记录验证结果
    logging.info(f"数据完整性验证: {'成功' if all_valid else '失败'}")
    for table, result in verification_results.items():
        logging.info(f"表 {table}: {result['status']} - {result['message']}")
    
    return all_valid

def simulate_disaster():
    """模拟灾难场景（停止主数据库服务）"""
    logging.info("模拟灾难场景...")
    
    # 停止主数据库服务
    stop_cmd = "sudo systemctl stop postgresql"
    success, output = execute_remote_command(CONFIG['primary_db']['host'], stop_cmd)
    
    if success:
        logging.info("主数据库服务已停止")
        
        # 确认服务已停止
        check_cmd = "sudo systemctl status postgresql"
        _, status_output = execute_remote_command(CONFIG['primary_db']['host'], check_cmd)
        if "inactive" in status_output or "failed" in status_output:
            logging.info("确认主数据库服务已停止")
            return True
        else:
            logging.error("主数据库服务未成功停止")
            return False
    else:
        logging.error("无法停止主数据库服务")
        return False

def recover_from_disaster():
    """从灾难中恢复"""
    logging.info("开始灾难恢复流程...")
    
    # 记录恢复开始时间
    recovery_start_time = time.time()
    
    # 1. 从备份服务器获取最新备份
    latest_backup_cmd = f"ls -t {CONFIG['backup_server']['backup_dir']}/db_backup_*.sql | head -n 1"
    success, latest_backup = execute_remote_command(CONFIG['backup_server']['host'], latest_backup_cmd)
    if not success:
        return False, "无法获取最新备份"
    
    latest_backup = latest_backup.strip()
    logging.info(f"找到最新备份: {latest_backup}")
    
    # 2. 传输备份到DR站点
    scp_cmd = f"scp {CONFIG['backup_server']['host']}:{latest_backup} /tmp/latest_backup.sql"
    try:
        subprocess.run(scp_cmd, shell=True, check=True)
        logging.info("备份已传输到DR站点")
    except subprocess.CalledProcessError as e:
        logging.error(f"无法传输备份: {str(e)}")
        return False, "备份传输失败"
    
    # 3. 在DR站点恢复数据库
    # 3.1 停止DR站点数据库服务
    stop_dr_cmd = "sudo systemctl stop postgresql"
    success, _ = execute_remote_command(CONFIG['dr_site']['host'], stop_dr_cmd)
    if not success:
        return False, "无法停止DR站点数据库服务"
    
    # 3.2 删除并重新创建数据库
    drop_db_cmd = f"PGPASSWORD={CONFIG['dr_site']['password']} psql -h localhost -U {CONFIG['dr_site']['user']} -c \"DROP DATABASE IF EXISTS {CONFIG['dr_site']['dbname']};\""
    success, _ = execute_remote_command(CONFIG['dr_site']['host'], drop_db_cmd)
    if not success:
        return False, "无法删除DR站点数据库"
    
    create_db_cmd = f"PGPASSWORD={CONFIG['dr_site']['password']} psql -h localhost -U {CONFIG['dr_site']['user']} -c \"CREATE DATABASE {CONFIG['dr_site']['dbname']};\""
    success, _ = execute_remote_command(CONFIG['dr_site']['host'], create_db_cmd)
    if not success:
        return False, "无法创建DR站点数据库"
    
    # 3.3 恢复备份
    restore_cmd = f"PGPASSWORD={CONFIG['dr_site']['password']} psql -h localhost -U {CONFIG['dr_site']['user']} -d {CONFIG['dr_site']['dbname']} -f /tmp/latest_backup.sql"
    success, _ = execute_remote_command(CONFIG['dr_site']['host'], restore_cmd)
    if not success:
        return False, "数据库恢复失败"
    
    # 3.4 启动DR站点数据库服务
    start_dr_cmd = "sudo systemctl start postgresql"
    success, _ = execute_remote_command(CONFIG['dr_site']['host'], start_dr_cmd)
    if not success:
        return False, "无法启动DR站点数据库服务"
    
    # 4. 更新应用程序配置，指向DR站点数据库
    update_app_config_cmd = "sudo sed -i 's/primary-db.example.com/dr-db.example.com/g' /etc/application/database.conf"
    success, _ = execute_remote_command(CONFIG['dr_site']['host'], update_app_config_cmd)
    if not success:
        return False, "无法更新应用程序配置"
    
    # 5. 重启应用程序服务
    restart_app_cmd = "sudo systemctl restart application-service"
    success, _ = execute_remote_command(CONFIG['dr_site']['host'], restart_app_cmd)
    if not success:
        return False, "无法重启应用程序服务"
    
    # 计算恢复时间
    recovery_time = time.time() - recovery_start_time
    
    logging.info(f"灾难恢复流程完成，耗时: {recovery_time:.2f} 秒")
    
    return True, recovery_time

def verify_service_availability():
    """验证DR站点服务可用性"""
    logging.info("验证DR站点服务可用性...")
    
    # 检查数据库连接
    db_check_cmd = f"PGPASSWORD={CONFIG['dr_site']['password']} psql -h localhost -U {CONFIG['dr_site']['user']} -d {CONFIG['dr_site']['dbname']} -c \"SELECT 1;\""
    success, _ = execute_remote_command(CONFIG['dr_site']['host'], db_check_cmd)
    if not success:
        logging.error("DR站点数据库连接失败")
        return False
    
    # 检查应用程序服务
    app_check_cmd = "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/health"
    success, http_code = execute_remote_command(CONFIG['dr_site']['host'], app_check_cmd)
    if success and http_code.strip() == "200":
        logging.info("DR站点应用程序服务正常")
        return True
    else:
        logging.error(f"DR站点应用程序服务异常，HTTP状态码: {http_code}")
        return False

def run_disaster_recovery_test():
    """运行灾难恢复测试"""
    logging.info("开始灾难恢复测试")
    
    # 记录测试开始时间
    test_start_time = time.time()
    
    try:
        # 1. 记录最近备份时间（用于计算RPO）
        latest_backup_cmd = f"ls -lt {CONFIG['backup_server']['backup_dir']}/db_backup_*.sql | head -n 1 | awk '{{print $6, $7, $8}}'"
        success, backup_time_str = execute_remote_command(CONFIG['backup_server']['host'], latest_backup_cmd)
        if not success:
            raise Exception("无法获取备份时间")
        
        backup_time_str = backup_time_str.strip()
        logging.info(f"最近备份时间: {backup_time_str}")
        
        # 解析备份时间（这里简化处理，实际应根据实际格式调整）
        # 假设格式为 "MMM DD HH:MM" 或 "MMM DD YYYY"
        backup_time = datetime.strptime(backup_time_str, "%b %d %H:%M")
        current_year = datetime.now().year
        backup_time = backup_time.replace(year=current_year)
        
        # 2. 模拟灾难
        if not simulate_disaster():
            raise Exception("模拟灾难失败")
        
        # 3. 执行灾难恢复
        recovery_success, recovery_time = recover_from_disaster()
        if not recovery_success:
            raise Exception(f"灾难恢复失败: {recovery_time}")
        
        # 4. 验证服务可用性
        if not verify_service_availability():
            raise Exception("服务可用性验证失败")
        
        # 5. 验证数据完整性
        if not verify_data_integrity(CONFIG['primary_db'], CONFIG['dr_site']):
            raise Exception("数据完整性验证失败")
        
        # 计算RTO和RPO
        rto = recovery_time
        rpo = (datetime.now() - backup_time).total_seconds()
        
        # 检查是否满足目标
        rto_met = rto <= CONFIG['test']['rto_target']
        rpo_met = rpo <= CONFIG['test']['rpo_target']
        
        # 生成测试报告
        test_report = {
            'test_start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'test_duration': time.time() - test_start_time,
            'recovery_time': rto,
            'recovery_point_objective': rpo,
            'rto_target_met': rto_met,
            'rpo_target_met': rpo_met,
            'overall_result': rto_met and rpo_met,
            'verification_results': {
                'service_availability': True,
                'data_integrity': True
            }
        }
        
        # 记录测试报告
        logging.info("灾难恢复测试报告:")
        logging.info(json.dumps(test_report, indent=2))
        
        # 将报告保存到文件
        report_file = f"/logs/dr_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(test_report, f, indent=2)
        
        logging.info(f"测试报告已保存到: {report_file}")
        
        if test_report['overall_result']:
            logging.info("灾难恢复测试成功：满足RTO和RPO目标")
            print("测试成功：满足RTO和RPO目标")
        else:
            logging.warning("灾难恢复测试完成，但未满足所有目标")
            print("测试完成，但未满足所有目标")
            
            if not rto_met:
                print(f"警告：RTO未达标 - 实际: {rto:.2f}秒, 目标: {CONFIG['test']['rto_target']}秒")
            if not rpo_met:
                print(f"警告：RPO未达标 - 实际: {rpo:.2f}秒, 目标: {CONFIG['test']['rpo_target']}秒")
        
        return test_report['overall_result']
        
    except Exception as e:
        logging.error(f"灾难恢复测试失败: {str(e)}")
        print(f"测试失败: {str(e)}")
        return False
    finally:
        # 清理：恢复主数据库服务（在实际测试中可能不需要）
        # start_primary_cmd = "sudo systemctl start postgresql"
        # execute_remote_command(CONFIG['primary_db']['host'], start_primary_cmd)
        pass

if __name__ == "__main__":
    run_disaster_recovery_test()
