# 数据脱敏策略演示

这个模块演示了常见的数据脱敏技术，用于保护敏感信息。

```python
import re
import hashlib
from cryptography.fernet import Fernet
import pandas as pd

class DataMasking:
    """数据脱敏工具类"""

    def __init__(self):
        # 生成加密密钥（实际使用中应该从安全存储获取）
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def mask_phone_number(self, phone):
        """
        手机号脱敏：保留前3后4位
        """
        if not phone:
            return phone
        phone_str = str(phone)
        if len(phone_str) >= 7:
            return phone_str[:3] + '*' * (len(phone_str) - 7) + phone_str[-4:]
        return phone_str

    def mask_email(self, email):
        """
        邮箱脱敏：保留@前2位和域名
        """
        if not email or '@' not in email:
            return email
        username, domain = email.split('@', 1)
        if len(username) > 2:
            masked_username = username[:2] + '*' * (len(username) - 2)
        else:
            masked_username = username
        return f"{masked_username}@{domain}"

    def mask_id_card(self, id_card):
        """
        身份证号脱敏：保留前6后4位
        """
        if not id_card:
            return id_card
        id_str = str(id_card)
        if len(id_str) >= 10:
            return id_str[:6] + '*' * (len(id_str) - 10) + id_str[-4:]
        return id_str

    def hash_sensitive_data(self, data):
        """
        敏感数据哈希：使用SHA256
        """
        if not data:
            return data
        return hashlib.sha256(str(data).encode()).hexdigest()

    def encrypt_data(self, data):
        """
        数据加密
        """
        if not data:
            return data
        return self.cipher.encrypt(str(data).encode()).decode()

    def decrypt_data(self, encrypted_data):
        """
        数据解密
        """
        if not encrypted_data:
            return encrypted_data
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except:
            return encrypted_data

    def apply_masking_policy(self, df, policy_config):
        """
        应用脱敏策略到DataFrame
        policy_config示例:
        {
            'phone': 'mask',
            'email': 'mask',
            'id_card': 'mask',
            'password': 'hash',
            'credit_card': 'encrypt'
        }
        """
        masked_df = df.copy()

        for column, method in policy_config.items():
            if column not in masked_df.columns:
                continue

            if method == 'mask':
                if 'phone' in column.lower():
                    masked_df[column] = masked_df[column].apply(self.mask_phone_number)
                elif 'email' in column.lower():
                    masked_df[column] = masked_df[column].apply(self.mask_email)
                elif 'id' in column.lower() or 'card' in column.lower():
                    masked_df[column] = masked_df[column].apply(self.mask_id_card)
            elif method == 'hash':
                masked_df[column] = masked_df[column].apply(self.hash_sensitive_data)
            elif method == 'encrypt':
                masked_df[column] = masked_df[column].apply(self.encrypt_data)

        return masked_df

# 使用示例
if __name__ == "__main__":
    masking = DataMasking()

    # 测试单个字段脱敏
    print("手机号脱敏:", masking.mask_phone_number("13800138000"))
    print("邮箱脱敏:", masking.mask_email("user@example.com"))
    print("身份证脱敏:", masking.mask_id_card("110101199001011234"))

    # 测试DataFrame脱敏
    sample_data = pd.DataFrame({
        'name': ['张三', '李四', '王五'],
        'phone': ['13800138000', '13900139000', '13700137000'],
        'email': ['zhangsan@example.com', 'lisi@example.com', 'wangwu@example.com'],
        'id_card': ['110101199001011234', '120102199002022345', '130103199003033456'],
        'password': ['secret123', 'password456', 'qwerty789']
    })

    policy = {
        'phone': 'mask',
        'email': 'mask',
        'id_card': 'mask',
        'password': 'hash'
    }

    masked_data = masking.apply_masking_policy(sample_data, policy)
    print("\n原始数据:")
    print(sample_data)
    print("\n脱敏后数据:")
    print(masked_data)
```