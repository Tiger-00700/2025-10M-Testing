"""
SmartTestCaseGenerator

Extracted from book (Chapter 20). This is an illustrative snippet — it may need
small edits to be runnable (imports and line-wrapping converted into valid Python).
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


class SmartTestCaseGenerator:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)

    def train_model(self, historical_data, labels):
        # 训练预测模型
        X_train, X_test, y_train, y_test = train_test_split(historical_data, labels, test_size=0.2)
        self.model.fit(X_train, y_train)
        accuracy = self.model.score(X_test, y_test)
        print(f"模型训练完成，准确率: {accuracy:.2f}")
        return accuracy

    def generate_test_cases(self, feature_space, num_cases=100):
        # 生成测试用例
        test_cases = []
        for _ in range(num_cases):
            # 在特征空间中随机采样
            sample = np.random.uniform(feature_space[:, 0], feature_space[:, 1], size=(1, feature_space.shape[0]))
            importance = self.model.predict_proba(sample)[0][1]
            test_cases.append((sample[0], importance))

        # 按重要性排序
        test_cases.sort(key=lambda x: x[1], reverse=True)
        return test_cases


if __name__ == "__main__":
    generator = SmartTestCaseGenerator()
    # 示例（需要真实历史数据）
    # historical_data = ...
    # labels = ...
    # generator.train_model(historical_data, labels)
    # feature_space = np.array([[0, 100], [0, 1000], [0, 1]])
    # test_cases = generator.generate_test_cases(feature_space, num_cases=50)
