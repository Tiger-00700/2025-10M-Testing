# 数据记录完整性测试示例
def test_data_record_integrity():
    # 1. 获取源数据和目标数据
    source_data = get_source_data()
    target_data = get_target_data()

    # 2. 验证记录数量
    assert len(source_data) == len(target_data), "记录数量不一致"

    # 3. 验证主键唯一性
    source_primary_keys = [record["primary_key"] for record in source_data]
    target_primary_keys = [record["primary_key"] for record in target_data]

    assert len(source_primary_keys) == len(set(source_primary_keys)), "源数据主键不唯一"
    assert len(target_primary_keys) == len(set(target_primary_keys)), "目标数据主键不唯一"

    # 4. 验证主键一致性
    missing_keys = set(source_primary_keys) - set(target_primary_keys)
    assert len(missing_keys) == 0, f"存在丢失的主键: {missing_keys}"

    # 5. 验证引用完整性
    assert verify_referential_integrity(target_data) == True, "引用完整性验证失败"
