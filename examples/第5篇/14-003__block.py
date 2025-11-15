# HDFS数据存储测试示例
def test_hdfs_data_storage():
    # 1. 准备测试数据
    test_data = generate_test_data(size_gb=5)

    # 2. 写入HDFS
    hdfs_path = "/test/data/test_data.csv"
    write_to_hdfs(test_data, hdfs_path, replication_factor=3)

    # 3. 读取数据
    read_data = read_from_hdfs(hdfs_path)

    # 4. 验证数据一致性
    assert compare_data(test_data, read_data) == True, "数据不一致"

    # 5. 验证复制因子
    assert get_hdfs_replication_factor(hdfs_path) == 3, "复制因子错误"

    # 6. 验证权限控制
    assert verify_hdfs_permissions(hdfs_path, "read-only-group") == "READ", "权限错误"
