# 创建测试目录
hadoop fs -mkdir -p /test/upload_test

# 准备测试文件
seq 1000000 > local_test_file.txt

# 测试文件上传
hadoop fs -put local_test_file.txt /test/upload_test/

# 验证上传成功
hadoop fs -ls /test/upload_test/
hadoop fs -du -h /test/upload_test/local_test_file.txt

# 测试文件下载
hadoop fs -get /test/upload_test/local_test_file.txt local_download_test.txt

# 验证文件一致性
diff local_test_file.txt local_download_test.txt
