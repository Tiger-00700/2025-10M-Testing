# 跨云数据一致性校验工具
# Cross-Cloud Data Consistency Validation Tool

## 概述 (Overview)
本工具用于验证多云环境中数据的强一致性、最终一致性和因果一致性，确保跨云数据同步的准确性和可靠性。

## 核心功能 (Core Features)

### 1. 数据一致性模型 (Data Consistency Models)
```python
# examples/16_tools/data_consistency_validator.py
import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsistencyLevel(Enum):
    """一致性级别枚举"""
    STRONG = "strong"          # 强一致性
    EVENTUAL = "eventual"      # 最终一致性
    CAUSAL = "causal"          # 因果一致性
    SESSION = "session"        # 会话一致性

@dataclass
class DataRecord:
    """数据记录结构"""
    key: str
    value: Any
    version: int
    timestamp: datetime
    source: str  # 云提供商标识
    checksum: str

    def calculate_checksum(self) -> str:
        """计算数据校验和"""
        data_str = f"{self.key}:{json.dumps(self.value, sort_keys=True)}:{self.version}:{self.timestamp.isoformat()}"
        return hashlib.sha256(data_str.encode()).hexdigest()

class DataConsistencyValidator:
    """跨云数据一致性校验器"""

    def __init__(self):
        self.records: Dict[str, Dict[str, DataRecord]] = {}  # key -> {provider -> record}
        self.consistency_checks: Dict[str, List[Dict[str, Any]]] = {}
        self.inconsistencies: List[Dict[str, Any]] = []

    def register_record(self, record: DataRecord):
        """注册数据记录"""
        if record.key not in self.records:
            self.records[record.key] = {}

        self.records[record.key][record.source] = record

        # 验证校验和
        calculated_checksum = record.calculate_checksum()
        if calculated_checksum != record.checksum:
            logger.warning(f"Checksum mismatch for key {record.key} from {record.source}")
            self.inconsistencies.append({
                'type': 'checksum_mismatch',
                'key': record.key,
                'source': record.source,
                'expected': calculated_checksum,
                'actual': record.checksum,
                'timestamp': datetime.now().isoformat()
            })

    def check_strong_consistency(self, key: str) -> Dict[str, Any]:
        """检查强一致性"""
        if key not in self.records:
            return {'consistent': False, 'reason': 'key_not_found'}

        provider_records = self.records[key]
        if len(provider_records) < 2:
            return {'consistent': True, 'reason': 'insufficient_providers'}

        # 检查所有提供商的数据是否完全相同
        base_record = list(provider_records.values())[0]
        for provider, record in provider_records.items():
            if (record.value != base_record.value or
                record.version != base_record.version):
                return {
                    'consistent': False,
                    'reason': 'data_mismatch',
                    'details': {
                        'base_provider': base_record.source,
                        'inconsistent_provider': provider,
                        'base_value': base_record.value,
                        'inconsistent_value': record.value
                    }
                }

        return {'consistent': True}

    def check_eventual_consistency(self, key: str, max_delay: int = 300) -> Dict[str, Any]:
        """检查最终一致性"""
        if key not in self.records:
            return {'consistent': False, 'reason': 'key_not_found'}

        provider_records = self.records[key]
        if len(provider_records) < 2:
            return {'consistent': True, 'reason': 'insufficient_providers'}

        # 检查时间戳差异
        timestamps = [record.timestamp for record in provider_records.values()]
        max_timestamp = max(timestamps)
        min_timestamp = min(timestamps)
        time_diff = (max_timestamp - min_timestamp).total_seconds()

        if time_diff > max_delay:
            return {
                'consistent': False,
                'reason': 'time_delay_exceeded',
                'details': {
                    'max_delay_allowed': max_delay,
                    'actual_delay': time_diff,
                    'timestamps': {provider: ts.isoformat()
                                 for provider, ts in zip(provider_records.keys(), timestamps)}
                }
            }

        # 检查最终值是否一致
        final_values = set(record.value for record in provider_records.values())
        if len(final_values) > 1:
            return {
                'consistent': False,
                'reason': 'final_values_differ',
                'details': {'final_values': list(final_values)}
            }

        return {'consistent': True}

    def check_causal_consistency(self, key: str, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """检查因果一致性"""
        if key not in self.records:
            return {'consistent': False, 'reason': 'key_not_found'}

        # 重建操作序列
        operation_sequence = self._reconstruct_operation_sequence(operations)

        # 验证因果关系
        for i, op in enumerate(operation_sequence):
            if not self._validate_causal_dependency(op, operation_sequence[:i]):
                return {
                    'consistent': False,
                    'reason': 'causal_violation',
                    'details': {
                        'violating_operation': op,
                        'sequence_position': i
                    }
                }

        return {'consistent': True}

    def _reconstruct_operation_sequence(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """重建操作序列"""
        # 按时间戳和因果关系排序
        sorted_ops = sorted(operations, key=lambda x: (x['timestamp'], x.get('causal_deps', [])))
        return sorted_ops

    def _validate_causal_dependency(self, operation: Dict[str, Any], prior_ops: List[Dict[str, Any]]) -> bool:
        """验证因果依赖"""
        causal_deps = operation.get('causal_deps', [])
        for dep in causal_deps:
            if not any(op['id'] == dep for op in prior_ops):
                return False
        return True

    def run_comprehensive_check(self, keys: List[str] = None) -> Dict[str, Any]:
        """运行综合一致性检查"""
        if keys is None:
            keys = list(self.records.keys())

        results = {
            'total_keys': len(keys),
            'strong_consistent': 0,
            'eventual_consistent': 0,
            'causal_consistent': 0,
            'inconsistencies': len(self.inconsistencies),
            'details': {}
        }

        for key in keys:
            key_results = {
                'strong': self.check_strong_consistency(key),
                'eventual': self.check_eventual_consistency(key),
                'causal': self.check_causal_consistency(key, [])  # 需要操作历史
            }

            results['details'][key] = key_results

            if key_results['strong']['consistent']:
                results['strong_consistent'] += 1
            if key_results['eventual']['consistent']:
                results['eventual_consistent'] += 1
            if key_results['causal']['consistent']:
                results['causal_consistent'] += 1

        results['strong_consistency_rate'] = results['strong_consistent'] / results['total_keys']
        results['eventual_consistency_rate'] = results['eventual_consistent'] / results['total_keys']
        results['causal_consistency_rate'] = results['causal_consistent'] / results['total_keys']

        return results

    def generate_consistency_report(self) -> Dict[str, Any]:
        """生成一致性报告"""
        comprehensive_results = self.run_comprehensive_check()

        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_records': sum(len(providers) for providers in self.records.values()),
                'total_keys': len(self.records),
                'providers': list(set(
                    provider for providers in self.records.values()
                    for provider in providers.keys()
                )),
                'inconsistencies_found': len(self.inconsistencies)
            },
            'consistency_metrics': {
                'strong_consistency_rate': comprehensive_results['strong_consistency_rate'],
                'eventual_consistency_rate': comprehensive_results['eventual_consistency_rate'],
                'causal_consistency_rate': comprehensive_results['causal_consistency_rate']
            },
            'inconsistencies': self.inconsistencies,
            'recommendations': self._generate_recommendations(comprehensive_results)
        }

        return report

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """生成修复建议"""
        recommendations = []

        if results['strong_consistency_rate'] < 0.95:
            recommendations.append("强一致性率较低，建议检查数据同步机制")

        if results['eventual_consistency_rate'] < 0.99:
            recommendations.append("最终一致性延迟过高，建议优化同步频率")

        if results['causal_consistency_rate'] < 0.90:
            recommendations.append("因果一致性存在问题，建议检查操作排序逻辑")

        if self.inconsistencies:
            recommendations.append(f"发现{len(self.inconsistencies)}个不一致问题，建议立即调查")

        return recommendations
```

