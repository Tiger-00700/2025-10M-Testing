"""
AnomalyDetector

Extracted from book (Chapter 20). Illustrative snippet using sklearn.IsolationForest.
"""
import pandas as pd
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(contamination=contamination)

    def train(self, training_data):
        # 训练异常检测模型
        self.model.fit(training_data)
        print("异常检测模型训练完成")

    def detect_anomalies(self, test_data):
        # 检测异常
        predictions = self.model.predict(test_data)
        # -1 表示异常，1 表示正常
        anomalies = test_data[predictions == -1]
        normal = test_data[predictions == 1]
        print(f"检测到 {len(anomalies)} 个异常，{len(normal)} 个正常样本")
        return anomalies, normal


if __name__ == "__main__":
    detector = AnomalyDetector(contamination=0.05)
    # training_data = pd.read_csv("training_data.csv")
    # detector.train(training_data)
    # test_data = pd.read_csv("test_data.csv")
    # anomalies, normal = detector.detect_anomalies(test_data)
