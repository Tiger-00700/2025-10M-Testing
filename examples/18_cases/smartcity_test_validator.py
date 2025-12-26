# examples/18_cases/smartcity_test_validator.py
"""
智慧城市行业大数据测试验证器
用于验证城市交通、环境监测、公共安全等系统的测试质量和性能
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
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
class SmartCityTestCase:
    """智慧城市测试案例"""
    case_id: str
    scenario_type: str  # 'traffic_management', 'environmental_monitoring', 'public_safety'
    priority_level: str  # 'low', 'medium', 'high', 'critical'
    quality_requirements: List[str]
    test_data: Dict[str, Any]
    expected_results: Dict[str, Any]
    validation_rules: Dict[str, Any]

class SmartCityTestValidator:
    """智慧城市行业测试验证器"""

    def __init__(self, config_path: str = 'smartcity_test_config.json'):
        self.config = {
            'max_traffic_delay': 1.0,  # 最大交通延迟1秒
            'min_prediction_accuracy': 0.85,  # 最小预测准确率85%
            'max_environmental_error': 0.10,  # 最大环境监测误差10%
            'min_safety_detection_rate': 0.90,  # 最小安全检测率90%
            'max_false_alarm_rate': 0.05,  # 最大误报率5%
            'min_data_coverage': 0.85  # 最小数据覆盖率85%
        }
        self.test_results: List[TestResult] = []

    def validate_traffic_management(self, traffic_data: pd.DataFrame,
                                  prediction_model: Any = None) -> TestResult:
        """验证交通管理系统"""
        start_time = datetime.now()

        try:
            # 1. 交通流量实时分析
            flow_analysis_score = self._analyze_traffic_flow(traffic_data)

            # 2. 拥堵预测准确性
            prediction_accuracy = self._evaluate_congestion_prediction(traffic_data, prediction_model)

            # 3. 智能信号灯优化效果
            signal_optimization_score = self._assess_signal_optimization(traffic_data)

            # 4. 系统响应性能
            performance_score = self._evaluate_system_performance(traffic_data)

            # 综合评分
            overall_score = (flow_analysis_score * 0.3 +
                           prediction_accuracy * 0.4 +
                           signal_optimization_score * 0.2 +
                           performance_score * 0.1)

            # 合规检查
            compliance_score = self._check_traffic_compliance(traffic_data)

            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            if overall_score >= 0.85 and performance_score >= 0.9:
                status = 'pass'
                risk_score = 1.0 - overall_score
            elif overall_score >= 0.75:
                status = 'warning'
                risk_score = 1.0 - overall_score
            else:
                status = 'fail'
                risk_score = 1.0 - overall_score

            details = {
                'flow_analysis_score': flow_analysis_score,
                'prediction_accuracy': prediction_accuracy,
                'signal_optimization_score': signal_optimization_score,
                'performance_score': performance_score,
                'overall_score': overall_score,
                'compliance_score': compliance_score,
                'execution_time': execution_time
            }

            return TestResult(
                case_id="TRAFFIC_MANAGEMENT_001",
                status=status,
                execution_time=execution_time,
                risk_score=risk_score,
                compliance_score=compliance_score,
                details=details
            )

        except Exception as e:
            logger.error(f"交通管理验证失败: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestResult(
                case_id="TRAFFIC_MANAGEMENT_001",
                status='fail',
                execution_time=execution_time,
                risk_score=1.0,
                compliance_score=0.0,
                details={'error': str(e)}
            )

    def validate_environmental_monitoring(self, sensor_data: pd.DataFrame,
                                        environmental_model: Any = None) -> TestResult:
        """验证环境监测网络"""
        start_time = datetime.now()

        try:
            # 1. 空气质量综合评估
            air_quality_score = self._assess_air_quality(sensor_data)

            # 2. 噪音污染控制
            noise_control_score = self._evaluate_noise_control(sensor_data)

            # 3. 水资源使用优化
            water_optimization_score = self._assess_water_management(sensor_data)

            # 4. 监测网络覆盖率
            coverage_score = self._evaluate_sensor_coverage(sensor_data)

            # 综合评分
            overall_score = (air_quality_score * 0.4 +
                           noise_control_score * 0.25 +
                           water_optimization_score * 0.25 +
                           coverage_score * 0.1)

            # 环境标准合规检查
            compliance_score = self._check_environmental_compliance(sensor_data)

            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            if overall_score >= 0.85 and coverage_score >= self.config['min_data_coverage']:
                status = 'pass'
                risk_score = 1.0 - overall_score
            elif overall_score >= 0.75:
                status = 'warning'
                risk_score = 1.0 - overall_score
            else:
                status = 'fail'
                risk_score = 1.0 - overall_score

            details = {
                'air_quality_score': air_quality_score,
                'noise_control_score': noise_control_score,
                'water_optimization_score': water_optimization_score,
                'coverage_score': coverage_score,
                'overall_score': overall_score,
                'compliance_score': compliance_score,
                'execution_time': execution_time
            }

            return TestResult(
                case_id="ENVIRONMENTAL_MONITORING_001",
                status=status,
                execution_time=execution_time,
                risk_score=risk_score,
                compliance_score=compliance_score,
                details=details
            )

        except Exception as e:
            logger.error(f"环境监测验证失败: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestResult(
                case_id="ENVIRONMENTAL_MONITORING_001",
                status='fail',
                execution_time=execution_time,
                risk_score=1.0,
                compliance_score=0.0,
                details={'error': str(e)}
            )

    def validate_public_safety_platform(self, safety_data: pd.DataFrame,
                                      security_model: Any = None) -> TestResult:
        """验证公共安全平台"""
        start_time = datetime.now()

        try:
            # 1. 视频监控智能分析
            video_analysis_score = self._evaluate_video_analysis(safety_data)

            # 2. 人群密度实时监测
            crowd_monitoring_score = self._assess_crowd_monitoring(safety_data)

            # 3. 应急事件快速响应
            emergency_response_score = self._evaluate_emergency_response(safety_data)

            # 4. 隐私保护合规性
            privacy_compliance_score = self._check_privacy_compliance(safety_data)

            # 综合评分
            overall_score = (video_analysis_score * 0.3 +
                           crowd_monitoring_score * 0.25 +
                           emergency_response_score * 0.25 +
                           privacy_compliance_score * 0.2)

            # 安全标准合规检查
            compliance_score = self._check_safety_compliance(safety_data)

            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            if overall_score >= self.config['min_safety_detection_rate'] and privacy_compliance_score >= 0.95:
                status = 'pass'
                risk_score = 1.0 - overall_score
            elif overall_score >= 0.80:
                status = 'warning'
                risk_score = 1.0 - overall_score
            else:
                status = 'fail'
                risk_score = 1.0 - overall_score

            details = {
                'video_analysis_score': video_analysis_score,
                'crowd_monitoring_score': crowd_monitoring_score,
                'emergency_response_score': emergency_response_score,
                'privacy_compliance_score': privacy_compliance_score,
                'overall_score': overall_score,
                'compliance_score': compliance_score,
                'execution_time': execution_time
            }

            return TestResult(
                case_id="PUBLIC_SAFETY_001",
                status=status,
                execution_time=execution_time,
                risk_score=risk_score,
                compliance_score=compliance_score,
                details=details
            )

        except Exception as e:
            logger.error(f"公共安全验证失败: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            return TestResult(
                case_id="PUBLIC_SAFETY_001",
                status='fail',
                execution_time=execution_time,
                risk_score=1.0,
                compliance_score=0.0,
                details={'error': str(e)}
            )

    def _analyze_traffic_flow(self, traffic_data: pd.DataFrame) -> float:
        """分析交通流量"""
        analysis_scores = []

        # 数据完整性检查
        completeness = 1.0 - traffic_data.isnull().sum().sum() / (traffic_data.shape[0] * traffic_data.shape[1])
        analysis_scores.append(completeness)

        # 流量模式识别
        if 'vehicle_count' in traffic_data.columns and len(traffic_data) > 10:
            # 计算流量变化趋势
            flow_trend = traffic_data['vehicle_count'].pct_change().abs().mean()
            trend_stability = 1.0 - min(flow_trend, 1.0)  # 流量变化稳定性
            analysis_scores.append(trend_stability)

        # 路口通行效率
        if 'intersection_delay' in traffic_data.columns:
            avg_delay = traffic_data['intersection_delay'].mean()
            delay_score = 1.0 - min(avg_delay / self.config['max_traffic_delay'], 1.0)
            analysis_scores.append(delay_score)

        # 峰值流量处理能力
        if 'peak_flow' in traffic_data.columns:
            peak_handling = traffic_data['peak_flow'].max() / traffic_data['peak_flow'].mean()
            peak_score = min(peak_handling / 2.0, 1.0)  # 峰值是均值的2倍以内为佳
            analysis_scores.append(peak_score)

        return np.mean(analysis_scores) if analysis_scores else 0.5

    def _evaluate_congestion_prediction(self, traffic_data: pd.DataFrame, model: Any = None) -> float:
        """评估拥堵预测"""
        if model is None or 'actual_congestion' not in traffic_data.columns:
            return 0.5

        try:
            # 准备预测数据
            feature_cols = [col for col in traffic_data.columns if col not in ['actual_congestion', 'timestamp']]
            X = traffic_data[feature_cols]
            y_true = traffic_data['actual_congestion']

            # 生成预测
            y_pred = model.predict(X)

            # 计算预测准确性
            mse = mean_squared_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)

            # 综合评分 (R²权重更高)
            accuracy_score = (r2 + 1.0) / 2.0  # R²从-1到1转换为0到1
            accuracy_score = max(0, min(accuracy_score, 1.0))  # 确保在0-1范围内

            return accuracy_score

        except Exception as e:
            logger.warning(f"拥堵预测评估失败: {e}")
            return 0.5

    def _assess_signal_optimization(self, traffic_data: pd.DataFrame) -> float:
        """评估信号灯优化效果"""
        optimization_scores = []

        # 信号灯调整频率
        if 'signal_changes' in traffic_data.columns:
            change_frequency = traffic_data['signal_changes'].mean()
            # 合理调整频率 (每小时1-5次)
            frequency_score = 1.0 - min(abs(change_frequency - 3) / 3, 1.0)
            optimization_scores.append(frequency_score)

        # 绿灯利用率
        if 'green_light_utilization' in traffic_data.columns:
            avg_utilization = traffic_data['green_light_utilization'].mean()
            utilization_score = avg_utilization  # 直接使用利用率
            optimization_scores.append(utilization_score)

        # 排队长度减少
        if 'queue_length' in traffic_data.columns:
            queue_reduction = 1.0 - traffic_data['queue_length'].mean() / traffic_data['queue_length'].max()
            queue_score = max(0, queue_reduction)
            optimization_scores.append(queue_score)

        return np.mean(optimization_scores) if optimization_scores else 0.5

    def _evaluate_system_performance(self, traffic_data: pd.DataFrame) -> float:
        """评估系统性能"""
        performance_scores = []

        # 响应时间
        if 'response_time' in traffic_data.columns:
            avg_response = traffic_data['response_time'].mean()
            response_score = 1.0 - min(avg_response / 1000, 1.0)  # 1秒目标响应时间
            performance_scores.append(response_score)

        # 数据处理延迟
        if 'processing_delay' in traffic_data.columns:
            avg_delay = traffic_data['processing_delay'].mean()
            delay_score = 1.0 - min(avg_delay / 500, 1.0)  # 500ms处理延迟
            performance_scores.append(delay_score)

        # 系统可用性
        if 'system_uptime' in traffic_data.columns:
            avg_uptime = traffic_data['system_uptime'].mean()
            uptime_score = avg_uptime  # 直接使用可用性百分比
            performance_scores.append(uptime_score)

        return np.mean(performance_scores) if performance_scores else 0.5

    def _check_traffic_compliance(self, traffic_data: pd.DataFrame) -> float:
        """检查交通合规性"""
        compliance_checks = []

        # 数据隐私保护
        sensitive_fields = ['license_plate', 'personal_info']
        privacy_compliance = 1.0
        for field in sensitive_fields:
            if field in traffic_data.columns:
                # 检查是否已脱敏
                masked_ratio = traffic_data[field].astype(str).str.contains(r'\*+', regex=True).mean()
                privacy_compliance *= masked_ratio
        compliance_checks.append(privacy_compliance)

        # 数据质量标准
        required_fields = ['timestamp', 'vehicle_count', 'speed']
        field_completeness = sum(1 for field in required_fields if field in traffic_data.columns) / len(required_fields)
        compliance_checks.append(field_completeness)

        # 时间序列完整性
        if 'timestamp' in traffic_data.columns:
            time_gaps = traffic_data['timestamp'].diff().dt.total_seconds().fillna(0)
            gap_compliance = (time_gaps <= 3600).mean()  # 1小时内数据连续
            compliance_checks.append(gap_compliance)

        return np.mean(compliance_checks) if compliance_checks else 0.0

    def _assess_air_quality(self, sensor_data: pd.DataFrame) -> float:
        """评估空气质量"""
        quality_scores = []

        # AQI计算准确性
        if 'pm25' in sensor_data.columns and 'pm10' in sensor_data.columns:
            # 简化的AQI计算
            pm25 = sensor_data['pm25'].mean()
            pm10 = sensor_data['pm10'].mean()

            # AQI计算公式 (简化版)
            aqi_pm25 = self._calculate_aqi(pm25, 'pm25')
            aqi_pm10 = self._calculate_aqi(pm10, 'pm10')
            aqi = max(aqi_pm25, aqi_pm10)

            # AQI准确性评分 (0-500范围)
            aqi_accuracy = 1.0 - min(aqi / 500, 1.0)
            quality_scores.append(aqi_accuracy)

        # 传感器一致性
        pollutant_cols = [col for col in sensor_data.columns if col in ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']]
        if len(pollutant_cols) >= 2:
            correlations = sensor_data[pollutant_cols].corr().abs()
            avg_correlation = correlations.mean().mean()
            consistency_score = min(avg_correlation, 1.0)
            quality_scores.append(consistency_score)

        # 数据覆盖率
        coverage = 1.0 - sensor_data.isnull().sum().sum() / (sensor_data.shape[0] * sensor_data.shape[1])
        quality_scores.append(coverage)

        return np.mean(quality_scores) if quality_scores else 0.5

    def _evaluate_noise_control(self, sensor_data: pd.DataFrame) -> float:
        """评估噪音控制"""
        if 'noise_level' not in sensor_data.columns:
            return 0.5

        noise_scores = []

        # 噪音水平评估
        avg_noise = sensor_data['noise_level'].mean()
        # 噪音标准: 白天<70dB, 夜间<55dB (简化处理)
        noise_standard = 65  # 平均标准
        noise_compliance = 1.0 - min(avg_noise / noise_standard, 1.0)
        noise_scores.append(noise_compliance)

        # 噪音变化趋势
        if len(sensor_data) > 10:
            noise_trend = sensor_data['noise_level'].pct_change().abs().mean()
            trend_stability = 1.0 - min(noise_trend, 1.0)
            noise_scores.append(trend_stability)

        # 超标区域识别
        if 'noise_threshold' in sensor_data.columns:
            exceedance_rate = (sensor_data['noise_level'] > sensor_data['noise_threshold']).mean()
            control_effectiveness = 1.0 - exceedance_rate
            noise_scores.append(control_effectiveness)

        return np.mean(noise_scores) if noise_scores else 0.5

    def _assess_water_management(self, sensor_data: pd.DataFrame) -> float:
        """评估水资源管理"""
        water_scores = []

        # 漏水检测准确性
        if 'water_flow' in sensor_data.columns and 'pressure' in sensor_data.columns:
            # 基于流量和压力异常检测漏水
            flow_anomalies = self._detect_anomalies(sensor_data['water_flow'])
            pressure_anomalies = self._detect_anomalies(sensor_data['pressure'])

            leak_detection_rate = (flow_anomalies | pressure_anomalies).mean()
            detection_score = leak_detection_rate  # 检测率越高越好
            water_scores.append(detection_score)

        # 用水效率分析
        if 'water_usage' in sensor_data.columns:
            avg_usage = sensor_data['water_usage'].mean()
            # 与基准值比较 (简化处理)
            benchmark = sensor_data['water_usage'].quantile(0.5)  # 中位数作为基准
            efficiency = 1.0 - min(avg_usage / benchmark, 1.0)
            water_scores.append(efficiency)

        # 水质监测
        water_quality_cols = [col for col in sensor_data.columns if 'quality' in col.lower() or col in ['ph', 'turbidity', 'chlorine']]
        if water_quality_cols:
            quality_completeness = 1.0 - sensor_data[water_quality_cols].isnull().sum().sum() / (sensor_data.shape[0] * len(water_quality_cols))
            water_scores.append(quality_completeness)

        return np.mean(water_scores) if water_scores else 0.5

    def _evaluate_sensor_coverage(self, sensor_data: pd.DataFrame) -> float:
        """评估传感器覆盖率"""
        coverage_scores = []

        # 地理覆盖率
        if 'location' in sensor_data.columns:
            unique_locations = sensor_data['location'].nunique()
            total_expected = len(sensor_data)  # 简化假设
            location_coverage = min(unique_locations / total_expected, 1.0)
            coverage_scores.append(location_coverage)

        # 时间覆盖率
        if 'timestamp' in sensor_data.columns:
            time_span = sensor_data['timestamp'].max() - sensor_data['timestamp'].min()
            expected_readings = time_span.total_seconds() / 3600  # 每小时一个读数
            actual_readings = len(sensor_data)
            time_coverage = min(actual_readings / expected_readings, 1.0)
            coverage_scores.append(time_coverage)

        # 数据完整性
        completeness = 1.0 - sensor_data.isnull().sum().sum() / (sensor_data.shape[0] * sensor_data.shape[1])
        coverage_scores.append(completeness)

        return np.mean(coverage_scores) if coverage_scores else 0.5

    def _check_environmental_compliance(self, sensor_data: pd.DataFrame) -> float:
        """检查环境合规性"""
        compliance_checks = []

        # 监测频率合规
        if 'timestamp' in sensor_data.columns:
            time_diffs = sensor_data['timestamp'].diff().dt.total_seconds().dropna()
            avg_interval = time_diffs.mean()
            # 每15分钟一次监测
            frequency_compliance = 1.0 - min(abs(avg_interval - 900) / 900, 1.0)
            compliance_checks.append(frequency_compliance)

        # 数据质量标准
        required_params = ['pm25', 'pm10', 'temperature', 'humidity']
        param_coverage = sum(1 for param in required_params if param in sensor_data.columns) / len(required_params)
        compliance_checks.append(param_coverage)

        # 校准记录
        if 'last_calibration' in sensor_data.columns:
            days_since_calibration = (datetime.now() - sensor_data['last_calibration'].max()).days
            calibration_compliance = 1.0 - min(days_since_calibration / 365, 1.0)  # 一年校准一次
            compliance_checks.append(calibration_compliance)

        return np.mean(compliance_checks) if compliance_checks else 0.0

    def _evaluate_video_analysis(self, safety_data: pd.DataFrame) -> float:
        """评估视频分析"""
        analysis_scores = []

        # 异常检测准确性
        if 'anomaly_detected' in safety_data.columns and 'actual_anomaly' in safety_data.columns:
            detection_accuracy = (safety_data['anomaly_detected'] == safety_data['actual_anomaly']).mean()
            analysis_scores.append(detection_accuracy)

        # 处理速度
        if 'processing_time' in safety_data.columns:
            avg_processing_time = safety_data['processing_time'].mean()
            speed_score = 1.0 - min(avg_processing_time / 1000, 1.0)  # 1秒处理时间
            analysis_scores.append(speed_score)

        # 误报率控制
        if 'false_positive' in safety_data.columns:
            false_positive_rate = safety_data['false_positive'].mean()
            false_positive_score = 1.0 - false_positive_rate
            analysis_scores.append(false_positive_score)

        return np.mean(analysis_scores) if analysis_scores else 0.5

    def _assess_crowd_monitoring(self, safety_data: pd.DataFrame) -> float:
        """评估人群监测"""
        monitoring_scores = []

        # 密度估计准确性
        if 'estimated_density' in safety_data.columns and 'actual_density' in safety_data.columns:
            density_error = abs(safety_data['estimated_density'] - safety_data['actual_density']).mean()
            max_density = safety_data['actual_density'].max()
            density_accuracy = 1.0 - min(density_error / max_density, 1.0)
            monitoring_scores.append(density_accuracy)

        # 实时性
        if 'density_update_time' in safety_data.columns:
            avg_update_time = safety_data['density_update_time'].mean()
            real_time_score = 1.0 - min(avg_update_time / 5000, 1.0)  # 5秒更新
            monitoring_scores.append(real_time_score)

        # 覆盖范围
        if 'coverage_area' in safety_data.columns:
            avg_coverage = safety_data['coverage_area'].mean()
            coverage_score = min(avg_coverage / 10000, 1.0)  # 10000平方米覆盖
            monitoring_scores.append(coverage_score)

        return np.mean(monitoring_scores) if monitoring_scores else 0.5

    def _evaluate_emergency_response(self, safety_data: pd.DataFrame) -> float:
        """评估应急响应"""
        response_scores = []

        # 响应时间
        if 'response_time' in safety_data.columns:
            avg_response_time = safety_data['response_time'].mean()
            response_time_score = 1.0 - min(avg_response_time / 180, 1.0)  # 3分钟响应
            response_scores.append(response_time_score)

        # 响应成功率
        if 'response_success' in safety_data.columns:
            success_rate = safety_data['response_success'].mean()
            response_scores.append(success_rate)

        # 资源分配效率
        if 'resources_allocated' in safety_data.columns and 'resources_needed' in safety_data.columns:
            allocation_efficiency = (safety_data['resources_allocated'] / safety_data['resources_needed']).mean()
            allocation_efficiency = min(allocation_efficiency, 1.0)
            response_scores.append(allocation_efficiency)

        return np.mean(response_scores) if response_scores else 0.5

    def _check_privacy_compliance(self, safety_data: pd.DataFrame) -> float:
        """检查隐私合规性"""
        privacy_checks = []

        # 面部模糊处理
        if 'face_blur_ratio' in safety_data.columns:
            avg_blur_ratio = safety_data['face_blur_ratio'].mean()
            privacy_checks.append(avg_blur_ratio)

        # 数据保留期限
        if 'data_retention_days' in safety_data.columns:
            avg_retention = safety_data['data_retention_days'].mean()
            retention_compliance = 1.0 - min(avg_retention / 90, 1.0)  # 90天最大保留期
            privacy_checks.append(retention_compliance)

        # 访问控制
        if 'access_control_score' in safety_data.columns:
            avg_access_control = safety_data['access_control_score'].mean()
            privacy_checks.append(avg_access_control)

        return np.mean(privacy_checks) if privacy_checks else 0.5

    def _check_safety_compliance(self, safety_data: pd.DataFrame) -> float:
        """检查安全合规性"""
        compliance_checks = []

        # 监控覆盖率
        if 'monitoring_coverage' in safety_data.columns:
            avg_coverage = safety_data['monitoring_coverage'].mean()
            compliance_checks.append(avg_coverage)

        # 告警响应时间
        if 'alert_response_time' in safety_data.columns:
            avg_response = safety_data['alert_response_time'].mean()
            response_compliance = 1.0 - min(avg_response / 300, 1.0)  # 5分钟响应
            compliance_checks.append(response_compliance)

        # 系统冗余
        if 'system_redundancy' in safety_data.columns:
            avg_redundancy = safety_data['system_redundancy'].mean()
            compliance_checks.append(avg_redundancy)

        return np.mean(compliance_checks) if compliance_checks else 0.0

    def _calculate_aqi(self, concentration: float, pollutant: str) -> float:
        """计算空气质量指数 (简化版)"""
        # 简化的AQI计算
        if pollutant == 'pm25':
            if concentration <= 35:
                return (concentration / 35) * 50
            elif concentration <= 75:
                return 50 + ((concentration - 35) / 40) * 50
            else:
                return 100 + ((concentration - 75) / 25) * 100
        elif pollutant == 'pm10':
            if concentration <= 50:
                return (concentration / 50) * 50
            elif concentration <= 150:
                return 50 + ((concentration - 50) / 100) * 50
            else:
                return 100 + ((concentration - 150) / 50) * 100
        return 50  # 默认值

    def _detect_anomalies(self, data: pd.Series, threshold: float = 2.0) -> pd.Series:
        """检测异常值"""
        if len(data) < 10:
            return pd.Series([False] * len(data), index=data.index)

        mean_val = data.mean()
        std_val = data.std()

        if std_val == 0:
            return pd.Series([False] * len(data), index=data.index)

        z_scores = abs((data - mean_val) / std_val)
        return z_scores > threshold

    def run_comprehensive_validation(self, test_cases: List[SmartCityTestCase]) -> Dict[str, Any]:
        """运行综合验证"""
        logger.info("开始智慧城市测试综合验证...")

        results = []
        for test_case in test_cases:
            if test_case.scenario_type == 'traffic_management':
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=1.2,
                    risk_score=0.08,
                    compliance_score=0.95,
                    details={'simulated': True}
                )
            elif test_case.scenario_type == 'environmental_monitoring':
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=1.8,
                    risk_score=0.05,
                    compliance_score=0.97,
                    details={'simulated': True}
                )
            elif test_case.scenario_type == 'public_safety_platform':
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=2.5,
                    risk_score=0.03,
                    compliance_score=0.98,
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
    validator = SmartCityTestValidator()

    # 创建测试案例
    test_cases = [
        SmartCityTestCase(
            case_id="TRAFFIC_MANAGEMENT_001",
            scenario_type="traffic_management",
            priority_level="high",
            quality_requirements=["实时性", "准确性", "可扩展性"],
            test_data={},
            expected_results={"flow_analysis_accuracy": "> 0.95"},
            validation_rules={"min_accuracy": 0.95}
        ),
        SmartCityTestCase(
            case_id="ENVIRONMENTAL_MONITORING_001",
            scenario_type="environmental_monitoring",
            priority_level="medium",
            quality_requirements=["覆盖率", "准确性", "连续性"],
            test_data={},
            expected_results={"aqi_accuracy": "> 0.90"},
            validation_rules={"min_aqi_accuracy": 0.90}
        ),
        SmartCityTestCase(
            case_id="PUBLIC_SAFETY_001",
            scenario_type="public_safety_platform",
            priority_level="critical",
            quality_requirements=["检测率", "响应时间", "隐私保护"],
            test_data={},
            expected_results={"detection_rate": "> 0.90"},
            validation_rules={"min_detection_rate": 0.90}
        )
    ]

    # 运行验证
    validation_report = validator.run_comprehensive_validation(test_cases)

    # 输出结果
    print("智慧城市测试验证报告:")
    print(json.dumps(validation_report, indent=2, ensure_ascii=False))

    print("智慧城市测试验证完成")</content>
<parameter name="filePath">e:\DONT_TOUCH\10M-2025-Testing\examples\18_cases\smartcity_test_validator.py