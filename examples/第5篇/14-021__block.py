# 数据加密测试示例
def test_data_encryption():
    # 1. 准备测试数据
    sensitive_data = {"ssn": "123-45-6789", "credit_card": "4111111111111111"}

    # 2. 测试传输加密
    transport_results = test_transport_encryption(sensitive_data)
    assert transport_results["encrypted"], "传输加密失败"
    assert transport_results["protocol"] == "TLSv1.3", "使用了不安全的加密协议"
    assert transport_results["cipher_strength"] >= 256, "加密强度不足"

    # 3. 测试存储加密
    encrypted_record = store_encrypted_data(sensitive_data)
    storage_results = test_storage_encryption(encrypted_record)
    assert storage_results["encrypted"], "存储加密失败"
    assert storage_results["algorithm"] in ["AES-256-GCM", "AES-256-CBC"], "使用了不安全的加密算法"

    # 4. 测试密钥管理
    key_management_results = test_key_management()
    assert key_management_results["key_rotation"], "密钥轮换机制未启用"
    assert key_management_results["key_storage_secure"], "密钥存储不安全"

    # 5. 测试解密功能
    decrypted_data = retrieve_and_decrypt_data(encrypted_record)
    assert compare_data(sensitive_data, decrypted_data), "解密后数据不一致"
