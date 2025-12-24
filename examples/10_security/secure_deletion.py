# examples/10_security/secure_deletion.py
# 安全数据删除工具示例

import os
import hashlib
import logging
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecureDeletionTool:
    """安全数据删除工具"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.deletion_methods = {
            'single_pass': self._single_pass_overwrite,
            'three_pass': self._three_pass_overwrite,
            'gutmann': self._gutmann_method,
            'crypto_erase': self._cryptographic_erase
        }

    def secure_delete_file(self, file_path, method='three_pass', verify=True):
        """安全删除文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # 记录删除操作
        self._log_deletion_start(file_path, method)

        # 选择删除方法
        deletion_func = self.deletion_methods.get(method, self._three_pass_overwrite)

        try:
            # 执行安全删除
            deletion_func(file_path)

            # 验证删除（可选）
            if verify:
                self._verify_deletion(file_path)

            # 删除文件系统条目
            os.remove(file_path)

            self._log_deletion_success(file_path)
            return True

        except Exception as e:
            self._log_deletion_failure(file_path, str(e))
            raise

    def secure_delete_directory(self, dir_path, method='three_pass', recursive=True):
        """安全删除目录"""
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        deleted_files = []

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                self.secure_delete_file(file_path, method)
                deleted_files.append(file_path)

            if not recursive:
                break

        # 删除目录
        if recursive:
            os.rmdir(dir_path)

        return deleted_files

    def _single_pass_overwrite(self, file_path):
        """单次覆盖删除"""
        file_size = os.path.getsize(file_path)

        with open(file_path, 'wb') as f:
            # 用随机数据覆盖
            random_data = os.urandom(4096)
            bytes_written = 0

            while bytes_written < file_size:
                chunk_size = min(4096, file_size - bytes_written)
                f.write(random_data[:chunk_size])
                bytes_written += chunk_size

    def _three_pass_overwrite(self, file_path):
        """三遍覆盖删除（DoD 5220.22-M标准）"""
        file_size = os.path.getsize(file_path)

        # 第一遍：全0
        self._overwrite_with_pattern(file_path, b'\x00')

        # 第二遍：全1
        self._overwrite_with_pattern(file_path, b'\xFF')

        # 第三遍：随机数据
        self._random_overwrite(file_path)

    def _gutmann_method(self, file_path):
        """Gutmann方法（35遍覆盖）"""
        patterns = [
            b'\x00', b'\xFF',  # 基础模式
            b'\x55', b'\xAA',  # 5% and 95% duty cycle
            # ... 其他33种模式（简化实现）
        ]

        for pattern in patterns:
            self._overwrite_with_pattern(file_path, pattern)

    def _cryptographic_erase(self, file_path):
        """加密擦除"""
        # 生成随机密钥
        key = os.urandom(32)

        # 用加密数据覆盖
        with open(file_path, 'rb') as f:
            data = f.read()

        # 简单XOR加密（实际应使用AES）
        encrypted_data = bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))

        with open(file_path, 'wb') as f:
            f.write(encrypted_data)

    def _overwrite_with_pattern(self, file_path, pattern):
        """用指定模式覆盖文件"""
        file_size = os.path.getsize(file_path)

        with open(file_path, 'wb') as f:
            bytes_written = 0
            while bytes_written < file_size:
                chunk_size = min(len(pattern), file_size - bytes_written)
                f.write(pattern[:chunk_size])
                bytes_written += chunk_size

    def _random_overwrite(self, file_path):
        """用随机数据覆盖"""
        file_size = os.path.getsize(file_path)

        with open(file_path, 'wb') as f:
            bytes_written = 0
            while bytes_written < file_size:
                chunk = os.urandom(min(4096, file_size - bytes_written))
                f.write(chunk)
                bytes_written += len(chunk)

    def _verify_deletion(self, file_path):
        """验证文件是否已被安全删除"""
        if os.path.exists(file_path):
            # 读取文件内容验证
            with open(file_path, 'rb') as f:
                sample = f.read(1024)
                if len(set(sample)) > 1:  # 如果不是单一模式
                    raise ValueError("File deletion verification failed")

    def _log_deletion_start(self, file_path, method):
        """记录删除开始"""
        self.logger.info(f"Starting secure deletion of {file_path} using method: {method}")

    def _log_deletion_success(self, file_path):
        """记录删除成功"""
        self.logger.info(f"Successfully deleted {file_path}")

    def _log_deletion_failure(self, file_path, error):
        """记录删除失败"""
        self.logger.error(f"Failed to delete {file_path}: {error}")


# 使用示例
if __name__ == "__main__":
    deletion_tool = SecureDeletionTool()

    # 删除单个文件
    # deletion_tool.secure_delete_file("sensitive_data.txt", method="three_pass")

    # 删除目录
    # deletion_tool.secure_delete_directory("temp_data/", method="crypto_erase")