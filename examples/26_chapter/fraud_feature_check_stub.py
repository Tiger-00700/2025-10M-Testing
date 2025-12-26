#!/usr/bin/env python3
"""
金融大数据测试策略 - 欺诈特征检查存根
Finance Big Data Testing Strategy - Fraud Feature Check Stub

此脚本用于金融交易数据的欺诈特征验证和风险评估。
This script validates fraud features and risk assessment for financial transaction data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudFeatureChecker:
    def __init__(self, config: Dict):
        self.config = config
        self.transaction_types = config.get('transaction_types', ['payment', 'transfer', 'investment'])
        self.risk_thresholds = config.get('risk_thresholds', {
            'high_risk_score': 0.8,
            'suspicious_amount_threshold': 10000,
            'unusual_frequency_threshold': 10
        })
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()

    def validate_transaction_integrity(self, transaction_data: pd.DataFrame) -> Dict:
        """
        验证交易数据完整性
        Validate transaction data integrity
        """
        results = {}

        # 检查必需字段
        required_fields = ['transaction_id', 'amount', 'timestamp', 'sender_id', 'receiver_id']
        for field in required_fields:
            completeness = transaction_data[field].notna().sum() / len(transaction_data)
            results[f'{field}_completeness'] = completeness
            results[f'{field}_pass'] = completeness >= 0.99

        # 验证交易类型分布
        type_distribution = transaction_data['transaction_type'].value_counts(normalize=True)
        for tx_type in self.transaction_types:
            if tx_type in type_distribution:
                results[f'{tx_type}_proportion'] = type_distribution[tx_type]
            else:
                results[f'{tx_type}_proportion'] = 0

        return results

    def detect_fraud_patterns(self, data: pd.DataFrame) -> Dict:
        """
        检测欺诈模式
        Detect fraud patterns
        """
        fraud_results = {}

        # 异常金额检测
        amount_anomalies = self._detect_amount_anomalies(data)
        fraud_results.update(amount_anomalies)

        # 频率异常检测
        frequency_anomalies = self._detect_frequency_anomalies(data)
        fraud_results.update(frequency_anomalies)

        # 模式识别
        pattern_anomalies = self._detect_pattern_anomalies(data)
        fraud_results.update(pattern_anomalies)

        return fraud_results

    def _detect_amount_anomalies(self, data: pd.DataFrame) -> Dict:
        """检测异常金额"""
        results = {}

        # 统计金额分布
        amounts = data['amount']
        mean_amount = amounts.mean()
        std_amount = amounts.std()

        # 识别异常值 (3-sigma rule)
        upper_threshold = mean_amount + 3 * std_amount
        anomalies = amounts > upper_threshold
        anomaly_rate = anomalies.sum() / len(amounts)

        results['amount_anomaly_rate'] = anomaly_rate
        results['amount_anomaly_pass'] = anomaly_rate <= 0.05  # 5% threshold

        # 高风险金额检查
        high_risk_count = (amounts > self.risk_thresholds['suspicious_amount_threshold']).sum()
        results['high_risk_amount_count'] = high_risk_count
        results['high_risk_amount_rate'] = high_risk_count / len(amounts)

        return results

    def _detect_frequency_anomalies(self, data: pd.DataFrame) -> Dict:
        """检测频率异常"""
        results = {}

        # 按用户分组计算交易频率
        if 'user_id' in data.columns:
            user_freq = data.groupby('user_id').size()
            unusual_freq_users = (user_freq > self.risk_thresholds['unusual_frequency_threshold']).sum()
            results['unusual_frequency_users'] = unusual_freq_users
            results['unusual_frequency_rate'] = unusual_freq_users / data['user_id'].nunique()

        return results

    def _detect_pattern_anomalies(self, data: pd.DataFrame) -> Dict:
        """使用机器学习检测模式异常"""
        results = {}

        # 准备特征
        features = self._extract_features(data)

        if len(features) > 0:
            # 标准化特征
            scaled_features = self.scaler.fit_transform(features)

            # 训练隔离森林模型
            self.model.fit(scaled_features)

            # 预测异常分数
            anomaly_scores = self.model.decision_function(scaled_features)
            predictions = self.model.predict(scaled_features)

            # 计算异常比例
            anomaly_rate = (predictions == -1).sum() / len(predictions)
            results['ml_anomaly_rate'] = anomaly_rate
            results['ml_anomaly_pass'] = anomaly_rate <= 0.1  # 10% threshold

            # 高风险分数比例
            high_risk_scores = (anomaly_scores < self.risk_thresholds['high_risk_score']).sum() / len(anomaly_scores)
            results['high_risk_score_rate'] = high_risk_scores

        return results

    def _extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """提取用于异常检测的特征"""
        features = pd.DataFrame()

        if 'amount' in data.columns:
            features['amount'] = data['amount']
            features['amount_log'] = np.log1p(data['amount'])

        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            features['hour_of_day'] = data['timestamp'].dt.hour
            features['day_of_week'] = data['timestamp'].dt.dayofweek

        # 添加更多特征...
        return features

    def assess_compliance(self, data: pd.DataFrame) -> Dict:
        """评估合规性"""
        compliance_results = {}

        # 示例合规检查
        compliance_checks = {
            'data_retention': self._check_data_retention(data),
            'audit_trail': self._check_audit_trail(data),
            'privacy_compliance': self._check_privacy_compliance(data)
        }

        compliance_results.update(compliance_checks)
        return compliance_results

    def _check_data_retention(self, data: pd.DataFrame) -> bool:
        """检查数据保留期"""
        if 'timestamp' in data.columns:
            oldest_record = pd.to_datetime(data['timestamp']).min()
            retention_days = (pd.Timestamp.now() - oldest_record).days
            return retention_days <= 2555  # 示例保留期
        return False

    def _check_audit_trail(self, data: pd.DataFrame) -> bool:
        """检查审计线索"""
        required_audit_fields = ['transaction_id', 'timestamp', 'user_id', 'action']
        return all(field in data.columns for field in required_audit_fields)

    def _check_privacy_compliance(self, data: pd.DataFrame) -> bool:
        """检查隐私合规"""
        sensitive_fields = ['ssn', 'account_number', 'personal_info']
        has_sensitive = any(field in data.columns for field in sensitive_fields)
        if has_sensitive:
            # 检查是否加密或脱敏
            return 'encrypted' in data.columns or 'masked' in data.columns
        return True

def main():
    # 示例配置
    config = {
        'transaction_types': ['payment', 'transfer', 'investment'],
        'risk_thresholds': {
            'high_risk_score': 0.8,
            'suspicious_amount_threshold': 10000,
            'unusual_frequency_threshold': 10
        }
    }

    checker = FraudFeatureChecker(config)

    # 示例数据
    sample_data = pd.DataFrame({
        'transaction_id': ['tx' + str(i) for i in range(100)],
        'amount': np.random.exponential(1000, 100),
        'timestamp': pd.date_range('2025-01-01', periods=100, freq='H'),
        'sender_id': ['user' + str(np.random.randint(1, 20)) for _ in range(100)],
        'receiver_id': ['user' + str(np.random.randint(1, 20)) for _ in range(100)],
        'transaction_type': np.random.choice(['payment', 'transfer', 'investment'], 100),
        'user_id': ['user' + str(np.random.randint(1, 20)) for _ in range(100)]
    })

    # 运行验证
    integrity_results = checker.validate_transaction_integrity(sample_data)
    fraud_results = checker.detect_fraud_patterns(sample_data)
    compliance_results = checker.assess_compliance(sample_data)

    logger.info("Transaction Integrity Results:")
    for key, value in integrity_results.items():
        logger.info(f"  {key}: {value}")

    logger.info("Fraud Detection Results:")
    for key, value in fraud_results.items():
        logger.info(f"  {key}: {value}")

    logger.info("Compliance Assessment Results:")
    for key, value in compliance_results.items():
        logger.info(f"  {key}: {value}")

if __name__ == "__main__":
    main()