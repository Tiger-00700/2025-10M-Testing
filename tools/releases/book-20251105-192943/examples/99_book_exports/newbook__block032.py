
## 时间一致性测试示例

# 【阅读提示】本篇聚焦：时间一致性测试示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

def test_temporal_consistency():
    # 1. 获取时序数据
    time_series_data = get_time_series_data(start_date="2023-01-01", end_date="2023-12-31")

    # 2. 执行时间一致性验证
    validation_results = {
        "timestamp_order": verify_timestamp_order(time_series_data),
        "time_gaps": detect_time_gaps(time_series_data, max_allowed_gap="1h"),
        "duplicate_timestamps": detect_duplicate_timestamps(time_series_data),
        "time_partition_integrity": verify_time_partition_integrity(time_series_data)
    }

    # 3. 验证结果
    assert validation_results["timestamp_order"], "时间戳顺序错误"
    assert validation_results["time_gaps"] == 0, f"存在时间间隔: {validation_results['time_gaps']}"
    assert validation_results["duplicate_timestamps"] == 0, f"存在重复时间戳: {validation_results['duplicate_timestamps']}"
    assert validation_results["time_partition_integrity"], "时间分区完整性验证失败"