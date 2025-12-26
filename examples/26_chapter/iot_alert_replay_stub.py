#!/usr/bin/env python3
"""
物联网大数据测试策略 - 物联网告警重放存根
IoT Big Data Testing Strategy - IoT Alert Replay Stub

此脚本用于物联网设备告警数据的重放测试和实时流处理验证。
This script replays IoT device alert data for testing and validates real-time stream processing.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import time
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IoTAlertReplay:
    def __init__(self, config: Dict):
        self.config = config
        self.sensor_types = config.get('sensor_types', ['temperature', 'pressure', 'vibration'])
        self.stream_config = config.get('stream_config', {
            'window_size_seconds': 60,
            'latency_threshold_ms': 1000,
            'throughput_target': 10000
        })

    def replay_alert_stream(self, alert_data: pd.DataFrame, replay_speed: float = 1.0) -> Dict:
        """
        重放告警数据流
        Replay alert data stream
        """
        results = {
            'total_alerts': len(alert_data),
            'replay_duration': 0,
            'latency_measurements': [],
            'throughput_measurements': []
        }

        start_time = time.time()
        processed_count = 0

        # 按时间排序
        alert_data = alert_data.sort_values('timestamp').reset_index(drop=True)

        for idx, alert in alert_data.iterrows():
            # 模拟处理延迟
            processing_start = time.time()

            # 验证告警数据
            validation_result = self._validate_alert(alert)

            processing_end = time.time()
            latency = (processing_end - processing_start) * 1000  # ms
            results['latency_measurements'].append(latency)

            processed_count += 1

            # 计算吞吐量
            if processed_count % 100 == 0:
                current_time = time.time()
                throughput = processed_count / (current_time - start_time)
                results['throughput_measurements'].append(throughput)

            # 控制重放速度
            if idx < len(alert_data) - 1:
                next_timestamp = pd.to_datetime(alert_data.loc[idx + 1, 'timestamp'])
                current_timestamp = pd.to_datetime(alert['timestamp'])
                time_diff = (next_timestamp - current_timestamp).total_seconds() / replay_speed

                if time_diff > 0:
                    time.sleep(min(time_diff, 0.1))  # 最大延迟0.1秒

        results['replay_duration'] = time.time() - start_time
        results['avg_latency_ms'] = np.mean(results['latency_measurements'])
        results['max_latency_ms'] = np.max(results['latency_measurements'])
        results['avg_throughput'] = np.mean(results['throughput_measurements']) if results['throughput_measurements'] else 0

        # 性能评估
        results['latency_pass'] = results['avg_latency_ms'] <= self.stream_config['latency_threshold_ms']
        results['throughput_pass'] = results['avg_throughput'] >= self.stream_config['throughput_target']

        return results

    def _validate_alert(self, alert: pd.Series) -> bool:
        """验证单个告警"""
        # 检查必需字段
        required_fields = ['device_id', 'sensor_type', 'value', 'timestamp', 'alert_level']
        for field in required_fields:
            if field not in alert or pd.isna(alert[field]):
                return False

        # 验证传感器类型
        if alert['sensor_type'] not in self.sensor_types:
            return False

        # 验证数值范围
        if not self._validate_sensor_value(alert['sensor_type'], alert['value']):
            return False

        # 验证时间戳
        try:
            pd.to_datetime(alert['timestamp'])
        except:
            return False

        return True

    def _validate_sensor_value(self, sensor_type: str, value: float) -> bool:
        """验证传感器数值范围"""
        ranges = {
            'temperature': (-50, 100),  # 摄氏度
            'pressure': (0, 1000),     # kPa
            'vibration': (0, 100),     # mm/s
            'humidity': (0, 100),      # %
            'power': (0, 1000)         # W
        }

        if sensor_type in ranges:
            min_val, max_val = ranges[sensor_type]
            return min_val <= value <= max_val
        return True  # 未知传感器类型默认通过

    def analyze_alert_patterns(self, alert_data: pd.DataFrame) -> Dict:
        """
        分析告警模式
        Analyze alert patterns
        """
        patterns = {}

        # 告警频率分析
        alert_freq = self._calculate_alert_frequency(alert_data)
        patterns.update(alert_freq)

        # 设备告警分布
        device_distribution = self._analyze_device_distribution(alert_data)
        patterns.update(device_distribution)

        # 传感器类型分布
        sensor_distribution = self._analyze_sensor_distribution(alert_data)
        patterns.update(sensor_distribution)

        # 时间模式分析
        time_patterns = self._analyze_time_patterns(alert_data)
        patterns.update(time_patterns)

        return patterns

    def _calculate_alert_frequency(self, data: pd.DataFrame) -> Dict:
        """计算告警频率"""
        freq_results = {}

        # 总体频率
        total_alerts = len(data)
        time_span_hours = (pd.to_datetime(data['timestamp']).max() - pd.to_datetime(data['timestamp']).min()).total_seconds() / 3600
        if time_span_hours > 0:
            overall_freq = total_alerts / time_span_hours
            freq_results['overall_alerts_per_hour'] = overall_freq

        # 按设备频率
        device_freq = data.groupby('device_id').size() / time_span_hours
        freq_results['avg_alerts_per_device_per_hour'] = device_freq.mean()
        freq_results['max_alerts_per_device_per_hour'] = device_freq.max()

        return freq_results

    def _analyze_device_distribution(self, data: pd.DataFrame) -> Dict:
        """分析设备告警分布"""
        dist_results = {}

        device_alerts = data['device_id'].value_counts()
        dist_results['unique_devices'] = len(device_alerts)
        dist_results['most_active_device'] = device_alerts.index[0]
        dist_results['most_active_device_alerts'] = device_alerts.iloc[0]

        # 设备活跃度分布
        dist_results['device_alerts_std'] = device_alerts.std()
        dist_results['device_alerts_skewness'] = device_alerts.skew()

        return dist_results

    def _analyze_sensor_distribution(self, data: pd.DataFrame) -> Dict:
        """分析传感器类型分布"""
        dist_results = {}

        sensor_alerts = data['sensor_type'].value_counts()
        for sensor_type in self.sensor_types:
            if sensor_type in sensor_alerts:
                dist_results[f'{sensor_type}_alerts'] = sensor_alerts[sensor_type]
            else:
                dist_results[f'{sensor_type}_alerts'] = 0

        return dist_results

    def _analyze_time_patterns(self, data: pd.DataFrame) -> Dict:
        """分析时间模式"""
        time_results = {}

        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['hour'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek

        # 小时分布
        hourly_dist = data['hour'].value_counts().sort_index()
        time_results['peak_hour'] = hourly_dist.idxmax()
        time_results['peak_hour_alerts'] = hourly_dist.max()

        # 星期分布
        weekly_dist = data['day_of_week'].value_counts().sort_index()
        time_results['peak_day'] = weekly_dist.idxmax()
        time_results['peak_day_alerts'] = weekly_dist.max()

        return time_results

def main():
    # 示例配置
    config = {
        'sensor_types': ['temperature', 'pressure', 'vibration', 'humidity'],
        'stream_config': {
            'window_size_seconds': 60,
            'latency_threshold_ms': 1000,
            'throughput_target': 10000
        }
    }

    replay = IoTAlertReplay(config)

    # 示例数据
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'device_id': ['device_' + str(i % 100) for i in range(1000)],
        'sensor_type': np.random.choice(['temperature', 'pressure', 'vibration'], 1000),
        'value': np.random.uniform(0, 100, 1000),
        'timestamp': pd.date_range('2025-01-01', periods=1000, freq='1min'),
        'alert_level': np.random.choice(['low', 'medium', 'high'], 1000)
    })

    # 运行重放测试
    replay_results = replay.replay_alert_stream(sample_data, replay_speed=2.0)

    logger.info("Alert Replay Results:")
    for key, value in replay_results.items():
        logger.info(f"  {key}: {value}")

    # 分析模式
    pattern_results = replay.analyze_alert_patterns(sample_data)

    logger.info("Alert Pattern Analysis:")
    for key, value in pattern_results.items():
        logger.info(f"  {key}: {value}")

if __name__ == "__main__":
    main()