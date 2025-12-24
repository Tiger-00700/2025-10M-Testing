# examples/13_data_gov/metadata_management.py
# 测试数据元数据管理系统示例

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class DataMetadata:
    """数据元数据类"""
    dataset_id: str
    name: str
    description: str
    version: str
    created_at: datetime
    created_by: str
    data_source: str
    data_type: str
    record_count: int
    size_bytes: int
    schema: Dict
    tags: List[str]
    quality_score: float
    retention_policy: str
    access_level: str
    last_accessed: Optional[datetime] = None
    checksum: Optional[str] = None

class MetadataManager:
    """元数据管理器"""

    def __init__(self, storage_path: str = "metadata_store.json"):
        self.storage_path = storage_path
        self.metadata_cache = {}
        self._load_metadata()

    def register_dataset(self, dataset_info: Dict) -> str:
        """注册新数据集"""
        dataset_id = self._generate_dataset_id(dataset_info)

        metadata = DataMetadata(
            dataset_id=dataset_id,
            name=dataset_info.get('name'),
            description=dataset_info.get('description', ''),
            version=dataset_info.get('version', '1.0.0'),
            created_at=datetime.now(),
            created_by=dataset_info.get('created_by'),
            data_source=dataset_info.get('data_source'),
            data_type=dataset_info.get('data_type'),
            record_count=dataset_info.get('record_count', 0),
            size_bytes=dataset_info.get('size_bytes', 0),
            schema=dataset_info.get('schema', {}),
            tags=dataset_info.get('tags', []),
            quality_score=dataset_info.get('quality_score', 0.0),
            retention_policy=dataset_info.get('retention_policy', 'default'),
            access_level=dataset_info.get('access_level', 'internal')
        )

        # 计算校验和
        metadata.checksum = self._calculate_checksum(dataset_info)

        self.metadata_cache[dataset_id] = metadata
        self._save_metadata()

        return dataset_id

    def get_metadata(self, dataset_id: str) -> Optional[DataMetadata]:
        """获取数据集元数据"""
        return self.metadata_cache.get(dataset_id)

    def update_metadata(self, dataset_id: str, updates: Dict) -> bool:
        """更新数据集元数据"""
        if dataset_id not in self.metadata_cache:
            return False

        metadata = self.metadata_cache[dataset_id]

        # 更新允许的字段
        for key, value in updates.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)

        metadata.last_accessed = datetime.now()
        self._save_metadata()
        return True

    def search_datasets(self, query: Dict) -> List[DataMetadata]:
        """搜索数据集"""
        results = []

        for metadata in self.metadata_cache.values():
            match = True

            for key, value in query.items():
                if not hasattr(metadata, key):
                    match = False
                    break

                attr_value = getattr(metadata, key)
                if isinstance(attr_value, list):
                    if value not in attr_value:
                        match = False
                        break
                elif attr_value != value:
                    match = False
                    break

            if match:
                results.append(metadata)

        return results

    def validate_dataset_integrity(self, dataset_id: str, current_checksum: str) -> bool:
        """验证数据集完整性"""
        metadata = self.get_metadata(dataset_id)
        if not metadata:
            return False

        return metadata.checksum == current_checksum

    def get_lineage(self, dataset_id: str) -> Dict:
        """获取数据血缘信息"""
        metadata = self.get_metadata(dataset_id)
        if not metadata:
            return {}

        return {
            'source': metadata.data_source,
            'transformations': [],  # 简化实现
            'dependencies': [],     # 简化实现
            'derived_datasets': []  # 简化实现
        }

    def generate_report(self, report_type: str = "summary") -> Dict:
        """生成元数据报告"""
        if report_type == "summary":
            return {
                'total_datasets': len(self.metadata_cache),
                'total_size_bytes': sum(m.size_bytes for m in self.metadata_cache.values()),
                'average_quality_score': sum(m.quality_score for m in self.metadata_cache.values()) / len(self.metadata_cache) if self.metadata_cache else 0,
                'datasets_by_type': self._count_by_attribute('data_type'),
                'datasets_by_access_level': self._count_by_attribute('access_level')
            }
        elif report_type == "detailed":
            return {
                dataset_id: asdict(metadata)
                for dataset_id, metadata in self.metadata_cache.items()
            }

        return {}

    def _generate_dataset_id(self, dataset_info: Dict) -> str:
        """生成数据集ID"""
        name = dataset_info.get('name', 'unknown')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name}_{timestamp}"

    def _calculate_checksum(self, dataset_info: Dict) -> str:
        """计算数据集校验和"""
        # 简化实现，实际应基于数据内容计算
        data_str = json.dumps(dataset_info, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _count_by_attribute(self, attribute: str) -> Dict:
        """按属性统计数据集数量"""
        counts = {}
        for metadata in self.metadata_cache.values():
            value = getattr(metadata, attribute, 'unknown')
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _load_metadata(self):
        """加载元数据"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.values():
                    # 转换时间字符串
                    item['created_at'] = datetime.fromisoformat(item['created_at'])
                    if item.get('last_accessed'):
                        item['last_accessed'] = datetime.fromisoformat(item['last_accessed'])

                    metadata = DataMetadata(**item)
                    self.metadata_cache[metadata.dataset_id] = metadata
        except FileNotFoundError:
            self.metadata_cache = {}

    def _save_metadata(self):
        """保存元数据"""
        data = {
            dataset_id: asdict(metadata)
            for dataset_id, metadata in self.metadata_cache.items()
        }

        # 转换datetime对象为字符串
        for item in data.values():
            item['created_at'] = item['created_at'].isoformat()
            if item.get('last_accessed'):
                item['last_accessed'] = item['last_accessed'].isoformat()

        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# 使用示例
if __name__ == "__main__":
    manager = MetadataManager()

    # 注册新数据集
    dataset_info = {
        'name': 'customer_test_data',
        'description': 'Customer test dataset for regression testing',
        'created_by': 'test_engineer',
        'data_source': 'production_backup',
        'data_type': 'customer_records',
        'record_count': 10000,
        'size_bytes': 5242880,
        'tags': ['test', 'customer', 'regression'],
        'quality_score': 0.95
    }

    dataset_id = manager.register_dataset(dataset_info)
    print(f"Registered dataset: {dataset_id}")

    # 获取元数据
    metadata = manager.get_metadata(dataset_id)
    print(f"Dataset metadata: {metadata}")

    # 生成报告
    report = manager.generate_report("summary")
    print(f"Summary report: {report}")