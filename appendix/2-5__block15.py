import time
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, rand
import threading

class ThroughputTest:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("ThroughputTest") \
            .master("local[*]") \
            .getOrCreate()
    
    def test_batch_throughput(self, data_size_gb):
        """测试批处理吞吐量"""
        # 估算每条记录大小，生成近似指定GB的数据
        # 假设每条记录约1KB
        records_per_gb = 1024 * 1024
        num_records = int(data_size_gb * records_per_gb)
        
        print(f"开始批处理吞吐量测试：{data_size_gb}GB 数据")
        
        # 生成测试数据
        start_time = time.time()
        
        # 使用Spark生成测试数据
        df = self.spark.range(num_records) \
            .withColumn("random_data", rand().cast("string")) \
            .withColumn("data", (col("id").cast("string") + col("random_data")).substr(0, 1000))
        
        # 缓存数据以确保后续操作只测量计算性能
        df.cache()
        df.count()  # 触发缓存
        
        data_gen_time = time.time() - start_time
        print(f"数据生成时间: {data_gen_time:.2f}秒")
        
        # 执行数据处理操作
        process_start = time.time()
        
        # 执行典型的数据转换操作
        result = df \
            .filter(col("id") % 2 == 0) \
            .groupBy(col("id") % 1000)
            .count()
        
        # 触发执行并获取结果数量
        count = result.count()
        
        process_time = time.time() - process_start
        
        # 计算吞吐量
        throughput_gb_per_hour = (data_size_gb / process_time) * 3600
        throughput_records_per_second = (num_records / process_time)
        
        print(f"批处理完成，处理记录数: {count}")
        print(f"处理时间: {process_time:.2f}秒")
        print(f"吞吐量: {throughput_gb_per_hour:.2f} GB/小时")
        print(f"吞吐量: {throughput_records_per_second:,.2f} 记录/秒")
        
        return throughput_gb_per_hour
    
    def test_concurrent_throughput(self, num_threads, data_size_per_thread):
        """测试并发吞吐量"""
        print(f"开始并发吞吐量测试：{num_threads} 线程，每线程 {data_size_per_thread}GB")
        
        threads = []
        results = [0] * num_threads
        
        def worker(thread_id):
            try:
                # 为每个线程创建独立的Spark上下文可能更准确
                # 但为简化示例，这里复用主SparkSession
                thread_spark = SparkSession.builder \
                    .appName(f"ConcurrentTest-{thread_id}") \
                    .getOrCreate()
                
                # 生成线程特定的数据
                records_per_gb = 1024 * 1024  # 假设每条记录约1KB
                num_records = int(data_size_per_thread * records_per_gb)
                
                df = thread_spark.range(num_records) \
                    .withColumn("thread_id", col("id") % num_threads) \
                    .filter(col("thread_id") == thread_id)
                
                # 执行操作
                start_time = time.time()
                count = df.count()
                process_time = time.time() - start_time
                
                # 计算线程吞吐量
                thread_throughput = (data_size_per_thread / process_time) * 3600
                results[thread_id] = thread_throughput
                
                print(f"线程 {thread_id} 完成，处理记录数: {count}, 时间: {process_time:.2f}秒, 吞吐量: {thread_throughput:.2f} GB/小时")
            except Exception as e:
                print(f"线程 {thread_id} 错误: {str(e)}")
        
        # 启动所有线程
        start_time = time.time()
        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        total_throughput = sum(results)
        
        print(f"并发测试完成，总时间: {total_time:.2f}秒")
        print(f"总吞吐量: {total_throughput:.2f} GB/小时")
        print(f"平均单线程吞吐量: {np.mean(results):.2f} GB/小时")
        print(f"吞吐量比率 (总吞吐量/(单线程吞吐量*线程数)): {total_throughput/(np.mean(results)*num_threads):.2f}")
        
        return total_throughput
    
    def test_long_term_stability(self, duration_minutes, data_size_per_iteration):
        """测试长期稳定性"""
        print(f"开始长期稳定性测试：持续 {duration_minutes} 分钟")
        
        end_time = time.time() + (duration_minutes * 60)
        iteration = 0
        throughputs = []
        
        while time.time() < end_time:
            iteration += 1
            print(f"\n迭代 {iteration} 开始")
            
            try:
                throughput = self.test_batch_throughput(data_size_per_iteration)
                throughputs.append(throughput)
                
                # 短暂休息避免系统过载
                time.sleep(5)
            except Exception as e:
                print(f"迭代 {iteration} 错误: {str(e)}")
        
        # 分析结果
        avg_throughput = np.mean(throughputs)
        std_throughput = np.std(throughputs)
        max_throughput = np.max(throughputs)
        min_throughput = np.min(throughputs)
        
        print("\n长期稳定性测试结果:")
        print(f"执行迭代次数: {iteration}")
        print(f"平均吞吐量: {avg_throughput:.2f} GB/小时")
        print(f"吞吐量标准差: {std_throughput:.2f} GB/小时")
        print(f"最大吞吐量: {max_throughput:.2f} GB/小时")
        print(f"最小吞吐量: {min_throughput:.2f} GB/小时")
        print(f"吞吐量波动: {(max_throughput - min_throughput) / avg_throughput * 100:.2f}%")
    
    def close(self):
        """关闭Spark会话"""
        if self.spark:
            self.spark.stop()

# 主函数示例
if __name__ == "__main__":
    test = ThroughputTest()
    try:
        # 测试不同数据量的批处理吞吐量
        test.test_batch_throughput(0.1)  # 0.1GB数据
        test.test_batch_throughput(0.5)  # 0.5GB数据
        
        # 测试并发吞吐量
        test.test_concurrent_throughput(4, 0.1)  # 4线程，每线程0.1GB
        
        # 测试长期稳定性（10分钟）
        test.test_long_term_stability(10, 0.05)  # 10分钟，每次0.05GB
    finally:
        test.close()
