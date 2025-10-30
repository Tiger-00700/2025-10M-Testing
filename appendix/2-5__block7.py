import unittest
from pyspark.sql import SparkSession
from pyspark.sql.functions import window, count, expr
from pyspark.sql.types import StructType, StringType, TimestampType

class SparkStreamingTest(unittest.TestCase):
    def setUp(self):
        # 创建测试Spark会话
        self.spark = SparkSession.builder \
            .appName("SparkStreamingTest") \
            .master("local[*]") \
            .config("spark.sql.shuffle.partitions", "1") \
            .getOrCreate()
        
        # 定义测试数据模式
        self.schema = StructType() \
            .add("event_time", TimestampType()) \
            .add("event_type", StringType()) \
            .add("user_id", StringType())
    
    def tearDown(self):
        self.spark.stop()
    
    def test_window_aggregation(self):
        # 创建测试数据
        test_data = [
            ("2023-01-01 00:00:00", "click", "user1"),
            ("2023-01-01 00:01:30", "click", "user2"),
            ("2023-01-01 00:02:00", "view", "user1"),
            ("2023-01-01 00:03:30", "click", "user3"),
            ("2023-01-01 00:04:00", "view", "user2")
        ]
        
        # 创建测试DataFrame
        df = self.spark.createDataFrame(test_data, schema=self.schema)
        
        # 创建内存流表
        df.createOrReplaceTempView("input_table")
        
        # 定义流处理查询
        streaming_df = self.spark.readStream \
            .format("memory") \
            .option("tableName", "input_table") \
            .load(schema=self.schema)
        
        # 执行窗口聚合
        windowed_counts = streaming_df \
            .groupBy(
                window(streaming_df.event_time, "2 minutes"),
                streaming_df.event_type
            ) \
            .count() \
            .orderBy("window")
        
        # 输出到内存表以进行测试
        query = windowed_counts.writeStream \
            .queryName("windowed_results") \
            .outputMode("complete") \
            .format("memory") \
            .start()
        
        # 等待查询完成
        query.awaitTermination(5000)  # 等待5秒
        query.stop()
        
        # 验证结果
        results = self.spark.sql("SELECT * FROM windowed_results").collect()
        
        # 验证窗口聚合结果
        self.assertEqual(len(results), 4)
        
        # 查找特定窗口的计数
        click_count = 0
        view_count = 0
        for row in results:
            if row.event_type == "click":
                click_count += row["count"]
            elif row.event_type == "view":
                view_count += row["count"]
        
        self.assertEqual(3, click_count)  # 总共有3次click事件
        self.assertEqual(2, view_count)   # 总共有2次view事件

if __name__ == "__main__":
    unittest.main()
