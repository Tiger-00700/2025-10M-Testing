#!/usr/bin/env python3
"""
电商大数据测试策略 - 电商漏斗验证脚本
E-commerce Big Data Testing Strategy - E-commerce Funnel Validation Script

此脚本用于验证电商平台的用户行为漏斗转化率和数据完整性。
This script validates user behavior funnel conversion rates and data integrity for e-commerce platforms.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EcommerceFunnelChecker:
    def __init__(self, config: Dict):
        self.config = config
        self.funnel_stages = config.get('funnel_stages', ['awareness', 'interest', 'consideration', 'purchase'])
        self.quality_thresholds = config.get('quality_thresholds', {
            'completeness': 0.99,
            'accuracy': 0.95,
            'timeliness': 24  # hours
        })

    def validate_funnel_integrity(self, event_data: pd.DataFrame) -> Dict:
        """
        验证漏斗数据完整性
        Validate funnel data integrity
        """
        results = {}

        # 检查必需事件
        required_events = ['page_view', 'product_view', 'add_to_cart', 'purchase']
        for event in required_events:
            coverage = event_data[event_data['event_type'] == event].shape[0] / len(event_data)
            results[f'{event}_coverage'] = coverage
            results[f'{event}_pass'] = coverage >= self.quality_thresholds['completeness']

        # 验证转化率逻辑
        conversion_rates = self._calculate_conversion_rates(event_data)
        results.update(conversion_rates)

        return results

    def _calculate_conversion_rates(self, data: pd.DataFrame) -> Dict:
        """计算各阶段转化率"""
        rates = {}
        for i in range(len(self.funnel_stages) - 1):
            current_stage = self.funnel_stages[i]
            next_stage = self.funnel_stages[i + 1]

            current_count = data[data['stage'] == current_stage].shape[0]
            next_count = data[data['stage'] == next_stage].shape[0]

            if current_count > 0:
                rate = next_count / current_count
                rates[f'{current_stage}_to_{next_stage}_rate'] = rate
                rates[f'{current_stage}_to_{next_stage}_pass'] = rate >= 0.1  # 示例阈值
            else:
                rates[f'{current_stage}_to_{next_stage}_rate'] = 0
                rates[f'{current_stage}_to_{next_stage}_pass'] = False

        return rates

    def check_data_quality(self, data: pd.DataFrame) -> Dict:
        """检查数据质量指标"""
        quality_results = {}

        # 完整性检查
        null_rates = data.isnull().sum() / len(data)
        quality_results['null_rate_max'] = null_rates.max()
        quality_results['completeness_pass'] = null_rates.max() <= (1 - self.quality_thresholds['completeness'])

        # 准确性检查 - 简单的业务规则验证
        accuracy_checks = self._validate_business_rules(data)
        quality_results.update(accuracy_checks)

        # 时效性检查
        if 'timestamp' in data.columns:
            latest_timestamp = pd.to_datetime(data['timestamp']).max()
            data_freshness = (pd.Timestamp.now() - latest_timestamp).total_seconds() / 3600
            quality_results['data_freshness_hours'] = data_freshness
            quality_results['timeliness_pass'] = data_freshness <= self.quality_thresholds['timeliness']

        return quality_results

    def _validate_business_rules(self, data: pd.DataFrame) -> Dict:
        """验证业务规则"""
        rules = {
            'valid_user_ids': data['user_id'].notna() & (data['user_id'] != ''),
            'valid_product_ids': data['product_id'].notna() & (data['product_id'] != ''),
            'reasonable_prices': (data['price'] >= 0) & (data['price'] <= 10000),  # 示例价格范围
            'valid_timestamps': pd.to_datetime(data['timestamp'], errors='coerce').notna()
        }

        results = {}
        for rule_name, condition in rules.items():
            pass_rate = condition.sum() / len(data)
            results[f'{rule_name}_pass_rate'] = pass_rate
            results[f'{rule_name}_pass'] = pass_rate >= self.quality_thresholds['accuracy']

        return results

def main():
    # 示例配置
    config = {
        'funnel_stages': ['awareness', 'interest', 'consideration', 'purchase'],
        'quality_thresholds': {
            'completeness': 0.99,
            'accuracy': 0.95,
            'timeliness': 24
        }
    }

    checker = EcommerceFunnelChecker(config)

    # 示例数据
    sample_data = pd.DataFrame({
        'user_id': ['user1', 'user2', 'user3'] * 10,
        'event_type': np.random.choice(['page_view', 'product_view', 'add_to_cart', 'purchase'], 30),
        'stage': np.random.choice(['awareness', 'interest', 'consideration', 'purchase'], 30),
        'product_id': ['prod' + str(i) for i in range(30)],
        'price': np.random.uniform(10, 1000, 30),
        'timestamp': pd.date_range('2025-01-01', periods=30, freq='H')
    })

    # 运行验证
    funnel_results = checker.validate_funnel_integrity(sample_data)
    quality_results = checker.check_data_quality(sample_data)

    logger.info("Funnel Validation Results:")
    for key, value in funnel_results.items():
        logger.info(f"  {key}: {value}")

    logger.info("Data Quality Results:")
    for key, value in quality_results.items():
        logger.info(f"  {key}: {value}")

if __name__ == "__main__":
    main()