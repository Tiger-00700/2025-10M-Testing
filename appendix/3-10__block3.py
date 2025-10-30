import os
import json
import logging
import datetime
import hashlib
import base64
import secrets
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from cryptography.hazmat.primitives import hashes, padding, ciphers
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   filename='test_data_security.log')
logger = logging.getLogger(__name__)

class SecurityManager:
    """测试数据安全管理器"""
    
    def __init__(self, config_path: str = 'security_config.json'):
        self.config = self._load_config(config_path)
        self.audit_logger = AuditLogger(self.config.get('audit_log_path', 'security_audit.log'))
        self.crypto_engine = CryptoEngine()
        self.access_control = AccessControl()
        logger.info("测试数据安全管理器初始化完成")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载安全配置"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
        
        # 返回默认配置
        return {
            'encryption_key_path': 'master_key.key',
            'audit_log_path': 'security_audit.log',
            'sensitive_data_patterns': {
                'phone': r'1[3-9]\d{9}',
                'id_card': r'[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]',
                'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            },
            'data_retention_days': 90
        }

class CryptoEngine:
    """加密引擎类"""
    
    def __init__(self, key_path: str = 'master_key.key'):
        self.key_path = key_path
        self.key = self._load_or_generate_key()
        self.fernet = Fernet(self.key)
        logger.info("加密引擎初始化完成")
    
    def _load_or_generate_key(self) -> bytes:
        """加载或生成加密密钥"""
        if os.path.exists(self.key_path):
            try:
                with open(self.key_path, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"加载密钥失败: {e}")
        
        # 生成新密钥
        key = Fernet.generate_key()
        # 安全保存密钥（实际生产环境应使用更安全的密钥管理方案）
        with open(self.key_path, 'wb') as f:
            f.write(key)
        logger.info(f"新密钥已生成并保存到: {self.key_path}")
        return key
    
    def encrypt_data(self, data: str) -> str:
        """加密数据"""
        try:
            encrypted = self.fernet.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"加密数据失败: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """解密数据"""
        try:
            encrypted = base64.b64decode(encrypted_data)
            decrypted = self.fernet.decrypt(encrypted)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"解密数据失败: {e}")
            raise
    
    def hash_data(self, data: str, salt: Optional[str] = None) -> str:
        """对数据进行哈希处理"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        salted_data = (data + salt).encode('utf-8')
        hashed = hashlib.sha256(salted_data).hexdigest()
        return f"{salt}:{hashed}"
    
    def verify_hash(self, data: str, hashed_data: str) -> bool:
        """验证哈希值"""
        try:
            salt, hash_value = hashed_data.split(':', 1)
            salted_data = (data + salt).encode('utf-8')
            new_hash = hashlib.sha256(salted_data).hexdigest()
            return new_hash == hash_value
        except Exception as e:
            logger.error(f"验证哈希失败: {e}")
            return False
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """加密文件"""
        if output_path is None:
            output_path = file_path + '.encrypted'
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted_data = self.fernet.encrypt(data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"文件已加密: {file_path} -> {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"加密文件失败: {e}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """解密文件"""
        if output_path is None:
            output_path = encrypted_file_path.replace('.encrypted', '')
        
        try:
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"文件已解密: {encrypted_file_path} -> {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"解密文件失败: {e}")
            raise

class AccessControl:
    """访问控制类"""
    
    def __init__(self):
        # 角色定义
        self.roles = {
            'admin': {
                'permissions': ['read', 'write', 'delete', 'manage_users', 'encrypt', 'decrypt'],
                'description': '系统管理员，拥有所有权限'
            },
            'security_officer': {
                'permissions': ['read', 'audit', 'encrypt', 'decrypt'],
                'description': '安全官员，负责数据安全和审计'
            },
            'data_manager': {
                'permissions': ['read', 'write', 'delete'],
                'description': '数据管理员，负责数据管理'
            },
            'tester': {
                'permissions': ['read', 'write'],
                'description': '测试人员，可读写测试数据'
            },
            'viewer': {
                'permissions': ['read'],
                'description': '查看人员，仅可读取数据'
            }
        }
        
        # 用户到角色的映射
        self.user_roles: Dict[str, List[str]] = {}
        # 用户信息
        self.users: Dict[str, Dict[str, Any]] = {}
        
        logger.info("访问控制系统初始化完成")
    
    def add_user(self, username: str, password: str, email: str, full_name: str) -> bool:
        """添加用户"""
        if username in self.users:
            logger.error(f"用户已存在: {username}")
            return False
        
        crypto = CryptoEngine()
        hashed_password = crypto.hash_data(password)
        
        self.users[username] = {
            'password': hashed_password,
            'email': email,
            'full_name': full_name,
            'created_at': datetime.datetime.now().isoformat(),
            'last_login': None,
            'status': 'active'
        }
        
        # 默认角色
        self.user_roles[username] = ['viewer']
        
        logger.info(f"已添加用户: {username}")
        return True
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """验证用户身份"""
        if username not in self.users:
            logger.warning(f"尝试登录不存在的用户: {username}")
            return False
        
        user = self.users[username]
        
        # 检查用户状态
        if user['status'] != 'active':
            logger.warning(f"尝试登录非活跃用户: {username}")
            return False
        
        crypto = CryptoEngine()
        if not crypto.verify_hash(password, user['password']):
            logger.warning(f"用户密码验证失败: {username}")
            return False
        
        # 更新最后登录时间
        user['last_login'] = datetime.datetime.now().isoformat()
        logger.info(f"用户登录成功: {username}")
        return True
    
    def assign_role(self, username: str, role: str) -> bool:
        """为用户分配角色"""
        if role not in self.roles:
            logger.error(f"未知角色: {role}")
            return False
        
        if username not in self.user_roles:
            self.user_roles[username] = []
        
        if role not in self.user_roles[username]:
            self.user_roles[username].append(role)
            logger.info(f"已为用户 {username} 分配角色 {role}")
        return True
    
    def remove_role(self, username: str, role: str) -> bool:
        """从用户移除角色"""
        if username not in self.user_roles or role not in self.user_roles[username]:
            logger.error(f"用户 {username} 没有角色 {role}")
            return False
        
        self.user_roles[username].remove(role)
        logger.info(f"已从用户 {username} 移除角色 {role}")
        return True
    
    def check_permission(self, username: str, permission: str, resource: Optional[str] = None) -> bool:
        """检查用户是否有指定权限"""
        if username not in self.user_roles:
            logger.warning(f"检查未知用户的权限: {username}")
            return False
        
        # 检查用户的所有角色
        for role in self.user_roles[username]:
            if permission in self.roles.get(role, {}).get('permissions', []):
                logger.debug(f"用户 {username} 拥有权限: {permission}")
                return True
        
        logger.warning(f"用户 {username} 缺少权限: {permission}")
        return False
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        if username not in self.users:
            return None
        
        user_info = self.users[username].copy()
        # 不返回密码
        user_info.pop('password', None)
        user_info['roles'] = self.user_roles.get(username, [])
        return user_info
    
    def update_user_status(self, username: str, status: str) -> bool:
        """更新用户状态"""
        if username not in self.users:
            logger.error(f"用户不存在: {username}")
            return False
        
        valid_statuses = ['active', 'inactive', 'locked', 'suspended']
        if status not in valid_statuses:
            logger.error(f"无效的用户状态: {status}")
            return False
        
        self.users[username]['status'] = status
        logger.info(f"用户 {username} 状态已更新为: {status}")
        return True

class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, log_path: str = 'security_audit.log'):
        self.log_path = log_path
        self._setup_logger()
        logger.info(f"审计日志系统初始化完成，日志路径: {log_path}")
    
    def _setup_logger(self):
        """设置审计日志记录器"""
        self.logger = logging.getLogger('security_audit')
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_path)
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(user)s - %(action)s - %(resource)s - %(details)s'
            ))
            self.logger.addHandler(handler)
    
    def log_access(self, username: str, action: str, resource: str, details: Optional[Dict[str, Any]] = None):
        """记录访问日志"""
        if details is None:
            details = {}
        
        self.logger.info(
            '',
            extra={
                'user': username,
                'action': action,
                'resource': resource,
                'details': json.dumps(details)
            }
        )
    
    def log_security_event(self, event_type: str, username: Optional[str], 
                          details: Dict[str, Any], severity: str = 'info'):
        """记录安全事件"""
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        
        log_method(
            '',
            extra={
                'user': username or 'system',
                'action': event_type,
                'resource': 'security_event',
                'details': json.dumps(details)
            }
        )
    
    def log_data_access(self, username: str, data_type: str, operation: str, 
                       data_id: str, result: bool = True):
        """记录数据访问"""
        self.log_access(
            username=username,
            action=f'data_{operation}',
            resource=f'{data_type}:{data_id}',
            details={'result': result}
        )
    
    def log_encryption_event(self, username: str, operation: str, 
                            resource_type: str, resource_id: str, 
                            result: bool = True):
        """记录加密相关事件"""
        self.log_access(
            username=username,
            action=f'crypto_{operation}',
            resource=f'{resource_type}:{resource_id}',
            details={'result': result}
        )
    
    def get_audit_logs(self, start_time: Optional[datetime.datetime] = None, 
                      end_time: Optional[datetime.datetime] = None,
                      username: Optional[str] = None,
                      action: Optional[str] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """获取审计日志"""
        logs = []
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        # 解析日志行
                        log_parts = line.split(' - ', 4)
                        if len(log_parts) >= 5:
                            timestamp_str = log_parts[0]
                            level = log_parts[1]
                            user = log_parts[2]
                            action_logged = log_parts[3]
                            resource_details = log_parts[4].split(' - ', 1)
                            
                            if len(resource_details) >= 2:
                                resource = resource_details[0]
                                details_str = resource_details[1].strip()
                                
                                # 解析时间戳
                                timestamp = datetime.datetime.strptime(
                                    timestamp_str, '%Y-%m-%d %H:%M:%S,%f'
                                )
                                
                                # 应用过滤条件
                                if start_time and timestamp < start_time:
                                    continue
                                if end_time and timestamp > end_time:
                                    continue
                                if username and user != username:
                                    continue
                                if action and action_logged != action:
                                    continue
                                
                                try:
                                    details = json.loads(details_str)
                                except:
                                    details = {'raw': details_str}
                                
                                logs.append({
                                    'timestamp': timestamp,
                                    'level': level,
                                    'user': user,
                                    'action': action_logged,
                                    'resource': resource,
                                    'details': details
                                })
                                
                                # 限制结果数量
                                if len(logs) >= limit:
                                    break
                    except Exception as e:
                        logger.error(f"解析审计日志失败: {e}, 行内容: {line}")
        except Exception as e:
            logger.error(f"读取审计日志失败: {e}")
        
        return logs

class DataMaskingEngine:
    """数据脱敏引擎"""
    
    def __init__(self):
        self.masking_rules = {
            'phone': self._mask_phone,
            'id_card': self._mask_id_card,
            'email': self._mask_email,
            'name': self._mask_name,
            'bank_card': self._mask_bank_card
        }
        logger.info("数据脱敏引擎初始化完成")
    
    def _mask_phone(self, data: str) -> str:
        """脱敏手机号"""
        import re
        # 匹配中国大陆手机号
        pattern = r'1[3-9]\d{9}'
        return re.sub(pattern, lambda x: x.group(0)[:3] + '****' + x.group(0)[-4:], data)
    
    def _mask_id_card(self, data: str) -> str:
        """脱敏身份证号"""
        import re
        # 匹配中国大陆身份证号
        pattern = r'([1-9]\d{5})\d{8}(\d{4}[\dXx])'
        return re.sub(pattern, lambda x: x.group(1) + '********' + x.group(2), data)
    
    def _mask_email(self, data: str) -> str:
        """脱敏邮箱"""
        import re
        # 匹配邮箱
        pattern = r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        return re.sub(pattern, lambda x: x.group(1)[:2] + '***@' + x.group(2), data)
    
    def _mask_name(self, data: str) -> str:
        """脱敏姓名"""
        if len(data) <= 1:
            return data
        elif len(data) == 2:
            return data[0] + '*'
        else:
            return data[0] + '*' * (len(data) - 2) + data[-1]
    
    def _mask_bank_card(self, data: str) -> str:
        """脱敏银行卡号"""
        import re
        # 匹配银行卡号（16-19位数字）
        pattern = r'(\d{4})\d{8,11}(\d{4})'
        return re.sub(pattern, lambda x: x.group(1) + '********' + x.group(2), data)
    
    def mask_data(self, data: str, data_type: str) -> str:
        """根据数据类型进行脱敏"""
        if data_type in self.masking_rules:
            return self.masking_rules[data_type](data)
        else:
            logger.warning(f"未知的数据脱敏类型: {data_type}")
            return data
    
    def mask_file(self, file_path: str, output_path: Optional[str] = None, 
                 data_types: Optional[List[str]] = None) -> str:
        """脱敏文件中的敏感数据"""
        if output_path is None:
            output_path = file_path + '.masked'
        
        if data_types is None:
            data_types = list(self.masking_rules.keys())
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 应用所有指定的脱敏规则
            masked_content = content
            for data_type in data_types:
                if data_type in self.masking_rules:
                    masked_content = self.masking_rules[data_type](masked_content)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(masked_content)
            
            logger.info(f"文件已脱敏: {file_path} -> {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"脱敏文件失败: {e}")
            raise
    
    def mask_dataframe(self, df: pd.DataFrame, column_masks: Dict[str, str]) -> pd.DataFrame:
        """脱敏DataFrame中的敏感数据"""
        masked_df = df.copy()
        
        for column, data_type in column_masks.items():
            if column in masked_df.columns and data_type in self.masking_rules:
                masked_df[column] = masked_df[column].astype(str).apply(
                    lambda x: self.masking_rules[data_type](x)
                )
                logger.info(f"已脱敏列: {column}, 类型: {data_type}")
        
        return masked_df

# 使用示例
def main():
    print("=== 测试数据安全管理系统演示 ===")
    
    # 创建安全管理器
    security_manager = SecurityManager()
    access_control = security_manager.access_control
    crypto_engine = security_manager.crypto_engine
    audit_logger = security_manager.audit_logger
    masking_engine = DataMaskingEngine()
    
    # 1. 用户管理演示
    print("\n=== 1. 用户管理 ===")
    # 添加用户
    access_control.add_user('admin', 'Admin123!', 'admin@example.com', '系统管理员')
    access_control.add_user('tester1', 'Tester123!', 'tester1@example.com', '测试人员')
    
    # 分配角色
    access_control.assign_role('admin', 'admin')
    access_control.assign_role('tester1', 'tester')
    
    # 验证用户
    admin_auth = access_control.authenticate_user('admin', 'Admin123!')
    print(f"管理员认证: {'成功' if admin_auth else '失败'}")
    
    # 检查权限
    admin_has_perm = access_control.check_permission('admin', 'encrypt')
    tester_has_perm = access_control.check_permission('tester1', 'encrypt')
    print(f"管理员是否有加密权限: {admin_has_perm}")
    print(f"测试人员是否有加密权限: {tester_has_perm}")
    
    # 2. 数据加密演示
    print("\n=== 2. 数据加密 ===")
    test_data = "这是一段包含敏感信息的测试数据: 电话13800138000，身份证110101199001011234"
    encrypted_data = crypto_engine.encrypt_data(test_data)
    print(f"加密后的数据: {encrypted_data}")
    
    decrypted_data = crypto_engine.decrypt_data(encrypted_data)
    print(f"解密后的数据: {decrypted_data}")
    print(f"解密是否成功: {test_data == decrypted_data}")
    
    # 3. 数据脱敏演示
    print("\n=== 3. 数据脱敏 ===")
    sensitive_data = "联系电话: 13800138000, 邮箱: user123@example.com, 身份证号: 110101199001011234"
    print(f"原始数据: {sensitive_data}")
    
    # 脱敏手机号
    masked_phone = masking_engine.mask_data(sensitive_data, 'phone')
    print(f"脱敏手机号: {masked_phone}")
    
    # 脱敏身份证
    masked_id_card = masking_engine.mask_data(masked_phone, 'id_card')
    print(f"脱敏身份证: {masked_id_card}")
    
    # 脱敏邮箱
    fully_masked = masking_engine.mask_data(masked_id_card, 'email')
    print(f"完全脱敏后: {fully_masked}")
    
    # 4. 审计日志演示
    print("\n=== 4. 审计日志 ===")
    # 记录访问日志
    audit_logger.log_data_access('admin', 'test_data', 'read', 'data_001')
    audit_logger.log_encryption_event('admin', 'encrypt', 'file', 'sensitive_data.txt')
    
    # 记录安全事件
    audit_logger.log_security_event('login_attempt', 'tester1', {
        'ip_address': '192.168.1.100',
        'success': True
    })
    
    # 获取审计日志
    logs = audit_logger.get_audit_logs(limit=5)
    print(f"最近 {len(logs)} 条审计日志:")
    for log in logs:
        print(f"- {log['timestamp']} | {log['user']} | {log['action']} | {log['resource']}")
    
    print("\n=== 演示完成 ===")

if __name__ == "__main__":
    main()
