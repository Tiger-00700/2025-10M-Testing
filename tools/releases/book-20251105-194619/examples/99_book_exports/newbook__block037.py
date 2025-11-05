
# 【章节重点难点总结】

# - 要点：覆盖/真实性/隔离/可重现、元数据与血缘管理

# 【小结】
# - 用 3~5 条项目化要点复盘本章内容
# - 指出易错点/反模式与纠正建议
# - 给出可延伸阅读或下一步实践方向

# - 难点：隐私合规与可用性之间的平衡（k匿名、差分隐私）

# 【课后思考/练习题】

# 1. 为某敏感字段设计兼顾业务可用的脱敏规则。
# 2. 如何建立测试数据版本化与回滚机制？


# 【课后思考/练习题】

# 1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
# 2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。

## SQL注入测试示例

# 【阅读提示】本篇聚焦：SQL注入测试示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

def test_sql_injection_vulnerability():
    # 1. 准备测试环境
    setup_vulnerability_test_env()

    # 2. 定义SQL注入测试向量
    sql_injection_tests = [
        {"input": "1' OR '1'='1", "description": "经典SQL注入"},
        {"input": "1' DROP TABLE users--", "description": "尝试删除表"},
        {"input": "1' UNION SELECT username, password FROM admin--", "description": "联合查询注入"},
        {"input": "1'; EXEC sp_addlogin 'hacker', 'password'--", "description": "尝试添加用户"}
    ]

    # 3. 执行SQL注入测试
    results = []
    for test in sql_injection_tests:
        response = submit_vulnerable_input(test["input"])
        result = {
            "test": test["description"],
            "vulnerable": is_response_vulnerable(response, test["input"]),
            "details": analyze_response(response)
        }
        results.append(result)

    # 4. 验证测试结果
    vulnerable_tests = [r for r in results if r["vulnerable"]]
    assert len(vulnerable_tests) == 0, f"发现SQL注入漏洞: {[v['test'] for v in vulnerable_tests]}"

    # 5. 验证输入验证日志
    validation_logs = check_input_validation_logs()
    assert len(validation_logs) == len(sql_injection_tests), "未记录所有注入尝试"