# 数据字段完整性测试示例
def test_data_field_integrity():
    # 1. 获取测试数据
    test_data = get_test_data()

    # 2. 定义必填字段和规则
    required_fields = ["id", "name", "timestamp"]
    field_rules = {
        "id": {"min_length": 1, "max_length": 50},
        "name": {"min_length": 1, "max_length": 255},
        "amount": {"min_value": 0, "max_value": 1000000},
        "status": {"allowed_values": ["ACTIVE", "INACTIVE", "PENDING"]}
    }

    # 3. 执行字段验证
    validation_results = validate_data_fields(test_data, required_fields, field_rules)

    # 4. 验证结果
    assert validation_results["missing_required_fields"] == 0, "存在必填字段缺失"
    assert validation_results["invalid_field_lengths"] == 0, "存在字段长度错误"
    assert validation_results["invalid_field_values"] == 0, "存在字段值错误"
    assert validation_results["invalid_field_formats"] == 0, "存在字段格式错误"
