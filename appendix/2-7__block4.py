# 大数据加密与脱敏测试框架
import unittest
import hashlib
import base64
import os
import re
import logging
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding, hashes, hmac
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Crypto_Test_Framework')

class EncryptionTester:
    """加密测试工具类"""
    
    def __init__(self):
        self.backend = default_backend()
    
    def generate_key(self, key_length=32):
        """生成指定长度的随机密钥"""
        return os.urandom(key_length)
    
    def aes_encrypt(self, data, key, iv=None):
        """AES加密"""
        # 如果数据不是bytes类型，转换为bytes
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # 如果没有提供IV，生成新的IV
        if iv is None:
            iv = os.urandom(16)  # AES块大小为16字节
        
        # 创建填充器
        padder = padding.PKCS7(128).padder()  # 128位 = 16字节
        padded_data = padder.update(data) + padder.finalize()
        
        # 创建密码器
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        # 加密数据
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # 返回IV和加密数据（IV需要在解密时使用）
        return iv + encrypted_data
    
    def aes_decrypt(self, encrypted_data, key):
        """AES解密"""
        # 提取IV（前16字节）
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # 创建密码器
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        
        # 解密数据
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 移除填充
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data
    
    def generate_hmac(self, data, key):
        """生成HMAC"""
        # 如果数据不是bytes类型，转换为bytes
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # 创建HMAC对象
        h = hmac.HMAC(key, hashes.SHA256(), backend=self.backend)
        h.update(data)
        
        return h.finalize()
    
    def verify_hmac(self, data, key, signature):
        """验证HMAC"""
        # 如果数据不是bytes类型，转换为bytes
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # 创建HMAC对象
        h = hmac.HMAC(key, hashes.SHA256(), backend=self.backend)
        h.update(data)
        
        try:
            h.verify(signature)
            return True
        except:
            return False

