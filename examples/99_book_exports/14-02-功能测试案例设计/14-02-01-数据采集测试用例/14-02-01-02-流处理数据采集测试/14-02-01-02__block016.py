# 流处理数据采集测试示例
def test_stream_data_collection():
    # 1. 设置流处理环境和监控
    setup_stream_processing_pipeline()
    start_metrics_collection()

    # 2. 生成测试事件流
    event_generator = start_event_generation(rate=1000, duration=300)  # 每秒1000条，持续5分钟

    # 3. 注入异常情况
    inject_network_delay(duration=10)  # 注入10秒网络延迟
    inject_backpressure_condition(duration=30)  # 注入30秒背压

    # 4. 验证处理结果
    source_events = get_generated_events()
    processed_events = get_processed_events()

    # 5. 断言验证
    assert len(source_events) == len(processed_events), "事件丢失"
    assert verify_event_order_consistency(source_events, processed_events), "事件顺序错误"
    assert verify_latency_metrics(max_acceptable_latency=500), "延迟超过阈值"
