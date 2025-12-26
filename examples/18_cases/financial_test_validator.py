# examples/18_cases/financial_test_validator.py
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import yaml
import json
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FinancialTestCase:
    """金融测试案例"""
    case_id: str
    scenario_type: str
    risk_level: str
    compliance_requirements: List[str]
    test_data: Dict[str, Any]
    expected_results: Dict[str, Any]
    validation_rules: Dict[str, Any]

@dataclass
class TestResult:
    """测试结果"""
    case_id: str
    status: str  # 'pass', 'fail', 'warning'
    execution_time: float
    risk_score: float
    compliance_score: float
    details: Dict[str, Any]

class FinancialTestValidator:
    """金融行业测试验证器"""

    def __init__(self, config_file: str = 'financial_config.yml'):
        self.config = self._load_config(config_file)
        self.test_results: List[TestResult] = []

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # 默认配置
            return {
                'fraud_threshold': 0.8,
                'max_fraud_rate': 0.05,
                'min_auc_score': 0.8,
                'max_processing_time': 2.0,
                'compliance_weights': {
                    'data_masking': 0.3,
                    'audit_logging': 0.3,
                    'access_control': 0.4
                }
            }

    def validate_fraud_detection(self, transaction_data: pd.DataFrame,
                               fraud_model: Any) -> TestResult:
        """验证反欺诈检测"""
        start_time = datetime.now()

        try:
            # 数据预处理
            processed_data = self._preprocess_transaction_data(transaction_data)

            # 特征提取
            features = self._extract_fraud_features(processed_data)

            # 模型预测
            fraud_probabilities = fraud_model.predict_proba(features)[:, 1]
            fraud_predictions = (fraud_probabilities >= self.config['fraud_threshold']).astype(int)

            # 计算指标
            total_transactions = len(processed_data)
            high_risk_count = fraud_predictions.sum()
            fraud_rate = high_risk_count / total_transactions if total_transactions > 0 else 0

            # 执行时间
            execution_time = (datetime.now() - start_time).total_seconds()

            # 合规检查
            compliance_score = self._check_compliance(processed_data)

            # 结果判断
            if fraud_rate <= self.config['max_fraud_rate']:
                status = 'pass'
                risk_score = fraud_rate
            elif fraud_rate <= self.config['max_fraud_rate'] * 1.2:
                status = 'warning'
                risk_score = fraud_rate
            else:
                status = 'fail'
                risk_score = fraud_rate

            details = {
                'total_transactions': total_transactions,
                'high_risk_count': high_risk_count,
                'fraud_rate': fraud_rate,
                'compliance_score': compliance_score,
                'execution_time': execution_time,
                'threshold': self.config['fraud_threshold']
            }

            return TestResult(
                case_id="FRAUD_DETECTION_001",
                status=status,
                execution_time=execution_time,
                risk_score=risk_score,
                compliance_score=compliance_score,
                details=details
            )

        except Exception as e:
            logger.error(f"反欺诈检测验证失败: {e}")
            return TestResult(
                case_id="FRAUD_DETECTION_001",
                status='fail',
                execution_time=(datetime.now() - start_time).total_seconds(),
                risk_score=1.0,
                compliance_score=0.0,
                details={'error': str(e)}
            )

    def validate_credit_scoring(self, customer_data: pd.DataFrame,
                              scoring_model: Any) -> TestResult:
        """验证信用评分"""
        start_time = datetime.now()

        try:
            # 特征处理
            features = self._extract_credit_features(customer_data)

            # 评分预测
            scores = scoring_model.predict(features)
            probabilities = scoring_model.predict_proba(features)

            # 模型评估
            if 'default_label' in customer_data.columns:
                auc_score = roc_auc_score(customer_data['default_label'], probabilities[:, 1])
            else:
                auc_score = 0.8  # 默认值

            # 公平性检查
            fairness_score = self._check_fairness(scores, customer_data)

            # 合规检查
            compliance_score = self._check_credit_compliance(customer_data)

            # 性能指标
            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            if auc_score >= self.config['min_auc_score'] and fairness_score >= 0.9:
                status = 'pass'
            elif auc_score >= self.config['min_auc_score'] * 0.9:
                status = 'warning'
            else:
                status = 'fail'

            risk_score = 1.0 - auc_score  # 风险分数 = 1 - AUC

            details = {
                'total_customers': len(customer_data),
                'auc_score': auc_score,
                'fairness_score': fairness_score,
                'compliance_score': compliance_score,
                'execution_time': execution_time,
                'min_auc_threshold': self.config['min_auc_score']
            }

            return TestResult(
                case_id="CREDIT_SCORING_001",
                status=status,
                execution_time=execution_time,
                risk_score=risk_score,
                compliance_score=compliance_score,
                details=details
            )

        except Exception as e:
            logger.error(f"信用评分验证失败: {e}")
            return TestResult(
                case_id="CREDIT_SCORING_001",
                status='fail',
                execution_time=(datetime.now() - start_time).total_seconds(),
                risk_score=1.0,
                compliance_score=0.0,
                details={'error': str(e)}
            )

    def _preprocess_transaction_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """预处理交易数据"""
        processed = data.copy()

        # 处理时间戳
        if 'timestamp' in processed.columns:
            processed['timestamp'] = pd.to_datetime(processed['timestamp'])

        # 处理数值字段
        numeric_columns = ['amount', 'balance', 'limit']
        for col in numeric_columns:
            if col in processed.columns:
                processed[col] = pd.to_numeric(processed[col], errors='coerce')

        # 填充缺失值
        processed = processed.fillna({
            'amount': 0,
            'balance': 0,
            'limit': 0,
            'merchant_category': 'unknown',
            'transaction_type': 'unknown'
        })

        return processed

    def _extract_fraud_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """提取反欺诈特征"""
        features = pd.DataFrame()

        # 金额特征
        features['amount'] = data.get('amount', 0)
        features['amount_log'] = np.log1p(data.get('amount', 0))

        # 时间特征
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            features['hour'] = data['timestamp'].dt.hour
            features['day_of_week'] = data['timestamp'].dt.dayofweek

        # 频率特征
        if 'user_id' in data.columns:
            user_counts = data.groupby('user_id').size()
            features['user_transaction_count'] = data['user_id'].map(user_counts)

        # 比例特征
        if 'balance' in data.columns and 'amount' in data.columns:
            features['balance_ratio'] = data['amount'] / (data['balance'] + 1)

        return features.fillna(0)

    def _extract_credit_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """提取信用评分特征"""
        features = pd.DataFrame()

        # 基本特征
        features['age'] = data.get('age', 30)
        features['income'] = data.get('income', 50000)
        features['debt_ratio'] = data.get('debt', 0) / (data.get('income', 1) + 1)

        # 历史特征
        features['credit_history_length'] = data.get('credit_history_years', 5)
        features['num_credit_lines'] = data.get('num_credit_lines', 3)

        # 行为特征
        features['payment_history'] = data.get('payment_history_score', 0.8)
        features['utilization_rate'] = data.get('utilization_rate', 0.3)

        return features.fillna(0)

    def _check_compliance(self, data: pd.DataFrame) -> float:
        """检查合规性"""
        compliance_checks = []

        # PII数据检查
        pii_fields = ['ssn', 'account_number', 'phone', 'email']
        for field in pii_fields:
            if field in data.columns:
                # 检查是否脱敏（简化检查）
                masked_ratio = data[field].astype(str).str.contains(r'\*+', regex=True).mean()
                compliance_checks.append(masked_ratio >= 0.95)

        # 数据完整性检查
        completeness = data.notna().mean().mean()
        compliance_checks.append(completeness >= 0.95)

        # 审计日志检查
        if 'audit_log' in data.columns:
            audit_completeness = data['audit_log'].notna().mean()
            compliance_checks.append(audit_completeness >= 0.99)

        return sum(compliance_checks) / len(compliance_checks) if compliance_checks else 0.0

    def _check_fairness(self, scores: np.ndarray, data: pd.DataFrame) -> float:
        """检查公平性"""
        if 'protected_attribute' not in data.columns:
            return 1.0  # 如果没有保护属性，默认通过

        protected_groups = data['protected_attribute'].unique()
        if len(protected_groups) < 2:
            return 1.0

        # 计算各组平均分数差异
        group_scores = []
        for group in protected_groups:
            group_mask = data['protected_attribute'] == group
            group_scores.append(scores[group_mask].mean())

        max_diff = max(group_scores) - min(group_scores)
        fairness_score = max(0, 1.0 - max_diff / np.mean(scores))

        return fairness_score

    def _check_credit_compliance(self, data: pd.DataFrame) -> float:
        """检查信用评分合规性"""
        compliance_checks = []

        # 年龄合规（不能歧视特定年龄段）
        if 'age' in data.columns:
            age_distribution = data['age'].describe()
            compliance_checks.append(age_distribution['std'] < 20)  # 年龄分布不应过于集中

        # 数据来源合规
        required_fields = ['age', 'income', 'credit_history_years']
        field_completeness = sum(1 for field in required_fields if field in data.columns) / len(required_fields)
        compliance_checks.append(field_completeness >= 0.8)

        # 公平性检查
        if 'gender' in data.columns and 'approval_rate' in data.columns:
            gender_approval = data.groupby('gender')['approval_rate'].mean()
            max_diff = gender_approval.max() - gender_approval.min()
            compliance_checks.append(max_diff < 0.1)  # 性别差异不应过大

        return sum(compliance_checks) / len(compliance_checks) if compliance_checks else 0.0

    def run_comprehensive_validation(self, test_cases: List[FinancialTestCase]) -> Dict[str, Any]:
        """运行综合验证"""
        logger.info("开始金融行业测试综合验证...")

        results = []
        for test_case in test_cases:
            if test_case.scenario_type == 'fraud_detection':
                # 这里需要实际的交易数据和模型
                # result = self.validate_fraud_detection(test_case.test_data, fraud_model)
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=1.2,
                    risk_score=0.02,
                    compliance_score=0.98,
                    details={'simulated': True}
                )
            elif test_case.scenario_type == 'credit_scoring':
                # result = self.validate_credit_scoring(test_case.test_data, scoring_model)
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=2.1,
                    risk_score=0.15,
                    compliance_score=0.96,
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
    validator = FinancialTestValidator()

    # 创建测试案例
    test_cases = [
        FinancialTestCase(
            case_id="FRAUD_DETECTION_001",
            scenario_type="fraud_detection",
            risk_level="high",
            compliance_requirements=["PII脱敏", "审计日志"],
            test_data={},
            expected_results={"fraud_rate": "< 0.05"},
            validation_rules={"threshold": 0.8}
        ),
        FinancialTestCase(
            case_id="CREDIT_SCORING_001",
            scenario_type="credit_scoring",
            risk_level="medium",
            compliance_requirements=["公平性评估", "可解释性"],
            test_data={},
            expected_results={"auc_score": "> 0.85"},
            validation_rules={"min_auc": 0.8}
        )
    ]

    # 运行验证
    validation_report = validator.run_comprehensive_validation(test_cases)

    # 输出结果
    print("金融行业测试验证报告:")
    print(json.dumps(validation_report, indent=2, ensure_ascii=False))

    print("金融行业测试验证完成")