class DataMaskingTester:
    """数据脱敏测试工具类"""
    
    @staticmethod
    def mask_phone_number(phone_number, show_digits=3):
        """掩码手机号（保留前3位和后4位，中间用*代替）"""
        if not phone_number or len(phone_number) < show_digits * 2:
            return phone_number
            
        # 提取数字
        digits = re.sub(r'\\D', '', phone_number)
        if len(digits) < show_digits * 2:
            return phone_number
            
        # 掩码处理
        masked = digits[:show_digits] + '*' * (len(digits) - show_digits * 2) + digits[-show_digits:]
        
        # 还原格式
        result = ''
        digit_index = 0
        for char in phone_number:
            if char.isdigit() and digit_index < len(masked):
                result += masked[digit_index]
                digit_index += 1
            else:
                result += char
        
        return result
    
    @staticmethod
    def mask_id_card(id_card, show_digits=6):
        """掩码身份证号（保留前6位和后4位，中间用*代替）"""
        if not id_card or len(id_card) < show_digits + 4:
            return id_card
            
        # 提取数字
        digits = re.sub(r'\\D', '', id_card)
        if len(digits) < show_digits + 4:
            return id_card
            
        # 掩码处理
        masked = digits[:show_digits] + '*' * (len(digits) - show_digits - 4) + digits[-4:]
        
        # 还原格式
        result = ''
        digit_index = 0
        for char in id_card:
            if char.isdigit() and digit_index < len(masked):
                result += masked[digit_index]
                digit_index += 1
            else:
                result += char
        
        return result
    
    @staticmethod
    def mask_bank_card(bank_card, show_digits=4):
        """掩码银行卡号（保留前4位和后4位，中间用*代替）"""
        if not bank_card or len(bank_card) < show_digits * 2:
            return bank_card
            
        # 提取数字
        digits = re.sub(r'\\D', '', bank_card)
        if len(digits) < show_digits * 2:
            return bank_card
            
        # 掩码处理
        masked = digits[:show_digits] + '*' * (len(digits) - show_digits * 2) + digits[-show_digits:]
        
        # 按组显示（每4位一组）
        grouped = ' '.join([masked[i:i+4] for i in range(0, len(masked), 4)])
        
        return grouped
    
    @staticmethod
    def hash_pii(data):
        """对个人身份信息（PII）进行哈希处理"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def tokenize_data(data, token_map=None):
        """对数据进行标记化处理"""
        if token_map is None:
            token_map = {}
        
        if data in token_map:
            return token_map[data]
        
        # 生成新的令牌
        token = f"TOKEN_{base64.b32encode(os.urandom(5)).decode('utf-8')}"
        token_map[data] = token
        return token

class EncryptionSecurityTest(unittest.TestCase):
    """加密安全测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.encryptor = EncryptionTester()
        self.key = self.encryptor.generate_key()
        self.test_data = [
            "简单文本数据",
            "包含敏感信息的测试数据：13812345678，310101199001011234",
            json.dumps({"name": "张三", "phone": "13987654321", "id_card": "110101198001012345"})
        ]
    
    def test_encryption_decryption_cycle(self):
        """测试加密解密循环"""
        logger.info("开始测试加密解密循环")
        
        for data in self.test_data:
            # 加密
            encrypted = self.encryptor.aes_encrypt(data, self.key)
            
            # 解密
            decrypted = self.encryptor.aes_decrypt(encrypted, self.key)
            
            # 验证解密后的数据与原始数据匹配
            if isinstance(data, str):
                self.assertEqual(data, decrypted.decode('utf-8'))
            else:
                self.assertEqual(data, decrypted)
        
        logger.info("加密解密循环测试通过")
    
    def test_encryption_uniqueness(self):
        """测试相同数据的加密结果唯一性"""
        logger.info("开始测试相同数据的加密结果唯一性")
        
        # 对相同数据进行多次加密
        encrypted1 = self.encryptor.aes_encrypt(self.test_data[0], self.key)
        encrypted2 = self.encryptor.aes_encrypt(self.test_data[0], self.key)
        
        # 验证每次加密的结果不同（由于IV不同）
        self.assertNotEqual(encrypted1, encrypted2)
        
        logger.info("相同数据的加密结果唯一性测试通过")
    
    def test_encryption_sensitivity(self):
        """测试加密的敏感性（即使只有一个比特的变化，加密结果也应显著不同）"""
        logger.info("开始测试加密的敏感性")
        
        # 两个只有一个字符不同的数据
        data1 = "测试数据1"
        data2 = "测试数据2"
        
        # 加密
        encrypted1 = self.encryptor.aes_encrypt(data1, self.key)
        encrypted2 = self.encryptor.aes_encrypt(data2, self.key)
        
        # 计算加密结果的不同位数
        diff_count = sum(1 for a, b in zip(encrypted1, encrypted2) if a != b)
        
        # 验证至少有一半的位不同
        self.assertTrue(diff_count > len(encrypted1) / 2)
        
        logger.info(f"加密的敏感性测试通过 - 不同位数: {diff_count}/{len(encrypted1)}")
    
    def test_hmac_integrity(self):
        """测试HMAC完整性验证"""
        logger.info("开始测试HMAC完整性验证")
        
        hmac_key = self.encryptor.generate_key()
        
        for data in self.test_data:
            # 生成HMAC
            signature = self.encryptor.generate_hmac(data, hmac_key)
            
            # 验证有效签名
            self.assertTrue(self.encryptor.verify_hmac(data, hmac_key, signature))
            
            # 验证无效签名（修改数据）
            if isinstance(data, str):
                tampered_data = data + "修改"
            else:
                tampered_data = data + b"修改"
            self.assertFalse(self.encryptor.verify_hmac(tampered_data, hmac_key, signature))
        
        logger.info("HMAC完整性验证测试通过")

