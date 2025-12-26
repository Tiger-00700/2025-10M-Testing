# examples/18_cases/ecommerce_funnel_check.py
"""
电商用户转化漏斗分析验证脚本
验证电商平台用户行为数据处理和转化分析的准确性
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
class FunnelStep:
    """漏斗步骤"""
    step_name: str
    event_type: str
    count: int
    conversion_rate: float

@dataclass
class FunnelAnalysisResult:
    """漏斗分析结果"""
    funnel_steps: List[FunnelStep]
    overall_conversion: float
    bottleneck_step: str
    recommendations: List[str]

class EcommerceFunnelValidator:
    """电商漏斗验证器"""

    def __init__(self, config_file: str = 'ecommerce_config.yml'):
        self.config = self._load_config(config_file)

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {
                'funnel_steps': [
                    {'name': 'browse', 'event': 'page_view'},
                    {'name': 'view_product', 'event': 'product_view'},
                    {'name': 'add_to_cart', 'event': 'add_to_cart'},
                    {'name': 'checkout', 'event': 'checkout_start'},
                    {'name': 'purchase', 'event': 'purchase_complete'}
                ],
                'expected_conversion_rates': {
                    'browse_to_view_product': 0.6,
                    'view_product_to_add_to_cart': 0.15,
                    'add_to_cart_to_checkout': 0.7,
                    'checkout_to_purchase': 0.8
                },
                'analysis_window_days': 30
            }

    def validate_funnel_data(self, user_events: pd.DataFrame,
                           session_data: pd.DataFrame) -> FunnelAnalysisResult:
        """验证漏斗数据"""
        logger.info("开始电商漏斗数据验证...")

        try:
            # 数据预处理
            processed_events = self._preprocess_event_data(user_events)
            processed_sessions = self._preprocess_session_data(session_data)

            # 计算漏斗步骤
            funnel_steps = self._calculate_funnel_steps(processed_events, processed_sessions)

            # 计算转化率
            conversion_rates = self._calculate_conversion_rates(funnel_steps)

            # 识别瓶颈
            bottleneck_step = self._identify_bottleneck(conversion_rates)

            # 生成建议
            recommendations = self._generate_recommendations(conversion_rates, bottleneck_step)

            # 整体转化率
            overall_conversion = (funnel_steps[-1].count / funnel_steps[0].count) if funnel_steps else 0.0

            return FunnelAnalysisResult(
                funnel_steps=funnel_steps,
                overall_conversion=overall_conversion,
                bottleneck_step=bottleneck_step,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"漏斗数据验证失败: {e}")
            # 返回空结果
            return FunnelAnalysisResult(
                funnel_steps=[],
                overall_conversion=0.0,
                bottleneck_step="",
                recommendations=[f"验证失败: {str(e)}"]
            )

    def _preprocess_event_data(self, events: pd.DataFrame) -> pd.DataFrame:
        """预处理事件数据"""
        processed = events.copy()

        # 确保必要的列存在
        required_columns = ['user_id', 'event_type', 'timestamp', 'session_id']
        for col in required_columns:
            if col not in processed.columns:
                logger.warning(f"缺少必要列: {col}")
                if col == 'session_id':
                    processed[col] = processed.get('user_id', 'unknown')  # 简化的会话ID

        # 处理时间戳
        if 'timestamp' in processed.columns:
            processed['timestamp'] = pd.to_datetime(processed['timestamp'])

        # 排序
        if 'timestamp' in processed.columns:
            processed = processed.sort_values(['user_id', 'timestamp'])

        return processed

    def _preprocess_session_data(self, sessions: pd.DataFrame) -> pd.DataFrame:
        """预处理会话数据"""
        processed = sessions.copy()

        # 确保必要的列存在
        required_columns = ['session_id', 'user_id', 'start_time', 'end_time']
        for col in required_columns:
            if col not in processed.columns:
                logger.warning(f"会话数据缺少列: {col}")

        # 处理时间戳
        time_columns = ['start_time', 'end_time']
        for col in time_columns:
            if col in processed.columns:
                processed[col] = pd.to_datetime(processed[col])

        return processed

    def _calculate_funnel_steps(self, events: pd.DataFrame,
                              sessions: pd.DataFrame) -> List[FunnelStep]:
        """计算漏斗步骤"""
        funnel_steps = []

        for step_config in self.config['funnel_steps']:
            step_name = step_config['name']
            event_type = step_config['event']

            # 计算步骤计数
            if event_type in events['event_type'].values:
                step_count = events[events['event_type'] == event_type]['user_id'].nunique()
            else:
                step_count = 0

            # 计算转化率（相对于上一步）
            conversion_rate = 1.0  # 第一步转化率为1
            if funnel_steps:
                prev_count = funnel_steps[-1].count
                conversion_rate = step_count / prev_count if prev_count > 0 else 0.0

            funnel_step = FunnelStep(
                step_name=step_name,
                event_type=event_type,
                count=step_count,
                conversion_rate=conversion_rate
            )

            funnel_steps.append(funnel_step)

        return funnel_steps

    def _calculate_conversion_rates(self, funnel_steps: List[FunnelStep]) -> Dict[str, float]:
        """计算各步骤间的转化率"""
        conversion_rates = {}

        for i in range(len(funnel_steps) - 1):
            current_step = funnel_steps[i]
            next_step = funnel_steps[i + 1]

            step_key = f"{current_step.step_name}_to_{next_step.step_name}"
            conversion_rate = next_step.count / current_step.count if current_step.count > 0 else 0.0

            conversion_rates[step_key] = conversion_rate

        return conversion_rates

    def _identify_bottleneck(self, conversion_rates: Dict[str, float]) -> str:
        """识别瓶颈步骤"""
        expected_rates = self.config['expected_conversion_rates']

        min_rate = float('inf')
        bottleneck = ""

        for step, actual_rate in conversion_rates.items():
            expected_rate = expected_rates.get(step, 0.5)  # 默认期望值

            # 计算偏离程度
            deviation = abs(actual_rate - expected_rate) / expected_rate if expected_rate > 0 else 0

            if actual_rate < expected_rate * 0.7:  # 偏离期望值30%以上
                if actual_rate < min_rate:
                    min_rate = actual_rate
                    bottleneck = step

        return bottleneck if bottleneck else "无明显瓶颈"

    def _generate_recommendations(self, conversion_rates: Dict[str, float],
                                bottleneck: str) -> List[str]:
        """生成改进建议"""
        recommendations = []
        expected_rates = self.config['expected_conversion_rates']

        # 基于瓶颈的建议
        if bottleneck and bottleneck != "无明显瓶颈":
            recommendations.append(f"重点优化{bottleneck}步骤的转化率")

            if "browse_to_view_product" in bottleneck:
                recommendations.extend([
                    "改善产品页面加载速度",
                    "优化搜索结果相关性",
                    "增强产品图片质量"
                ])
            elif "view_product_to_add_to_cart" in bottleneck:
                recommendations.extend([
                    "简化添加购物车流程",
                    "提供更多产品信息",
                    "优化价格展示"
                ])
            elif "add_to_cart_to_checkout" in bottleneck:
                recommendations.extend([
                    "减少结账步骤",
                    "提供多种支付方式",
                    "优化移动端体验"
                ])
            elif "checkout_to_purchase" in bottleneck:
                recommendations.extend([
                    "加强信任信号",
                    "提供客户支持",
                    "优化退货政策"
                ])

        # 基于整体表现的建议
        overall_performance = sum(conversion_rates.values()) / len(conversion_rates)
        if overall_performance < 0.3:
            recommendations.append("整体转化率偏低，建议进行全面的用户体验优化")
        elif overall_performance > 0.6:
            recommendations.append("转化表现良好，可关注用户留存和复购")

        # 数据质量建议
        if len([r for r in conversion_rates.values() if r == 0]) > 0:
            recommendations.append("存在数据缺失，建议完善事件跟踪")

        return recommendations

    def validate_funnel_accuracy(self, actual_funnel: FunnelAnalysisResult,
                               expected_funnel: Dict[str, Any]) -> Dict[str, Any]:
        """验证漏斗分析准确性"""
        validation_results = {
            'overall_conversion_match': False,
            'step_counts_match': False,
            'bottleneck_identified': False,
            'accuracy_score': 0.0,
            'issues': []
        }

        # 检查整体转化率
        expected_conversion = expected_funnel.get('overall_conversion', 0.05)
        actual_conversion = actual_funnel.overall_conversion

        conversion_diff = abs(actual_conversion - expected_conversion) / expected_conversion
        if conversion_diff <= 0.1:  # 允许10%的误差
            validation_results['overall_conversion_match'] = True
        else:
            validation_results['issues'].append(f"整体转化率偏差过大: 期望{expected_conversion:.3f}, 实际{actual_conversion:.3f}")

        # 检查步骤计数
        expected_steps = expected_funnel.get('step_counts', {})
        actual_steps = {step.step_name: step.count for step in actual_funnel.funnel_steps}

        step_matches = 0
        for step_name, expected_count in expected_steps.items():
            actual_count = actual_steps.get(step_name, 0)
            if abs(actual_count - expected_count) / expected_count <= 0.2:  # 允许20%的误差
                step_matches += 1
            else:
                validation_results['issues'].append(f"{step_name}步骤计数偏差: 期望{expected_count}, 实际{actual_count}")

        if step_matches == len(expected_steps):
            validation_results['step_counts_match'] = True

        # 检查瓶颈识别
        expected_bottleneck = expected_funnel.get('bottleneck_step', '')
        if actual_funnel.bottleneck_step == expected_bottleneck:
            validation_results['bottleneck_identified'] = True
        else:
            validation_results['issues'].append(f"瓶颈识别不准确: 期望{expected_bottleneck}, 实际{actual_funnel.bottleneck_step}")

        # 计算准确性分数
        score_components = [
            validation_results['overall_conversion_match'],
            validation_results['step_counts_match'],
            validation_results['bottleneck_identified']
        ]
        validation_results['accuracy_score'] = sum(score_components) / len(score_components)

        return validation_results

# 使用示例
if __name__ == "__main__":
    validator = EcommerceFunnelValidator()

    # 创建模拟电商事件数据
    np.random.seed(42)
    n_events = 10000

    # 用户ID
    user_ids = np.random.randint(1, 1001, n_events)

    # 事件类型（基于典型电商漏斗）
    event_types = ['page_view', 'product_view', 'add_to_cart', 'checkout_start', 'purchase_complete']
    event_weights = [0.4, 0.3, 0.15, 0.1, 0.05]  # 归一化概率

    events = []
    for user_id in np.unique(user_ids):
        user_events = np.random.choice(event_types, size=np.random.poisson(3), p=event_weights)
        for i, event in enumerate(user_events):
            events.append({
                'user_id': user_id,
                'event_type': event,
                'timestamp': datetime.now() - timedelta(hours=np.random.randint(0, 24*30)),
                'session_id': f"session_{user_id}_{i}"
            })

    events_df = pd.DataFrame(events)

    # 创建模拟会话数据
    sessions_df = pd.DataFrame({
        'session_id': [f"session_{i}_{j}" for i in range(1, 1001) for j in range(3)],
        'user_id': [i for i in range(1, 1001) for j in range(3)],
        'start_time': [datetime.now() - timedelta(hours=np.random.randint(0, 24*30)) for _ in range(3000)],
        'end_time': [datetime.now() - timedelta(hours=np.random.randint(0, 24*30)) for _ in range(3000)]
    })

    # 运行验证
    result = validator.validate_funnel_data(events_df, sessions_df)

    print("电商转化漏斗分析结果:")
    print(f"整体转化率: {result.overall_conversion:.3f}")
    print(f"瓶颈步骤: {result.bottleneck_step}")

    print("\n各步骤详情:")
    for step in result.funnel_steps:
        print(f"  {step.step_name}: {step.count} 用户, 转化率: {step.conversion_rate:.3f}")

    print("\n改进建议:")
    for rec in result.recommendations:
        print(f"  - {rec}")

    print("\n电商漏斗验证完成")