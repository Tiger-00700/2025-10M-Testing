## 数值计算准确性测试示例


def test_numeric_calculation_accuracy():
    # 1. 准备测试数据
    source_data = generate_test_numeric_data(count=1000)

    # 2. 执行数据处理/转换
    processed_data = process_numeric_data(source_data)

    # 3. 执行关键计算验证
    validation_results = {
        "sum_validation": verify_sum_calculations(source_data, processed_data),
        "average_validation": verify_average_calculations(source_data, processed_data),
        "max_min_validation": verify_max_min_calculations(source_data, processed_data),
        "percentage_validation": verify_percentage_calculations(source_data, processed_data)
    }

    # 4. 验证计算结果
    for validation_type, result in validation_results.items():
        assert result["accuracy"] > 0.999, f"{validation_type}准确性不足: {result['accuracy']}"
        assert result["error_count"] == 0, f"{validation_type}存在错误: {result['error_count']}"

    # 5. 验证边界情况处理
    boundary_data = generate_boundary_test_data()
    boundary_results = process_numeric_data(boundary_data)
    assert verify_boundary_conditions(boundary_results) == True, "边界条件处理错误"
