# 批处理数据采集测试示例
def test_batch_data_collection():
    # 1. 准备测试数据
    source_data = prepare_source_data(record_count=1000, with_edge_cases=True)
    load_test_data_to_source(source_data)

    # 2. 执行数据采集作业
    job_id = trigger_data_collection_job(config=batch_collection_config)
    wait_for_job_completion(job_id)

    # 3. 验证采集结果
    source_records = get_source_records()
    target_records = get_target_records()

    # 4. 断言验证
    assert len(source_records) == len(target_records), "数据量不匹配"
    assert verify_data_consistency(source_records, target_records), "数据不一致"
    assert verify_metadata_preservation(source_records, target_records), "元数据丢失"
