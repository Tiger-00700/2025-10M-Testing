
# 【章节重点难点总结】

# - 要点：RBAC/ABAC、KMS、密钥轮换、审计与告警
# - 难点：性能与安全的权衡、跨组件信任链验证

# 【课后思考/练习题】

# 1. 设计一次端到端数据加密（At-Rest/In-Transit）的验证方案。
# 2. 如何验证最低权限原则在数据湖的落地有效？


## API安全测试示例

# 【阅读提示】本篇聚焦：API安全测试示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

import requests
import json
import time

def test_api_authentication(api_url, invalid_tokens):
    """测试API认证机制"""
    results = []

    for token in invalid_tokens:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(api_url, headers=headers)

        # 验证无效令牌被拒绝（应返回401或403）
        if response.status_code not in [401, 403]:
            result = {
                'token': token,
                'status': '失败',
                'reason': f'使用无效令牌访问成功，状态码: {response.status_code}'
            }
        else:
            result = {
                'token': token,
                'status': '通过',
                'status_code': response.status_code
            }

        results.append(result)

    # 检查是否所有测试都通过
    all_passed = all(r['status'] == '通过' for r in results)
    return {
        'overall_result': '通过' if all_passed else '失败',
        'detailed_results': results
    }

def test_api_rate_limiting(api_url, valid_token):
    """测试API速率限制"""
    headers = {'Authorization': f'Bearer {valid_token}'}
    success_count = 0
    blocked_count = 0

    # 快速发送多个请求以触发速率限制
    for i in range(20):
        response = requests.get(api_url, headers=headers)

        if response.status_code == 429:  # Too Many Requests
            blocked_count += 1
        elif response.status_code == 200:
            success_count += 1

        # 短暂延迟
        time.sleep(0.1)

    # 验证是否有请求被阻止
    rate_limiting_working = blocked_count > 0

    return {
        'rate_limiting_working': rate_limiting_working,
        'success_count': success_count,
        'blocked_count': blocked_count,
        'result': '通过' if rate_limiting_working else '失败'
    }

def test_api_injection(api_url, valid_token):
    """测试API注入漏洞"""
    headers = {
        'Authorization': f'Bearer {valid_token}',
        'Content-Type': 'application/json'
    }

    # SQL注入测试向量
    sql_injection_payloads = [
        "' OR '1'='1",
        "1'; DROP TABLE users; --",
        "admin' --"
    ]

    # NoSQL注入测试向量
    nosql_injection_payloads = [
        {"$ne": ""},
        {"$gt": ""},
        {"$where": "1 == 1"}
    ]

    results = []

    # 测试SQL注入
    for payload in sql_injection_payloads:
        data = {'username': payload, 'password': 'test'}
        response = requests.post(f"{api_url}/login", headers=headers, json=data)

        # 检查是否注入成功（例如，不应返回200或包含SQL错误信息）
        is_vulnerable = response.status_code == 200 or "SQL" in response.text

        results.append({
            'type': 'SQL注入',
            'payload': payload,
            'vulnerable': is_vulnerable,
            'status_code': response.status_code
        })

    # 测试NoSQL注入
    for payload in nosql_injection_payloads:
        try:
            data = {'username': payload, 'password': 'test'}
            response = requests.post(f"{api_url}/login", headers=headers, json=data)

            is_vulnerable = response.status_code == 200

            results.append({
                'type': 'NoSQL注入',
                'payload': str(payload),
                'vulnerable': is_vulnerable,
                'status_code': response.status_code
            })
        except Exception as e:
            results.append({
                'type': 'NoSQL注入',
                'payload': str(payload),
                'vulnerable': False,
                'error': str(e)
            })

    # 检查是否有漏洞
    vulnerabilities_found = any(r['vulnerable'] for r in results)

    return {
        'vulnerabilities_found': vulnerabilities_found,
        'detailed_results': results,
        'result': '失败' if vulnerabilities_found else '通过'
    }