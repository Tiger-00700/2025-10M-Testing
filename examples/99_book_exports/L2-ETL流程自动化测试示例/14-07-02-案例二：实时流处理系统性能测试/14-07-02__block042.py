## 性能测试监控示例


def monitor_performance_metrics():
    metrics = {
        "throughput": get_messages_per_second(),
        "latency": get_end_to_end_latency(),
        "resource_usage": get_cluster_resource_usage(),
        "error_rate": get_error_rate()
    }

    # 记录和分析指标
    log_metrics(metrics)
    assert metrics["throughput"] > expected_throughput
    assert metrics["latency"] < max_acceptable_latency
    assert metrics["error_rate"] < max_acceptable_error_rate
