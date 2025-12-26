# ai_model_explainability.py
# AI模型解释性分析案例

import shap
import numpy as np
import pandas as pd
from ai_anomaly_deployment import AIAnomalyDetector
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

class AIModelExplainability:
    def __init__(self, model):
        self.model = model
        self.explainer = None

    def prepare_explanation_data(self, data, sample_size=1000):
        """准备解释性分析数据"""
        if isinstance(data, list):
            data = np.array(data)
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)

        # 随机采样以提高解释效率
        if len(data) > sample_size:
            indices = np.random.choice(len(data), sample_size, replace=False)
            return data[indices]
        return data

    def shap_explanation(self, background_data, test_instance):
        """使用SHAP进行全局和局部解释"""
        # 创建SHAP解释器
        self.explainer = shap.KernelExplainer(
            lambda x: self.model.predict(x) if hasattr(self.model, 'predict') else [0]*len(x),
            background_data
        )

        # 计算SHAP值
        shap_values = self.explainer.shap_values(test_instance.reshape(1, -1))

        return {
            'shap_values': shap_values,
            'expected_value': self.explainer.expected_value,
            'feature_importance': np.abs(shap_values).mean(axis=0)
        }

    def lime_explanation(self, test_instance, feature_names=None):
        """使用LIME进行局部解释"""
        try:
            import lime.lime_tabular

            # 创建LIME解释器
            if feature_names is None:
                feature_names = [f'feature_{i}' for i in range(len(test_instance))]

            # 模拟训练数据（实际应使用真实数据）
            train_data = np.random.normal(0, 1, (1000, len(test_instance)))

            explainer = lime.lime_tabular.LimeTabularExplainer(
                train_data,
                feature_names=feature_names,
                class_names=['normal', 'anomaly'],
                mode='classification'
            )

            # 生成解释
            exp = explainer.explain_instance(
                test_instance,
                lambda x: self.model.predict(x) if hasattr(self.model, 'predict') else [0]*len(x),
                num_features=len(test_instance)
            )

            return {
                'lime_explanation': exp.as_list(),
                'prediction': exp.predict_proba
            }
        except ImportError:
            return {"error": "LIME not installed"}

    def generate_explanation_report(self, test_data, feature_names=None):
        """生成完整的解释性报告"""
        report = {
            'global_explanation': {},
            'local_explanations': [],
            'feature_importance': {},
            'recommendations': []
        }

        # 全局解释
        background_data = self.prepare_explanation_data(test_data, 100)
        global_shap = self.shap_explanation(background_data, background_data[0])
        report['global_explanation'] = {
            'expected_value': global_shap['expected_value'],
            'feature_importance': dict(zip(feature_names or [f'feature_{i}' for i in range(len(global_shap['feature_importance']))],
                                          global_shap['feature_importance']))
        }

        # 局部解释（前5个样本）
        for i in range(min(5, len(test_data))):
            local_shap = self.shap_explanation(background_data, test_data[i])
            lime_exp = self.lime_explanation(test_data[i], feature_names)

            report['local_explanations'].append({
                'sample_id': i,
                'shap_values': local_shap['shap_values'].flatten(),
                'lime_explanation': lime_exp.get('lime_explanation', []),
                'prediction': self.model.predict([test_data[i]])[0] if hasattr(self.model, 'predict') else 0
            })

        # 生成建议
        top_features = sorted(report['global_explanation']['feature_importance'].items(),
                            key=lambda x: x[1], reverse=True)

        report['recommendations'] = [
            f"重点关注特征 '{top_features[0][0]}'，其对模型决策的影响最大",
            "定期重新训练模型以适应数据分布变化",
            "使用SHAP值监控特征重要性漂移",
            "对高风险预测结果提供LIME局部解释"
        ]

        return report

    def visualize_explanations(self, report, save_path=None):
        """可视化解释结果"""
        try:
            # 特征重要性图
            features = list(report['global_explanation']['feature_importance'].keys())
            importance = list(report['global_explanation']['feature_importance'].values())

            plt.figure(figsize=(10, 6))
            plt.barh(features, importance)
            plt.title('Global Feature Importance (SHAP)')
            plt.xlabel('Mean |SHAP value|')
            if save_path:
                plt.savefig(save_path)
            plt.show()

        except Exception as e:
            print(f"可视化失败: {e}")

# 使用示例
if __name__ == "__main__":
    # 创建模拟模型
    detector = AIAnomalyDetector()

    # 模拟测试数据
    test_data = np.random.normal(0, 1, (100, 3))  # 100个样本，3个特征
    feature_names = ['latency', 'throughput', 'error_rate']

    explainability = AIModelExplainability(detector.model)
    report = explainability.generate_explanation_report(test_data, feature_names)

    print("AI模型解释性分析报告:")
    print(f"全局特征重要性: {report['global_explanation']['feature_importance']}")
    print(f"建议: {report['recommendations'][0]}")

    # 可视化
    explainability.visualize_explanations(report)