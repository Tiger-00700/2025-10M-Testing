import time
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, rand
import matplotlib.pyplot as plt
import os

class ScalabilityTest:
    def __init__(self):
        # 初始化为空，在测试方法中根据需要创建不同配置的Spark会话
        self.spark = None
    
    def _create_spark_session(self, app_name, num_executors=None, executor_cores=None, executor_memory=None):
        """创建具有指定配置的Spark会话"""
        builder = SparkSession.builder \
            .appName(app_name) \
            .master("local[*]")  # 在实际测试中应替换为集群URL
        
        # 添加配置参数（如果指定）
        if num_executors is not None:
            builder = builder.config("spark.executor.instances", num_executors)
        if executor_cores is not None:
            builder = builder.config("spark.executor.cores", executor_cores)
        if executor_memory is not None:
            builder = builder.config("spark.executor.memory", executor_memory)
        
        # 关闭之前的Spark会话（如果存在）
        if self.spark is not None:
            self.spark.stop()
        
        # 创建新的Spark会话
        self.spark = builder.getOrCreate()
        print(f"创建Spark会话: {app_name}")
        print(f"配置: 执行器={num_executors}, 核心数={executor_cores}, 内存={executor_memory}")
    
    def test_vertical_scalability(self, data_size_gb):
        """测试垂直扩展性（增加单机资源）"""
        print(f"\n开始垂直扩展性测试: 数据量={data_size_gb}GB")
        
        # 定义不同的资源配置（模拟不同规格的服务器）
        configurations = [
            {"name": "小配置", "executor_cores": 2, "executor_memory": "2g"},
            {"name": "中配置", "executor_cores": 4, "executor_memory": "4g"},
            {"name": "大配置", "executor_cores": 8, "executor_memory": "8g"}
        ]
        
        results = []
        
        for config in configurations:
            # 创建指定配置的Spark会话
            self._create_spark_session(
                f"VerticalTest-{config['name']}",
                num_executors=1,  # 单机测试，只有一个执行器
                executor_cores=config['executor_cores'],
                executor_memory=config['executor_memory']
            )
            
            # 运行性能测试
            performance = self._run_performance_test(data_size_gb)
            results.append({
                "name": config['name'],
                "cores": config['executor_cores'],
                "memory": config['executor_memory'],
                "time": performance['time'],
                "throughput": performance['throughput']
            })
            
            print(f"配置: {config['name']}, 处理时间: {performance['time']:.2f}秒, 吞吐量: {performance['throughput']:.2f} GB/小时")
        
        # 分析扩展性
        self._analyze_scalability(results, "垂直扩展性")
        
        return results
    
    def test_horizontal_scalability(self, data_size_gb):
        """测试水平扩展性（增加节点数量）"""
        print(f"\n开始水平扩展性测试: 数据量={data_size_gb}GB")
        
        # 定义不同的节点配置（模拟不同规模的集群）
        configurations = [
            {"name": "1节点", "executors": 1},
            {"name": "2节点", "executors": 2},
            {"name": "4节点", "executors": 4},
            {"name": "8节点", "executors": 8}
        ]
        
        results = []
        
        for config in configurations:
            # 创建指定配置的Spark会话
            self._create_spark_session(
                f"HorizontalTest-{config['name']}",
                num_executors=config['executors'],
                executor_cores=2,  # 每节点固定2核
                executor_memory="2g"  # 每节点固定2GB内存
            )
            
            # 运行性能测试
            performance = self._run_performance_test(data_size_gb)
            results.append({
                "name": config['name'],
                "executors": config['executors'],
                "time": performance['time'],
                "throughput": performance['throughput']
            })
            
            print(f"配置: {config['name']}, 处理时间: {performance['time']:.2f}秒, 吞吐量: {performance['throughput']:.2f} GB/小时")
        
        # 分析扩展性
        self._analyze_scalability(results, "水平扩展性")
        
        return results
    
    def test_data_scalability(self):
        """测试数据扩展性（增加数据量）"""
        print("\n开始数据扩展性测试")
        
        # 创建固定配置的Spark会话
        self._create_spark_session(
            "DataScalabilityTest",
            num_executors=4,
            executor_cores=2,
            executor_memory="4g"
        )
        
        # 测试不同数据量
        data_sizes = [0.1, 0.2, 0.4, 0.8, 1.6]  # GB
        results = []
        
        for size in data_sizes:
            # 运行性能测试
            performance = self._run_performance_test(size)
            results.append({
                "data_size": size,
                "time": performance['time'],
                "throughput": performance['throughput']
            })
            
            print(f"数据量: {size}GB, 处理时间: {performance['time']:.2f}秒, 吞吐量: {performance['throughput']:.2f} GB/小时")
        
        # 分析数据扩展性
        self._analyze_data_scalability(results)
        
        return results
    
    def _run_performance_test(self, data_size_gb):
        """运行基本性能测试"""
        # 估算记录数（假设每条记录约1KB）
        records_per_gb = 1024 * 1024
        num_records = int(data_size_gb * records_per_gb)
        
        # 生成测试数据
        df = self.spark.range(num_records) \
            .withColumn("random_data", rand().cast("string")) \
            .withColumn("data", (col("id").cast("string") + col("random_data")).substr(0, 1000))
        
        # 缓存数据以确保后续操作只测量计算性能
        df.cache()
        df.count()  # 触发缓存
        
        # 执行数据处理操作并测量时间
        start_time = time.time()
        
        # 执行典型的数据转换和聚合操作
        result = df \
            .filter(col("id") % 2 == 0) \
            .withColumn("processed", col("data").substr(0, 500)) \
            .groupBy(col("id") % 1000) \
            .count()
        
        # 触发执行
        count = result.count()
        
        end_time = time.time()
        process_time = end_time - start_time
        
        # 计算吞吐量（GB/小时）
        throughput = (data_size_gb / process_time) * 3600
        
        return {
            "time": process_time,
            "throughput": throughput,
            "count": count
        }
    
    def _analyze_scalability(self, results, test_type):
        """分析扩展性测试结果"""
        print(f"\n{test_type}分析:")
        
        # 计算扩展比率和效率
        for i in range(1, len(results)):
            prev = results[i-1]
            current = results[i]
            
            # 根据测试类型确定资源比率
            if "cores" in current:
                resource_ratio = current["cores"] / prev["cores"]
                resource_type = "核心数"
            else:
                resource_ratio = current["executors"] / prev["executors"]
                resource_type = "执行器数量"
            
            # 计算性能比率
            time_ratio = prev["time"] / current["time"]
            throughput_ratio = current["throughput"] / prev["throughput"]
            
            # 计算扩展效率
            time_efficiency = time_ratio / resource_ratio * 100
            throughput_efficiency = throughput_ratio / resource_ratio * 100
            
            print(f"从 {prev['name']} 到 {current['name']} ({resource_type}增加{resource_ratio:.1f}倍):")
            print(f"  处理时间减少: {time_ratio:.2f}倍 (效率: {time_efficiency:.1f}%)")
            print(f"  吞吐量提升: {throughput_ratio:.2f}倍 (效率: {throughput_efficiency:.1f}%)")
    
    def _analyze_data_scalability(self, results):
        """分析数据扩展性测试结果"""
        print("\n数据扩展性分析:")
        
        # 计算数据增长和时间增长的比例
        for i in range(1, len(results)):
            prev = results[i-1]
            current = results[i]
            
            data_ratio = current["data_size"] / prev["data_size"]
            time_ratio = current["time"] / prev["time"]
            throughput_ratio = prev["throughput"] / current["throughput"]  # 反向比较
            
            print(f"从 {prev['data_size']}GB 到 {current['data_size']}GB (数据增加{data_ratio:.1f}倍):")
            print(f"  处理时间增加: {time_ratio:.2f}倍 (理想应为{data_ratio:.1f}倍)")
            print(f"  吞吐量变化: {throughput_ratio:.2f}倍 (理想应为1.0倍)")
    
    def close(self):
        """关闭Spark会话"""
        if self.spark is not None:
            self.spark.stop()
            print("Spark会话已关闭")

