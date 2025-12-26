# examples/18_cases/internet_test_validator.py
"""
互联网行业大数据测试验证器
验证用户行为分析、推荐系统、广告投放等互联网业务场景
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import yaml
import json
from sklearn.metrics import precision_score, recall_score, f1_score
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InternetTestCase:
    """互联网测试案例"""
    case_id: str
    scenario_type: str
    business_impact: str
    key_metrics: List[str]
    test_data: Dict[str, Any]
    expected_results: Dict[str, Any]
    validation_rules: Dict[str, Any]

@dataclass
class TestResult:
    """测试结果"""
    case_id: str
    status: str  # 'pass', 'fail', 'warning'
    execution_time: float
    quality_score: float
    business_score: float
    details: Dict[str, Any]

class InternetTestValidator:
    """互联网行业测试验证器"""

    def __init__(self, config_file: str = 'internet_config.yml'):
        self.config = self._load_config(config_file)
        self.test_results: List[TestResult] = []

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {
                'expected_funnel_rates': {
                    'browse_to_cart': 0.15,
                    'cart_to_purchase': 0.7,
                    'purchase_to_repeat': 0.25
                },
                'min_recommendation_precision': 0.15,
                'min_click_through_rate': 0.08,
                'max_ad_fraud_rate': 0.05
            }

    def validate_ecommerce_funnel(self, user_events: pd.DataFrame,
                                session_data: pd.DataFrame) -> TestResult:
        """验证电商转化漏斗"""
        start_time = datetime.now()

        try:
            # 计算漏斗转化率
            funnel_rates = self._calculate_funnel_conversion(user_events)

            # 行为序列分析
            behavior_patterns = self._analyze_behavior_sequences(session_data)

            # 质量评估
            quality_score = self._assess_funnel_quality(funnel_rates)

            # 业务影响评估
            business_score = self._evaluate_business_impact(funnel_rates)

            # 性能指标
            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            expected_rates = self.config['expected_funnel_rates']
            if all(funnel_rates.get(step, 0) >= expected_rates.get(step, 0) for step in expected_rates):
                status = 'pass'
            elif sum(funnel_rates.get(step, 0) >= expected_rates.get(step, 0) * 0.8 for step in expected_rates) >= len(expected_rates) * 0.7:
                status = 'warning'
            else:
                status = 'fail'

            details = {
                'funnel_rates': funnel_rates,
                'behavior_patterns_count': len(behavior_patterns),
                'quality_score': quality_score,
                'business_score': business_score,
                'execution_time': execution_time,
                'expected_rates': expected_rates
            }

            return TestResult(
                case_id="ECOMMERCE_FUNNEL_001",
                status=status,
                execution_time=execution_time,
                quality_score=quality_score,
                business_score=business_score,
                details=details
            )

        except Exception as e:
            logger.error(f"电商漏斗验证失败: {e}")
            return TestResult(
                case_id="ECOMMERCE_FUNNEL_001",
                status='fail',
                execution_time=(datetime.now() - start_time).total_seconds(),
                quality_score=0.0,
                business_score=0.0,
                details={'error': str(e)}
            )

    def validate_recommendation_system(self, interactions: pd.DataFrame,
                                     recommendations: pd.DataFrame) -> TestResult:
        """验证推荐系统"""
        start_time = datetime.now()

        try:
            # 计算推荐准确性指标
            precision, recall, f1 = self._calculate_recommendation_metrics(interactions, recommendations)

            # 多样性分析
            diversity_score = self._calculate_diversity_score(recommendations)

            # 新颖性分析
            novelty_score = self._calculate_novelty_score(recommendations, interactions)

            # A/B测试分析（如果有实验数据）
            ab_test_result = self._analyze_ab_test(recommendations)

            # 综合质量评分
            quality_score = (precision * 0.4 + recall * 0.3 + diversity_score * 0.15 + novelty_score * 0.15)

            # 业务影响评估
            business_score = self._evaluate_recommendation_business_impact(precision, recall)

            # 性能指标
            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            min_precision = self.config['min_recommendation_precision']
            if precision >= min_precision and quality_score >= 0.7:
                status = 'pass'
            elif precision >= min_precision * 0.8:
                status = 'warning'
            else:
                status = 'fail'

            details = {
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'diversity_score': diversity_score,
                'novelty_score': novelty_score,
                'ab_test_result': ab_test_result,
                'quality_score': quality_score,
                'business_score': business_score,
                'execution_time': execution_time,
                'min_precision_threshold': min_precision
            }

            return TestResult(
                case_id="RECOMMENDATION_SYSTEM_001",
                status=status,
                execution_time=execution_time,
                quality_score=quality_score,
                business_score=business_score,
                details=details
            )

        except Exception as e:
            logger.error(f"推荐系统验证失败: {e}")
            return TestResult(
                case_id="RECOMMENDATION_SYSTEM_001",
                status='fail',
                execution_time=(datetime.now() - start_time).total_seconds(),
                quality_score=0.0,
                business_score=0.0,
                details={'error': str(e)}
            )

    def validate_advertising_system(self, ad_impressions: pd.DataFrame,
                                  ad_clicks: pd.DataFrame) -> TestResult:
        """验证广告投放系统"""
        start_time = datetime.now()

        try:
            # 计算广告效果指标
            ctr, cpc, cpm = self._calculate_ad_metrics(ad_impressions, ad_clicks)

            # 欺诈检测
            fraud_rate = self._detect_ad_fraud(ad_impressions, ad_clicks)

            # 投放质量评估
            quality_score = self._assess_ad_quality(ad_impressions)

            # 业务价值评估
            business_score = self._evaluate_ad_business_value(ctr, cpc, fraud_rate)

            # 性能指标
            execution_time = (datetime.now() - start_time).total_seconds()

            # 结果判断
            min_ctr = self.config['min_click_through_rate']
            max_fraud = self.config['max_ad_fraud_rate']

            if ctr >= min_ctr and fraud_rate <= max_fraud and quality_score >= 0.8:
                status = 'pass'
            elif ctr >= min_ctr * 0.8 or fraud_rate <= max_fraud * 1.2:
                status = 'warning'
            else:
                status = 'fail'

            details = {
                'ctr': ctr,
                'cpc': cpc,
                'cpm': cpm,
                'fraud_rate': fraud_rate,
                'quality_score': quality_score,
                'business_score': business_score,
                'execution_time': execution_time,
                'min_ctr_threshold': min_ctr,
                'max_fraud_threshold': max_fraud
            }

            return TestResult(
                case_id="ADVERTISING_SYSTEM_001",
                status=status,
                execution_time=execution_time,
                quality_score=quality_score,
                business_score=business_score,
                details=details
            )

        except Exception as e:
            logger.error(f"广告系统验证失败: {e}")
            return TestResult(
                case_id="ADVERTISING_SYSTEM_001",
                status='fail',
                execution_time=(datetime.now() - start_time).total_seconds(),
                quality_score=0.0,
                business_score=0.0,
                details={'error': str(e)}
            )

    def _calculate_funnel_conversion(self, events: pd.DataFrame) -> Dict[str, float]:
        """计算漏斗转化率"""
        funnel_steps = ['browse', 'view_product', 'add_to_cart', 'checkout', 'purchase']
        funnel_counts = {}

        for step in funnel_steps:
            if step in events.columns:
                funnel_counts[step] = events[step].sum()
            else:
                funnel_counts[step] = 0

        # 计算转化率
        conversion_rates = {}
        previous_count = funnel_counts.get('browse', 0)

        for i, step in enumerate(funnel_steps[1:], 1):
            current_count = funnel_counts.get(step, 0)
            if previous_count > 0:
                conversion_rates[f"{funnel_steps[i-1]}_to_{step}"] = current_count / previous_count
            else:
                conversion_rates[f"{funnel_steps[i-1]}_to_{step}"] = 0.0
            previous_count = current_count

        return conversion_rates

    def _analyze_behavior_sequences(self, session_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """分析行为序列模式"""
        patterns = []

        if 'user_id' in session_data.columns and 'event_sequence' in session_data.columns:
            # 简单的序列模式识别
            for user_id, group in session_data.groupby('user_id'):
                sequence = group['event_sequence'].tolist()
                if len(sequence) > 2:
                    # 识别常见模式
                    if 'view_product' in sequence and 'add_to_cart' in sequence:
                        patterns.append({
                            'user_id': user_id,
                            'pattern': 'browse_to_cart',
                            'confidence': 0.8
                        })
                    if 'add_to_cart' in sequence and 'purchase' in sequence:
                        patterns.append({
                            'user_id': user_id,
                            'pattern': 'cart_to_purchase',
                            'confidence': 0.9
                        })

        return patterns

    def _calculate_recommendation_metrics(self, interactions: pd.DataFrame,
                                        recommendations: pd.DataFrame) -> Tuple[float, float, float]:
        """计算推荐系统指标"""
        # 简化的准确性计算
        if 'user_id' in interactions.columns and 'item_id' in interactions.columns:
            if 'rating' in interactions.columns:
                # 有评分数据的情况
                actual_items = set(interactions[interactions['rating'] >= 4]['item_id'])
            else:
                # 无评分数据的情况
                actual_items = set(interactions['item_id'])

            if 'recommended_items' in recommendations.columns:
                recommended_items = set()
                for rec_list in recommendations['recommended_items']:
                    if isinstance(rec_list, list):
                        recommended_items.update(rec_list)

                # 计算精确率和召回率
                true_positives = len(actual_items.intersection(recommended_items))
                predicted_positives = len(recommended_items)
                actual_positives = len(actual_items)

                precision = true_positives / predicted_positives if predicted_positives > 0 else 0.0
                recall = true_positives / actual_positives if actual_positives > 0 else 0.0
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

                return precision, recall, f1

        # 默认返回值
        return 0.1, 0.05, 0.07

    def _calculate_diversity_score(self, recommendations: pd.DataFrame) -> float:
        """计算推荐多样性"""
        if 'recommended_items' in recommendations.columns:
            all_items = set()
            for rec_list in recommendations['recommended_items']:
                if isinstance(rec_list, list):
                    all_items.update(rec_list)

            # 简化的多样性计算：基于类别分布
            if len(all_items) > 0:
                # 假设物品有类别信息，这里简化处理
                diversity = min(1.0, len(all_items) / 100)  # 归一化到0-1
                return diversity

        return 0.5

    def _calculate_novelty_score(self, recommendations: pd.DataFrame,
                               interactions: pd.DataFrame) -> float:
        """计算推荐新颖性"""
        if 'recommended_items' in recommendations.columns and 'user_id' in recommendations.columns:
            novelty_scores = []

            for _, row in recommendations.iterrows():
                user_id = row['user_id']
                rec_items = row.get('recommended_items', [])

                # 获取用户历史交互物品
                user_history = set()
                if user_id in interactions['user_id'].values:
                    user_interactions = interactions[interactions['user_id'] == user_id]
                    user_history = set(user_interactions['item_id'])

                # 计算新颖性：推荐物品中未交互过的比例
                if rec_items:
                    novel_items = len(set(rec_items) - user_history)
                    novelty = novel_items / len(rec_items)
                    novelty_scores.append(novelty)

            return sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0.5

        return 0.5

    def _analyze_ab_test(self, recommendations: pd.DataFrame) -> Dict[str, Any]:
        """分析A/B测试结果"""
        if 'experiment_group' in recommendations.columns and 'metric' in recommendations.columns:
            groups = recommendations.groupby('experiment_group')
            control_group = groups.get_group('control')['metric'] if 'control' in groups.groups else None
            treatment_group = groups.get_group('treatment')['metric'] if 'treatment' in groups.groups else None

            if control_group is not None and treatment_group is not None:
                # t检验
                t_stat, p_value = stats.ttest_ind(control_group, treatment_group)

                return {
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05,
                    'control_mean': control_group.mean(),
                    'treatment_mean': treatment_group.mean(),
                    'improvement': (treatment_group.mean() - control_group.mean()) / control_group.mean()
                }

        return {'message': 'A/B测试数据不足'}

    def _calculate_ad_metrics(self, impressions: pd.DataFrame,
                            clicks: pd.DataFrame) -> Tuple[float, float, float]:
        """计算广告指标"""
        total_impressions = len(impressions) if impressions is not None else 0
        total_clicks = len(clicks) if clicks is not None else 0

        # 点击率
        ctr = total_clicks / total_impressions if total_impressions > 0 else 0.0

        # 每次点击成本 (假设有成本数据)
        cpc = impressions['cost'].mean() if 'cost' in impressions.columns else 0.5

        # 每千次展示成本
        cpm = (cpc * ctr * 1000) if ctr > 0 else 0.0

        return ctr, cpc, cpm

    def _detect_ad_fraud(self, impressions: pd.DataFrame, clicks: pd.DataFrame) -> float:
        """检测广告欺诈"""
        fraud_indicators = []

        # 检查异常点击模式
        if clicks is not None and 'timestamp' in clicks.columns:
            clicks['timestamp'] = pd.to_datetime(clicks['timestamp'])
            clicks_per_minute = clicks.groupby(clicks['timestamp'].dt.floor('min')).size()
            suspicious_minutes = (clicks_per_minute > clicks_per_minute.quantile(0.95)).sum()
            fraud_indicators.append(suspicious_minutes / len(clicks_per_minute) if len(clicks_per_minute) > 0 else 0)

        # 检查IP重复
        if 'ip_address' in clicks.columns:
            ip_counts = clicks['ip_address'].value_counts()
            suspicious_ips = (ip_counts > ip_counts.quantile(0.95)).sum()
            fraud_indicators.append(suspicious_ips / len(ip_counts) if len(ip_counts) > 0 else 0)

        return sum(fraud_indicators) / len(fraud_indicators) if fraud_indicators else 0.0

    def _assess_ad_quality(self, impressions: pd.DataFrame) -> float:
        """评估广告质量"""
        quality_factors = []

        # 广告位置质量
        if 'position' in impressions.columns:
            top_positions = impressions[impressions['position'] <= 3]
            quality_factors.append(len(top_positions) / len(impressions))

        # 广告相关性
        if 'relevance_score' in impressions.columns:
            avg_relevance = impressions['relevance_score'].mean()
            quality_factors.append(avg_relevance)

        # 用户反馈
        if 'user_feedback' in impressions.columns:
            positive_feedback = (impressions['user_feedback'] > 3).mean()
            quality_factors.append(positive_feedback)

        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.5

    def _assess_funnel_quality(self, funnel_rates: Dict[str, float]) -> float:
        """评估漏斗质量"""
        expected_rates = self.config.get('expected_funnel_rates', {})
        quality_scores = []

        for step, expected_rate in expected_rates.items():
            actual_rate = funnel_rates.get(step, 0)
            if expected_rate > 0:
                score = min(1.0, actual_rate / expected_rate)
                quality_scores.append(score)

        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.5

    def _evaluate_business_impact(self, funnel_rates: Dict[str, float]) -> float:
        """评估业务影响"""
        # 基于关键转化率的业务评分
        purchase_rate = funnel_rates.get('checkout_to_purchase', 0)
        cart_rate = funnel_rates.get('view_product_to_add_to_cart', 0)

        # 简化的业务评分模型
        business_score = (purchase_rate * 0.6 + cart_rate * 0.4)
        return min(1.0, business_score)

    def _evaluate_recommendation_business_impact(self, precision: float, recall: float) -> float:
        """评估推荐系统业务影响"""
        # 基于准确性和召回率的业务评分
        business_score = (precision * 0.7 + recall * 0.3)
        return min(1.0, business_score)

    def _evaluate_ad_business_value(self, ctr: float, cpc: float, fraud_rate: float) -> float:
        """评估广告业务价值"""
        # 基于点击率、成本和欺诈率的综合评分
        base_score = ctr * 0.5 + (1 - fraud_rate) * 0.3 + (1 / (1 + cpc)) * 0.2
        return min(1.0, base_score)

    def run_comprehensive_validation(self, test_cases: List[InternetTestCase]) -> Dict[str, Any]:
        """运行综合验证"""
        logger.info("开始互联网行业测试综合验证...")

        results = []
        for test_case in test_cases:
            if test_case.scenario_type == 'ecommerce_funnel':
                # 这里需要实际的用户事件和会话数据
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=1.8,
                    quality_score=0.85,
                    business_score=0.78,
                    details={'simulated': True}
                )
            elif test_case.scenario_type == 'recommendation_system':
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=3.2,
                    quality_score=0.82,
                    business_score=0.75,
                    details={'simulated': True}
                )
            elif test_case.scenario_type == 'advertising_system':
                result = TestResult(
                    case_id=test_case.case_id,
                    status='pass',  # 模拟结果
                    execution_time=2.5,
                    quality_score=0.88,
                    business_score=0.81,
                    details={'simulated': True}
                )
            else:
                result = TestResult(
                    case_id=test_case.case_id,
                    status='warning',
                    execution_time=0.8,
                    quality_score=0.6,
                    business_score=0.5,
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
            'average_quality_score': sum(r.quality_score for r in results) / len(results),
            'average_business_score': sum(r.business_score for r in results) / len(results),
            'average_execution_time': sum(r.execution_time for r in results) / len(results)
        }

        return {
            'summary': summary,
            'detailed_results': [asdict(r) for r in results]
        }

# 使用示例
if __name__ == "__main__":
    validator = InternetTestValidator()

    # 创建测试案例
    test_cases = [
        InternetTestCase(
            case_id="ECOMMERCE_FUNNEL_001",
            scenario_type="ecommerce_funnel",
            business_impact="提升转化率",
            key_metrics=["转化率>3%", "复购率>25%"],
            test_data={},
            expected_results={"funnel_completion": "> 0.03"},
            validation_rules={"min_conversion": 0.03}
        ),
        InternetTestCase(
            case_id="RECOMMENDATION_SYSTEM_001",
            scenario_type="recommendation_system",
            business_impact="提升用户体验",
            key_metrics=["准确率>15%", "点击率>8%"],
            test_data={},
            expected_results={"precision": "> 0.15"},
            validation_rules={"min_precision": 0.15}
        ),
        InternetTestCase(
            case_id="ADVERTISING_SYSTEM_001",
            scenario_type="advertising_system",
            business_impact="优化广告投放",
            key_metrics=["点击率>8%", "欺诈率<5%"],
            test_data={},
            expected_results={"ctr": "> 0.08"},
            validation_rules={"min_ctr": 0.08}
        )
    ]

    # 运行验证
    validation_report = validator.run_comprehensive_validation(test_cases)

    # 输出结果
    print("互联网行业测试验证报告:")
    print(json.dumps(validation_report, indent=2, ensure_ascii=False))

    print("互联网行业测试验证完成")