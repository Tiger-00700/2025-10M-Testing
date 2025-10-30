import unittest
import numpy as np
import pickle
import joblib
import time
import threading
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

class ModelDeploymentTest(unittest.TestCase):
    def setUp(self):
        # 创建测试数据
        self.X, self.y = make_classification(
            n_samples=1000, n_features=20, n_classes=2, random_state=42
        )
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
        
        # 训练模型
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(self.X_train, self.y_train)
        
        # 创建测试样本
        self.single_sample = self.X_test[0].reshape(1, -1)
        self.batch_samples = self.X_test[:100]  # 100个样本的批次
    
    def test_model_serialization(self):
        # 测试模型序列化和反序列化
        # 使用pickle
        with open('model_pickle.pkl', 'wb') as f:
            pickle.dump(self.model, f)
        
        with open('model_pickle.pkl', 'rb') as f:
            loaded_model_pickle = pickle.load(f)
        
        # 使用joblib（scikit-learn推荐）
        joblib.dump(self.model, 'model_joblib.pkl')
        loaded_model_joblib = joblib.load('model_joblib.pkl')
        
        # 验证序列化前后的预测结果一致性
        original_pred = self.model.predict(self.single_sample)
        pickle_pred = loaded_model_pickle.predict(self.single_sample)
        joblib_pred = loaded_model_joblib.predict(self.single_sample)
        
        print(f"原始模型预测: {original_pred}")
        print(f"Pickle加载模型预测: {pickle_pred}")
        print(f"Joblib加载模型预测: {joblib_pred}")
        
        self.assertTrue(np.array_equal(original_pred, pickle_pred))
        self.assertTrue(np.array_equal(original_pred, joblib_pred))
        
        # 清理生成的文件
        import os
        os.remove('model_pickle.pkl')
        os.remove('model_joblib.pkl')
    
    def test_inference_performance(self):
        # 测试单样本推理延迟
        inference_times = []
        for _ in range(100):
            start_time = time.time()
            self.model.predict(self.single_sample)
            inference_time = time.time() - start_time
            inference_times.append(inference_time)
        
        avg_latency = np.mean(inference_times)
        p95_latency = np.percentile(inference_times, 95)
        p99_latency = np.percentile(inference_times, 99)
        
        print(f"平均推理延迟: {avg_latency*1000:.2f}毫秒")
        print(f"P95推理延迟: {p95_latency*1000:.2f}毫秒")
        print(f"P99推理延迟: {p99_latency*1000:.2f}毫秒")
        
        # 验证推理延迟在合理范围内
        self.assertLess(avg_latency, 0.1)  # 平均延迟应小于100毫秒
    
    def test_batch_inference(self):
        # 测试批量推理性能
        batch_sizes = [1, 10, 50, 100]
        
        for batch_size in batch_sizes:
            batch = self.X_test[:batch_size]
            start_time = time.time()
            predictions = self.model.predict(batch)
            inference_time = time.time() - start_time
            
            throughput = batch_size / inference_time  # 每秒处理样本数
            latency_per_sample = (inference_time / batch_size) * 1000  # 每样本毫秒数
            
            print(f"批次大小: {batch_size}")
            print(f"  总推理时间: {inference_time*1000:.2f}毫秒")
            print(f"  吞吐量: {throughput:.2f} 样本/秒")
            print(f"  每样本延迟: {latency_per_sample:.2f}毫秒")
            
            # 验证批量推理的效率（批量应比单样本有更好的吞吐量）
            if batch_size > 1:
                self.assertTrue(throughput > 10)  # 吞吐量应大于10样本/秒
    
    def test_concurrent_requests(self):
        # 测试并发请求处理
        def inference_task(results, index):
            """执行推理并存储结果"""
            start_time = time.time()
            pred = self.model.predict(self.single_sample)
            results[index] = (time.time() - start_time, pred)
        
        num_threads = 20
        results = [None] * num_threads
        threads = []
        
        # 创建并启动线程
        start_time = time.time()
        for i in range(num_threads):
            thread = threading.Thread(target=inference_task, args=(results, i))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # 分析结果
        latencies = [r[0] for r in results]
        avg_latency = np.mean(latencies)
        max_latency = np.max(latencies)
        throughput = num_threads / total_time
        
        print(f"并发请求数: {num_threads}")
        print(f"总耗时: {total_time*1000:.2f}毫秒")
        print(f"平均延迟: {avg_latency*1000:.2f}毫秒")
        print(f"最大延迟: {max_latency*1000:.2f}毫秒")
        print(f"吞吐量: {throughput:.2f} 请求/秒")
    
    def test_model_versioning(self):
        # 测试模型版本管理
        versions = {
            'v1': RandomForestClassifier(n_estimators=50, random_state=42),
            'v2': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        
        # 训练不同版本的模型
        trained_models = {}
        for version, model in versions.items():
            model.fit(self.X_train, self.y_train)
            trained_models[version] = model
            
            # 保存模型
            joblib.dump(model, f'model_{version}.pkl')
        
        # 评估不同版本的性能
        performance = {}
        for version, model in trained_models.items():
            accuracy = model.score(self.X_test, self.y_test)
            performance[version] = accuracy
            print(f"模型版本 {version} 测试集准确率: {accuracy:.4f}")
        
        # 验证新版本性能是否优于或等于旧版本
        self.assertGreaterEqual(performance['v2'], performance['v1'])
        
        # 清理文件
        import os
        for version in versions.keys():
            os.remove(f'model_{version}.pkl')

if __name__ == '__main__':
    unittest.main()
