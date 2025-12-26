# ai_anomaly_deployment.py
# AI异常检测实际部署示例

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import time
import numpy as np

class AIAnomalyDetector:
    def __init__(self, model_path='anomaly_model.pkl'):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.model = None
        self.load_or_train_model()

    def load_or_train_model(self):
        """加载或训练模型"""
        try:
            self.model = joblib.load(self.model_path)
            print("模型加载成功")
        except:
            print("模型不存在，开始训练...")
            self.train_initial_model()

    def train_initial_model(self):
        """初始模型训练"""
        # 模拟历史数据
        np.random.seed(42)
        data = np.random.normal(0, 1, (1000, 3))  # 延迟、吞吐量、错误率
        # 添加一些异常
        data[100:110] = np.random.normal(5, 2, (10, 3))

        scaled_data = self.scaler.fit_transform(data)
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.model.fit(scaled_data)
        joblib.dump(self.model, self.model_path)
        print("模型训练完成")

    def predict_anomaly(self, metrics):
        """预测异常"""
        scaled_metrics = self.scaler.transform([metrics])
        prediction = self.model.predict(scaled_metrics)
        score = self.model.decision_function(scaled_metrics)
        return prediction[0], score[0]

    def update_model(self, new_data):
        """在线学习更新模型"""
        scaled_data = self.scaler.transform(new_data)
        self.model.fit(scaled_data)
        joblib.dump(self.model, self.model_path)

    def get_model_stats(self):
        """获取模型统计信息"""
        return {
            'contamination': self.model.contamination,
            'n_estimators': self.model.n_estimators,
            'scaler_mean': self.scaler.mean_,
            'scaler_scale': self.scaler.scale_
        }

# 部署示例
if __name__ == "__main__":
    detector = AIAnomalyDetector()

    print("模型统计:", detector.get_model_stats())

    # 模拟实时监控
    print("开始实时异常检测...")
    for i in range(10):
        # 模拟采集指标
        latency = 150 + np.random.normal(0, 10)
        throughput = 1000 + np.random.normal(0, 50)
        error_rate = 0.01 + np.random.normal(0, 0.005)

        metrics = [latency, throughput, error_rate]
        prediction, score = detector.predict_anomaly(metrics)

        if prediction == -1:
            print(f"[{i+1}] 检测到异常！指标: {metrics}, 异常分数: {score:.3f}")
            # 发送告警逻辑
        else:
            print(f"[{i+1}] 正常指标: {metrics}")

        time.sleep(0.1)  # 模拟检测间隔

    print("异常检测演示完成")