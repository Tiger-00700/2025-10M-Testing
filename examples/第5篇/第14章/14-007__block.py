# Spark批处理性能测试示例
def test_spark_batch_performance():
    # 1. 初始化性能测试环境
    spark = initialize_spark_cluster(executors=10, memory_per_executor="8g")
    metrics_collector = start_performance_metrics_collection()

    # 2. 准备测试数据（不同规模）
    data_sizes = [10, 100, 1000]  # 单位：GB
    results = {}

    for size in data_sizes:
        # 生成测试数据
        test_data = generate_test_dataset(size_gb=size)

        # 执行批处理作业
        start_time = time.time()
        job_id = submit_spark_job(spark, test_data, job_config)
        wait_for_job_completion(job_id)
        end_time = time.time()

        # 收集性能指标
        execution_time = end_time - start_time
        resource_metrics = metrics_collector.get_job_metrics(job_id)

        # 记录结果
        results[size] = {
            "execution_time": execution_time,
            "resource_usage": resource_metrics,
            "throughput": size / execution_time  # GB/sec
        }

    # 3. 分析性能趋势
    assert analyze_performance_scaling(results) == "linear", "性能扩展不符合预期"
    assert verify_resource_utilization(results) > 0.8, "资源利用率过低"
    assert verify_performance_baseline(results) == True, "未达到性能基线"
