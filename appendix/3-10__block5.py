import os
import json
import time
import hashlib
import shutil
import datetime
import logging
import threading
from pathlib import Path
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TDLM')

# 生命周期阶段枚举
class LifecycleStage(Enum):
    PLANNING = "planning"
    CREATION = "creation"
    USAGE = "usage"
    MAINTENANCE = "maintenance"
    ARCHIVING = "archiving"
    DESTRUCTION = "destruction"

# 数据分类枚举
class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

# 数据元数据类
@dataclass
class TestDataMetadata:
    data_id: str
    name: str
    description: str
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    stage: LifecycleStage = LifecycleStage.CREATION
    classification: DataClassification = DataClassification.INTERNAL
    size: int = 0
    location: str = ""
    owner: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    expiration_date: Optional[str] = None
    version: str = "1.0.0"
    quality_score: float = 1.0
    access_count: int = 0
    last_accessed: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_id": self.data_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "stage": self.stage.value,
            "classification": self.classification.value,
            "size": self.size,
            "location": self.location,
            "owner": self.owner,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "expiration_date": self.expiration_date,
            "version": self.version,
            "quality_score": self.quality_score,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestDataMetadata':
        return cls(
            data_id=data["data_id"],
            name=data["name"],
            description=data["description"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            stage=LifecycleStage(data["stage"]),
            classification=DataClassification(data["classification"]),
            size=data["size"],
            location=data["location"],
            owner=data["owner"],
            tags=data["tags"],
            dependencies=data["dependencies"],
            expiration_date=data["expiration_date"],
            version=data["version"],
            quality_score=data["quality_score"],
            access_count=data["access_count"],
            last_accessed=data["last_accessed"]
        )

# 测试数据生成器基类
class TestDataGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.generated_data: Dict[str, Any] = {}

    def generate(self) -> Dict[str, Any]:
        """生成测试数据"""
        raise NotImplementedError("Subclasses must implement this method")

    def validate(self) -> bool:
        """验证生成的数据"""
        return True

# CSV数据生成器实现
class CSVTestDataGenerator(TestDataGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.output_path = config.get("output_path", "./")
        self.file_name = config.get("file_name", "test_data.csv")
        self.row_count = config.get("row_count", 1000)
        self.columns = config.get("columns", [])

    def generate(self) -> Dict[str, Any]:
        """生成CSV格式的测试数据"""
        import csv
        import random
        
        full_path = os.path.join(self.output_path, self.file_name)
        os.makedirs(self.output_path, exist_ok=True)
        
        with open(full_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入表头
            header = [col["name"] for col in self.columns]
            writer.writerow(header)
            
            # 写入数据
            for _ in range(self.row_count):
                row = []
                for col in self.columns:
                    col_type = col.get("type", "string")
                    if col_type == "string":
                        value = "Test" + str(random.randint(1, 1000))
                    elif col_type == "integer":
                        min_val = col.get("min", 0)
                        max_val = col.get("max", 1000)
                        value = random.randint(min_val, max_val)
                    elif col_type == "float":
                        min_val = col.get("min", 0.0)
                        max_val = col.get("max", 100.0)
                        value = round(random.uniform(min_val, max_val), 2)
                    elif col_type == "date":
                        # 生成最近一年内的随机日期
                        days = random.randint(0, 365)
                        date = datetime.datetime.now() - datetime.timedelta(days=days)
                        value = date.strftime(col.get("format", "%Y-%m-%d"))
                    else:
                        value = ""
                    row.append(value)
                writer.writerow(row)
        
        file_size = os.path.getsize(full_path)
        self.generated_data = {
            "file_path": full_path,
            "file_size": file_size,
            "row_count": self.row_count,
            "column_count": len(self.columns)
        }
        
        logger.info(f"Generated CSV test data at {full_path}, size: {file_size} bytes")
        return self.generated_data

# JSON数据生成器实现
class JSONTestDataGenerator(TestDataGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.output_path = config.get("output_path", "./")
        self.file_name = config.get("file_name", "test_data.json")
        self.item_count = config.get("item_count", 100)
        self.schema = config.get("schema", {})

    def _generate_value(self, schema_node: Any) -> Any:
        """根据模式生成单个值"""
        import random
        
        if isinstance(schema_node, dict):
            if "type" in schema_node:
                data_type = schema_node["type"]
                if data_type == "string":
                    return schema_node.get("value", "Test") + str(random.randint(1, 1000))
                elif data_type == "integer":
                    return random.randint(schema_node.get("min", 0), schema_node.get("max", 1000))
                elif data_type == "float":
                    return round(random.uniform(schema_node.get("min", 0.0), schema_node.get("max", 100.0)), 2)
                elif data_type == "boolean":
                    return random.choice([True, False])
                elif data_type == "array":
                    item_schema = schema_node.get("items", {})
                    length = schema_node.get("length", 5)
                    return [self._generate_value(item_schema) for _ in range(length)]
                elif data_type == "object":
                    properties = schema_node.get("properties", {})
                    return {key: self._generate_value(value) for key, value in properties.items()}
            else:
                # 递归处理嵌套对象
                return {key: self._generate_value(value) for key, value in schema_node.items()}
        elif isinstance(schema_node, list):
            return [self._generate_value(item) for item in schema_node]
        else:
            return schema_node

    def generate(self) -> Dict[str, Any]:
        """生成JSON格式的测试数据"""
        full_path = os.path.join(self.output_path, self.file_name)
        os.makedirs(self.output_path, exist_ok=True)
        
        data_items = []
        for _ in range(self.item_count):
            data_item = self._generate_value(self.schema)
            data_items.append(data_item)
        
        with open(full_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data_items, jsonfile, indent=2, ensure_ascii=False)
        
        file_size = os.path.getsize(full_path)
        self.generated_data = {
            "file_path": full_path,
            "file_size": file_size,
            "item_count": self.item_count
        }
        
        logger.info(f"Generated JSON test data at {full_path}, size: {file_size} bytes")
        return self.generated_data

# 测试数据目录服务
class TestDataCatalog:
    def __init__(self, catalog_path: str = "./catalog"):
        self.catalog_path = catalog_path
        self.metadata_file = os.path.join(catalog_path, "metadata.json")
        self.metadata_store: Dict[str, TestDataMetadata] = {}
        self._lock = threading.RLock()
        self._initialize()

    def _initialize(self):
        """初始化目录服务"""
        os.makedirs(self.catalog_path, exist_ok=True)
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for data_id, metadata_dict in data.items():
                        self.metadata_store[data_id] = TestDataMetadata.from_dict(metadata_dict)
                logger.info(f"Loaded {len(self.metadata_store)} metadata entries from catalog")
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
        else:
            # 创建空的元数据文件
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def _save_metadata(self):
        """保存元数据到文件"""
        with self._lock:
            data = {}
            for data_id, metadata in self.metadata_store.items():
                data[data_id] = metadata.to_dict()
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def register_data(self, metadata: TestDataMetadata) -> str:
        """注册测试数据"""
        with self._lock:
            # 确保数据ID唯一
            if not metadata.data_id:
                # 生成基于名称和时间的唯一ID
                hash_input = f"{metadata.name}{metadata.created_at}".encode()
                metadata.data_id = hashlib.sha256(hash_input).hexdigest()[:16]
            
            # 更新元数据
            metadata.updated_at = datetime.datetime.now().isoformat()
            self.metadata_store[metadata.data_id] = metadata
            self._save_metadata()
            
            logger.info(f"Registered test data: {metadata.name} (ID: {metadata.data_id})")
            return metadata.data_id

    def get_metadata(self, data_id: str) -> Optional[TestDataMetadata]:
        """获取元数据"""
        return self.metadata_store.get(data_id)

    def update_metadata(self, data_id: str, updates: Dict[str, Any]) -> bool:
        """更新元数据"""
        with self._lock:
            if data_id not in self.metadata_store:
                return False
            
            metadata = self.metadata_store[data_id]
            for key, value in updates.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
            
            metadata.updated_at = datetime.datetime.now().isoformat()
            self._save_metadata()
            
            logger.info(f"Updated metadata for {data_id}")
            return True

    def search_data(self, **criteria) -> List[TestDataMetadata]:
        """搜索测试数据"""
        results = []
        for metadata in self.metadata_store.values():
            match = True
            for key, value in criteria.items():
                if not hasattr(metadata, key):
                    match = False
                    break
                
                attr_value = getattr(metadata, key)
                if isinstance(attr_value, (int, float, str)):
                    if attr_value != value:
                        match = False
                        break
                elif isinstance(attr_value, list):
                    if isinstance(value, list):
                        if not all(v in attr_value for v in value):
                            match = False
                            break
                    elif value not in attr_value:
                        match = False
                        break
                elif isinstance(attr_value, Enum):
                    if attr_value.value != value:
                        match = False
                        break
            
            if match:
                results.append(metadata)
        
        return results

    def delete_metadata(self, data_id: str) -> bool:
        """删除元数据"""
        with self._lock:
            if data_id not in self.metadata_store:
                return False
            
            del self.metadata_store[data_id]
            self._save_metadata()
            
            logger.info(f"Deleted metadata for {data_id}")
            return True

    def list_all_data(self) -> List[TestDataMetadata]:
        """列出所有测试数据"""
        return list(self.metadata_store.values())

# 测试数据生命周期管理器
class TestDataLifecycleManager:
    def __init__(self, data_root: str = "./test_data", catalog: Optional[TestDataCatalog] = None):
        self.data_root = data_root
        self.catalog = catalog or TestDataCatalog()
        self.usage_log_path = os.path.join(data_root, "usage_logs")
        self._lock = threading.RLock()
        
        # 创建必要的目录
        os.makedirs(data_root, exist_ok=True)
        os.makedirs(self.usage_log_path, exist_ok=True)
        
        # 创建阶段特定的目录
        for stage in LifecycleStage:
            stage_dir = os.path.join(data_root, stage.value)
            os.makedirs(stage_dir, exist_ok=True)

    def create_data(self, generator: TestDataGenerator, metadata: TestDataMetadata) -> str:
        """创建测试数据"""
        with self._lock:
            # 生成数据
            generated_data = generator.generate()
            
            # 更新元数据
            if "file_path" in generated_data:
                metadata.location = generated_data["file_path"]
            if "file_size" in generated_data:
                metadata.size = generated_data["file_size"]
            
            metadata.stage = LifecycleStage.CREATION
            
            # 注册到目录
            data_id = self.catalog.register_data(metadata)
            
            return data_id

    def access_data(self, data_id: str) -> Optional[TestDataMetadata]:
        """访问测试数据"""
        metadata = self.catalog.get_metadata(data_id)
        if not metadata:
            logger.warning(f"Data not found: {data_id}")
            return None
        
        # 记录访问
        with self._lock:
            updates = {
                "access_count": metadata.access_count + 1,
                "last_accessed": datetime.datetime.now().isoformat()
            }
            self.catalog.update_metadata(data_id, updates)
            
            # 记录访问日志
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "data_id": data_id,
                "data_name": metadata.name
            }
            log_file = os.path.join(self.usage_log_path, f"access_{datetime.date.today().isoformat()}.jsonl")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            logger.info(f"Accessed data: {metadata.name} (ID: {data_id})")
            
            return self.catalog.get_metadata(data_id)

    def update_data(self, data_id: str, updates: Dict[str, Any]) -> bool:
        """更新测试数据"""
        metadata = self.catalog.get_metadata(data_id)
        if not metadata:
            logger.warning(f"Data not found: {data_id}")
            return False
        
        with self._lock:
            # 更新元数据
            success = self.catalog.update_metadata(data_id, updates)
            
            # 如果阶段变更，可能需要移动文件
            if "stage" in updates and metadata.location:
                old_stage_dir = os.path.join(self.data_root, metadata.stage.value)
                new_stage_dir = os.path.join(self.data_root, updates["stage"].value)
                
                if old_stage_dir != new_stage_dir and os.path.exists(metadata.location):
                    # 确保目标目录存在
                    os.makedirs(new_stage_dir, exist_ok=True)
                    
                    # 移动文件
                    filename = os.path.basename(metadata.location)
                    new_location = os.path.join(new_stage_dir, filename)
                    shutil.move(metadata.location, new_location)
                    
                    # 更新位置信息
                    self.catalog.update_metadata(data_id, {"location": new_location})
            
            return success

    def archive_data(self, data_id: str, archive_reason: str) -> bool:
        """归档测试数据"""
        metadata = self.catalog.get_metadata(data_id)
        if not metadata:
            logger.warning(f"Data not found: {data_id}")
            return False
        
        with self._lock:
            # 记录归档原因
            archive_info = {
                "timestamp": datetime.datetime.now().isoformat(),
                "reason": archive_reason
            }
            
            # 更新阶段
            updates = {
                "stage": LifecycleStage.ARCHIVING,
                "tags": metadata.tags + ["archived"]
            }
            
            # 执行归档
            success = self.update_data(data_id, updates)
            
            # 压缩数据
            if success and metadata.location and os.path.exists(metadata.location):
                import zipfile
                
                # 创建归档文件
                archive_dir = os.path.join(self.data_root, LifecycleStage.ARCHIVING.value)
                archive_filename = f"{data_id}.zip"
                archive_path = os.path.join(archive_dir, archive_filename)
                
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(metadata.location, os.path.basename(metadata.location))
                
                # 删除原始文件
                os.remove(metadata.location)
                
                # 更新位置信息
                self.catalog.update_metadata(data_id, {"location": archive_path})
                
                logger.info(f"Archived data: {metadata.name} (ID: {data_id}) to {archive_path}")
            
            return success

    def destroy_data(self, data_id: str, destroy_reason: str) -> bool:
        """销毁测试数据"""
        metadata = self.catalog.get_metadata(data_id)
        if not metadata:
            logger.warning(f"Data not found: {data_id}")
            return False
        
        # 记录销毁信息
        destroy_info = {
            "timestamp": datetime.datetime.now().isoformat(),
            "data_id": data_id,
            "data_name": metadata.name,
            "reason": destroy_reason
        }
        
        # 保存销毁记录
        destroy_log_file = os.path.join(self.data_root, "destroyed_data_log.jsonl")
        with open(destroy_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(destroy_info) + '\n')
        
        with self._lock:
            # 删除物理文件
            if metadata.location and os.path.exists(metadata.location):
                # 对于敏感数据，使用安全删除
                if metadata.classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
                    # 多次覆盖文件内容
                    file_size = os.path.getsize(metadata.location)
                    with open(metadata.location, "wb") as f:
                        f.write(os.urandom(file_size))
                    
                    # 重命名文件多次
                    for i in range(3):
                        temp_name = f"{metadata.location}.{i}"
                        os.rename(metadata.location, temp_name)
                        metadata.location = temp_name
                
                # 删除文件
                os.remove(metadata.location)
                logger.info(f"Destroyed physical file: {metadata.location}")
            
            # 更新阶段
            self.catalog.update_metadata(data_id, {"stage": LifecycleStage.DESTRUCTION})
            
            # 从目录中移除
            # 注意：实际应用中可能需要保留元数据但标记为已销毁
            # self.catalog.delete_metadata(data_id)
            
            logger.info(f"Destroyed data: {metadata.name} (ID: {data_id})")
            return True

    def check_expired_data(self) -> List[str]:
        """检查过期数据"""
        expired_ids = []
        current_time = datetime.datetime.now().isoformat()
        
        for metadata in self.catalog.list_all_data():
            if (metadata.expiration_date and 
                metadata.expiration_date < current_time and 
                metadata.stage not in [LifecycleStage.ARCHIVING, LifecycleStage.DESTRUCTION]):
                expired_ids.append(metadata.data_id)
        
        return expired_ids

    def generate_report(self, report_type: str = "usage") -> Dict[str, Any]:
        """生成报告"""
        report = {
            "generated_at": datetime.datetime.now().isoformat(),
            "report_type": report_type
        }
        
        if report_type == "usage":
            # 统计各阶段数据数量
            stage_counts = {stage.value: 0 for stage in LifecycleStage}
            classification_counts = {cls.value: 0 for cls in DataClassification}
            total_size = 0
            
            for metadata in self.catalog.list_all_data():
                stage_counts[metadata.stage.value] += 1
                classification_counts[metadata.classification.value] += 1
                total_size += metadata.size
            
            report.update({
                "total_data_count": len(self.catalog.list_all_data()),
                "stage_distribution": stage_counts,
                "classification_distribution": classification_counts,
                "total_size_bytes": total_size,
                "total_size_human": self._human_readable_size(total_size)
            })
        elif report_type == "expiration":
            # 生成过期数据报告
            upcoming_expired = []
            already_expired = []
            current_time = datetime.datetime.now()
            
            for metadata in self.catalog.list_all_data():
                if metadata.expiration_date:
                    exp_date = datetime.datetime.fromisoformat(metadata.expiration_date)
                    days_to_expire = (exp_date - current_time).days
                    
                    if days_to_expire < 0:
                        already_expired.append({
                            "data_id": metadata.data_id,
                            "name": metadata.name,
                            "expired_days": -days_to_expire
                        })
                    elif days_to_expire <= 30:
                        upcoming_expired.append({
                            "data_id": metadata.data_id,
                            "name": metadata.name,
                            "days_to_expire": days_to_expire
                        })
            
            report.update({
                "already_expired_count": len(already_expired),
                "upcoming_expired_count": len(upcoming_expired),
                "already_expired": already_expired,
                "upcoming_expired": upcoming_expired
            })
        
        return report

    def _human_readable_size(self, size_bytes: int) -> str:
        """将字节大小转换为人类可读格式"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

# 生命周期策略管理器
class LifecyclePolicyManager:
    def __init__(self, lifecycle_manager: TestDataLifecycleManager):
        self.lifecycle_manager = lifecycle_manager
        self.policies: List[Dict[str, Any]] = []
        
    def add_policy(self, name: str, condition: Callable[[TestDataMetadata], bool], 
                  action: Callable[[str], bool], description: str = ""):
        """添加生命周期策略"""
        policy = {
            "name": name,
            "condition": condition,
            "action": action,
            "description": description,
            "created_at": datetime.datetime.now().isoformat()
        }
        self.policies.append(policy)
        logger.info(f"Added policy: {name}")

    def evaluate_policies(self):
        """评估所有策略并执行相应操作"""
        results = {
            "evaluated_at": datetime.datetime.now().isoformat(),
            "policy_results": []
        }
        
        for policy in self.policies:
            policy_name = policy["name"]
            condition = policy["condition"]
            action = policy["action"]
            
            applied_count = 0
            
            for metadata in self.lifecycle_manager.catalog.list_all_data():
                if condition(metadata):
                    try:
                        success = action(metadata.data_id)
                        if success:
                            applied_count += 1
                    except Exception as e:
                        logger.error(f"Error applying policy {policy_name} to {metadata.data_id}: {e}")
            
            results["policy_results"].append({
                "policy_name": policy_name,
                "applied_count": applied_count
            })
            
            logger.info(f"Policy {policy_name} applied to {applied_count} data items")
        
        return results

# 使用示例
def main():
    # 创建生命周期管理器
    lifecycle_manager = TestDataLifecycleManager(data_root="./test_data_lifecycle")
    
    # 创建策略管理器
    policy_manager = LifecyclePolicyManager(lifecycle_manager)
    
    # 定义CSV数据生成配置
    csv_config = {
        "output_path": "./test_data_lifecycle/creation",
        "file_name": "user_test_data.csv",
        "row_count": 1000,
        "columns": [
            {"name": "user_id", "type": "integer", "min": 1, "max": 10000},
            {"name": "username", "type": "string"},
            {"name": "age", "type": "integer", "min": 18, "max": 80},
            {"name": "score", "type": "float", "min": 0, "max": 100},
            {"name": "registration_date", "type": "date", "format": "%Y-%m-%d"}
        ]
    }
    
    # 创建CSV生成器
    csv_generator = CSVTestDataGenerator(csv_config)
    
    # 创建元数据
    csv_metadata = TestDataMetadata(
        data_id="",  # 将由系统生成
        name="用户测试数据",
        description="用于用户管理功能测试的CSV格式数据",
        classification=DataClassification.INTERNAL,
        owner="测试团队",
        tags=["CSV", "用户数据", "功能测试"],
        # 设置30天后过期
        expiration_date=(datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
    )
    
    # 生成数据
    csv_data_id = lifecycle_manager.create_data(csv_generator, csv_metadata)
    print(f"Created CSV test data with ID: {csv_data_id}")
    
    # 定义JSON数据生成配置
    json_config = {
        "output_path": "./test_data_lifecycle/creation",
        "file_name": "order_test_data.json",
        "item_count": 100,
        "schema": {
            "order_id": {"type": "string", "value": "ORD-"},
            "order_date": {"type": "date", "format": "%Y-%m-%dT%H:%M:%S"},
            "customer_id": {"type": "integer", "min": 1000, "max": 9999},
            "items": {
                "type": "array",
                "length": {"type": "integer", "min": 1, "max": 5},
                "items": {
                    "product_id": {"type": "string", "value": "PROD-"},
                    "quantity": {"type": "integer", "min": 1, "max": 10},
                    "price": {"type": "float", "min": 10.0, "max": 1000.0}
                }
            },
            "total_amount": {"type": "float", "min": 10.0, "max": 5000.0},
            "status": {"type": "string", "value": "PENDING"}
        }
    }
    
    # 创建JSON生成器
    json_generator = JSONTestDataGenerator(json_config)
    
    # 创建元数据
    json_metadata = TestDataMetadata(
        data_id="",  # 将由系统生成
        name="订单测试数据",
        description="用于订单处理功能测试的JSON格式数据",
        classification=DataClassification.CONFIDENTIAL,
        owner="测试团队",
        tags=["JSON", "订单数据", "功能测试"],
        # 设置60天后过期
        expiration_date=(datetime.datetime.now() + datetime.timedelta(days=60)).isoformat()
    )
    
    # 生成数据
    json_data_id = lifecycle_manager.create_data(json_generator, json_metadata)
    print(f"Created JSON test data with ID: {json_data_id}")
    
    # 访问数据
    lifecycle_manager.access_data(csv_data_id)
    lifecycle_manager.access_data(json_data_id)
    
    # 更新数据阶段
    lifecycle_manager.update_data(csv_data_id, {"stage": LifecycleStage.USAGE})
    
    # 定义自动归档策略
    def archive_condition(metadata: TestDataMetadata) -> bool:
        # 归档30天内未访问的使用阶段数据
        if metadata.stage == LifecycleStage.USAGE and metadata.last_accessed:
            last_access = datetime.datetime.fromisoformat(metadata.last_accessed)
            days_since_access = (datetime.datetime.now() - last_access).days
            return days_since_access >= 30
        return False
    
    def archive_action(data_id: str) -> bool:
        return lifecycle_manager.archive_data(data_id, "超过30天未访问")
    
    policy_manager.add_policy(
        name="自动归档策略",
        condition=archive_condition,
        action=archive_action,
        description="自动归档30天内未访问的测试数据"
    )
    
    # 定义自动销毁策略
    def destroy_condition(metadata: TestDataMetadata) -> bool:
        # 销毁过期且已归档90天的数据
        if (metadata.stage == LifecycleStage.ARCHIVING and 
            metadata.updated_at and 
            metadata.expiration_date and
            metadata.expiration_date < datetime.datetime.now().isoformat()):
            updated = datetime.datetime.fromisoformat(metadata.updated_at)
            days_since_archive = (datetime.datetime.now() - updated).days
            return days_since_archive >= 90
        return False
    
    def destroy_action(data_id: str) -> bool:
        return lifecycle_manager.destroy_data(data_id, "已归档超过90天且已过期")
    
    policy_manager.add_policy(
        name="自动销毁策略",
        condition=destroy_condition,
        action=destroy_action,
        description="自动销毁已归档90天且已过期的测试数据"
    )
    
    # 生成使用报告
    usage_report = lifecycle_manager.generate_report(report_type="usage")
    print("\n使用报告:")
    print(json.dumps(usage_report, indent=2, ensure_ascii=False))
    
    # 生成过期报告
    expiration_report = lifecycle_manager.generate_report(report_type="expiration")
    print("\n过期报告:")
    print(json.dumps(expiration_report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
