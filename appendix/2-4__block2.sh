# 创建测试文件并设置权限
hadoop fs -mkdir -p /test/permission_test
hadoop fs -put local_test_file.txt /test/permission_test/
hadoop fs -chmod 600 /test/permission_test/local_test_file.txt

# 使用不同用户尝试访问
su - test_user -c "hadoop fs -cat /test/permission_test/local_test_file.txt"