# 主函数示例
if __name__ == "__main__":
    test = ScalabilityTest()
    try:
        # 测试垂直扩展性
        test.test_vertical_scalability(0.5)  # 0.5GB数据
        
        # 测试水平扩展性
        test.test_horizontal_scalability(1.0)  # 1GB数据
        
        # 测试数据扩展性
        test.test_data_scalability()
    finally:
        test.close()

## 5.6 测试工具

在大数据处理测试中，选择合适的测试工具对于提高测试效率和质量至关重要。本节将介绍各类数据处理测试中常用的工具，包括批处理、流处理、机器学习、性能测试以及监控和调试工具，帮助读者根据实际需求选择合适的测试工具。

### 5.6.1 批处理测试工具
批处理测试工具专门用于验证批处理作业的正确性、性能和稳定性。以下是几种常用的批处理测试工具：

- **Hadoop MRUnit**：MapReduce单元测试框架，提供模拟MapReduce作业执行环境的能力。它允许开发者独立测试Mapper、Reducer和整个MapReduce作业，无需启动完整的Hadoop集群。MRUnit支持不同的测试模式，包括流模式和管道模式，可以验证输入/输出关系和中间结果。
- **Spark Testing Base**：Spark测试库，提供了丰富的测试工具和断言方法，简化Spark应用的测试。它支持对RDD、DataFrame和Dataset的测试，提供了测试Spark Streaming和结构化流处理的功能。Spark Testing Base可以帮助开发者编写简洁、可靠的Spark应用测试用例。
- **HiveRunner**：Hive查询测试框架，允许在隔离环境中测试Hive查询。它可以创建内存中的Hive元数据和数据存储，支持模拟外部表和UDF，使Hive查询的单元测试变得简单高效。
- **Apache Airflow**：工作流调度和测试工具，可以用于测试数据处理管道的端到端执行。Airflow提供了丰富的测试功能，包括DAG验证、任务依赖检查和模拟执行。它还支持与多种数据源和处理引擎的集成，使复杂数据处理流程的测试变得更加简单。
- **Luigi**：Python批处理工作流测试工具，专注于数据处理管道的构建和测试。Luigi提供了任务依赖管理、并行执行和失败重试机制，支持测试单个任务和整个工作流。它的简单API和丰富的集成使其成为Python数据处理测试的理想选择。
- **Dagster**：现代化数据编排和测试工具，提供了强大的开发体验和测试功能。Dagster的设计理念是将数据处理视为代码，支持单元测试、集成测试和端到端测试。它还提供了丰富的可视化工具，帮助开发者理解和调试数据处理流程。

