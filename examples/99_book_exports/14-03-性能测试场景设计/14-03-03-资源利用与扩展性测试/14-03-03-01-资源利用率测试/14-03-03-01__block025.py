# 资源利用率测试示例
def test_resource_utilization():
    # 1. 配置监控系统
    monitor = start_resource_monitoring()

    # 2. 执行不同负载的测试作业
    workloads = [
        {"name": "cpu_intensive", "config": cpu_intensive_config},
        {"name": "memory_intensive", "config": memory_intensive_config},
        {"name": "io_intensive", "config": io_intensive_config},
        {"name": "balanced", "config": balanced_workload_config}
    ]

    results = {}
    for workload in workloads:
        # 启动监控收集
        monitor.start_collection()

        # 执行工作负载
        execute_workload(workload["config"])

        # 获取资源指标
        metrics = monitor.get_metrics()

        # 记录结果
        results[workload["name"]] = metrics

    # 3. 分析资源利用情况
    assert verify_cpu_utilization(results) > 0.7, "CPU利用率过低"
    assert verify_memory_utilization(results) < 0.9, "内存使用率过高"
    assert verify_io_balance(results) == True, "IO负载不均衡"
    assert verify_resource_efficiency(results) > 0.8, "资源利用效率低"
