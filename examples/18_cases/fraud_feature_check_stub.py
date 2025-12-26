# examples/18_cases/fraud_feature_check_stub.py
"""
金融行业欺诈检测特征验证存根
用于验证反欺诈模型的特征工程和数据质量
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import yaml
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FraudFeatureCheck:
    """欺诈特征检查结果"""
    feature_name: str
    check_type: str
    status: str  # 'pass', 'fail', 'warning'
    score: float
    details: Dict[str, Any]

class FraudFeatureValidator:
    """欺诈特征验证器"""

    def __init__(self, config_file: str = 'fraud_feature_config.yml'):
        self.config = self._load_config(config_file)
        self.check_results: List[FraudFeatureCheck] = []

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {
                'required_features': [
                    'amount', 'amount_log', 'hour', 'day_of_week',
                    'user_transaction_count', 'balance_ratio'
                ],
                'feature_quality_thresholds': {
                    'completeness': 0.95,
                    'consistency': 0.98,
                    'accuracy': 0.99
                }
            }

    def validate_feature_completeness(self, data: pd.DataFrame) -> List[FraudFeatureCheck]:
        """验证特征完整性"""
        results = []

        for feature in self.config['required_features']:
            if feature in data.columns:
                completeness = data[feature].notna().mean()
                threshold = self.config['feature_quality_thresholds']['completeness']

                if completeness >= threshold:
                    status = 'pass'
                    score = completeness
                elif completeness >= threshold * 0.9:
                    status = 'warning'
                    score = completeness
                else:
                    status = 'fail'
                    score = completeness

                results.append(FraudFeatureCheck(
                    feature_name=feature,
                    check_type='completeness',
                    status=status,
                    score=score,
                    details={
                        'completeness_ratio': completeness,
                        'threshold': threshold,
                        'missing_count': data[feature].isna().sum()
                    }
                ))
            else:
                results.append(FraudFeatureCheck(
                    feature_name=feature,
                    check_type='completeness',
                    status='fail',
                    score=0.0,
                    details={'error': 'feature_not_found'}
                ))

        return results

    def validate_feature_consistency(self, data: pd.DataFrame) -> List[FraudFeatureCheck]:
        """验证特征一致性"""
        results = []

        # 检查数值范围合理性
        if 'amount' in data.columns:
            amount_data = data['amount'].dropna()
            if len(amount_data) > 0:
                # 检查负值比例
                negative_ratio = (amount_data < 0).mean()
                if negative_ratio > 0.01:  # 允许1%的负值
                    results.append(FraudFeatureCheck(
                        feature_name='amount',
                        check_type='consistency',
                        status='warning',
                        score=1 - negative_ratio,
                        details={'negative_ratio': negative_ratio}
                    ))

                # 检查异常值
                q1, q3 = amount_data.quantile([0.25, 0.75])
                iqr = q3 - q1
                outliers = ((amount_data < (q1 - 1.5 * iqr)) | (amount_data > (q3 + 1.5 * iqr))).sum()
                outlier_ratio = outliers / len(amount_data)

                results.append(FraudFeatureCheck(
                    feature_name='amount',
                    check_type='consistency',
                    status='pass' if outlier_ratio < 0.05 else 'warning',
                    score=1 - outlier_ratio,
                    details={'outlier_ratio': outlier_ratio}
                ))

        # 检查时间特征一致性
        if 'hour' in data.columns:
            hour_data = data['hour'].dropna()
            valid_hours = ((hour_data >= 0) & (hour_data <= 23)).mean()

            results.append(FraudFeatureCheck(
                feature_name='hour',
                check_type='consistency',
                status='pass' if valid_hours >= 0.99 else 'fail',
                score=valid_hours,
                details={'valid_hour_ratio': valid_hours}
            ))

        return results

    def validate_feature_accuracy(self, data: pd.DataFrame,
                                reference_data: Optional[pd.DataFrame] = None) -> List[FraudFeatureCheck]:
        """验证特征准确性"""
        results = []

        # 如果有参考数据，进行交叉验证
        if reference_data is not None:
            for feature in self.config['required_features']:
                if feature in data.columns and feature in reference_data.columns:
                    # 计算相关性
                    correlation = data[feature].corr(reference_data[feature])
                    if not pd.isna(correlation):
                        results.append(FraudFeatureCheck(
                            feature_name=feature,
                            check_type='accuracy',
                            status='pass' if correlation >= 0.8 else 'warning',
                            score=max(0, correlation),
                            details={'correlation': correlation}
                        ))

        # 检查业务规则一致性
        if 'amount_log' in data.columns and 'amount' in data.columns:
            # amount_log 应该是 log(1 + amount)
            expected_log = np.log1p(data['amount'])
            actual_log = data['amount_log']
            diff = np.abs(expected_log - actual_log)
            accuracy = (diff < 0.01).mean()  # 允许小误差

            results.append(FraudFeatureCheck(
                feature_name='amount_log',
                check_type='accuracy',
                status='pass' if accuracy >= 0.99 else 'fail',
                score=accuracy,
                details={'accuracy_ratio': accuracy}
            ))

        return results

    def run_comprehensive_check(self, data: pd.DataFrame,
                              reference_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """运行综合特征检查"""
        logger.info("开始欺诈特征综合检查...")

        # 执行各项检查
        completeness_results = self.validate_feature_completeness(data)
        consistency_results = self.validate_feature_consistency(data)
        accuracy_results = self.validate_feature_accuracy(data, reference_data)

        all_results = completeness_results + consistency_results + accuracy_results
        self.check_results.extend(all_results)

        # 生成汇总报告
        summary = {
            'total_checks': len(all_results),
            'passed_checks': sum(1 for r in all_results if r.status == 'pass'),
            'warning_checks': sum(1 for r in all_results if r.status == 'warning'),
            'failed_checks': sum(1 for r in all_results if r.status == 'fail'),
            'overall_score': sum(r.score for r in all_results) / len(all_results) if all_results else 0.0
        }

        # 按特征分组的结果
        feature_results = {}
        for result in all_results:
            if result.feature_name not in feature_results:
                feature_results[result.feature_name] = []
            feature_results[result.feature_name].append({
                'check_type': result.check_type,
                'status': result.status,
                'score': result.score,
                'details': result.details
            })

        return {
            'summary': summary,
            'feature_results': feature_results,
            'detailed_results': [{
                'feature_name': r.feature_name,
                'check_type': r.check_type,
                'status': r.status,
                'score': r.score,
                'details': r.details
            } for r in all_results]
        }

# 使用示例
if __name__ == "__main__":
    validator = FraudFeatureValidator()

    # 创建模拟数据
    np.random.seed(42)
    n_samples = 1000

    data = pd.DataFrame({
        'amount': np.random.exponential(100, n_samples),
        'amount_log': np.log1p(np.random.exponential(100, n_samples)),
        'hour': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'user_transaction_count': np.random.poisson(5, n_samples),
        'balance_ratio': np.random.beta(2, 5, n_samples)
    })

    # 添加一些缺失值和异常值进行测试
    data.loc[np.random.choice(n_samples, 20), 'amount'] = np.nan
    data.loc[np.random.choice(n_samples, 10), 'hour'] = 25  # 无效小时

    # 运行检查
    check_report = validator.run_comprehensive_check(data)

    print("欺诈特征检查报告:")
    print(json.dumps(check_report['summary'], indent=2, ensure_ascii=False))

    print("\n各特征检查结果:")
    for feature, results in check_report['feature_results'].items():
        print(f"\n{feature}:")
        for result in results:
            print(f"  {result['check_type']}: {result['status']} (score: {result['score']:.3f})")

    print("\n欺诈特征检查完成")