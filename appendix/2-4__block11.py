#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    filename='/logs/hdfs_restore_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# HDFS配置
HDFS_CMD = '/usr/bin/hadoop fs'
LOCAL_BACKUP_DIR = '/backup/hdfs'
HDFS_TEST_DIR = '/test_restore'
HDFS_TEST_FILES = [
    'file1.txt',
    'file2.txt',
    'file3.txt'
]

def execute_command(command):
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

def prepare_test_data():
    """准备测试数据"""
    logging.info("准备HDFS测试数据...")
    
    # 创建本地测试文件
    local_test_dir = os.path.join('/tmp', 'hdfs_test_data')
    os.makedirs(local_test_dir, exist_ok=True)
    
    # 创建测试文件
    for i, filename in enumerate(HDFS_TEST_FILES, 1):
        file_path = os.path.join(local_test_dir, filename)
        with open(file_path, 'w') as f:
            f.write(f"这是测试文件 {i} 的内容。\n")
            f.write(f"生成时间: {datetime.now()}\n")
            f.write(f"包含{i*1000}个随机字符: {'x' * (i*1000)}")
    
    # 创建HDFS目录
    execute_command(f"{HDFS_CMD} -mkdir -p {HDFS_TEST_DIR}")
    
    # 上传文件到HDFS
    for filename in HDFS_TEST_FILES:
        local_path = os.path.join(local_test_dir, filename)
        hdfs_path = f"{HDFS_TEST_DIR}/{filename}"
        execute_command(f"{HDFS_CMD} -put {local_path} {hdfs_path}")
    
    logging.info("HDFS测试数据准备完成")

def create_partial_backup():
    """创建部分备份"""
    logging.info("创建HDFS部分备份...")
    
    # 确保备份目录存在
    os.makedirs(LOCAL_BACKUP_DIR, exist_ok=True)
    
    # 创建部分文件的备份
    backup_files = HDFS_TEST_FILES[:2]  # 只备份前两个文件
    backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(LOCAL_BACKUP_DIR, f"partial_backup_{backup_timestamp}")
    os.makedirs(backup_dir)
    
    for filename in backup_files:
        hdfs_path = f"{HDFS_TEST_DIR}/{filename}"
        local_path = os.path.join(backup_dir, filename)
        execute_command(f"{HDFS_CMD} -get {hdfs_path} {local_path}")
    
    logging.info(f"HDFS部分备份完成，备份目录: {backup_dir}")
    return backup_dir, backup_files

def simulate_data_loss():
    """模拟数据丢失"""
    logging.info("模拟HDFS数据丢失...")
    
    # 删除所有测试文件
    for filename in HDFS_TEST_FILES:
        hdfs_path = f"{HDFS_TEST_DIR}/{filename}"
        execute_command(f"{HDFS_CMD} -rm -f {hdfs_path}")
    
    logging.info("HDFS数据已删除")

def restore_partial_data(backup_dir, backup_files):
    """恢复部分数据"""
    logging.info("恢复HDFS部分数据...")
    
    # 确保HDFS目录存在
    execute_command(f"{HDFS_CMD} -mkdir -p {HDFS_TEST_DIR}")
    
    # 恢复备份的文件
    for filename in backup_files:
        local_path = os.path.join(backup_dir, filename)
        hdfs_path = f"{HDFS_TEST_DIR}/{filename}"
        execute_command(f"{HDFS_CMD} -put {local_path} {hdfs_path}")
    
    logging.info("HDFS部分数据恢复完成")

def verify_partial_restore(backup_files):
    """验证部分恢复结果"""
    logging.info("验证HDFS部分恢复结果...")
    
    # 检查已恢复的文件
    success = True
    for filename in backup_files:
        hdfs_path = f"{HDFS_TEST_DIR}/{filename}"
        exists, _ = execute_command(f"{HDFS_CMD} -test -e {hdfs_path}")
        if not exists:
            logging.error(f"文件 {filename} 未成功恢复")
            success = False
        else:
            # 检查文件内容
            check_cmd = f"{HDFS_CMD} -cat {hdfs_path} | wc -c"
            exists, output = execute_command(check_cmd)
            if exists:
                file_size = output.strip()
                logging.info(f"文件 {filename} 恢复成功，大小: {file_size} 字节")
            else:
                logging.error(f"无法读取文件 {filename} 的内容")
                success = False
    
    # 确认未备份的文件不存在
    for filename in HDFS_TEST_FILES[2:]:  # 第三个文件未备份
        hdfs_path = f"{HDFS_TEST_DIR}/{filename}"
        exists, _ = execute_command(f"{HDFS_CMD} -test -e {hdfs_path}")
        if exists:
            logging.error(f"未备份的文件 {filename} 不应该存在")
            success = False
        else:
            logging.info(f"确认未备份的文件 {filename} 不存在")
    
    return success

def test_partial_restore():
    """测试HDFS部分恢复功能"""
    logging.info("开始HDFS部分恢复测试")
    
    try:
        # 记录开始时间
        start_time = time.time()
        
        # 1. 准备测试数据
        prepare_test_data()
        
        # 2. 创建部分备份
        backup_dir, backup_files = create_partial_backup()
        
        # 3. 模拟数据丢失
        simulate_data_loss()
        
        # 4. 恢复部分数据
        restore_partial_data(backup_dir, backup_files)
        
        # 5. 验证恢复结果
        verification_success = verify_partial_restore(backup_files)
        
        # 计算总耗时
        duration = time.time() - start_time
        logging.info(f"HDFS部分恢复测试{'成功' if verification_success else '失败'}，耗时: {duration:.2f} 秒")
        
        return verification_success
        
    except Exception as e:
        logging.error(f"测试过程中发生错误: {str(e)}")
        return False
    finally:
        # 清理测试数据
        cleanup_cmd = f"{HDFS_CMD} -rm -r -f {HDFS_TEST_DIR}"
        execute_command(cleanup_cmd)
        logging.info("测试数据清理完成")

if __name__ == "__main__":
    success = test_partial_restore()
    if success:
        logging.info("HDFS部分恢复测试成功")
        print("测试成功")
    else:
        logging.error("HDFS部分恢复测试失败")
        print("测试失败")