### 2. 一致性测试配置 (Consistency Test Configuration)
```yaml
# 跨云数据一致性测试配置
data_consistency_test:
  test_scenarios:
    - name: strong_consistency_test
      description: "强一致性测试场景"
      keys_to_test: ["user_profile_*", "inventory_*", "order_*"]
      providers: ["aws", "azure", "gcp"]
      parameters:
        max_delay: 5  # 秒
        retry_count: 3
        timeout: 30

    - name: eventual_consistency_test
      description: "最终一致性测试场景"
      keys_to_test: ["analytics_*", "logs_*", "metrics_*"]
      providers: ["aws", "azure", "gcp"]
      parameters:
        max_delay: 300  # 5分钟
        check_interval: 10  # 秒
        max_checks: 30

    - name: causal_consistency_test
      description: "因果一致性测试场景"
      keys_to_test: ["workflow_*", "transaction_*"]
      providers: ["aws", "azure"]
      parameters:
        operation_history_window: 3600  # 1小时
        causal_chain_max_length: 10

  data_patterns:
    - name: user_operations
      key_pattern: "user_{user_id}_*"
      operations:
        - type: create
          causal_deps: []
        - type: update_profile
          causal_deps: ["create"]
        - type: delete
          causal_deps: ["create", "update_profile"]

    - name: inventory_operations
      key_pattern: "inventory_{product_id}_*"
      operations:
        - type: stock_in
          causal_deps: []
        - type: stock_out
          causal_deps: ["stock_in"]
        - type: adjust
          causal_deps: ["stock_in", "stock_out"]

  monitoring:
    metrics:
      - name: consistency_check_duration
        type: histogram
        buckets: [1, 5, 10, 30, 60, 300]
      - name: consistency_violations
        type: counter
        labels: ["consistency_type", "key_pattern"]
      - name: data_sync_latency
        type: histogram
        labels: ["source_provider", "target_provider"]
        buckets: [0.1, 0.5, 1, 5, 10, 30, 60]

  alerting:
    rules:
      - name: strong_consistency_violation
        condition: strong_consistency_rate < 0.95
        severity: critical
        message: "强一致性违规率过高"
      - name: eventual_consistency_delay
        condition: eventual_consistency_delay > 300
        severity: warning
        message: "最终一致性延迟过高"
      - name: causal_consistency_broken
        condition: causal_consistency_violations > 0
        severity: critical
        message: "因果一致性被破坏"
```

