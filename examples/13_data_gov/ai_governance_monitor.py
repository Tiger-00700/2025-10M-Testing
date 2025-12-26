# AI增强的数据治理监控系统
# 对应锚点13-005: AI治理配置模板

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime, timedelta
import json

class SensitiveDataClassifier:
    """AI驱动的敏感数据分类器"""

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.confidence_threshold = 0.85

    def train(self, training_data: List[Dict[str, Any]]):
        """训练分类模型"""
        # 简化实现 - 实际应使用BERT或其他NLP模型
        print("🤖 训练敏感数据分类模型...")

        # 模拟训练过程
        self.model = "bert_sensitive_data_classifier"
        print("✅ 模型训练完成")

    def predict(self, data_access_log: Dict[str, Any]) -> Dict[str, float]:
        """预测数据敏感度"""
        # 简化预测逻辑
        predictions = {}

        # 基于字段名和访问模式的启发式分类
        field_name = data_access_log.get('field_name', '').lower()
        access_pattern = data_access_log.get('access_pattern', '')

        if 'email' in field_name:
            predictions['email'] = 0.95
        elif 'phone' in field_name:
            predictions['phone'] = 0.90
        elif 'ssn' in field_name or 'social' in field_name:
            predictions['ssn'] = 0.98
        elif 'credit' in field_name:
            predictions['credit_card'] = 0.96
        elif 'address' in field_name:
            predictions['address'] = 0.85
        else:
            predictions['normal'] = 0.20

        return predictions

class DataUsageAnomalyDetector:
    """数据使用异常检测器"""

    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def train(self, historical_data: pd.DataFrame):
        """训练异常检测模型"""
        print("🔍 训练数据使用异常检测模型...")

        # 特征工程
        features = self._extract_features(historical_data)

        # 标准化
        scaled_features = self.scaler.fit_transform(features)

        # 训练模型
        self.model.fit(scaled_features)
        self.is_trained = True

        print("✅ 异常检测模型训练完成")

    def score(self, data_access_log: Dict[str, Any]) -> float:
        """计算异常分数"""
        if not self.is_trained:
            return 0.0

        # 提取特征
        features = self._extract_single_features(data_access_log)

        # 标准化
        scaled_features = self.scaler.transform([features])

        # 预测异常分数
        anomaly_score = self.model.decision_function(scaled_features)[0]

        # 转换为0-1范围的分数
        normalized_score = (anomaly_score + 1) / 2

        return normalized_score

    def _extract_features(self, data: pd.DataFrame) -> np.ndarray:
        """从历史数据提取特征"""
        features = []

        for _, row in data.iterrows():
            feature_vector = self._extract_single_features(row.to_dict())
            features.append(feature_vector)

        return np.array(features)

    def _extract_single_features(self, log_entry: Dict[str, Any]) -> List[float]:
        """从单个日志条目提取特征"""
        features = []

        # 时间特征
        timestamp = log_entry.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

        features.extend([
            timestamp.hour,  # 访问小时
            timestamp.weekday(),  # 星期几
            1 if timestamp.hour < 6 or timestamp.hour > 22 else 0,  # 非工作时间
        ])

        # 访问模式特征
        access_type = log_entry.get('access_type', 'read')
        features.extend([
            1 if access_type == 'write' else 0,
            1 if access_type == 'delete' else 0,
            1 if access_type == 'bulk_export' else 0,
        ])

        # 数据量特征
        data_volume = log_entry.get('data_volume', 0)
        features.extend([
            np.log1p(data_volume),  # 对数变换
            1 if data_volume > 10000 else 0,  # 大数据量访问
        ])

        # 用户特征
        user_role = log_entry.get('user_role', 'user')
        features.extend([
            1 if user_role == 'admin' else 0,
            1 if user_role == 'developer' else 0,
            1 if user_role == 'analyst' else 0,
        ])

        # 频率特征
        access_frequency = log_entry.get('access_frequency', 1)
        features.extend([
            np.log1p(access_frequency),
            1 if access_frequency > 10 else 0,  # 高频访问
        ])

        return features

