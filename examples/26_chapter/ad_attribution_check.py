#!/usr/bin/env python3
"""
广告大数据测试策略 - 广告归因检查脚本
Advertising Big Data Testing Strategy - Ad Attribution Check Script

此脚本用于验证广告投放的归因模型准确性和转化跟踪。
This script validates ad attribution model accuracy and conversion tracking.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics import mean_absolute_error, r2_score
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdAttributionChecker:
    def __init__(self, config: Dict):
        self.config = config
        self.attribution_window_days = config.get('attribution_window_days', 30)
        self.attribution_models = config.get('attribution_models', ['last_touch', 'first_touch', 'linear', 'time_decay'])
        self.quality_thresholds = config.get('quality_thresholds', {
            'accuracy_threshold': 0.8,
            'completeness_threshold': 0.95,
            'timeliness_threshold': 24  # hours
        })

    def validate_attribution_accuracy(self, attribution_data: pd.DataFrame, ground_truth: pd.DataFrame) -> Dict:
        """
        验证归因准确性
        Validate attribution accuracy
        """
        results = {}

        for model in self.attribution_models:
            if model in attribution_data.columns:
                # 计算预测准确性
                accuracy_metrics = self._calculate_accuracy_metrics(
                    attribution_data[model],
                    ground_truth['actual_attribution']
                )
                results[f'{model}_accuracy'] = accuracy_metrics

                # 检查准确性阈值
                results[f'{model}_accuracy_pass'] = accuracy_metrics['r2_score'] >= self.quality_thresholds['accuracy_threshold']

        return results

    def _calculate_accuracy_metrics(self, predicted: pd.Series, actual: pd.Series) -> Dict:
        """计算准确性指标"""
        metrics = {}

        # 确保数据对齐
        common_index = predicted.index.intersection(actual.index)
        pred_aligned = predicted.loc[common_index]
        actual_aligned = actual.loc[common_index]

        # 计算MAE
        mae = mean_absolute_error(actual_aligned, pred_aligned)
        metrics['mae'] = mae

        # 计算R²分数
        r2 = r2_score(actual_aligned, pred_aligned)
        metrics['r2_score'] = r2

        # 计算平均绝对百分比误差
        mape = np.mean(np.abs((actual_aligned - pred_aligned) / actual_aligned)) * 100
        metrics['mape'] = mape

        return metrics

    def check_conversion_tracking(self, conversion_data: pd.DataFrame) -> Dict:
        """
        检查转化跟踪完整性
        Check conversion tracking completeness
        """
        tracking_results = {}

        # 检查必需转化事件
        required_events = ['click', 'view', 'purchase', 'sign_up', 'lead_generation']
        for event in required_events:
            if event in conversion_data.columns:
                event_count = conversion_data[event].sum()
                tracking_results[f'{event}_count'] = event_count

                # 检查事件完整性
                completeness = conversion_data[event].notna().sum() / len(conversion_data)
                tracking_results[f'{event}_completeness'] = completeness
                tracking_results[f'{event}_completeness_pass'] = completeness >= self.quality_thresholds['completeness_threshold']
            else:
                tracking_results[f'{event}_count'] = 0
                tracking_results[f'{event}_completeness'] = 0
                tracking_results[f'{event}_completeness_pass'] = False

        # 检查转化窗口
        window_results = self._validate_attribution_window(conversion_data)
        tracking_results.update(window_results)

        return tracking_results

    def _validate_attribution_window(self, data: pd.DataFrame) -> Dict:
        """验证归因窗口"""
        window_results = {}

        if 'click_timestamp' in data.columns and 'conversion_timestamp' in data.columns:
            data['click_timestamp'] = pd.to_datetime(data['click_timestamp'])
            data['conversion_timestamp'] = pd.to_datetime(data['conversion_timestamp'])

            # 计算转化延迟
            time_diff = (data['conversion_timestamp'] - data['click_timestamp']).dt.days
            valid_conversions = time_diff <= self.attribution_window_days

            window_results['valid_conversions_ratio'] = valid_conversions.sum() / len(data)
            window_results['avg_conversion_delay_days'] = time_diff.mean()
            window_results['max_conversion_delay_days'] = time_diff.max()

            # 检查窗口合规性
            window_results['window_compliance_pass'] = window_results['valid_conversions_ratio'] >= 0.9

        return window_results

    def analyze_attribution_model_performance(self, model_data: pd.DataFrame) -> Dict:
        """
        分析归因模型性能
        Analyze attribution model performance
        """
        performance_results = {}

        # 跨渠道一致性检查
        channel_consistency = self._check_channel_consistency(model_data)
        performance_results.update(channel_consistency)

        # 时间衰减验证
        time_decay_validation = self._validate_time_decay(model_data)
        performance_results.update(time_decay_validation)

        # 预算分配影响分析
        budget_impact = self._analyze_budget_impact(model_data)
        performance_results.update(budget_impact)

        return performance_results

    def _check_channel_consistency(self, data: pd.DataFrame) -> Dict:
        """检查跨渠道一致性"""
        consistency_results = {}

        if 'channel' in data.columns and 'attribution_score' in data.columns:
            channel_scores = data.groupby('channel')['attribution_score'].agg(['mean', 'std', 'count'])

            # 计算渠道间变异系数
            cv = channel_scores['std'] / channel_scores['mean']
            consistency_results['channel_variation_coefficient'] = cv.mean()

            # 检查一致性阈值
            consistency_results['channel_consistency_pass'] = cv.mean() <= 0.5

            # 识别异常渠道
            abnormal_channels = cv[cv > 1.0].index.tolist()
            consistency_results['abnormal_channels'] = abnormal_channels

        return consistency_results

    def _validate_time_decay(self, data: pd.DataFrame) -> Dict:
        """验证时间衰减效果"""
        decay_results = {}

        if 'days_since_click' in data.columns and 'attribution_weight' in data.columns:
            # 计算衰减相关性
            correlation = data['days_since_click'].corr(data['attribution_weight'])
            decay_results['time_decay_correlation'] = correlation

            # 检查衰减趋势
            recent_weight = data[data['days_since_click'] <= 7]['attribution_weight'].mean()
            old_weight = data[data['days_since_click'] > 7]['attribution_weight'].mean()

            decay_results['recent_vs_old_weight_ratio'] = recent_weight / old_weight if old_weight > 0 else 0
            decay_results['time_decay_effective'] = decay_results['recent_vs_old_weight_ratio'] > 1.2

        return decay_results

    def _analyze_budget_impact(self, data: pd.DataFrame) -> Dict:
        """分析预算分配影响"""
        budget_results = {}

        if 'budget_allocated' in data.columns and 'roi' in data.columns:
            # 计算预算效率
            budget_efficiency = data['roi'] / data['budget_allocated']
            budget_results['avg_budget_efficiency'] = budget_efficiency.mean()

            # 预算分配优化潜力
            optimal_allocation = data.loc[budget_efficiency.idxmax()]
            budget_results['optimal_budget_channel'] = optimal_allocation.get('channel', 'unknown')
            budget_results['optimal_roi'] = optimal_allocation['roi']

        return budget_results

    def validate_fraud_detection(self, fraud_data: pd.DataFrame) -> Dict:
        """
        验证欺诈检测能力
        Validate fraud detection capabilities
        """
        fraud_results = {}

        # 像素触发验证
        pixel_validation = self._validate_pixel_firing(fraud_data)
        fraud_results.update(pixel_validation)

        # 转化验证
        conversion_validation = self._validate_conversions(fraud_data)
        fraud_results.update(conversion_validation)

        # 异常检测
        anomaly_detection = self._detect_attribution_anomalies(fraud_data)
        fraud_results.update(anomaly_detection)

        return fraud_results

    def _validate_pixel_firing(self, data: pd.DataFrame) -> Dict:
        """验证像素触发"""
        pixel_results = {}

        if 'pixel_fired' in data.columns:
            fire_rate = data['pixel_fired'].sum() / len(data)
            pixel_results['pixel_fire_rate'] = fire_rate
            pixel_results['pixel_fire_pass'] = fire_rate >= 0.99

        return pixel_results

    def _validate_conversions(self, data: pd.DataFrame) -> Dict:
        """验证转化数据"""
        conversion_results = {}

        if 'conversion_events' in data.columns:
            # 检查转化事件完整性
            conversion_completeness = data['conversion_events'].notna().sum() / len(data)
            conversion_results['conversion_completeness'] = conversion_completeness
            conversion_results['conversion_completeness_pass'] = conversion_completeness >= self.quality_thresholds['completeness_threshold']

        return conversion_results

    def _detect_attribution_anomalies(self, data: pd.DataFrame) -> Dict:
        """检测归因异常"""
        anomaly_results = {}

        if 'attribution_score' in data.columns:
            # 简单的异常检测
            scores = data['attribution_score']
            mean_score = scores.mean()
            std_score = scores.std()

            anomalies = abs(scores - mean_score) > 3 * std_score
            anomaly_rate = anomalies.sum() / len(data)

            anomaly_results['attribution_anomaly_rate'] = anomaly_rate
            anomaly_results['attribution_anomaly_pass'] = anomaly_rate <= 0.05

        return anomaly_results

def main():
    # 示例配置
    config = {
        'attribution_window_days': 30,
        'attribution_models': ['last_touch', 'first_touch', 'linear', 'time_decay'],
        'quality_thresholds': {
            'accuracy_threshold': 0.8,
            'completeness_threshold': 0.95,
            'timeliness_threshold': 24
        }
    }

    checker = AdAttributionChecker(config)

    # 示例数据
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'campaign_id': ['camp_' + str(i % 10) for i in range(1000)],
        'channel': np.random.choice(['search', 'display', 'social', 'email'], 1000),
        'click_timestamp': pd.date_range('2025-01-01', periods=1000, freq='1H'),
        'conversion_timestamp': pd.date_range('2025-01-01 01:00:00', periods=1000, freq='1H'),
        'last_touch': np.random.uniform(0, 1, 1000),
        'first_touch': np.random.uniform(0, 1, 1000),
        'linear': np.random.uniform(0, 1, 1000),
        'time_decay': np.random.uniform(0, 1, 1000),
        'actual_attribution': np.random.uniform(0, 1, 1000),
        'budget_allocated': np.random.uniform(100, 10000, 1000),
        'roi': np.random.uniform(0.5, 5.0, 1000),
        'pixel_fired': np.random.choice([True, False], 1000, p=[0.98, 0.02]),
        'conversion_events': np.random.choice([True, False], 1000, p=[0.1, 0.9])
    })

    # 运行验证
    accuracy_results = checker.validate_attribution_accuracy(sample_data, sample_data[['actual_attribution']])
    tracking_results = checker.check_conversion_tracking(sample_data)
    performance_results = checker.analyze_attribution_model_performance(sample_data)
    fraud_results = checker.validate_fraud_detection(sample_data)

    logger.info("Attribution Accuracy Results:")
    for model, metrics in accuracy_results.items():
        logger.info(f"  {model}: {metrics}")

    logger.info("Conversion Tracking Results:")
    for key, value in tracking_results.items():
        logger.info(f"  {key}: {value}")

    logger.info("Model Performance Results:")
    for key, value in performance_results.items():
        logger.info(f"  {key}: {value}")

    logger.info("Fraud Detection Results:")
    for key, value in fraud_results.items():
        logger.info(f"  {key}: {value}")

if __name__ == "__main__":
    main()