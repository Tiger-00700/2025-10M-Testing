> 【章节重点难点总结】

- 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准
- 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡

> 【课后思考/练习题】

1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。

## 加密实现安全测试示例

> 【阅读提示】本篇聚焦：加密实现安全测试示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

import ssl
import hashlib
import cryptography.hazmat.primitives.ciphers as ciphers
import cryptography.hazmat.primitives.hashes as hashes

def test_tls_configuration(server_address, port):
    # 测试TLS配置
    context = ssl.create_default_context()
    # 仅允许强加密套件
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    context.set_ciphers('HIGH:!aNULL:!MD5:!3DES')

    try:
        with socket.create_connection((server_address, port)) as sock:
            with context.wrap_socket(sock, server_hostname=server_address) as ssock:
                # 获取TLS版本和加密套件
                tls_version = ssock.version()
                cipher = ssock.cipher()

                # 验证TLS版本至少为1.2
                assert tls_version in ['TLSv1.2', 'TLSv1.3'], f"不支持的TLS版本: {tls_version}"

                # 验证加密套件强度
                assert cipher[0] not in ['DES-CBC3-SHA', 'RC4-MD5'], f"弱加密套件: {cipher[0]}"

                print(f"TLS版本: {tls_version}")
                print(f"加密套件: {cipher[0]}")
                return True
    except ssl.SSLError as e:
        print(f"TLS错误: {e}")
        return False

def test_encryption_algorithm(encrypted_data, encryption_method):
    # 验证加密算法强度
    if encryption_method == 'AES':
        # 检查AES密钥长度
        # 实际测试中应检查密钥管理系统中的密钥配置
        key_length = 256  # 假设从配置中获取
        assert key_length >= 256, f"AES密钥长度不足: {key_length}位"
    elif encryption_method == 'RSA':
        # 检查RSA密钥长度
        key_length = 2048  # 假设从配置中获取
        assert key_length >= 2048, f"RSA密钥长度不足: {key_length}位"

    print(f"{encryption_method}加密算法测试通过")
    return True
