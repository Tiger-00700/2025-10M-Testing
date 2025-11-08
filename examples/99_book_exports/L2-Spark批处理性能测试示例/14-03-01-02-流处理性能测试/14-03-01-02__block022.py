## Kafka+Spark Streaming性能测试示例


def test_streaming_performance():
    # 1. 配置测试环境
    kafka_brokers = ["broker1:9092", "broker2:9092"]
    initialize_kafka_topics(kafka_brokers, topics=["test_topic"])

    # 2. 启动流处理作业
    spark_streaming_job = start_spark_streaming_job(kafka_brokers)

    # 3. 执行性能测试（不同消息速率）
    message_rates = [10000, 50000, 100000, 200000]  # 消息/秒
    results = {}

    for rate in message_rates:
        # 启动消息生成器
        producer = start_message_production(kafka_brokers, "test_topic", rate=rate, duration=300)

        # 收集性能指标
        metrics = collect_streaming_metrics(spark_streaming_job, duration=300)

        # 记录结果
        results[rate] = {
            "throughput": metrics["messages_processed_per_second"],
            "latency": metrics["average_latency_ms"],
            "error_rate": metrics["error_rate"],
            "resource_usage": metrics["resource_utilization"]
        }

    # 4. 分析性能结果
    assert verify_max_throughput(results) > 150000, "最大吞吐量未达标"
    assert verify_latency_under_load(results, max_rate=200000) < 500, "高负载下延迟过高"
    assert verify_error_rate(results) < 0.001, "错误率过高"