class DataMaskingTest(unittest.TestCase):
    """数据脱敏测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.masker = DataMaskingTester()
    
    def test_phone_number_masking(self):
        """测试手机号掩码"""
        logger.info("开始测试手机号掩码")
        
        test_cases = [
            ("13812345678", "138*****678"),
            ("+86-138-1234-5678", "+86-138-*****678"),
            ("12345", "12345")  # 太短的数字串不处理
        ]
        
        for input_phone, expected_output in test_cases:
            masked = self.masker.mask_phone_number(input_phone)
            self.assertEqual(masked, expected_output)
        
        logger.info("手机号掩码测试通过")
    
    def test_id_card_masking(self):
        """测试身份证号掩码"""
        logger.info("开始测试身份证号掩码")
        
        test_cases = [
            ("310101199001011234", "310101********1234"),
            ("110101198001012345X", "110101********2345X"),
            ("123456", "123456")  # 太短的数字串不处理
        ]
        
        for input_id, expected_output in test_cases:
            masked = self.masker.mask_id_card(input_id)
            self.assertEqual(masked, expected_output)
        
        logger.info("身份证号掩码测试通过")
    
    def test_bank_card_masking(self):
        """测试银行卡号掩码"""
        logger.info("开始测试银行卡号掩码")
        
        test_cases = [
            ("6222021234567890123", "6222 **** **** 0123"),
            ("6222 0212 3456 7890 123", "6222 **** **** 0123"),
            ("1234", "1234")  # 太短的数字串不处理
        ]
        
        for input_card, expected_output in test_cases:
            masked = self.masker.mask_bank_card(input_card)
            self.assertEqual(masked, expected_output)
        
        logger.info("银行卡号掩码测试通过")
    
    def test_pii_hashing(self):
        """测试个人身份信息哈希处理"""
        logger.info("开始测试个人身份信息哈希处理")
        
        # 相同数据的哈希结果应该相同
        data = "敏感个人信息"
        hash1 = self.masker.hash_pii(data)
        hash2 = self.masker.hash_pii(data)
        self.assertEqual(hash1, hash2)
        
        # 不同数据的哈希结果应该不同
        different_data = "不同的敏感信息"
        different_hash = self.masker.hash_pii(different_data)
        self.assertNotEqual(hash1, different_hash)
        
        logger.info("个人身份信息哈希处理测试通过")
    
    def test_data_tokenization(self):
        """测试数据标记化处理"""
        logger.info("开始测试数据标记化处理")
        
        token_map = {}
        
        # 相同数据应得到相同的令牌
        data = "需要标记化的数据"
        token1 = self.masker.tokenize_data(data, token_map)
        token2 = self.masker.tokenize_data(data, token_map)
        self.assertEqual(token1, token2)
        
        # 不同数据应得到不同的令牌
        different_data = "不同的数据"
        different_token = self.masker.tokenize_data(different_data, token_map)
        self.assertNotEqual(token1, different_token)
        
        logger.info("数据标记化处理测试通过")
    
    def test_comprehensive_masking_strategy(self):
        """测试综合数据脱敏策略"""
        logger.info("开始测试综合数据脱敏策略")
        
        # 模拟包含多种敏感信息的数据记录
        sensitive_record = {
            "name": "张三",
            "phone": "13812345678",
            "id_card": "310101199001011234",
            "bank_card": "6222021234567890123",
            "email": "zhangsan@example.com",
            "address": "上海市浦东新区张江高科技园区"
        }
        
        # 应用多种脱敏策略
        masked_record = {
            "name": sensitive_record["name"][0] + "*" * (len(sensitive_record["name"]) - 1),
            "phone": self.masker.mask_phone_number(sensitive_record["phone"]),
            "id_card": self.masker.mask_id_card(sensitive_record["id_card"]),
            "bank_card": self.masker.mask_bank_card(sensitive_record["bank_card"]),
            "email": self.masker.hash_pii(sensitive_record["email"]),
            "address": sensitive_record["address"].split("市")[0] + "市***"
        }
        
        # 验证敏感信息已被适当脱敏
        self.assertNotEqual(sensitive_record["phone"], masked_record["phone"])
        self.assertNotEqual(sensitive_record["id_card"], masked_record["id_card"])
        self.assertNotEqual(sensitive_record["bank_card"], masked_record["bank_card"])
        
        # 验证仍保留了数据的基本结构和部分信息
        self.assertTrue(masked_record["phone"].startswith(sensitive_record["phone"][:3]))
        self.assertTrue(masked_record["id_card"].startswith(sensitive_record["id_card"][:6]))
        
        # 生成脱敏报告
        self._generate_masking_report(sensitive_record, masked_record)
        
        logger.info("综合数据脱敏策略测试通过")
    
    def _generate_masking_report(self, original, masked):
        """生成数据脱敏报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "original_record": original,
            "masked_record": masked,
            "masking_analysis": {}
        }
        
        # 分析每个字段的脱敏程度
        for field in original:
            if field in masked:
                orig_str = str(original[field])
                masked_str = str(masked[field])
                
                # 计算相似度（简单的字符匹配）
                similarity = sum(1 for o, m in zip(orig_str, masked_str) if o == m) / max(len(orig_str), len(masked_str))
                
                report["masking_analysis"][field] = {
                    "original_length": len(orig_str),
                    "masked_length": len(masked_str),
                    "similarity": similarity,
                    "masked_percentage": 1 - similarity
                }
        
        # 保存报告到文件
        with open('data_masking_audit_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info("数据脱敏审计报告已生成: data_masking_audit_report.json")

class KeyManagementTest(unittest.TestCase):
    """密钥管理测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.encryptor = EncryptionTester()
    
    def test_key_generation_adequacy(self):
        """测试密钥生成的充分性"""
        logger.info("开始测试密钥生成的充分性")
        
        # 生成多个密钥并验证它们的唯一性
        keys = set()
        for _ in range(100):
            key = self.encryptor.generate_key()
            self.assertNotIn(key, keys)
            keys.add(key)
        
        # 验证密钥长度
        for key in keys:
            self.assertEqual(len(key), 32)  # 默认生成32字节（256位）的密钥
        
        # 测试不同长度的密钥
        for key_length in [16, 24, 32]:  # AES支持的密钥长度：128位、192位、256位
            key = self.encryptor.generate_key(key_length)
            self.assertEqual(len(key), key_length)
        
        logger.info("密钥生成的充分性测试通过")
    
    def test_key_rotation_scenario(self):
        """测试密钥轮换场景"""
        logger.info("开始测试密钥轮换场景")
        
        # 模拟密钥轮换过程
        data = "需要加密的数据"
        
        # 使用旧密钥加密
        old_key = self.encryptor.generate_key()
        encrypted_data = self.encryptor.aes_encrypt(data, old_key)
        
        # 生成新密钥
        new_key = self.encryptor.generate_key()
        
        # 密钥轮换：解密旧数据并使用新密钥重新加密
        decrypted_data = self.encryptor.aes_decrypt(encrypted_data, old_key).decode('utf-8')
        re_encrypted_data = self.encryptor.aes_encrypt(decrypted_data, new_key)
        
        # 验证使用新密钥可以正确解密
        final_decrypted = self.encryptor.aes_decrypt(re_encrypted_data, new_key).decode('utf-8')
        self.assertEqual(final_decrypted, data)
        
        logger.info("密钥轮换场景测试通过")

# 性能测试类
class EncryptionPerformanceTest:
    """加密性能测试类"""
    
    def __init__(self):
        self.encryptor = EncryptionTester()
        self.key = self.encryptor.generate_key()
    
    def test_encryption_performance(self, data_sizes=[1024, 10240, 102400, 1048576]):
        """测试不同数据量的加密性能"""
        import time
        
        results = []
        
        for size in data_sizes:
            # 生成指定大小的随机数据
            data = os.urandom(size)
            
            # 测量加密时间
            start_time = time.time()
            encrypted = self.encryptor.aes_encrypt(data, self.key)
            encrypt_time = time.time() - start_time
            
            # 测量解密时间
            start_time = time.time()
            decrypted = self.encryptor.aes_decrypt(encrypted, self.key)
            decrypt_time = time.time() - start_time
            
            # 验证解密后的数据与原始数据匹配
            is_correct = (data == decrypted)
            
            # 计算性能指标
            encrypt_speed = size / encrypt_time / 1024 / 1024 if encrypt_time > 0 else 0  # MB/s
            decrypt_speed = size / decrypt_time / 1024 / 1024 if decrypt_time > 0 else 0  # MB/s
            
            result = {
                "data_size_bytes": size,
                "data_size_mb": size / 1024 / 1024,
                "encrypt_time_ms": encrypt_time * 1000,
                "decrypt_time_ms": decrypt_time * 1000,
                "encrypt_speed_mb_per_s": encrypt_speed,
                "decrypt_speed_mb_per_s": decrypt_speed,
                "is_correct": is_correct
            }
            
            results.append(result)
            logger.info(f"数据大小: {size/1024:.2f}KB - 加密时间: {encrypt_time*1000:.2f}ms - 解密时间: {decrypt_time*1000:.2f}ms")
        
        # 生成性能报告
        self._generate_performance_report(results)
        
        return results
    
    def _generate_performance_report(self, results):
        """生成性能测试报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "加密解密性能测试",
            "results": results,
            "summary": {
                "total_test_cases": len(results),
                "passed_tests": sum(1 for r in results if r["is_correct"]),
                "average_encrypt_speed_mb_per_s": sum(r["encrypt_speed_mb_per_s"] for r in results) / len(results),
                "average_decrypt_speed_mb_per_s": sum(r["decrypt_speed_mb_per_s"] for r in results) / len(results)
            }
        }
        
        # 保存报告到文件
        with open('encryption_performance_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info("加密解密性能报告已生成: encryption_performance_report.json")

def run_security_tests():
    """运行所有安全测试"""
    # 运行加密安全测试
    encryption_suite = unittest.TestLoader().loadTestsFromTestCase(EncryptionSecurityTest)
    encryption_result = unittest.TextTestRunner(verbosity=2).run(encryption_suite)
    
    # 运行数据脱敏测试
    masking_suite = unittest.TestLoader().loadTestsFromTestCase(DataMaskingTest)
    masking_result = unittest.TextTestRunner(verbosity=2).run(masking_suite)
    
    # 运行密钥管理测试
    key_management_suite = unittest.TestLoader().loadTestsFromTestCase(KeyManagementTest)
    key_management_result = unittest.TextTestRunner(verbosity=2).run(key_management_suite)
    
    # 运行性能测试
    performance_tester = EncryptionPerformanceTest()
    performance_results = performance_tester.test_encryption_performance()
    
    # 返回测试结果摘要
    return {
        'encryption_tests': {
            'total': encryption_result.testsRun,
            'failures': len(encryption_result.failures),
            'errors': len(encryption_result.errors)
        },
        'masking_tests': {
            'total': masking_result.testsRun,
            'failures': len(masking_result.failures),
            'errors': len(masking_result.errors)
        },
        'key_management_tests': {
            'total': key_management_result.testsRun,
            'failures': len(key_management_result.failures),
            'errors': len(key_management_result.errors)
        },
        'performance_tests': {
            'total': len(performance_results),
            'passed': sum(1 for r in performance_results if r["is_correct"])
        }
    }

if __name__ == "__main__":
    # 运行所有测试
    test_results = run_security_tests()
    
    # 输出测试结果摘要
    print(f"\n安全测试结果摘要:")
    print(f"加密安全测试 - 总测试数: {test_results['encryption_tests']['total']}, 失败: {test_results['encryption_tests']['failures']}, 错误: {test_results['encryption_tests']['errors']}")
    print(f"数据脱敏测试 - 总测试数: {test_results['masking_tests']['total']}, 失败: {test_results['masking_tests']['failures']}, 错误: {test_results['masking_tests']['errors']}")
    print(f"密钥管理测试 - 总测试数: {test_results['key_management_tests']['total']}, 失败: {test_results['key_management_tests']['failures']}, 错误: {test_results['key_management_tests']['errors']}")
    print(f"性能测试 - 总测试数: {test_results['performance_tests']['total']}, 通过: {test_results['performance_tests']['passed']}")
    
    # 判断是否所有测试通过
    all_passed = (
        test_results['encryption_tests']['failures'] == 0 and 
        test_results['encryption_tests']['errors'] == 0 and
        test_results['masking_tests']['failures'] == 0 and
        test_results['masking_tests']['errors'] == 0 and
        test_results['key_management_tests']['failures'] == 0 and
        test_results['key_management_tests']['errors'] == 0 and
        test_results['performance_tests']['total'] == test_results['performance_tests']['passed']
    )
    
    if all_passed:
        print("\n所有安全测试通过!")
    else:
        print("\n安全测试存在失败，请检查问题并修复。")