### 3. 一致性测试执行器 (Consistency Test Executor)
```python
# 一致性测试执行器
class ConsistencyTestExecutor:
    """一致性测试执行器"""

    def __init__(self, validator: DataConsistencyValidator, config: Dict[str, Any]):
        self.validator = validator
        self.config = config
        self.test_results: Dict[str, Any] = {}

    def execute_test_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """执行测试场景"""
        scenario = self._get_scenario_config(scenario_name)
        if not scenario:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        logger.info(f"Executing consistency test scenario: {scenario_name}")

        results = {
            'scenario': scenario_name,
            'start_time': datetime.now().isoformat(),
            'tests': []
        }

        for test_config in scenario.get('test_scenarios', []):
            test_result = self._execute_single_test(test_config)
            results['tests'].append(test_result)

        results['end_time'] = datetime.now().isoformat()
        results['summary'] = self._generate_scenario_summary(results['tests'])

        self.test_results[scenario_name] = results
        return results

    def _execute_single_test(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个测试"""
        test_name = test_config['name']
        test_type = test_config.get('type', 'strong')

        logger.info(f"Executing test: {test_name} ({test_type})")

        result = {
            'test_name': test_name,
            'test_type': test_type,
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }

        try:
            if test_type == 'strong':
                consistency_result = self.validator.check_strong_consistency(test_config.get('key'))
            elif test_type == 'eventual':
                consistency_result = self.validator.check_eventual_consistency(
                    test_config.get('key'),
                    test_config.get('max_delay', 300)
                )
            elif test_type == 'causal':
                consistency_result = self.validator.check_causal_consistency(
                    test_config.get('key'),
                    test_config.get('operations', [])
                )
            else:
                raise ValueError(f"Unknown test type: {test_type}")

            result.update({
                'status': 'completed',
                'consistency_result': consistency_result,
                'end_time': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Test {test_name} failed: {str(e)}")
            result.update({
                'status': 'failed',
                'error': str(e),
                'end_time': datetime.now().isoformat()
            })

        return result

    def _get_scenario_config(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """获取场景配置"""
        return self.config.get('test_scenarios', {}).get(scenario_name)

    def _generate_scenario_summary(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成场景汇总"""
        total_tests = len(test_results)
        passed_tests = sum(1 for test in test_results if test['status'] == 'completed')
        failed_tests = total_tests - passed_tests

        consistent_tests = sum(
            1 for test in test_results
            if test.get('consistency_result', {}).get('consistent', False)
        )

        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'consistent_tests': consistent_tests,
            'consistency_rate': consistent_tests / total_tests if total_tests > 0 else 0,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0
        }

    def generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'test_results': self.test_results,
            'overall_summary': self._calculate_overall_summary(),
            'recommendations': self._generate_test_recommendations()
        }

        return report

    def _calculate_overall_summary(self) -> Dict[str, Any]:
        """计算总体汇总"""
        all_tests = []
        for scenario_results in self.test_results.values():
            all_tests.extend(scenario_results.get('tests', []))

        total_tests = len(all_tests)
        if total_tests == 0:
            return {'total_tests': 0}

        passed_tests = sum(1 for test in all_tests if test['status'] == 'completed')
        consistent_tests = sum(
            1 for test in all_tests
            if test.get('consistency_result', {}).get('consistent', False)
        )

        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'consistent_tests': consistent_tests,
            'consistency_rate': consistent_tests / total_tests,
            'success_rate': passed_tests / total_tests
        }

    def _generate_test_recommendations(self) -> List[str]:
        """生成测试建议"""
        summary = self._calculate_overall_summary()
        recommendations = []

        if summary.get('success_rate', 0) < 0.95:
            recommendations.append("测试成功率较低，建议检查测试环境和配置")

        if summary.get('consistency_rate', 0) < 0.90:
            recommendations.append("数据一致性率较低，建议优化数据同步机制")

        if summary.get('failed_tests', 0) > 0:
            recommendations.append(f"有{summary['failed_tests']}个测试失败，建议详细分析失败原因")

        return recommendations
```

