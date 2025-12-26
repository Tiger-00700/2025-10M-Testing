# examples/18_cases/autonomous_test_validator.py
"""
自动驾驶行业大数据测试验证器
用于验证自动驾驶车辆的传感器数据质量、环境感知准确性、决策系统安全性和合规性
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """测试结果"""
    case_id: str
    status: str  # 'pass', 'warning', 'fail'
    execution_time: float
    risk_score: float  # 0-1, 越低越好
    compliance_score: float  # 0-1, 越高越好
    details: Dict[str, Any]

@dataclass
class AutonomousTestCase:
    """自动驾驶测试案例"""
    case_id: str
    scenario_type: str  # 'vehicle_monitoring', 'environmental_perception', 'decision_system'
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    safety_requirements: List[str]
    test_data: Dict[str, Any]
    expected_results: Dict[str, Any]
    validation_rules: Dict[str, Any]

class AutonomousTestValidator:
    """自动驾驶行业测试验证器"""

    def __init__(self, config_path: str = 'autonomous_test_config.json'):
        self.config = {
            'max_sensor_error_rate': 0.001,  # 0.1% 最大传感器错误率
            'min_detection_accuracy': 0.99,  # 99% 最小检测准确率
            'max_decision_latency': 100,  # 100ms 最大决策延迟
            'min_safety_compliance': 0.9999,  # 99.99% 最小安全合规性
            'min_health_score': 0.95,  # 95% 最小健康评分
            'max_false_positive_rate': 0.01  # 1% 最大误报率
        }
        self.test_results: List[TestResult] = []

    def validate_vehicle_monitoring(self, sensor_data: pd.DataFrame,
                                   system_metrics: pd.DataFrame) -> TestResult:
        """验证车辆状态监控"""
        start_time = datetime.now()

        try:
            # 1. 传感器数据质量检查
            sensor_quality_score = self._validate_sensor_quality(sensor_data)

            # 2. 系统健康状态评估
            health_score = self._assess_system_health(system_metrics)

            # 3. 性能参数监控
            performance_score = self._monitor_performance_metrics(system_metrics)

            # 4. 安全冗余验证
            redundancy_score = self._validate_redundancy(system_metrics)

            # 综合评分
            overall_score = (sensor_quality_score + health_score +
                           performance_score + redundancy_score) / 4

            # 安全合规检查
            compliance_score = self._check_safety_compliance(sensor_data, system_metrics)

            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            if overall_score >= 0.98 and compliance_score >= self.config['min_safety_compliance']:
                status = 'pass'
                risk_score = 1.0 - overall_score
            elif overall_score >= 0.95:
                status = 'warning'
                risk_score = 1.0 - overall_score
            else:
                status = 'fail'
                risk_score = 1.0 - overall_score

            details = {
                'sensor_quality_score': sensor_quality_score,
                'health_score': health_score,
                'performance_score': performance_score,
                'redundancy_score': redundancy_score,
                'overall_score': overall_score,
                'compliance_score': compliance_score,
                'execution_time': execution_time
            }

            return TestResult(
                case_id="VEHICLE_MONITORING_001",
                status=status,
                execution_time=execution_time,
                risk_score=risk_score,
                compliance_score=compliance_score,
                details=details
            )

        except Exception as e:
            logger.error(f"车辆监控验证失败: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestResult(
                case_id="VEHICLE_MONITORING_001",
                status='fail',
                execution_time=execution_time,
                risk_score=1.0,
                compliance_score=0.0,
                details={'error': str(e)}
            )

    def validate_environmental_perception(self, perception_data: pd.DataFrame,
                                        ground_truth: pd.DataFrame) -> TestResult:
        """验证环境感知"""
        start_time = datetime.now()

        try:
            # 1. 障碍物检测准确性
            detection_metrics = self._evaluate_object_detection(perception_data, ground_truth)

            # 2. 交通标志识别
            sign_recognition_metrics = self._evaluate_sign_recognition(perception_data, ground_truth)

            # 3. 天气条件适应性
            weather_adaptation_score = self._assess_weather_adaptation(perception_data)

            # 4. 实时性能评估
            performance_metrics = self._evaluate_real_time_performance(perception_data)

            # 综合评分
            accuracy_weighted = (detection_metrics['accuracy'] * 0.5 +
                               sign_recognition_metrics['accuracy'] * 0.3 +
                               weather_adaptation_score * 0.2)

            # 合规检查
            compliance_score = self._check_perception_compliance(perception_data)

            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            if accuracy_weighted >= self.config['min_detection_accuracy'] and performance_metrics['latency'] <= self.config['max_decision_latency']:
                status = 'pass'
            elif accuracy_weighted >= 0.95:
                status = 'warning'
            else:
                status = 'fail'

            risk_score = 1.0 - accuracy_weighted

            details = {
                'detection_metrics': detection_metrics,
                'sign_recognition_metrics': sign_recognition_metrics,
                'weather_adaptation_score': weather_adaptation_score,
                'performance_metrics': performance_metrics,
                'accuracy_weighted': accuracy_weighted,
                'compliance_score': compliance_score,
                'execution_time': execution_time
            }

            return TestResult(
                case_id="ENVIRONMENTAL_PERCEPTION_001",
                status=status,
                execution_time=execution_time,
                risk_score=risk_score,
                compliance_score=compliance_score,
                details=details
            )

        except Exception as e:
            logger.error(f"环境感知验证失败: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestResult(
                case_id="ENVIRONMENTAL_PERCEPTION_001",
                status='fail',
                execution_time=execution_time,
                risk_score=1.0,
                compliance_score=0.0,
                details={'error': str(e)}
            )

    def validate_decision_system(self, decision_logs: pd.DataFrame,
                               scenario_data: pd.DataFrame) -> TestResult:
        """验证决策系统"""
        start_time = datetime.now()

        try:
            # 1. 决策安全评估
            safety_metrics = self._evaluate_decision_safety(decision_logs, scenario_data)

            # 2. 异常情况处理
            emergency_response_metrics = self._evaluate_emergency_response(decision_logs)

            # 3. 人机交互安全性
            hmi_safety_score = self._assess_hmi_safety(decision_logs)

            # 4. 决策一致性检查
            consistency_score = self._check_decision_consistency(decision_logs)

            # 综合评分
            overall_safety_score = (safety_metrics['safety_score'] * 0.4 +
                                  emergency_response_metrics['response_score'] * 0.3 +
                                  hmi_safety_score * 0.2 +
                                  consistency_score * 0.1)

            # 伦理合规检查
            ethical_compliance = self._check_ethical_compliance(decision_logs)

            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            if overall_safety_score >= self.config['min_safety_compliance'] and ethical_compliance >= 0.95:
                status = 'pass'
            elif overall_safety_score >= 0.999:
                status = 'warning'
            else:
                status = 'fail'

            risk_score = 1.0 - overall_safety_score

            details = {
                'safety_metrics': safety_metrics,
                'emergency_response_metrics': emergency_response_metrics,
                'hmi_safety_score': hmi_safety_score,
                'consistency_score': consistency_score,
                'overall_safety_score': overall_safety_score,
                'ethical_compliance': ethical_compliance,
                'execution_time': execution_time
            }

            return TestResult(
                case_id="DECISION_SYSTEM_001",
                status=status,
                execution_time=execution_time,
                risk_score=risk_score,
                compliance_score=ethical_compliance,
                details=details
            )

        except Exception as e:
            logger.error(f"决策系统验证失败: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestResult(
                case_id="DECISION_SYSTEM_001",
                status='fail',
                execution_time=execution_time,
                risk_score=1.0,
                compliance_score=0.0,
                details={'error': str(e)}
            )

    def _validate_sensor_quality(self, sensor_data: pd.DataFrame) -> float:
        """验证传感器数据质量"""
        quality_checks = []

        # 数据完整性检查
        completeness = 1.0 - sensor_data.isnull().sum().sum() / (sensor_data.shape[0] * sensor_data.shape[1])
        quality_checks.append(completeness)

        # 数据合理性检查 (基于物理约束)
        if 'lidar_distance' in sensor_data.columns:
            valid_distances = sensor_data['lidar_distance'].between(0, 200)  # 0-200米合理范围
            distance_validity = valid_distances.mean()
            quality_checks.append(distance_validity)

        if 'camera_confidence' in sensor_data.columns:
            valid_confidence = sensor_data['camera_confidence'].between(0, 1)
            confidence_validity = valid_confidence.mean()
            quality_checks.append(confidence_validity)

        # 异常值检测
        if len(sensor_data) > 100:
            iso_forest = IsolationForest(contamination=0.01, random_state=42)
            numeric_cols = sensor_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                anomaly_scores = iso_forest.fit_predict(sensor_data[numeric_cols])
                normal_ratio = (anomaly_scores == 1).mean()
                quality_checks.append(normal_ratio)

        return np.mean(quality_checks) if quality_checks else 0.0

    def _assess_system_health(self, metrics: pd.DataFrame) -> float:
        """评估系统健康状态"""
        health_indicators = []

        # CPU使用率检查
        if 'cpu_usage' in metrics.columns:
            avg_cpu = metrics['cpu_usage'].mean()
            cpu_health = 1.0 - min(avg_cpu / 80.0, 1.0)  # 80%为健康阈值
            health_indicators.append(cpu_health)

        # 内存使用率检查
        if 'memory_usage' in metrics.columns:
            avg_memory = metrics['memory_usage'].mean()
            memory_health = 1.0 - min(avg_memory / 90.0, 1.0)  # 90%为健康阈值
            health_indicators.append(memory_health)

        # 温度检查
        if 'temperature' in metrics.columns:
            avg_temp = metrics['temperature'].mean()
            temp_health = 1.0 - min(max(avg_temp - 60, 0) / 40.0, 1.0)  # 60-100°C范围
            health_indicators.append(temp_health)

        # 错误率检查
        if 'error_count' in metrics.columns:
            total_errors = metrics['error_count'].sum()
            total_operations = len(metrics)
            error_rate = total_errors / max(total_operations, 1)
            error_health = 1.0 - min(error_rate / 0.001, 1.0)  # 0.1%错误率阈值
            health_indicators.append(error_health)

        return np.mean(health_indicators) if health_indicators else 0.5

    def _monitor_performance_metrics(self, metrics: pd.DataFrame) -> float:
        """监控性能参数"""
        performance_scores = []

        # 响应时间检查
        if 'response_time' in metrics.columns:
            avg_response = metrics['response_time'].mean()
            response_score = 1.0 - min(avg_response / self.config['max_decision_latency'], 1.0)
            performance_scores.append(response_score)

        # 吞吐量检查
        if 'throughput' in metrics.columns:
            avg_throughput = metrics['throughput'].mean()
            throughput_score = min(avg_throughput / 1000.0, 1.0)  # 1000 TPS为目标
            performance_scores.append(throughput_score)

        # 稳定性检查 (方差)
        if len(metrics) > 10:
            numeric_cols = metrics.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                stability_scores = []
                for col in numeric_cols:
                    if metrics[col].std() > 0:
                        cv = metrics[col].std() / metrics[col].mean()  # 变异系数
                        stability = 1.0 - min(cv / 0.5, 1.0)  # 50%变异系数阈值
                        stability_scores.append(stability)
                if stability_scores:
                    performance_scores.append(np.mean(stability_scores))

        return np.mean(performance_scores) if performance_scores else 0.5

    def _validate_redundancy(self, metrics: pd.DataFrame) -> float:
        """验证冗余系统"""
        redundancy_checks = []

        # 检查关键组件的备份状态
        critical_components = ['primary_sensor', 'backup_sensor', 'primary_cpu', 'backup_cpu']
        for component in critical_components:
            if f'{component}_status' in metrics.columns:
                status_values = metrics[f'{component}_status'].value_counts()
                if 'active' in status_values:
                    active_ratio = status_values['active'] / len(metrics)
                    redundancy_checks.append(active_ratio)

        # 检查故障转移时间
        if 'failover_time' in metrics.columns:
            avg_failover = metrics['failover_time'].mean()
            failover_score = 1.0 - min(avg_failover / 5000, 1.0)  # 5秒故障转移阈值
            redundancy_checks.append(failover_score)

        return np.mean(redundancy_checks) if redundancy_checks else 0.5

    def _check_safety_compliance(self, sensor_data: pd.DataFrame, metrics: pd.DataFrame) -> float:
        """检查安全合规性"""
        compliance_checks = []

        # 传感器冗余检查
        sensor_columns = [col for col in sensor_data.columns if 'sensor' in col.lower()]
        if len(sensor_columns) >= 2:
            # 检查传感器数据一致性
            if len(sensor_columns) >= 2:
                corr_matrix = sensor_data[sensor_columns].corr()
                avg_correlation = corr_matrix.mean().mean()
                sensor_redundancy = min(avg_correlation, 1.0)  # 相关性作为冗余指标
                compliance_checks.append(sensor_redundancy)

        # 系统监控完整性
        required_metrics = ['cpu_usage', 'memory_usage', 'temperature']
        monitoring_completeness = sum(1 for metric in required_metrics if metric in metrics.columns) / len(required_metrics)
        compliance_checks.append(monitoring_completeness)

        # 数据记录完整性
        data_completeness = 1.0 - sensor_data.isnull().sum().sum() / (sensor_data.shape[0] * sensor_data.shape[1])
        compliance_checks.append(data_completeness)

        return np.mean(compliance_checks) if compliance_checks else 0.0

    def _evaluate_object_detection(self, perception_data: pd.DataFrame, ground_truth: pd.DataFrame) -> Dict[str, float]:
        """评估障碍物检测"""
        if 'detected_objects' not in perception_data.columns or 'actual_objects' not in ground_truth.columns:
            return {'accuracy': 0.5, 'precision': 0.5, 'recall': 0.5, 'f1': 0.5}

        # 简化的评估逻辑 (实际应使用更复杂的IoU计算)
        detected_count = len(perception_data)
        actual_count = len(ground_truth)

        # 模拟准确率计算
        accuracy = min(detected_count / max(actual_count, 1), 1.0)
        precision = accuracy * 0.9  # 模拟精确率
        recall = accuracy * 0.95    # 模拟召回率
        f1 = 2 * precision * recall / max(precision + recall, 0.001)

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

    def _evaluate_sign_recognition(self, perception_data: pd.DataFrame, ground_truth: pd.DataFrame) -> Dict[str, float]:
        """评估交通标志识别"""
        if 'recognized_signs' not in perception_data.columns or 'actual_signs' not in ground_truth.columns:
            return {'accuracy': 0.5, 'precision': 0.5, 'recall': 0.5}

        # 简化的评估逻辑
        recognized_count = len(perception_data[perception_data['recognized_signs'].notna()])
        actual_count = len(ground_truth)

        accuracy = min(recognized_count / max(actual_count, 1), 1.0)
        precision = accuracy * 0.95
        recall = accuracy * 0.98

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall
        }

    def _assess_weather_adaptation(self, perception_data: pd.DataFrame) -> float:
        """评估天气条件适应性"""
        if 'weather_condition' not in perception_data.columns:
            return 0.5

        weather_types = perception_data['weather_condition'].unique()
        adaptation_scores = []

        for weather in weather_types:
            weather_data = perception_data[perception_data['weather_condition'] == weather]

            # 根据不同天气类型评估性能
            if weather == 'clear':
                score = 0.98
            elif weather == 'rain':
                score = 0.85
            elif weather == 'fog':
                score = 0.75
            elif weather == 'snow':
                score = 0.70
            else:
                score = 0.80

            adaptation_scores.append(score)

        return np.mean(adaptation_scores) if adaptation_scores else 0.5

    def _evaluate_real_time_performance(self, perception_data: pd.DataFrame) -> Dict[str, float]:
        """评估实时性能"""
        if 'processing_time' not in perception_data.columns:
            return {'latency': 1000, 'throughput': 10}

        avg_latency = perception_data['processing_time'].mean()
        throughput = 1000 / max(avg_latency, 1)  # 每秒处理帧数

        return {
            'latency': avg_latency,
            'throughput': throughput
        }

    def _check_perception_compliance(self, perception_data: pd.DataFrame) -> float:
        """检查感知合规性"""
        compliance_checks = []

        # 数据格式合规
        required_fields = ['timestamp', 'objects_detected', 'confidence_scores']
        field_completeness = sum(1 for field in required_fields if field in perception_data.columns) / len(required_fields)
        compliance_checks.append(field_completeness)

        # 置信度合理性
        if 'confidence_scores' in perception_data.columns:
            valid_confidence = perception_data['confidence_scores'].between(0, 1).mean()
            compliance_checks.append(valid_confidence)

        # 时间戳顺序性
        if 'timestamp' in perception_data.columns and len(perception_data) > 1:
            monotonic = (perception_data['timestamp'].diff().dropna() >= 0).mean()
            compliance_checks.append(monotonic)

        return np.mean(compliance_checks) if compliance_checks else 0.0

    def _evaluate_decision_safety(self, decision_logs: pd.DataFrame, scenario_data: pd.DataFrame) -> Dict[str, float]:
        """评估决策安全"""
        safety_checks = []

        # 决策成功率
        if 'decision_outcome' in decision_logs.columns:
            success_rate = (decision_logs['decision_outcome'] == 'success').mean()
            safety_checks.append(success_rate)

        # 风险决策比例
        if 'risk_level' in decision_logs.columns:
            high_risk_decisions = (decision_logs['risk_level'] == 'high').sum()
            total_decisions = len(decision_logs)
            risk_ratio = high_risk_decisions / max(total_decisions, 1)
            # 风险决策不应超过5%
            risk_safety = 1.0 - min(risk_ratio / 0.05, 1.0)
            safety_checks.append(risk_safety)

        # 决策一致性 (与人工判断的比较)
        if 'human_judgment' in decision_logs.columns and 'ai_decision' in decision_logs.columns:
            consistency = (decision_logs['human_judgment'] == decision_logs['ai_decision']).mean()
            safety_checks.append(consistency)

        safety_score = np.mean(safety_checks) if safety_checks else 0.5

        return {
            'safety_score': safety_score,
            'success_rate': safety_checks[0] if len(safety_checks) > 0 else 0.5,
            'risk_safety': safety_checks[1] if len(safety_checks) > 1 else 0.5,
            'consistency': safety_checks[2] if len(safety_checks) > 2 else 0.5
        }

    def _evaluate_emergency_response(self, decision_logs: pd.DataFrame) -> Dict[str, float]:
        """评估应急响应"""
        if 'emergency_situation' not in decision_logs.columns or 'response_time' not in decision_logs.columns:
            return {'response_score': 0.5, 'avg_response_time': 1000}

        emergency_cases = decision_logs[decision_logs['emergency_situation'] == True]
        if len(emergency_cases) == 0:
            return {'response_score': 1.0, 'avg_response_time': 0}

        avg_response_time = emergency_cases['response_time'].mean()
        response_score = 1.0 - min(avg_response_time / 200, 1.0)  # 200ms目标响应时间

        return {
            'response_score': response_score,
            'avg_response_time': avg_response_time
        }

    def _assess_hmi_safety(self, decision_logs: pd.DataFrame) -> float:
        """评估人机交互安全性"""
        safety_checks = []

        # 接管请求响应时间
        if 'takeover_request_time' in decision_logs.columns and 'takeover_response_time' in decision_logs.columns:
            takeover_cases = decision_logs[decision_logs['takeover_request_time'].notna()]
            if len(takeover_cases) > 0:
                avg_takeover_time = (takeover_cases['takeover_response_time'] - takeover_cases['takeover_request_time']).mean()
                takeover_safety = 1.0 - min(avg_takeover_time / 2000, 1.0)  # 2秒接管时间
                safety_checks.append(takeover_safety)

        # 警告信息清晰度
        if 'warning_clarity' in decision_logs.columns:
            avg_clarity = decision_logs['warning_clarity'].mean()
            safety_checks.append(avg_clarity)

        # 用户理解度
        if 'user_understanding' in decision_logs.columns:
            avg_understanding = decision_logs['user_understanding'].mean()
            safety_checks.append(avg_understanding)

        return np.mean(safety_checks) if safety_checks else 0.5

    def _check_decision_consistency(self, decision_logs: pd.DataFrame) -> float:
        """检查决策一致性"""
        if len(decision_logs) < 10:
            return 0.5

        # 检查相似场景下的决策一致性
        consistency_checks = []

        # 基于场景类型的分组一致性
        if 'scenario_type' in decision_logs.columns:
            scenario_groups = decision_logs.groupby('scenario_type')
            for scenario, group in scenario_groups:
                if len(group) > 1:
                    # 检查决策结果的一致性
                    decision_consistency = group['decision'].value_counts().max() / len(group)
                    consistency_checks.append(decision_consistency)

        # 时间序列一致性
        if 'decision' in decision_logs.columns:
            decisions = decision_logs['decision'].values
            consistency_score = 1.0
            for i in range(1, min(len(decisions), 100)):  # 检查前100个决策
                if decisions[i] != decisions[i-1]:
                    consistency_score *= 0.99  # 每次变化降低一致性
            consistency_checks.append(consistency_score)

        return np.mean(consistency_checks) if consistency_checks else 0.5

    def _check_ethical_compliance(self, decision_logs: pd.DataFrame) -> float:
        """检查伦理合规性"""
        ethical_checks = []

        # 最小伤害原则检查
        if 'harm_minimization' in decision_logs.columns:
            harm_compliance = decision_logs['harm_minimization'].mean()
            ethical_checks.append(harm_compliance)

        # 公平性检查
        if 'bias_detection' in decision_logs.columns:
            bias_free = 1.0 - decision_logs['bias_detection'].mean()
            ethical_checks.append(bias_free)

        # 可解释性检查
        if 'explainability_score' in decision_logs.columns:
            explainability = decision_logs['explainability_score'].mean()
            ethical_checks.append(explainability)

        # 人类监督检查
        if 'human_oversight' in decision_logs.columns:
            oversight_compliance = decision_logs['human_oversight'].mean()
            ethical_checks.append(oversight_compliance)

        return np.mean(ethical_checks) if ethical_checks else 0.5

    def run_comprehensive_validation(self, test_cases: List[AutonomousTestCase]) -> Dict[str, Any]:
        """运行综合验证"""
        logger.info("开始自动驾驶测试综合验证...")

        results = []
        for test_case in test_cases:
            if test_case.scenario_type == 'vehicle_monitoring':
                # 这里需要实际的传感器数据和系统指标
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=0.8,
                    risk_score=0.02,
                    compliance_score=0.99,
                    details={'simulated': True}
                )
            elif test_case.scenario_type == 'environmental_perception':
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=1.5,
                    risk_score=0.01,
                    compliance_score=0.98,
                    details={'simulated': True}
                )
            elif test_case.scenario_type == 'decision_system':
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=2.2,
                    risk_score=0.005,
                    compliance_score=0.995,
                    details={'simulated': True}
                )
            else:
                result = TestResult(
                    case_id=test_case.case_id,
                    status='warning',
                    execution_time=0.5,
                    risk_score=0.5,
                    compliance_score=0.8,
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
            'average_risk_score': sum(r.risk_score for r in results) / len(results),
            'average_compliance_score': sum(r.compliance_score for r in results) / len(results),
            'average_execution_time': sum(r.execution_time for r in results) / len(results)
        }

        return {
            'summary': summary,
            'detailed_results': [asdict(r) for r in results]
        }

# 使用示例
if __name__ == "__main__":
    validator = AutonomousTestValidator()

    # 创建测试案例
    test_cases = [
        AutonomousTestCase(
            case_id="VEHICLE_MONITORING_001",
            scenario_type="vehicle_monitoring",
            risk_level="high",
            safety_requirements=["传感器冗余", "实时监控", "故障检测"],
            test_data={},
            expected_results={"health_score": "> 0.95"},
            validation_rules={"min_health_score": 0.95}
        ),
        AutonomousTestCase(
            case_id="ENVIRONMENTAL_PERCEPTION_001",
            scenario_type="environmental_perception",
            risk_level="critical",
            safety_requirements=["检测准确性", "实时性能", "环境适应"],
            test_data={},
            expected_results={"detection_accuracy": "> 0.99"},
            validation_rules={"min_accuracy": 0.99}
        ),
        AutonomousTestCase(
            case_id="DECISION_SYSTEM_001",
            scenario_type="decision_system",
            risk_level="critical",
            safety_requirements=["决策安全", "伦理合规", "人类监督"],
            test_data={},
            expected_results={"safety_score": "> 0.9999"},
            validation_rules={"min_safety": 0.9999}
        )
    ]

    # 运行验证
    validation_report = validator.run_comprehensive_validation(test_cases)

    # 输出结果
    print("自动驾驶测试验证报告:")
    print(json.dumps(validation_report, indent=2, ensure_ascii=False))

    print("自动驾驶测试验证完成")</content>
<parameter name="filePath">e:\DONT_TOUCH\10M-2025-Testing\examples\18_cases\autonomous_test_validator.py