class AIGovernanceMonitor:
    """AI增强的数据治理监控系统"""

    def __init__(self):
        self.classifier = SensitiveDataClassifier()
        self.anomaly_detector = DataUsageAnomalyDetector()
        self.logger = logging.getLogger(__name__)

        # 配置参数
        self.config = {
            'intelligent_classification': {
                'model': 'bert_sensitive_data_classifier',
                'confidence_threshold': 0.85
            },
            'anomaly_detection': {
                'algorithm': 'isolation_forest',
                'sensitivity': 'medium',
                'alert_threshold': 0.95
            },
            'predictive_monitoring': {
                'forecast_window': '7_days',
                'risk_indicators': ['data_volume_spike', 'unusual_access_pattern']
            }
        }

    def initialize_models(self):
        """初始化AI模型"""
        print("🚀 初始化AI治理监控系统...")

        # 训练分类器（使用模拟数据）
        training_samples = self._generate_training_samples()
        self.classifier.train(training_samples)

        # 训练异常检测器（使用模拟历史数据）
        historical_logs = self._generate_historical_logs()
        self.anomaly_detector.train(historical_logs)

        print("✅ AI模型初始化完成")

    def intelligent_governance_check(self, data_access_log: Dict[str, Any]) -> Dict[str, Any]:
        """AI增强的治理检查"""
        print("🧠 执行AI增强治理检查...")

        results = {
            'timestamp': datetime.now().isoformat(),
            'input_log': data_access_log,
            'checks': {}
        }

        # 1. 智能分类检查
        classification_results = self._perform_classification_check(data_access_log)
        results['checks']['classification'] = classification_results

        # 2. 异常检测
        anomaly_results = self._perform_anomaly_check(data_access_log)
        results['checks']['anomaly'] = anomaly_results

        # 3. 风险评估
        risk_assessment = self._assess_risk(classification_results, anomaly_results)
        results['risk_assessment'] = risk_assessment

        # 4. 生成治理行动
        governance_actions = self._generate_governance_actions(risk_assessment)
        results['governance_actions'] = governance_actions

        print("✅ AI治理检查完成")
        return results

    def _perform_classification_check(self, data_access_log: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能分类检查"""
        predictions = self.classifier.predict(data_access_log)

        # 确定最高置信度的分类
        max_confidence = max(predictions.values())
        predicted_class = max(predictions.keys(), key=predictions.get)

        results = {
            'predictions': predictions,
            'predicted_class': predicted_class,
            'max_confidence': max_confidence,
            'above_threshold': max_confidence >= self.config['intelligent_classification']['confidence_threshold']
        }

        return results

    def _perform_anomaly_check(self, data_access_log: Dict[str, Any]) -> Dict[str, Any]:
        """执行异常检测"""
        anomaly_score = self.anomaly_detector.score(data_access_log)

        results = {
            'anomaly_score': anomaly_score,
            'is_anomaly': anomaly_score >= self.config['anomaly_detection']['alert_threshold'],
            'severity': self._calculate_severity(anomaly_score)
        }

        return results

    def _calculate_severity(self, anomaly_score: float) -> str:
        """计算异常严重程度"""
        if anomaly_score >= 0.95:
            return 'critical'
        elif anomaly_score >= 0.85:
            return 'high'
        elif anomaly_score >= 0.75:
            return 'medium'
        else:
            return 'low'

    def _assess_risk(self, classification_results: Dict[str, Any],
                    anomaly_results: Dict[str, Any]) -> Dict[str, Any]:
        """评估综合风险"""
        risk_score = 0.0
        risk_factors = []

        # 基于分类结果的风险
        if classification_results['above_threshold']:
            predicted_class = classification_results['predicted_class']
            if predicted_class in ['ssn', 'credit_card']:
                risk_score += 0.8
                risk_factors.append(f"高敏感数据类型: {predicted_class}")
            elif predicted_class in ['email', 'phone', 'address']:
                risk_score += 0.5
                risk_factors.append(f"中敏感数据类型: {predicted_class}")

        # 基于异常检测的风险
        if anomaly_results['is_anomaly']:
            severity = anomaly_results['severity']
            if severity == 'critical':
                risk_score += 0.9
                risk_factors.append("严重异常访问模式")
            elif severity == 'high':
                risk_score += 0.7
                risk_factors.append("高风险异常访问")
            elif severity == 'medium':
                risk_score += 0.4
                risk_factors.append("中等风险异常访问")

        # 确定风险等级
        if risk_score >= 1.0:
            risk_level = 'critical'
        elif risk_score >= 0.7:
            risk_level = 'high'
        elif risk_score >= 0.4:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'risk_score': min(risk_score, 1.0),
            'risk_level': risk_level,
            'risk_factors': risk_factors
        }

    def _generate_governance_actions(self, risk_assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成治理行动建议"""
        actions = []

        risk_level = risk_assessment['risk_level']

        if risk_level == 'critical':
            actions.extend([
                {
                    'action': 'immediate_block',
                    'description': '立即阻止数据访问',
                    'priority': 'urgent',
                    'automated': True
                },
                {
                    'action': 'security_alert',
                    'description': '触发安全警报',
                    'priority': 'urgent',
                    'automated': True
                },
                {
                    'action': 'manual_review',
                    'description': '人工安全审查',
                    'priority': 'high',
                    'automated': False
                }
            ])
        elif risk_level == 'high':
            actions.extend([
                {
                    'action': 'enhanced_monitoring',
                    'description': '增强监控模式',
                    'priority': 'high',
                    'automated': True
                },
                {
                    'action': 'access_logging',
                    'description': '详细访问日志记录',
                    'priority': 'high',
                    'automated': True
                }
            ])
        elif risk_level == 'medium':
            actions.extend([
                {
                    'action': 'additional_verification',
                    'description': '增加身份验证',
                    'priority': 'medium',
                    'automated': True
                }
            ])

        return actions

    def _generate_training_samples(self) -> List[Dict[str, Any]]:
        """生成训练样本数据"""
        return [
            {'field_name': 'user_email', 'is_sensitive': True},
            {'field_name': 'user_phone', 'is_sensitive': True},
            {'field_name': 'user_name', 'is_sensitive': False},
            {'field_name': 'order_id', 'is_sensitive': False},
        ]

    def _generate_historical_logs(self) -> pd.DataFrame:
        """生成历史日志数据"""
        # 生成30天的模拟数据
        dates = pd.date_range(start='2024-12-01', end='2024-12-24', freq='H')

        logs = []
        for timestamp in dates:
            log_entry = {
                'timestamp': timestamp,
                'access_type': np.random.choice(['read', 'write', 'delete'], p=[0.7, 0.2, 0.1]),
                'data_volume': np.random.exponential(1000),
                'user_role': np.random.choice(['user', 'admin', 'developer'], p=[0.8, 0.1, 0.1]),
                'access_frequency': np.random.poisson(5)
            }
            logs.append(log_entry)

        return pd.DataFrame(logs)

# 演示函数
def demo_ai_governance():
    """AI治理监控演示"""
    print("🤖 AI增强数据治理监控演示")
    print("=" * 50)

    # 创建监控系统
    monitor = AIGovernanceMonitor()

    # 初始化模型
    monitor.initialize_models()

    # 测试数据访问日志
    test_logs = [
        {
            'timestamp': '2025-12-24T14:30:00Z',
            'field_name': 'user_email',
            'access_type': 'read',
            'data_volume': 5000,
            'user_role': 'developer',
            'access_frequency': 15
        },
        {
            'timestamp': '2025-12-24T02:15:00Z',
            'field_name': 'user_ssn',
            'access_type': 'bulk_export',
            'data_volume': 50000,
            'user_role': 'admin',
            'access_frequency': 1
        }
    ]

    for i, log in enumerate(test_logs, 1):
        print(f"\n🔍 测试案例 {i}:")
        print(f"   字段: {log['field_name']}")
        print(f"   访问类型: {log['access_type']}")
        print(f"   数据量: {log['data_volume']}")
        print(f"   用户角色: {log['user_role']}")

        # 执行AI治理检查
        results = monitor.intelligent_governance_check(log)

        # 显示结果
        risk = results['risk_assessment']
        actions = results['governance_actions']

        print(f"   风险等级: {risk['risk_level']} (分数: {risk['risk_score']:.2f})")
        if risk['risk_factors']:
            print(f"   风险因素: {', '.join(risk['risk_factors'])}")

        if actions:
            print(f"   建议行动: {len(actions)} 项")
            for action in actions[:2]:  # 显示前两项
                print(f"     - {action['description']} ({action['priority']})")

    print("\n🎉 AI治理监控演示完成！")

if __name__ == "__main__":
    demo_ai_governance()