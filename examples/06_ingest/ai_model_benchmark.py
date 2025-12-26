# ai_model_benchmark.py
# AI模型性能基准测试框架

import time
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import psutil
import os

class AIModelBenchmark:
    def __init__(self, model):
        self.model = model
        self.metrics = {}

    def latency_benchmark(self, test_data, iterations=1000):
        """延迟基准测试"""
        latencies = []
        for _ in range(iterations):
            start_time = time.time()
            self.model.predict([test_data])
            latencies.append(time.time() - start_time)

        self.metrics['latency'] = {
            'mean': np.mean(latencies) * 1000,  # ms
            'p95': np.percentile(latencies, 95) * 1000,
            'p99': np.percentile(latencies, 99) * 1000
        }
        return self.metrics['latency']

    def throughput_benchmark(self, test_data, duration=60):
        """吞吐量基准测试"""
        predictions = 0
        start_time = time.time()

        while time.time() - start_time < duration:
            self.model.predict([test_data])
            predictions += 1

        self.metrics['throughput'] = predictions / duration  # predictions per second
        return self.metrics['throughput']

    def resource_benchmark(self, test_data, iterations=100):
        """资源使用基准测试"""
        process = psutil.Process(os.getpid())

        cpu_before = process.cpu_percent()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        for _ in range(iterations):
            self.model.predict([test_data])

        cpu_after = process.cpu_percent()
        mem_after = process.memory_info().rss / 1024 / 1024

        self.metrics['resources'] = {
            'cpu_usage': cpu_after - cpu_before,
            'memory_usage': mem_after - mem_before
        }
        return self.metrics['resources']

    def accuracy_benchmark(self, test_data, true_labels):
        """准确性基准测试"""
        predictions = self.model.predict(test_data)

        # 对于异常检测，转换为二分类
        pred_labels = [1 if p == -1 else 0 for p in predictions]
        true_binary = [1 if t > 0.5 else 0 for t in true_labels]  # 假设阈值0.5

        self.metrics['accuracy'] = classification_report(true_binary, pred_labels, output_dict=True)
        return self.metrics['accuracy']

    def run_full_benchmark(self, test_data, true_labels=None, iterations=1000, duration=60):
        """运行完整基准测试"""
        print("开始AI模型性能基准测试...")

        latency = self.latency_benchmark(test_data, iterations)
        print(f"延迟测试完成: 平均 {latency['mean']:.2f}ms, P95 {latency['p95']:.2f}ms")

        throughput = self.throughput_benchmark(test_data, duration)
        print(f"吞吐量测试完成: {throughput:.2f} predictions/sec")

        resources = self.resource_benchmark(test_data, min(iterations, 100))
        print(f"资源测试完成: CPU {resources['cpu_usage']:.1f}%, 内存 {resources['memory_usage']:.1f}MB")

        if true_labels is not None:
            accuracy = self.accuracy_benchmark(test_data, true_labels)
            print(f"准确性测试完成: 精确率 {accuracy['weighted avg']['precision']:.3f}")

        return self.metrics

# 使用示例
if __name__ == "__main__":
    from ai_anomaly_deployment import AIAnomalyDetector
    detector = AIAnomalyDetector()

    benchmark = AIModelBenchmark(detector)

    # 模拟测试数据
    test_sample = [150, 1000, 0.01]  # 延迟、吞吐量、错误率
    test_data = [test_sample] * 100  # 批量测试数据
    true_labels = [0] * 95 + [1] * 5  # 模拟真实标签

    results = benchmark.run_full_benchmark(test_data, true_labels, iterations=100, duration=10)
    print("基准测试完成，结果:", results)