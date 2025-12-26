# AI测试效果评估框架

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AITestingEvaluator:
    """AI测试效果评估器"""

    def __init__(self):
        self.metrics_history = []
        self.baseline_metrics = {}

    def evaluate_defect_prediction(self, predictions: List[int], actuals: List[int],
                                 model_name: str = "defect_predictor") -> Dict[str, Any]:
        """评估缺陷预测模型效果"""

        # 计算分类指标
        report = classification_report(actuals, predictions, output_dict=True)

        # 计算混淆矩阵
        cm = confusion_matrix(actuals, predictions)

        # 计算特有指标
        tn, fp, fn, tp = cm.ravel()
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        # 计算业务价值指标
        defect_detection_rate = recall  # 缺陷检测率
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        efficiency_gain = self._calculate_efficiency_gain(predictions, actuals)

        evaluation_result = {
            "model_name": model_name,
            "timestamp": pd.Timestamp.now(),
            "classification_metrics": {
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "accuracy": (tp + tn) / (tp + tn + fp + fn)
            },
            "business_metrics": {
                "defect_detection_rate": defect_detection_rate,
                "false_positive_rate": false_positive_rate,
                "efficiency_gain": efficiency_gain
            },
            "confusion_matrix": cm.tolist(),
            "recommendations": self._generate_recommendations(precision, recall, false_positive_rate)
        }

        self.metrics_history.append(evaluation_result)
        logger.info(f"Evaluated {model_name}: F1={f1_score:.3f}, Efficiency Gain={efficiency_gain:.1f}%")

        return evaluation_result

    def _calculate_efficiency_gain(self, predictions: List[int], actuals: List[int]) -> float:
        """计算效率提升"""
        # 简化的效率计算：假设AI能将测试工作量减少预测准确的比例
        correct_predictions = sum(1 for p, a in zip(predictions, actuals) if p == a)
        total_predictions = len(predictions)

        if total_predictions == 0:
            return 0

        accuracy = correct_predictions / total_predictions
        # 假设AI测试比人工测试效率高30-50%
        efficiency_gain = accuracy * 40  # 40%平均效率提升

        return efficiency_gain

    def _generate_recommendations(self, precision: float, recall: float, false_positive_rate: float) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if precision < 0.7:
            recommendations.append("提高模型精确度，减少误报")
        if recall < 0.8:
            recommendations.append("提高模型召回率，确保缺陷不遗漏")
        if false_positive_rate > 0.2:
            recommendations.append("优化特征工程，降低误报率")
        if precision > 0.9 and recall > 0.9:
            recommendations.append("模型性能优秀，可以考虑生产部署")

        return recommendations

    def evaluate_test_case_generation(self, generated_cases: List[Dict[str, Any]],
                                    expert_ratings: List[int]) -> Dict[str, Any]:
        """评估测试用例生成质量"""

        # 计算生成用例的多样性
        unique_scenarios = len(set(tc.get('title', '') for tc in generated_cases))

        # 计算覆盖率（简化的评估）
        coverage_score = min(unique_scenarios / len(generated_cases), 1.0) if generated_cases else 0

        # 基于专家评分的质量评估
        avg_rating = np.mean(expert_ratings) if expert_ratings else 0
        quality_score = avg_rating / 5.0  # 假设满分5分

        # 计算生成效率
        generation_time = len(generated_cases) * 0.5  # 假设每个用例生成0.5分钟
        manual_time = len(generated_cases) * 15  # 假设人工编写每个用例15分钟
        time_saving = (manual_time - generation_time) / manual_time * 100

        evaluation_result = {
            "total_cases_generated": len(generated_cases),
            "unique_scenarios": unique_scenarios,
            "coverage_score": coverage_score,
            "quality_score": quality_score,
            "time_saving_percentage": time_saving,
            "efficiency_metrics": {
                "cases_per_hour": len(generated_cases) / (generation_time / 60),
                "quality_efficiency_ratio": quality_score / max(generation_time, 1)
            }
        }

        logger.info(f"Evaluated test case generation: {len(generated_cases)} cases, Quality={quality_score:.2f}")
        return evaluation_result

    def compare_with_baseline(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """与基准比较"""

        if not self.baseline_metrics:
            self.baseline_metrics = current_metrics.copy()
            return {"comparison": "baseline_established", "improvements": {}}

        improvements = {}
        for key, current_value in current_metrics.items():
            if key in self.baseline_metrics:
                baseline_value = self.baseline_metrics[key]
                if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                    improvement = ((current_value - baseline_value) / baseline_value) * 100 if baseline_value != 0 else 0
                    improvements[key] = improvement

        return {
            "comparison": "improvement_analysis",
            "improvements": improvements,
            "significant_improvements": [k for k, v in improvements.items() if abs(v) > 10]
        }

    def generate_evaluation_report(self) -> Dict[str, Any]:
        """生成综合评估报告"""

        if not self.metrics_history:
            return {"error": "No evaluation data available"}

        # 计算趋势
        df = pd.DataFrame(self.metrics_history)

        # 性能趋势分析
        performance_trends = {}
        if 'classification_metrics' in df.columns:
            metrics_over_time = df['classification_metrics'].apply(pd.Series)
            for metric in ['precision', 'recall', 'f1_score']:
                if metric in metrics_over_time.columns:
                    trend = metrics_over_time[metric].pct_change().mean()
                    performance_trends[metric] = trend

        # 业务价值分析
        business_value = {}
        if len(df) > 1:
            latest = df.iloc[-1]
            baseline = df.iloc[0]

            for metric_key in ['business_metrics', 'efficiency_metrics']:
                if metric_key in latest and metric_key in baseline:
                    for sub_metric, value in latest[metric_key].items():
                        base_value = baseline[metric_key].get(sub_metric, 0)
                        if base_value != 0:
                            improvement = ((value - base_value) / base_value) * 100
                            business_value[f"{metric_key}.{sub_metric}"] = improvement

        return {
            "evaluation_period": {
                "start_date": df['timestamp'].min(),
                "end_date": df['timestamp'].max(),
                "total_evaluations": len(df)
            },
            "performance_trends": performance_trends,
            "business_value_improvements": business_value,
            "recommendations": self._generate_overall_recommendations(performance_trends, business_value),
            "maturity_assessment": self._assess_ai_testing_maturity(performance_trends)
        }

    def _generate_overall_recommendations(self, trends: Dict[str, float],
                                        improvements: Dict[str, float]) -> List[str]:
        """生成总体建议"""
        recommendations = []

        # 基于趋势的建议
        improving_metrics = [k for k, v in trends.items() if v > 0.05]
        declining_metrics = [k for k, v in trends.items() if v < -0.05]

        if improving_metrics:
            recommendations.append(f"继续优化 {', '.join(improving_metrics)} 指标")
        if declining_metrics:
            recommendations.append(f"重点关注 {', '.join(declining_metrics)} 指标下降问题")

        # 基于改进的建议
        significant_improvements = [k for k, v in improvements.items() if v > 20]
        if significant_improvements:
            recommendations.append(f"扩大 {', '.join(significant_improvements)} 的成功实践")

        return recommendations

    def _assess_ai_testing_maturity(self, trends: Dict[str, float]) -> str:
        """评估AI测试成熟度"""
        avg_trend = np.mean(list(trends.values())) if trends else 0

        if avg_trend > 0.1:
            return "成熟度高：AI测试效果持续提升"
        elif avg_trend > 0:
            return "成熟度中：AI测试效果稳步增长"
        elif avg_trend > -0.05:
            return "成熟度低：AI测试效果稳定但无明显提升"
        else:
            return "需要改进：AI测试效果出现下降"

    def create_evaluation_dashboard(self):
        """创建评估仪表板"""
        if not self.metrics_history:
            print("No evaluation data available")
            return

        df = pd.DataFrame(self.metrics_history)

        # 设置matplotlib样式
        plt.style.use('seaborn-v0_8')

        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('AI测试效果评估仪表板', fontsize=16)

        # 分类指标趋势
        if 'classification_metrics' in df.columns:
            metrics_df = df['classification_metrics'].apply(pd.Series)
            metrics_df.index = df['timestamp']

            axes[0, 0].plot(metrics_df.index, metrics_df['precision'], label='Precision', marker='o')
            axes[0, 0].plot(metrics_df.index, metrics_df['recall'], label='Recall', marker='s')
            axes[0, 0].plot(metrics_df.index, metrics_df['f1_score'], label='F1-Score', marker='^')
            axes[0, 0].set_title('分类性能指标趋势')
            axes[0, 0].set_xlabel('时间')
            axes[0, 0].set_ylabel('指标值')
            axes[0, 0].legend()
            axes[0, 0].tick_params(axis='x', rotation=45)

        # 业务指标
        if 'business_metrics' in df.columns:
            business_df = df['business_metrics'].apply(pd.Series)
            business_df.index = df['timestamp']

            axes[0, 1].plot(business_df.index, business_df['defect_detection_rate'] * 100,
                           label='缺陷检测率', color='green', marker='o')
            axes[0, 1].plot(business_df.index, business_df['efficiency_gain'],
                           label='效率提升', color='blue', marker='s')
            axes[0, 1].set_title('业务价值指标')
            axes[0, 1].set_xlabel('时间')
            axes[0, 1].set_ylabel('百分比')
            axes[0, 1].legend()
            axes[0, 1].tick_params(axis='x', rotation=45)

        # 混淆矩阵热力图（最新）
        if len(df) > 0 and 'confusion_matrix' in df.columns:
            latest_cm = df.iloc[-1]['confusion_matrix']
            if latest_cm:
                sns.heatmap(latest_cm, annot=True, fmt='d', cmap='Blues',
                           xticklabels=['Predicted Negative', 'Predicted Positive'],
                           yticklabels=['Actual Negative', 'Actual Positive'],
                           ax=axes[1, 0])
                axes[1, 0].set_title('最新混淆矩阵')

        # 改进趋势
        improvements_data = []
        for i in range(1, len(df)):
            current = df.iloc[i]
            previous = df.iloc[i-1]

            if 'business_metrics' in current and 'business_metrics' in previous:
                for metric, value in current['business_metrics'].items():
                    prev_value = previous['business_metrics'].get(metric, 0)
                    if prev_value != 0:
                        improvement = ((value - prev_value) / prev_value) * 100
                        improvements_data.append({
                            'metric': metric,
                            'improvement': improvement,
                            'date': current['timestamp']
                        })

        if improvements_data:
            imp_df = pd.DataFrame(improvements_data)
            metrics = imp_df['metric'].unique()

            for metric in metrics:
                metric_data = imp_df[imp_df['metric'] == metric]
                axes[1, 1].bar(range(len(metric_data)), metric_data['improvement'],
                              label=metric, alpha=0.7)

            axes[1, 1].set_title('指标改进趋势')
            axes[1, 1].set_xlabel('评估次数')
            axes[1, 1].set_ylabel('改进百分比')
            axes[1, 1].legend()

        plt.tight_layout()
        plt.show()

# 使用示例
if __name__ == "__main__":
    evaluator = AITestingEvaluator()

    # 模拟缺陷预测评估
    predictions = [0, 1, 0, 1, 1, 0, 1, 0, 0, 1]
    actuals = [0, 1, 0, 0, 1, 0, 1, 1, 0, 1]

    result = evaluator.evaluate_defect_prediction(predictions, actuals, "test_model_v1")
    print("缺陷预测评估结果:")
    print(json.dumps(result, indent=2, default=str))

    # 模拟测试用例生成评估
    generated_cases = [
        {"title": "用户登录-有效凭据", "description": "测试有效用户登录"},
        {"title": "用户登录-无效密码", "description": "测试无效密码登录"},
        {"title": "用户注册-邮箱格式", "description": "测试邮箱格式验证"}
    ]
    expert_ratings = [4, 5, 4]

    case_result = evaluator.evaluate_test_case_generation(generated_cases, expert_ratings)
    print("\n测试用例生成评估结果:")
    print(json.dumps(case_result, indent=2))

    # 生成综合报告
    report = evaluator.generate_evaluation_report()
    print("\n综合评估报告:")
    print(json.dumps(report, indent=2, default=str))