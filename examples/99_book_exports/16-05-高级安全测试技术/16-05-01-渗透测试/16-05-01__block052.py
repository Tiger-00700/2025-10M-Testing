> 【章节重点难点总结】

- 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准
- 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡

> 【课后思考/练习题】

1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。

## 简单的渗透测试脚本示例（仅用于合法授权测试）

> 【阅读提示】本篇聚焦：简单的渗透测试脚本示例（仅用于合法授权测试）。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

import requests
import socket
import threading
import time

def port_scan(target, port_range=(1, 1024)):
    """简单端口扫描"""
    open_ports = []

    def scan_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((target, port))
        if result == 0:
            open_ports.append(port)
        sock.close()

    # 多线程扫描
    threads = []
    for port in range(port_range[0], port_range[1] + 1):
        thread = threading.Thread(target=scan_port, args=(port,))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    return open_ports

def brute_force_login(url, username_list, password_list):
    """简单的暴力破解测试（仅用于合法授权测试）"""
    results = []

    for username in username_list:
        for password in password_list:
            data = {'username': username, 'password': password}
            try:
                response = requests.post(url, data=data, timeout=5)

                # 检查是否登录成功（根据应用特定响应判断）
                if "欢迎" in response.text or response.status_code == 302:
                    results.append({
                        'username': username,
                        'password': password,
                        'status': '成功',
                        'status_code': response.status_code
                    })
                    return results  # 找到一个就返回

                # 避免触发速率限制
                time.sleep(0.5)
            except Exception as e:
                results.append({
                    'username': username,
                    'password': password,
                    'status': '错误',
                    'error': str(e)
                })

    return results

def check_sensitive_files(target_url):
    """检查常见敏感文件是否可访问"""
    sensitive_files = [
        '/.git/config',
        '/.env',
        '/config.ini',
        '/backup.zip',
        '/database.sql',
        '/admin/login.php',
        '/wp-admin/',
        '/api/swagger.json'
    ]

    results = []

    for file_path in sensitive_files:
        url = target_url.rstrip('/') + file_path
        try:
            response = requests.get(url, timeout=5, allow_redirects=False)

            # 检查文件是否可访问
            if response.status_code == 200:
                results.append({
                    'path': file_path,
                    'status': '可访问',
                    'status_code': response.status_code,
                    'size': len(response.content)
                })
            elif response.status_code < 400:
                results.append({
                    'path': file_path,
                    'status': '重定向',
                    'status_code': response.status_code
                })
        except Exception as e:
            results.append({
                'path': file_path,
                'status': '错误',
                'error': str(e)
            })

    return results
