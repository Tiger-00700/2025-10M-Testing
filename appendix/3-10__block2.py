import os
import json
import shutil
import logging
import datetime
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestDataMetadata:
    """测试数据元数据类"""
    
    def __init__(self, data_id: str, name: str, description: str, 
                 data_type: str, creator: str, creation_date: Optional[datetime.datetime] = None):
        self.data_id = data_id
        self.name = name
        self.description = description
        self.data_type = data_type
        self.creator = creator
        self.creation_date = creation_date or datetime.datetime.now()
        self.last_modified = datetime.datetime.now()
        self.versions: List[Dict[str, Any]] = []
        self.tags: List[str] = []
        self.access_count = 0
        self.size = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'data_id': self.data_id,
            'name': self.name,
            'description': self.description,
            'data_type': self.data_type,
            'creator': self.creator,
            'creation_date': self.creation_date.isoformat(),
            'last_modified': self.last_modified.isoformat(),
            'versions': self.versions,
            'tags': self.tags,
            'access_count': self.access_count,
            'size': self.size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestDataMetadata':
        """从字典创建实例"""
        instance = cls(
            data_id=data['data_id'],
            name=data['name'],
            description=data['description'],
            data_type=data['data_type'],
            creator=data['creator'],
            creation_date=datetime.datetime.fromisoformat(data['creation_date'])
        )
        instance.last_modified = datetime.datetime.fromisoformat(data['last_modified'])
        instance.versions = data.get('versions', [])
        instance.tags = data.get('tags', [])
        instance.access_count = data.get('access_count', 0)
        instance.size = data.get('size', 0)
        return instance

class AccessControl:
    """访问控制类"""
    
    def __init__(self):
        # 角色定义
        self.roles = {
            'admin': ['read', 'write', 'delete', 'manage_users'],
            'data_manager': ['read', 'write', 'delete'],
            'tester': ['read', 'write'],
            'viewer': ['read']
        }
        # 用户到角色的映射
        self.user_roles: Dict[str, List[str]] = {}
    
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
    
    def check_permission(self, username: str, permission: str) -> bool:
        """检查用户是否有指定权限"""
        if username not in self.user_roles:
            return False
        
        # 检查用户的所有角色
        for role in self.user_roles[username]:
            if permission in self.roles.get(role, []):
                return True
        
        return False