## 使用示例 (Usage Examples)

### 基本一致性检查
```python
from data_consistency_validator import DataConsistencyValidator, DataRecord, ConsistencyTestExecutor
import yaml

# 初始化校验器
validator = DataConsistencyValidator()

# 注册测试数据
record1 = DataRecord(
    key="user_123_profile",
    value={"name": "John Doe", "email": "john@example.com"},
    version=1,
    timestamp=datetime.now(),
    source="aws",
    checksum=""
)
record1.checksum = record1.calculate_checksum()
validator.register_record(record1)

# 检查一致性
strong_result = validator.check_strong_consistency("user_123_profile")
eventual_result = validator.check_eventual_consistency("user_123_profile")

print("Strong consistency:", strong_result)
print("Eventual consistency:", eventual_result)

# 生成一致性报告
report = validator.generate_consistency_report()
print("Consistency report:", json.dumps(report, indent=2, default=str))
```

### 自动化测试执行
```python
# 加载测试配置
with open('data_consistency_test.yml', 'r') as f:
    config = yaml.safe_load(f)

# 创建测试执行器
executor = ConsistencyTestExecutor(validator, config)

# 执行测试场景
results = executor.execute_test_scenario('strong_consistency_test')
print("Test results:", json.dumps(results, indent=2, default=str))

# 生成完整报告
report = executor.generate_test_report()
print("Full test report:", json.dumps(report, indent=2, default=str))
```

## 最佳实践 (Best Practices)

1. **定期一致性检查**: 建立自动化的一致性监控，避免问题积累
2. **分层一致性策略**: 根据数据重要性选择不同的一致性级别
3. **冲突解决机制**: 建立明确的数据冲突解决策略和流程
4. **性能监控**: 监控一致性检查的性能影响，避免影响生产系统
5. **审计日志**: 详细记录所有一致性检查和修复操作
6. **渐进式部署**: 先在非关键数据上验证，再扩展到关键业务数据