**Spark Testing Base使用示例**：
```scala
import com.holdenkarau.spark.testing.{DataFrameSuiteBase, SharedSparkContext}
import org.apache.spark.sql.{Row, SparkSession}
import org.apache.spark.sql.types.{IntegerType, StringType, StructField, StructType}
import org.scalatest.FunSuite

class SparkDataProcessorTest extends FunSuite with DataFrameSuiteBase {
  
  test("测试数据过滤功能") {
    // 准备测试数据
    val schema = StructType(Seq(
      StructField("id", IntegerType),
      StructField("name", StringType),
      StructField("age", IntegerType)
    ))
    
    val testData = Seq(
      Row(1, "Alice", 30),
      Row(2, "Bob", 25),
      Row(3, "Charlie", 35),
      Row(4, "David", 20)
    )
    
    val inputDF = spark.createDataFrame(spark.sparkContext.parallelize(testData), schema)
    
    // 执行被测试的处理逻辑
    val resultDF = inputDF.filter("age > 25")
    
    // 准备期望结果
    val expectedData = Seq(
      Row(1, "Alice", 30),
      Row(3, "Charlie", 35)
    )
    
    val expectedDF = spark.createDataFrame(spark.sparkContext.parallelize(expectedData), schema)
    
    // 使用Spark Testing Base的断言方法验证结果
    assertDataFrameEquals(expectedDF, resultDF)
  }
  
  test("测试数据聚合功能") {
    // 准备测试数据
    import spark.implicits._
    val testData = Seq(
      ("A", 10),
      ("B", 20),
      ("A", 30),
      ("C", 15)
    ).toDF("category", "value")
    
    // 执行聚合操作
    val resultDF = testData.groupBy("category").sum("value")
    
    // 验证结果行数
    assert(resultDF.count() === 3)
    
    // 验证特定分组的聚合结果
    val aSum = resultDF.filter("category = 'A'")
      .select("sum(value)").head().getLong(0)
    assert(aSum === 40L)
  }
}
