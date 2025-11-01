# 水平扩展测试示例
def test_horizontal_scalability():
    # 1. 初始化测试环境
    test_cluster = initialize_test_cluster()

    # 2. 执行扩展测试
    node_counts = [2, 4, 8, 16]
    data_size_gb = 1000
    results = {}

    for node_count in node_counts:
        # 调整集群大小
        test_cluster.resize(node_count)

        # 准备测试数据
        prepare_test_data(test_cluster, size_gb=data_size_gb)

        # 执行性能测试
        start_time = time.time()
        execute_test_workload(test_cluster)
        execution_time = time.time() - start_time

        # 收集性能指标
        metrics = collect_performance_metrics(test_cluster)

        # 记录结果
        results[node_count] = {
            "execution_time": execution_time,
            "throughput": data_size_gb / execution_time,
            "per_node_throughput": (data_size_gb / execution_time) / node_count,
            "resource_utilization": metrics["resource_utilization"]
        }

    # 3. 分析扩展性
    assert analyze_scaling_efficiency(results) > 0.8, "扩展效率低于预期"
    assert verify_linear_scaling(results) == True, "未实现线性扩展"
    assert verify_per_node_efficiency(results) > 0.9, "节点效率下降明显"
