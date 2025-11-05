
# 【章节重点难点总结】

# - 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准
# - 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡

# 【课后思考/练习题】

# 1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
# 2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。

## HDFS数据存储测试示例

# 【阅读提示】本篇聚焦：HDFS数据存储测试示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

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