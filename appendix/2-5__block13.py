import unittest
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
from scipy import stats

class ModelMonitoringTest(unittest.TestCase):
    def setUp(self):
        # 创建训练数据
        self.X, self.y = make_classification(
            n_samples=1000, n_features=10, n_classes=2, 
            random_state=42, n_informative=5, class_sep=0.8
        )
        
        # 划分训练集和测试集
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
        
        # 训练模型
        self.model = RandomForestClassifier(random_state=42)
        self.model.fit(self.X_train, self.y_train)
        
        # 创建特征名称
        self.feature_names = [f'feature_{i}' for i in range(self.X.shape[1])]
        
        # 创建基准数据分布统计信息
        self.train_stats = {}
        for i, feature in enumerate(self.feature_names):
            self.train_stats[feature] = {
                'mean': np.mean(self.X_train[:, i]),
                'std': np.std(self.X_train[:, i]),
                'min': np.min(self.X_train[:, i]),
                'max': np.max(self.X_train[:, i])
            }
    
    def test_data_drift_detection(self):
        # 测试数据漂移检测
        print("数据漂移检测测试")
        
        # 创建三种不同的数据分布
        # 1. 与训练数据相似的数据
        similar_data = self.X_test.copy()
        
        # 2. 有轻微漂移的数据（特征均值偏移0.5个标准差）
        slight_drift_data = self.X_test.copy()
        for i in range(slight_drift_data.shape[1]):
            # 为每个特征添加一个小偏移
            drift_amount = 0.5 * self.train_stats[f'feature_{i}']['std']
            slight_drift_data[:, i] += drift_amount
        
        # 3. 有严重漂移的数据（特征均值偏移2个标准差）
        severe_drift_data = self.X_test.copy()
        for i in range(severe_drift_data.shape[1]):
            # 为每个特征添加一个大偏移
            drift_amount = 2.0 * self.train_stats[f'feature_{i}']['std']
            severe_drift_data[:, i] += drift_amount
        
        # 计算每个数据集的漂移指标
        datasets = {
            '原始测试数据': self.X_test,
            '轻微漂移数据': slight_drift_data,
            '严重漂移数据': severe_drift_data
        }
        
        drift_results = {}
        for name, data in datasets.items():
            drift_metrics = []
            print(f"\n{name} 漂移指标:")
            
            for i, feature in enumerate(self.feature_names):
                # 使用KS检验比较分布差异
                ks_statistic, p_value = stats.kstest(
                    data[:, i], 'norm', 
                    args=(self.train_stats[feature]['mean'], self.train_stats[feature]['std'])
                )
                
                # 使用KL散度（近似）
                # 将数据离散化为10个bins进行比较
                n_bins = 10
                hist1, bin_edges = np.histogram(self.X_train[:, i], bins=n_bins, density=True)
                hist2, _ = np.histogram(data[:, i], bins=bin_edges, density=True)
                
                # 添加小量以避免除零错误
                hist1 = hist1 + 1e-10
                hist2 = hist2 + 1e-10
                
                kl_divergence = np.sum(hist1 * np.log(hist1 / hist2))
                
                drift_metrics.append({
                    'feature': feature,
                    'ks_statistic': ks_statistic,
                    'p_value': p_value,
                    'kl_divergence': kl_divergence
                })
                
                print(f"  {feature}: KS={ks_statistic:.4f}, p={p_value:.4f}, KL={kl_divergence:.4f}")
            
            drift_results[name] = drift_metrics
        
        # 验证漂移检测的有效性
        # 轻微漂移和严重漂移的KS统计量应大于原始数据
        orig_ks = np.mean([m['ks_statistic'] for m in drift_results['原始测试数据']])
        slight_ks = np.mean([m['ks_statistic'] for m in drift_results['轻微漂移数据']])
        severe_ks = np.mean([m['ks_statistic'] for m in drift_results['严重漂移数据']])
        
        print(f"\n平均KS统计量比较:")
        print(f"原始测试数据: {orig_ks:.4f}")
        print(f"轻微漂移数据: {slight_ks:.4f}")
        print(f"严重漂移数据: {severe_ks:.4f}")
        
        # 验证漂移的趋势
        self.assertGreater(slight_ks, orig_ks)  # 轻微漂移应比原始数据有更大的KS统计量
        self.assertGreater(severe_ks, slight_ks)  # 严重漂移应比轻微漂移有更大的KS统计量
    
    def test_model_performance_drift(self):
        # 测试模型性能漂移
        print("\n模型性能漂移测试")
        
        # 创建性能逐渐下降的场景
        scenarios = {
            '原始数据': self.X_test.copy(),
            '20%标签噪声': self._add_label_noise(self.y_test.copy(), noise_ratio=0.2),
            '50%标签噪声': self._add_label_noise(self.y_test.copy(), noise_ratio=0.5)
        }
        
        performance_results = {}
        for name, data in scenarios.items():
            if name == '原始数据':
                # 使用原始标签
                X = data
                y_true = self.y_test
            else:
                # 使用带噪声的标签
                X = self.X_test
                y_true = data
            
            # 进行预测
            y_pred = self.model.predict(X)
            
            # 计算性能指标
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred)
            recall = recall_score(y_true, y_pred)
            
            performance_results[name] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall
            }
            
            print(f"\n{name} 性能指标:")
            print(f"  准确率: {accuracy:.4f}")
            print(f"  精确率: {precision:.4f}")
            print(f"  召回率: {recall:.4f}")
        
        # 验证性能漂移
        orig_acc = performance_results['原始数据']['accuracy']
        noise20_acc = performance_results['20%标签噪声']['accuracy']
        noise50_acc = performance_results['50%标签噪声']['accuracy']
        
        print(f"\n准确率比较:")
        print(f"原始数据: {orig_acc:.4f}")
        print(f"20%标签噪声: {noise20_acc:.4f}")
        print(f"50%标签噪声: {noise50_acc:.4f}")
        
        # 验证性能下降趋势
        self.assertLess(noise20_acc, orig_acc)  # 20%噪声应导致准确率下降
        self.assertLess(noise50_acc, noise20_acc)  # 50%噪声应导致准确率进一步下降
    
    def test_error_rate_monitoring(self):
        # 测试错误率监控
        print("\n错误率监控测试")
        
        # 创建滑动窗口监控
        window_size = 50
        num_windows = len(self.X_test) // window_size
        
        error_rates = []
        for i in range(num_windows):
            start_idx = i * window_size
            end_idx = start_idx + window_size
            
            window_X = self.X_test[start_idx:end_idx]
            window_y = self.y_test[start_idx:end_idx]
            
            window_pred = self.model.predict(window_X)
            error_rate = 1 - accuracy_score(window_y, window_pred)
            
            error_rates.append({
                'window': i+1,
                'error_rate': error_rate
            })
            
            print(f"窗口 {i+1}: 错误率 = {error_rate:.4f}")
        
        # 计算错误率统计信息
        error_values = [e['error_rate'] for e in error_rates]
        mean_error = np.mean(error_values)
        std_error = np.std(error_values)
        max_error = np.max(error_values)
        
        print(f"\n错误率统计:")
        print(f"平均错误率: {mean_error:.4f}")
        print(f"错误率标准差: {std_error:.4f}")
        print(f"最大错误率: {max_error:.4f}")
        
        # 设置告警阈值（例如：平均错误率 + 2倍标准差）
        alert_threshold = mean_error + 2 * std_error
        print(f"告警阈值: {alert_threshold:.4f}")
    
    def test_alerting_mechanism(self):
        # 测试告警机制
        print("\n告警机制测试")
        
        # 模拟不同性能水平的场景
        scenarios = [
            {'name': '正常性能', 'accuracy': 0.95, 'latency': 50, 'error_rate': 0.05},
            {'name': '性能下降', 'accuracy': 0.80, 'latency': 80, 'error_rate': 0.20},
            {'name': '严重性能问题', 'accuracy': 0.60, 'latency': 200, 'error_rate': 0.40}
        ]
        
        # 设置告警阈值
        thresholds = {
            'accuracy_low': 0.85,
            'latency_high': 100,  # 毫秒
            'error_rate_high': 0.15
        }
        
        print(f"告警阈值设置:")
        for metric, threshold in thresholds.items():
            print(f"  {metric}: {threshold}")
        
        # 评估每个场景
        alert_results = []
        for scenario in scenarios:
            alerts = []
            
            # 检查准确率
            if scenario['accuracy'] < thresholds['accuracy_low']:
                alerts.append(f"准确率低于阈值: {scenario['accuracy']:.4f} < {thresholds['accuracy_low']}")
            
            # 检查延迟
            if scenario['latency'] > thresholds['latency_high']:
                alerts.append(f"延迟高于阈值: {scenario['latency']}ms > {thresholds['latency_high']}ms")
            
            # 检查错误率
            if scenario['error_rate'] > thresholds['error_rate_high']:
                alerts.append(f"错误率高于阈值: {scenario['error_rate']:.4f} > {thresholds['error_rate_high']}")
            
            alert_results.append({
                'scenario': scenario['name'],
                'alerts': alerts,
                'alert_triggered': len(alerts) > 0
            })
        
        # 打印告警结果
        for result in alert_results:
            print(f"\n场景: {result['scenario']}")
            print(f"告警触发: {result['alert_triggered']}")
            if result['alerts']:
                for alert in result['alerts']:
                    print(f"  - {alert}")
        
        # 验证告警机制的正确性
        self.assertFalse(alert_results[0]['alert_triggered'])  # 正常性能不应触发告警
        self.assertTrue(alert_results[1]['alert_triggered'])  # 性能下降应触发告警
        self.assertTrue(alert_results[2]['alert_triggered'])  # 严重性能问题应触发告警
    
    def _add_label_noise(self, y, noise_ratio=0.1):
        """向标签添加噪声"""
        noisy_y = y.copy()
        num_noise = int(len(noisy_y) * noise_ratio)
        noise_indices = np.random.choice(len(noisy_y), num_noise, replace=False)
        
        # 翻转选中的标签
        for idx in noise_indices:
            noisy_y[idx] = 1 - noisy_y[idx]  # 假设是二分类问题
        
        return noisy_y

if __name__ == '__main__':
    unittest.main()
