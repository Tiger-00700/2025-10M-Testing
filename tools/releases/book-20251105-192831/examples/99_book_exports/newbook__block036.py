
## 敏感数据保护测试示例

# 【阅读提示】本篇聚焦：敏感数据保护测试示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

def test_sensitive_data_protection():
    # 1. 准备包含敏感信息的测试数据
    test_data = generate_sensitive_test_data()

    # 2. 测试数据脱敏
    masked_data = apply_data_masking(test_data)
    masking_results = verify_data_masking(masked_data)
    assert masking_results["all_sensitive_masked"], "敏感数据未完全脱敏"
    assert masking_results["non_sensitive_preserved"], "非敏感数据被错误脱敏"

    # 3. 测试不同角色的数据访问
    roles = ["admin", "analyst", "viewer"]
    access_results = {}

    for role in roles:
        user = create_test_user_with_role(f"{role}_user", role)
        accessed_data = get_data_as_user(user)
        access_results[role] = verify_role_based_access(accessed_data, role)

    for role, result in access_results.items():
        assert result["access_correct"], f"角色 {role} 的数据访问不正确"

    # 4. 测试敏感数据访问审计
    audit_results = test_audit_logging(test_data)
    assert audit_results["all_access_logged"], "敏感数据访问未完全记录"
    assert audit_results["log_contains_required_fields"], "审计日志缺少必要字段"

    # 5. 测试数据导出限制
    export_results = test_data_export_restrictions()
    assert export_results["sensitive_restricted"], "敏感数据导出未受限制"
    assert export_results["export_audited"], "数据导出未记录审计日志"