#!/bin/bash

# 测试MySQL全量备份功能和性能

# 配置参数
DB_HOST="localhost"
DB_USER="backup_user"
DB_PASSWORD="secure_password"
DB_NAME="test_database"
BACKUP_DIR="/backup/mysql/full"
LOG_FILE="/logs/backup_test.log"

# 记录测试开始时间
start_time=$(date +%s)
echo "[$(date)] 开始MySQL全量备份测试" >> $LOG_FILE

# 执行全量备份
echo "[$(date)] 正在执行全量备份..." >> $LOG_FILE
mysqldump --host=$DB_HOST --user=$DB_USER --password=$DB_PASSWORD --single-transaction --quick --lock-tables=false --all-databases > $BACKUP_DIR/full_backup_$(date +%Y%m%d_%H%M%S).sql

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "[$(date)] 全量备份执行成功" >> $LOG_FILE
    
    # 验证备份文件大小
    backup_file=$(ls -t $BACKUP_DIR/full_backup_*.sql | head -n 1)
    file_size=$(du -h $backup_file | cut -f1)
    echo "[$(date)] 备份文件大小: $file_size" >> $LOG_FILE
    
    # 验证备份文件内容
    echo "[$(date)] 验证备份文件内容..." >> $LOG_FILE
    table_count=$(grep -c "CREATE TABLE" $backup_file)
    echo "[$(date)] 备份文件中包含 $table_count 个表" >> $LOG_FILE
    
    # 记录测试结束时间
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    echo "[$(date)] MySQL全量备份测试完成，耗时: $duration 秒" >> $LOG_FILE
else
    echo "[$(date)] 全量备份执行失败" >> $LOG_FILE
    exit 1
fi
