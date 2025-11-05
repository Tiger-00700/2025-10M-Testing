> 【章节重点难点总结】

- 要点：RBAC/ABAC、KMS、密钥轮换、审计与告警
- 难点：性能与安全的权衡、跨组件信任链验证

> 【课后思考/练习题】

1. 设计一次端到端数据加密（At-Rest/In-Transit）的验证方案。
2. 如何验证最低权限原则在数据湖的落地有效？


## 数据记录完整性测试示例

> 【阅读提示】本篇聚焦：数据记录完整性测试示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

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
