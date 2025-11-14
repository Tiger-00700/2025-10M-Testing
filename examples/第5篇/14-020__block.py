# 授权机制测试示例
def test_authorization_security():
    # 1. 准备测试环境
    setup_authorization_test_env()

    # 2. 定义测试用户和角色
    roles = [
        {"name": "admin", "permissions": ["read", "write", "delete", "admin"]},
        {"name": "editor", "permissions": ["read", "write"]},
        {"name": "viewer", "permissions": ["read"]}
    ]

    # 3. 创建测试用户
    users = {
        "admin_user": create_test_user_with_role("admin_user", "admin"),
        "editor_user": create_test_user_with_role("editor_user", "editor"),
        "viewer_user": create_test_user_with_role("viewer_user", "viewer")
    }

    # 4. 执行权限测试
    test_operations = [
        {"name": "read_operation", "required_permission": "read"},
        {"name": "write_operation", "required_permission": "write"},
        {"name": "delete_operation", "required_permission": "delete"},
        {"name": "admin_operation", "required_permission": "admin"}
    ]

    # 期望结果: 用户应该能执行有权限的操作，不能执行无权限的操作
    for username, user in users.items():
        for operation in test_operations:
            result = execute_operation_as_user(user, operation["name"])
            user_role = next(role for role in roles if role["name"] == user["role"])
            should_succeed = operation["required_permission"] in user_role["permissions"]

            assert result["success"] == should_succeed, \
                f"权限验证失败: 用户 {username} 执行 {operation['name']} 操作"

    # 5. 测试权限提升攻击
    privilege_escalation_test = attempt_privilege_escalation(users["viewer_user"])
    assert not privilege_escalation_test["success"], "权限提升攻击测试失败"
