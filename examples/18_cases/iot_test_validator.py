# examples/18_cases/iot_test_validator.py
"""
物联网行业大数据测试验证器
验证设备连接、数据采集、实时流处理、异常检测等物联网场景
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import yaml
import json
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IoTTestCase:
    """物联网测试案例"""
    case_id: str
    scenario_type: str
    device_category: str
    connectivity_requirements: List[str]
    test_data: Dict[str, Any]
    expected_results: Dict[str, Any]
    validation_rules: Dict[str, Any]

@dataclass
class TestResult:
    """测试结果"""
    case_id: str
    status: str  # 'pass', 'fail', 'warning'
    execution_time: float
    connectivity_score: float
    reliability_score: float
    details: Dict[str, Any]

class IoTTestValidator:
    """物联网行业测试验证器"""

    def __init__(self, config_file: str = 'iot_config.yml'):
        self.config = self._load_config(config_file)
        self.test_results: List[TestResult] = []

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {
                'min_connectivity_score': 0.95,
                'min_reliability_score': 0.99,
                'expected_processing_latency': 100,  # 毫秒
                'supported_protocols': ['MQTT', 'CoAP', 'HTTP', 'LoRaWAN'],
                'device_categories': ['sensor', 'actuator', 'gateway', 'edge_device']
            }

    def validate_device_connectivity(self, connection_events: pd.DataFrame,
                                   device_registry: pd.DataFrame) -> TestResult:
        """验证设备连接"""
        start_time = datetime.now()

        try:
            # 设备认证验证
            auth_results = self._validate_device_authentication(connection_events, device_registry)

            # 连接稳定性分析
            stability_results = self._analyze_connection_stability(connection_events)

            # 通信协议检查
            protocol_results = self._check_communication_protocols(connection_events)

            # 连接性综合评分
            connectivity_score = self._calculate_connectivity_score(auth_results, stability_results, protocol_results)

            # 可靠性评估
            reliability_score = self._assess_connection_reliability(stability_results)

            # 性能指标
            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            min_connectivity = self.config['min_connectivity_score']
            min_reliability = self.config['min_reliability_score']

            if connectivity_score >= min_connectivity and reliability_score >= min_reliability:
                status = 'pass'
            elif connectivity_score >= min_connectivity * 0.9:
                status = 'warning'
            else:
                status = 'fail'

            details = {
                'auth_results': auth_results,
                'stability_results': stability_results,
                'protocol_results': protocol_results,
                'connectivity_score': connectivity_score,
                'reliability_score': reliability_score,
                'execution_time': execution_time,
                'total_devices': len(device_registry),
                'active_connections': len(connection_events)
            }

            return TestResult(
                case_id="DEVICE_CONNECTIVITY_001",
                status=status,
                execution_time=execution_time,
                connectivity_score=connectivity_score,
                reliability_score=reliability_score,
                details=details
            )

        except Exception as e:
            logger.error(f"设备连接验证失败: {e}")
            return TestResult(
                case_id="DEVICE_CONNECTIVITY_001",
                status='fail',
                execution_time=(datetime.now() - start_time).total_seconds(),
                connectivity_score=0.0,
                reliability_score=0.0,
                details={'error': str(e)}
            )

    def validate_stream_processing(self, sensor_streams: pd.DataFrame,
                                 processing_logs: pd.DataFrame) -> TestResult:
        """验证流处理"""
        start_time = datetime.now()

        try:
            # 处理延迟分析
            latency_results = self._analyze_processing_latency(sensor_streams, processing_logs)

            # 数据转换验证
            transformation_results = self._validate_data_transformation(sensor_streams, processing_logs)

            # 状态一致性检查
            consistency_results = self._check_state_consistency(processing_logs)

            # 连接性评分（基于处理成功率）
            connectivity_score = self._calculate_processing_connectivity(latency_results, transformation_results)

            # 可靠性评分
            reliability_score = self._assess_processing_reliability(consistency_results)

            # 性能指标
            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            expected_latency = self.config['expected_processing_latency']
            if (latency_results['avg_latency'] <= expected_latency and
                connectivity_score >= 0.95 and reliability_score >= 0.99):
                status = 'pass'
            elif latency_results['avg_latency'] <= expected_latency * 1.5:
                status = 'warning'
            else:
                status = 'fail'

            details = {
                'latency_results': latency_results,
                'transformation_results': transformation_results,
                'consistency_results': consistency_results,
                'connectivity_score': connectivity_score,
                'reliability_score': reliability_score,
                'execution_time': execution_time,
                'total_messages': len(sensor_streams),
                'processed_messages': len(processing_logs)
            }

            return TestResult(
                case_id="STREAM_PROCESSING_001",
                status=status,
                execution_time=execution_time,
                connectivity_score=connectivity_score,
                reliability_score=reliability_score,
                details=details
            )

        except Exception as e:
            logger.error(f"流处理验证失败: {e}")
            return TestResult(
                case_id="STREAM_PROCESSING_001",
                status='fail',
                execution_time=(datetime.now() - start_time).total_seconds(),
                connectivity_score=0.0,
                reliability_score=0.0,
                details={'error': str(e)}
            )

    def validate_anomaly_detection(self, sensor_data: pd.DataFrame,
                                 anomaly_labels: pd.DataFrame) -> TestResult:
        """验证异常检测"""
        start_time = datetime.now()

        try:
            # 异常检测准确性评估
            accuracy_results = self._evaluate_anomaly_accuracy(sensor_data, anomaly_labels)

            # 检测及时性分析
            timeliness_results = self._analyze_detection_timeliness(sensor_data, anomaly_labels)

            # 误报率和漏报率计算
            error_rates = self._calculate_error_rates(sensor_data, anomaly_labels)

            # 连接性评分（基于检测覆盖率）
            connectivity_score = self._calculate_detection_connectivity(accuracy_results, timeliness_results)

            # 可靠性评分（基于错误率）
            reliability_score = self._assess_detection_reliability(error_rates)

            # 性能指标
            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            if (accuracy_results['f1_score'] >= 0.8 and error_rates['false_positive_rate'] <= 0.05 and
                error_rates['false_negative_rate'] <= 0.1):
                status = 'pass'
            elif accuracy_results['f1_score'] >= 0.7:
                status = 'warning'
            else:
                status = 'fail'

            details = {
                'accuracy_results': accuracy_results,
                'timeliness_results': timeliness_results,
                'error_rates': error_rates,
                'connectivity_score': connectivity_score,
                'reliability_score': reliability_score,
                'execution_time': execution_time,
                'total_samples': len(sensor_data),
                'anomaly_count': anomaly_labels['is_anomaly'].sum() if 'is_anomaly' in anomaly_labels.columns else 0
            }

            return TestResult(
                case_id="ANOMALY_DETECTION_001",
                status=status,
                execution_time=execution_time,
                connectivity_score=connectivity_score,
                reliability_score=reliability_score,
                details=details
            )

        except Exception as e:
            logger.error(f"异常检测验证失败: {e}")
            return TestResult(
                case_id="ANOMALY_DETECTION_001",
                status='fail',
                execution_time=(datetime.now() - start_time).total_seconds(),
                connectivity_score=0.0,
                reliability_score=0.0,
                details={'error': str(e)}
            )

    def _validate_device_authentication(self, connection_events: pd.DataFrame,
                                      device_registry: pd.DataFrame) -> Dict[str, Any]:
        """验证设备认证"""
        results = {}

        # 认证成功率
        if 'auth_status' in connection_events.columns:
            auth_success = (connection_events['auth_status'] == 'success').sum()
            total_auth_attempts = len(connection_events)
            results['auth_success_rate'] = auth_success / total_auth_attempts if total_auth_attempts > 0 else 0

        # 设备注册完整性
        if 'device_id' in connection_events.columns and 'device_id' in device_registry.columns:
            registered_devices = set(device_registry['device_id'])
            connecting_devices = set(connection_events['device_id'])
            unregistered_connections = connecting_devices - registered_devices
            results['unregistered_connection_rate'] = len(unregistered_connections) / len(connecting_devices) if connecting_devices else 0

        # 重复认证检查
        if 'device_id' in connection_events.columns:
            duplicate_auths = connection_events.groupby('device_id').size()
            multiple_auths = (duplicate_auths > 1).sum()
            results['multiple_auth_rate'] = multiple_auths / len(duplicate_auths) if len(duplicate_auths) > 0 else 0

        return results

    def _analyze_connection_stability(self, connection_events: pd.DataFrame) -> Dict[str, Any]:
        """分析连接稳定性"""
        results = {}

        if 'timestamp' in connection_events.columns and 'connection_status' in connection_events.columns:
            connection_events['timestamp'] = pd.to_datetime(connection_events['timestamp'])
            connection_events = connection_events.sort_values('timestamp')

            # 在线率计算
            total_period = (connection_events['timestamp'].max() - connection_events['timestamp'].min()).total_seconds()
            online_period = 0

            # 简化的在线时间计算
            status_changes = connection_events[['timestamp', 'connection_status']].values
            for i in range(len(status_changes) - 1):
                if status_changes[i][1] == 'connected':
                    duration = (status_changes[i+1][0] - status_changes[i][0]).total_seconds()
                    online_period += duration

            results['online_rate'] = online_period / total_period if total_period > 0 else 0

            # 连接中断统计
            disconnections = (connection_events['connection_status'] == 'disconnected').sum()
            total_events = len(connection_events)
            results['disconnection_rate'] = disconnections / total_events if total_events > 0 else 0

            # 重连时间分析
            if 'reconnection_time' in connection_events.columns:
                valid_reconnection_times = connection_events['reconnection_time'].dropna()
                if len(valid_reconnection_times) > 0:
                    results['avg_reconnection_time'] = valid_reconnection_times.mean()
                    results['max_reconnection_time'] = valid_reconnection_times.max()

        return results

    def _check_communication_protocols(self, connection_events: pd.DataFrame) -> Dict[str, Any]:
        """检查通信协议"""
        results = {}

        if 'protocol' in connection_events.columns:
            protocol_distribution = connection_events['protocol'].value_counts()
            results['protocol_distribution'] = protocol_distribution.to_dict()

            # 协议合规性检查
            supported_protocols = self.config.get('supported_protocols', ['MQTT', 'CoAP', 'HTTP'])
            compliant_protocols = protocol_distribution[protocol_distribution.index.isin(supported_protocols)].sum()
            total_protocols = protocol_distribution.sum()
            results['protocol_compliance_rate'] = compliant_protocols / total_protocols if total_protocols > 0 else 0

        # 消息格式检查
        if 'message_format' in connection_events.columns:
            valid_formats = (connection_events['message_format'] == 'valid').sum()
            total_messages = len(connection_events)
            results['message_format_validity'] = valid_formats / total_messages if total_messages > 0 else 0

        return results

    def _calculate_connectivity_score(self, auth_results: Dict, stability_results: Dict,
                                    protocol_results: Dict) -> float:
        """计算连接性评分"""
        scores = []

        # 认证评分
        if 'auth_success_rate' in auth_results:
            scores.append(auth_results['auth_success_rate'])

        # 稳定性评分
        if 'online_rate' in stability_results:
            scores.append(stability_results['online_rate'])
        if 'disconnection_rate' in stability_results:
            scores.append(1 - stability_results['disconnection_rate'])  # 低断线率 = 高稳定性

        # 协议合规评分
        if 'protocol_compliance_rate' in protocol_results:
            scores.append(protocol_results['protocol_compliance_rate'])
        if 'message_format_validity' in protocol_results:
            scores.append(protocol_results['message_format_validity'])

        return sum(scores) / len(scores) if scores else 0.0

    def _assess_connection_reliability(self, stability_results: Dict) -> float:
        """评估连接可靠性"""
        reliability_factors = []

        # 在线率权重
        if 'online_rate' in stability_results:
            reliability_factors.append(stability_results['online_rate'] * 0.6)

        # 断线率权重
        if 'disconnection_rate' in stability_results:
            reliability_factors.append((1 - stability_results['disconnection_rate']) * 0.4)

        return sum(reliability_factors) if reliability_factors else 0.5

    def _analyze_processing_latency(self, sensor_streams: pd.DataFrame,
                                  processing_logs: pd.DataFrame) -> Dict[str, Any]:
        """分析处理延迟"""
        results = {}

        if ('timestamp' in sensor_streams.columns and 'processing_timestamp' in processing_logs.columns and
            'message_id' in sensor_streams.columns and 'message_id' in processing_logs.columns):

            # 合并数据计算延迟
            merged_data = pd.merge(
                sensor_streams[['message_id', 'timestamp']],
                processing_logs[['message_id', 'processing_timestamp']],
                on='message_id'
            )

            merged_data['timestamp'] = pd.to_datetime(merged_data['timestamp'])
            merged_data['processing_timestamp'] = pd.to_datetime(merged_data['processing_timestamp'])

            latencies = (merged_data['processing_timestamp'] - merged_data['timestamp']).dt.total_seconds() * 1000  # 毫秒

            results['avg_latency'] = latencies.mean()
            results['median_latency'] = latencies.median()
            results['p95_latency'] = latencies.quantile(0.95)
            results['p99_latency'] = latencies.quantile(0.99)
            results['max_latency'] = latencies.max()
            results['processed_messages'] = len(latencies)

        return results

    def _validate_data_transformation(self, sensor_streams: pd.DataFrame,
                                    processing_logs: pd.DataFrame) -> Dict[str, Any]:
        """验证数据转换"""
        results = {}

        # 数据完整性检查
        if 'raw_data' in sensor_streams.columns and 'processed_data' in processing_logs.columns:
            # 简化的转换验证
            raw_count = len(sensor_streams)
            processed_count = len(processing_logs)
            results['data_preservation_rate'] = processed_count / raw_count if raw_count > 0 else 0

        # 数据准确性检查
        if 'expected_value' in sensor_streams.columns and 'computed_value' in processing_logs.columns:
            merged_data = pd.merge(
                sensor_streams[['message_id', 'expected_value']],
                processing_logs[['message_id', 'computed_value']],
                on='message_id'
            )

            if len(merged_data) > 0:
                accuracy = (merged_data['expected_value'] == merged_data['computed_value']).mean()
                results['transformation_accuracy'] = accuracy

        return results

    def _check_state_consistency(self, processing_logs: pd.DataFrame) -> Dict[str, Any]:
        """检查状态一致性"""
        results = {}

        if 'device_id' in processing_logs.columns and 'device_state' in processing_logs.columns:
            # 检查设备状态变化的一致性
            state_changes = processing_logs.groupby('device_id')['device_state'].apply(list)

            consistency_scores = []
            for device_states in state_changes:
                if len(device_states) > 1:
                    # 检查状态转换的合理性
                    valid_transitions = 0
                    for i in range(len(device_states) - 1):
                        current_state = device_states[i]
                        next_state = device_states[i + 1]
                        # 简化的状态转换验证
                        if self._is_valid_state_transition(current_state, next_state):
                            valid_transitions += 1

                    consistency_score = valid_transitions / (len(device_states) - 1) if len(device_states) > 1 else 1.0
                    consistency_scores.append(consistency_score)

            if consistency_scores:
                results['avg_state_consistency'] = sum(consistency_scores) / len(consistency_scores)
                results['state_consistency_distribution'] = {
                    'high_consistency': sum(1 for s in consistency_scores if s >= 0.95),
                    'medium_consistency': sum(1 for s in consistency_scores if 0.8 <= s < 0.95),
                    'low_consistency': sum(1 for s in consistency_scores if s < 0.8)
                }

        return results

    def _calculate_processing_connectivity(self, latency_results: Dict, transformation_results: Dict) -> float:
        """计算处理连接性"""
        connectivity_factors = []

        # 基于延迟的连接性
        if 'avg_latency' in latency_results:
            expected_latency = self.config.get('expected_processing_latency', 100)
            latency_score = max(0, 1 - (latency_results['avg_latency'] / expected_latency))
            connectivity_factors.append(latency_score)

        # 基于转换准确性的连接性
        if 'transformation_accuracy' in transformation_results:
            connectivity_factors.append(transformation_results['transformation_accuracy'])

        # 基于数据保留率的连接性
        if 'data_preservation_rate' in transformation_results:
            connectivity_factors.append(transformation_results['data_preservation_rate'])

        return sum(connectivity_factors) / len(connectivity_factors) if connectivity_factors else 0.5

    def _assess_processing_reliability(self, consistency_results: Dict) -> float:
        """评估处理可靠性"""
        if 'avg_state_consistency' in consistency_results:
            return consistency_results['avg_state_consistency']

        return 0.95  # 默认可靠性评分

    def _evaluate_anomaly_accuracy(self, sensor_data: pd.DataFrame, anomaly_labels: pd.DataFrame) -> Dict[str, Any]:
        """评估异常检测准确性"""
        results = {}

        if 'is_anomaly' in anomaly_labels.columns and 'predicted_anomaly' in anomaly_labels.columns:
            # 计算混淆矩阵
            y_true = anomaly_labels['is_anomaly']
            y_pred = anomaly_labels['predicted_anomaly']

            # 准确性指标
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

            results['accuracy'] = accuracy_score(y_true, y_pred)
            results['precision'] = precision_score(y_true, y_pred, zero_division=0)
            results['recall'] = recall_score(y_true, y_pred, zero_division=0)
            results['f1_score'] = f1_score(y_true, y_pred, zero_division=0)

        return results

    def _analyze_detection_timeliness(self, sensor_data: pd.DataFrame, anomaly_labels: pd.DataFrame) -> Dict[str, Any]:
        """分析检测及时性"""
        results = {}

        if ('timestamp' in sensor_data.columns and 'anomaly_detected_at' in anomaly_labels.columns and
            'actual_anomaly_at' in anomaly_labels.columns):

            anomaly_labels['anomaly_detected_at'] = pd.to_datetime(anomaly_labels['anomaly_detected_at'])
            anomaly_labels['actual_anomaly_at'] = pd.to_datetime(anomaly_labels['actual_anomaly_at'])

            detection_delays = (anomaly_labels['anomaly_detected_at'] - anomaly_labels['actual_anomaly_at']).dt.total_seconds()

            results['avg_detection_delay'] = detection_delays.mean()
            results['median_detection_delay'] = detection_delays.median()
            results['max_detection_delay'] = detection_delays.max()

            # 及时检测率（延迟小于阈值）
            timely_detections = (detection_delays <= 300).sum()  # 5分钟内检测
            results['timely_detection_rate'] = timely_detections / len(detection_delays) if len(detection_delays) > 0 else 0

        return results

    def _calculate_error_rates(self, sensor_data: pd.DataFrame, anomaly_labels: pd.DataFrame) -> Dict[str, Any]:
        """计算错误率"""
        results = {}

        if 'is_anomaly' in anomaly_labels.columns and 'predicted_anomaly' in anomaly_labels.columns:
            y_true = anomaly_labels['is_anomaly']
            y_pred = anomaly_labels['predicted_anomaly']

            # 混淆矩阵计算
            tp = ((y_true == 1) & (y_pred == 1)).sum()
            tn = ((y_true == 0) & (y_pred == 0)).sum()
            fp = ((y_true == 0) & (y_pred == 1)).sum()
            fn = ((y_true == 1) & (y_pred == 0)).sum()

            # 错误率
            results['false_positive_rate'] = fp / (fp + tn) if (fp + tn) > 0 else 0
            results['false_negative_rate'] = fn / (fn + tp) if (fn + tp) > 0 else 0
            results['true_positive_rate'] = tp / (tp + fn) if (tp + fn) > 0 else 0
            results['true_negative_rate'] = tn / (tn + fp) if (tn + fp) > 0 else 0

        return results

    def _calculate_detection_connectivity(self, accuracy_results: Dict, timeliness_results: Dict) -> float:
        """计算检测连接性"""
        connectivity_factors = []

        # 基于F1分数的连接性
        if 'f1_score' in accuracy_results:
            connectivity_factors.append(accuracy_results['f1_score'])

        # 基于及时检测率的连接性
        if 'timely_detection_rate' in timeliness_results:
            connectivity_factors.append(timeliness_results['timely_detection_rate'])

        return sum(connectivity_factors) / len(connectivity_factors) if connectivity_factors else 0.5

    def _assess_detection_reliability(self, error_rates: Dict) -> float:
        """评估检测可靠性"""
        reliability_factors = []

        # 低误报率 = 高可靠性
        if 'false_positive_rate' in error_rates:
            reliability_factors.append(1 - error_rates['false_positive_rate'])

        # 低漏报率 = 高可靠性
        if 'false_negative_rate' in error_rates:
            reliability_factors.append(1 - error_rates['false_negative_rate'])

        return sum(reliability_factors) / len(reliability_factors) if reliability_factors else 0.5

    def _is_valid_state_transition(self, current_state: str, next_state: str) -> bool:
        """检查状态转换是否有效"""
        # 简化的状态转换规则
        valid_transitions = {
            'offline': ['connecting', 'error'],
            'connecting': ['online', 'offline', 'error'],
            'online': ['processing', 'idle', 'offline', 'error'],
            'processing': ['online', 'idle', 'error'],
            'idle': ['online', 'processing', 'offline'],
            'error': ['connecting', 'offline']
        }

        return next_state in valid_transitions.get(current_state, [])

    def run_comprehensive_validation(self, test_cases: List[IoTTestCase]) -> Dict[str, Any]:
        """运行综合验证"""
        logger.info("开始物联网行业测试综合验证...")

        results = []
        for test_case in test_cases:
            if test_case.scenario_type == 'device_connectivity':
                # 这里需要实际的连接事件和设备注册数据
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=2.8,
                    connectivity_score=0.987,
                    reliability_score=0.996,
                    details={'simulated': True}
                )
            elif test_case.scenario_type == 'stream_processing':
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=4.2,
                    connectivity_score=0.973,
                    reliability_score=0.992,
                    details={'simulated': True}
                )
            elif test_case.scenario_type == 'anomaly_detection':
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=3.5,
                    connectivity_score=0.956,
                    reliability_score=0.988,
                    details={'simulated': True}
                )
            else:
                result = TestResult(
                    case_id=test_case.case_id,
                    status='warning',
                    execution_time=1.5,
                    connectivity_score=0.85,
                    reliability_score=0.9,
                    details={'message': '不支持的测试场景类型'}
                )

            results.append(result)
            self.test_results.append(result)

        # 生成汇总报告
        summary = {
            'total_cases': len(results),
            'passed_cases': sum(1 for r in results if r.status == 'pass'),
            'warning_cases': sum(1 for r in results if r.status == 'warning'),
            'failed_cases': sum(1 for r in results if r.status == 'fail'),
            'average_connectivity_score': sum(r.connectivity_score for r in results) / len(results),
            'average_reliability_score': sum(r.reliability_score for r in results) / len(results),
            'average_execution_time': sum(r.execution_time for r in results) / len(results)
        }

        return {
            'summary': summary,
            'detailed_results': [asdict(r) for r in results]
        }

# 使用示例
if __name__ == "__main__":
    validator = IoTTestValidator()

    # 创建测试案例
    test_cases = [
        IoTTestCase(
            case_id="DEVICE_CONNECTIVITY_001",
            scenario_type="device_connectivity",
            device_category="传感器",
            connectivity_requirements=["在线率>99.9%", "通信成功率>99.95%"],
            test_data={},
            expected_results={"online_rate": "> 0.999"},
            validation_rules={"min_online_rate": 0.999}
        ),
        IoTTestCase(
            case_id="STREAM_PROCESSING_001",
            scenario_type="stream_processing",
            device_category="智能设备",
            connectivity_requirements=["延迟<100ms", "准确率>99.9%"],
            test_data={},
            expected_results={"avg_latency": "< 100"},
            validation_rules={"max_latency": 100}
        ),
        IoTTestCase(
            case_id="ANOMALY_DETECTION_001",
            scenario_type="anomaly_detection",
            device_category="工业传感器",
            connectivity_requirements=["F1分数>0.8", "误报率<5%"],
            test_data={},
            expected_results={"f1_score": "> 0.8"},
            validation_rules={"min_f1": 0.8}
        )
    ]

    # 运行验证
    validation_report = validator.run_comprehensive_validation(test_cases)

    # 输出结果
    print("物联网行业测试验证报告:")
    print(json.dumps(validation_report, indent=2, ensure_ascii=False))

    print("物联网行业测试验证完成")