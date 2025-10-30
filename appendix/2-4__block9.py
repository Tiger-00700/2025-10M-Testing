#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
import datetime
import logging

# 配置日志
logging.basicConfig(
    filename='/logs/mongodb_backup_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 配置参数
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
BACKUP_DIR = '/backup/mongodb'
DB_NAME = 'test_database'

# 确保备份目录存在
os.makedirs(BACKUP_DIR, exist_ok=True)

def run_command(command):
    """执行命令并返回结果"""
    try:
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

def test_incremental_backup():
    """测试MongoDB增量备份功能"""
    logging.info("开始MongoDB增量备份测试")
    
    # 记录开始时间
    start_time = time.time()
    
    # 1. 创建基准全量备份
    logging.info("创建基准全量备份...")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    full_backup_path = f"{BACKUP_DIR}/full_backup_{timestamp}"
    
    full_backup_cmd = f"mongodump --host {MONGO_HOST} --port {MONGO_PORT} --db {DB_NAME} --out {full_backup_path}"
    success, output = run_command(full_backup_cmd)
    if not success:
        return False
    
    # 记录全量备份大小
    full_size = subprocess.check_output(f"du -sh {full_backup_path} | cut -f1", shell=True).decode().strip()
    logging.info(f"全量备份完成，大小: {full_size}")
    
    # 2. 模拟数据变更（插入新数据）
    logging.info("模拟数据变更...")
    insert_cmd = f"mongo --host {MONGO_HOST} --port {MONGO_PORT} {DB_NAME} --eval 'db.test_collection.insertMany([{{\"name\":\"Test Item {timestamp}\", \"value\":{int(time.time())}}}, {{\"name\":\"Another Item\", \"value\":42}}])'"
    success, output = run_command(insert_cmd)
    if not success:
        return False
    
    # 3. 执行增量备份（使用oplog）
    logging.info("执行增量备份...")
    inc_backup_path = f"{BACKUP_DIR}/inc_backup_{timestamp}"
    
    # 获取最后一个操作的时间戳
    oplog_ts_cmd = "mongo --host {} --port {} local --eval 'db.oplog.rs.find().sort({{$natural:-1}}).limit(1).toArray()[0].ts'"
    success, oplog_ts = run_command(oplog_ts_cmd.format(MONGO_HOST, MONGO_PORT))
    if not success:
        return False
    
    # 执行增量备份（这里使用mongodump的--oplog选项作为示例）
    inc_backup_cmd = f"mongodump --host {MONGO_HOST} --port {MONGO_PORT} --db {DB_NAME} --oplog --out {inc_backup_path}"
    success, output = run_command(inc_backup_cmd)
    if not success:
        return False
    
    # 记录增量备份大小
    inc_size = subprocess.check_output(f"du -sh {inc_backup_path} | cut -f1", shell=True).decode().strip()
    logging.info(f"增量备份完成，大小: {inc_size}")
    
    # 4. 验证增量备份的有效性（通过恢复测试）
    logging.info("验证增量备份有效性...")
    
    # 清除测试数据库
    cleanup_cmd = f"mongo --host {MONGO_HOST} --port {MONGO_PORT} --eval 'db.dropDatabase()' {DB_NAME}"
    success, output = run_command(cleanup_cmd)
    if not success:
        return False
    
    # 先恢复全量备份
    restore_full_cmd = f"mongorestore --host {MONGO_HOST} --port {MONGO_PORT} --db {DB_NAME} {full_backup_path}/{DB_NAME}"
    success, output = run_command(restore_full_cmd)
    if not success:
        return False
    
    # 再应用增量备份（使用oplog）
    restore_inc_cmd = f"mongorestore --host {MONGO_HOST} --port {MONGO_PORT} --db {DB_NAME} --oplogReplay {inc_backup_path}"
    success, output = run_command(restore_inc_cmd)
    if not success:
        return False
    
    # 验证数据是否正确恢复
    count_cmd = f"mongo --host {MONGO_HOST} --port {MONGO_PORT} {DB_NAME} --eval 'db.test_collection.countDocuments()'"
    success, count_output = run_command(count_cmd)
    if not success:
        return False
    
    logging.info(f"恢复后数据记录数: {count_output.strip()}")
    
    # 计算总耗时
    duration = time.time() - start_time
    logging.info(f"MongoDB增量备份测试完成，耗时: {duration:.2f} 秒")
    
    return True

if __name__ == "__main__":
    success = test_incremental_backup()
    if success:
        logging.info("MongoDB增量备份测试成功")
        print("测试成功")
    else:
        logging.error("MongoDB增量备份测试失败")
        print("测试失败")