class DataVersionManager:
    """数据版本管理类"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
    
    def create_version(self, data_path: str, metadata: TestDataMetadata) -> Dict[str, Any]:
        """创建数据版本"""
        data_id = metadata.data_id
        version_dir = os.path.join(self.data_dir, 'versions', data_id)
        os.makedirs(version_dir, exist_ok=True)
        
        # 计算新版本号
        version_num = len(metadata.versions) + 1
        version_path = os.path.join(version_dir, f"v{version_num}")
        
        # 复制数据到版本目录
        if os.path.isfile(data_path):
            shutil.copy2(data_path, version_path)
        elif os.path.isdir(data_path):
            shutil.copytree(data_path, version_path, dirs_exist_ok=True)
        
        # 计算数据哈希值
        data_hash = self._calculate_hash(version_path)
        
        # 创建版本记录
        version_info = {
            'version': version_num,
            'timestamp': datetime.datetime.now().isoformat(),
            'hash': data_hash,
            'size': self._get_size(version_path)
        }
        
        # 更新元数据
        metadata.versions.append(version_info)
        metadata.last_modified = datetime.datetime.now()
        
        logger.info(f"为数据 {data_id} 创建了版本 v{version_num}")
        return version_info
    
    def _calculate_hash(self, path: str) -> str:
        """计算文件或目录的哈希值"""
        if os.path.isfile(path):
            return self._calculate_file_hash(path)
        else:
            # 对于目录，计算所有文件哈希的组合
            hashes = []
            for root, _, files in os.walk(path):
                for file in sorted(files):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, path)
                    file_hash = self._calculate_file_hash(file_path)
                    hashes.append(f"{rel_path}:{file_hash}")
            combined = ''.join(hashes).encode()
            return hashlib.sha256(combined).hexdigest()
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算单个文件的哈希值"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _get_size(self, path: str) -> int:
        """获取文件或目录的大小"""
        if os.path.isfile(path):
            return os.path.getsize(path)
        else:
            total_size = 0
            for root, _, files in os.walk(path):
                for file in files:
                    total_size += os.path.getsize(os.path.join(root, file))
            return total_size

class TestDataManager:
    """测试数据管理器核心类"""
    
    def __init__(self, base_dir: str = './tdm_platform'):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data')
        self.metadata_dir = os.path.join(base_dir, 'metadata')
        self.version_manager = DataVersionManager(base_dir)
        self.access_control = AccessControl()
        
        # 初始化目录结构
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        os.makedirs(os.path.join(base_dir, 'versions'), exist_ok=True)
        
        logger.info(f"测试数据管理平台初始化完成，基础目录: {base_dir}")
    
    def add_test_data(self, username: str, data_name: str, description: str, 
                     data_path: str, data_type: str) -> Optional[str]:
        """添加测试数据"""
        # 检查权限
        if not self.access_control.check_permission(username, 'write'):
            logger.error(f"用户 {username} 没有添加数据的权限")
            return None
        
        # 生成数据ID
        data_id = hashlib.md5(f"{data_name}_{username}_{datetime.datetime.now().isoformat()}".encode()).hexdigest()
        
        # 创建元数据
        metadata = TestDataMetadata(
            data_id=data_id,
            name=data_name,
            description=description,
            data_type=data_type,
            creator=username
        )
        
        # 复制数据到存储目录
        data_storage_path = os.path.join(self.data_dir, data_id)
        if os.path.isfile(data_path):
            shutil.copy2(data_path, data_storage_path)
        elif os.path.isdir(data_path):
            shutil.copytree(data_path, data_storage_path)
        
        # 创建第一个版本
        self.version_manager.create_version(data_path, metadata)
        
        # 保存元数据
        self._save_metadata(metadata)
        
        logger.info(f"用户 {username} 添加了测试数据: {data_name} (ID: {data_id})")
        return data_id
    
    def get_test_data(self, username: str, data_id: str) -> Optional[Dict[str, Any]]:
        """获取测试数据"""
        # 检查权限
        if not self.access_control.check_permission(username, 'read'):
            logger.error(f"用户 {username} 没有读取数据的权限")
            return None
        
        # 加载元数据
        metadata = self._load_metadata(data_id)
        if not metadata:
            return None
        
        # 更新访问计数
        metadata.access_count += 1
        metadata.last_modified = datetime.datetime.now()
        self._save_metadata(metadata)
        
        # 获取最新版本的文件路径
        data_path = os.path.join(self.data_dir, data_id)
        
        result = metadata.to_dict()
        result['file_path'] = data_path if os.path.exists(data_path) else None
        
        logger.info(f"用户 {username} 访问了测试数据: {data_id}")
        return result
    
    def update_test_data(self, username: str, data_id: str, new_data_path: str, 
                        description: Optional[str] = None) -> bool:
        """更新测试数据"""
        # 检查权限
        if not self.access_control.check_permission(username, 'write'):
            logger.error(f"用户 {username} 没有更新数据的权限")
            return False
        
        # 加载元数据
        metadata = self._load_metadata(data_id)
        if not metadata:
            return False
        
        # 更新描述
        if description:
            metadata.description = description
        
        # 更新数据文件
        data_storage_path = os.path.join(self.data_dir, data_id)
        if os.path.exists(data_storage_path):
            if os.path.isdir(data_storage_path):
                shutil.rmtree(data_storage_path)
            else:
                os.remove(data_storage_path)
        
        if os.path.isfile(new_data_path):
            shutil.copy2(new_data_path, data_storage_path)
        elif os.path.isdir(new_data_path):
            shutil.copytree(new_data_path, data_storage_path)
        
        # 创建新版本
        self.version_manager.create_version(new_data_path, metadata)
        
        # 保存元数据
        self._save_metadata(metadata)
        
        logger.info(f"用户 {username} 更新了测试数据: {data_id}")
        return True
    
    def delete_test_data(self, username: str, data_id: str) -> bool:
        """删除测试数据"""
        # 检查权限
        if not self.access_control.check_permission(username, 'delete'):
            logger.error(f"用户 {username} 没有删除数据的权限")
            return False
        
        # 检查数据是否存在
        metadata_path = os.path.join(self.metadata_dir, f"{data_id}.json")
        if not os.path.exists(metadata_path):
            logger.error(f"数据不存在: {data_id}")
            return False
        
        # 删除数据文件
        data_path = os.path.join(self.data_dir, data_id)
        if os.path.exists(data_path):
            if os.path.isdir(data_path):
                shutil.rmtree(data_path)
            else:
                os.remove(data_path)
        
        # 删除版本历史
        versions_path = os.path.join(self.base_dir, 'versions', data_id)
        if os.path.exists(versions_path):
            shutil.rmtree(versions_path)
        
        # 删除元数据
        os.remove(metadata_path)
        
        logger.info(f"用户 {username} 删除了测试数据: {data_id}")
        return True
    
    def search_data(self, username: str, query: str = '', 
                   data_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索测试数据"""
        # 检查权限
        if not self.access_control.check_permission(username, 'read'):
            logger.error(f"用户 {username} 没有搜索数据的权限")
            return []
        
        results = []
        
        # 遍历所有元数据文件
        for filename in os.listdir(self.metadata_dir):
            if filename.endswith('.json'):
                data_id = filename[:-5]  # 移除.json后缀
                metadata = self._load_metadata(data_id)
                if metadata:
                    # 应用搜索条件
                    match_query = not query or (query.lower() in metadata.name.lower() or 
                                             query.lower() in metadata.description.lower())
                    match_type = not data_type or metadata.data_type == data_type
                    
                    if match_query and match_type:
                        results.append(metadata.to_dict())
        
        logger.info(f"用户 {username} 执行搜索: 查询='{query}', 类型='{data_type}', 找到 {len(results)} 个结果")
        return results
    
    def _save_metadata(self, metadata: TestDataMetadata) -> None:
        """保存元数据到文件"""
        metadata_path = os.path.join(self.metadata_dir, f"{metadata.data_id}.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _load_metadata(self, data_id: str) -> Optional[TestDataMetadata]:
        """从文件加载元数据"""
        metadata_path = os.path.join(self.metadata_dir, f"{data_id}.json")
        if not os.path.exists(metadata_path):
            logger.error(f"元数据文件不存在: {data_id}")
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return TestDataMetadata.from_dict(data)
        except Exception as e:
            logger.error(f"加载元数据失败: {e}")
            return None

# 使用示例
def main():
    # 创建测试数据管理器实例
    tdm = TestDataManager('./test_tdm_platform')
    
    # 设置用户权限
    tdm.access_control.assign_role('admin_user', 'admin')
    tdm.access_control.assign_role('tester_user', 'tester')
    
    # 创建临时测试数据文件
    test_data_path = 'test_sample.json'
    with open(test_data_path, 'w') as f:
        json.dump({'test_key': 'test_value', 'data': [1, 2, 3, 4, 5]}, f)
    
    try:
        # 添加测试数据
        print("=== 添加测试数据 ===")
        data_id = tdm.add_test_data(
            username='admin_user',
            data_name='示例测试数据',
            description='这是一个测试数据示例',
            data_path=test_data_path,
            data_type='JSON'
        )
        print(f"添加成功，数据ID: {data_id}")
        
        # 搜索数据
        print("\n=== 搜索数据 ===")
        results = tdm.search_data(username='tester_user', query='测试')
        print(f"搜索结果 ({len(results)}):")
        for result in results:
            print(f"- {result['name']}: {result['description']}")
        
        # 获取数据详情
        print(f"\n=== 获取数据详情 ===")
        data_detail = tdm.get_test_data(username='tester_user', data_id=data_id)
        print(f"数据名称: {data_detail['name']}")
        print(f"数据类型: {data_detail['data_type']}")
        print(f"创建者: {data_detail['creator']}")
        print(f"访问次数: {data_detail['access_count']}")
        print(f"文件路径: {data_detail['file_path']}")
        
        # 更新数据
        print("\n=== 更新数据 ===")
        updated_data_path = 'updated_test.json'
        with open(updated_data_path, 'w') as f:
            json.dump({'test_key': 'updated_value', 'data': [1, 2, 3, 4, 5, 6, 7]}, f)
        
        success = tdm.update_test_data(
            username='admin_user',
            data_id=data_id,
            new_data_path=updated_data_path,
            description='这是更新后的测试数据'
        )
        print(f"更新{'成功' if success else '失败'}")
        
        # 再次获取查看更新
        updated_detail = tdm.get_test_data(username='tester_user', data_id=data_id)
        print(f"更新后的描述: {updated_detail['description']}")
        print(f"版本数量: {len(updated_detail['versions'])}")
        
    finally:
        # 清理临时文件
        for file in [test_data_path, updated_data_path]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == "__main__":
    main()
