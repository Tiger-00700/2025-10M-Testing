
# 【章节重点难点总结】

# - 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准
# - 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡

# 【课后思考/练习题】

# 1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
# 2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。

## 网络安全配置测试示例

# 【阅读提示】本篇聚焦：网络安全配置测试示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

import socket
import subprocess
import re

def test_network_segmentation(source_ip, target_ip, ports_to_test):
    """测试网络分段，验证未授权访问被阻止"""
    results = {}

    for port in ports_to_test:
        try:
            # 尝试连接到目标端口
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((target_ip, port))
            sock.close()

            # 0表示连接成功，非0表示连接被阻止
            if result == 0:
                status = "失败: 未授权端口可访问"
                passed = False
            else:
                status = "通过: 未授权端口被正确阻止"
                passed = True

            results[port] = {
                'status': status,
                'passed': passed,
                'error_code': result
            }
        except Exception as e:
            results[port] = {
                'status': f"错误: {str(e)}",
                'passed': False
            }

    # 验证是否所有测试都通过
    all_passed = all(result['passed'] for result in results.values())
    return {
        'overall_result': '通过' if all_passed else '失败',
        'detailed_results': results
    }

def test_firewall_rules():
    """测试防火墙规则配置"""
    # 在Linux系统上获取防火墙规则
    # 在Windows系统上可能需要使用netsh命令
    try:
        # 示例：使用iptables获取规则
        result = subprocess.run(['iptables', '-L', '-n'],
                              capture_output=True, text=True, check=True)

        # 分析防火墙规则
        rules = result.stdout

        # 检查是否有危险的默认规则（如允许所有流量）
        if 'ACCEPT     all  --  0.0.0.0/0            0.0.0.0/0' in rules:
            print("警告: 发现过于宽松的防火墙规则")
            return False

        # 检查是否有必要的规则
        required_rules = ['--dport 22', '--dport 443', '--dport 8080']  # 示例
        for rule in required_rules:
            if rule not in rules:
                print(f"警告: 缺少必要的防火墙规则: {rule}")
                return False

        print("防火墙规则测试通过")
        return True
    except Exception as e:
        print(f"防火墙规则测试失败: {e}")
        return False