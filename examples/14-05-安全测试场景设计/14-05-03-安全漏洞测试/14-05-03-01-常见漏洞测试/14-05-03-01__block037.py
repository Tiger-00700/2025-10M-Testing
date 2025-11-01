# SQL注入测试示例
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
