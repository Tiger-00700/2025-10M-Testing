import pandas as pd
import unittest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, upper, regexp_replace

class DataTransformationTest(unittest.TestCase):
    def setUp(self):
        # 初始化Spark会话
        self.spark = SparkSession.builder \
            .appName("DataTransformationTest") \
            .master("local[*]") \
            .getOrCreate()
        
        # 创建测试数据
        self.test_data = [
            (1, "john doe", "25.5", "2023-01-15"),
            (2, "jane smith", "30.0", "2023-02-20"),
            (3, "BOB JONES", "45.25", "2023-03-10"),
            (4, "", "-999", "invalid-date")
        ]
        self.columns = ["id", "name", "score", "date"]
        self.df = self.spark.createDataFrame(self.test_data, self.columns)
    
    def tearDown(self):
        self.spark.stop()
    
    def test_field_mapping_and_transformation(self):
        # 执行数据转换
        transformed_df = self.df.select(
            col("id"),
            upper(col("name")).alias("name_upper"),
            when(col("score") == "-999", None).otherwise(col("score").cast("float")).alias("score_float"),
            when(col("date").rlike("\\d{4}-\\d{2}-\\d{2}"), col("date")).otherwise(None).alias("valid_date")
        )
        
        # 收集结果
        result = transformed_df.collect()
        
        # 验证转换结果
        self.assertEqual(result[0][1], "JOHN DOE")
        self.assertEqual(result[0][2], 25.5)
        self.assertEqual(result[0][3], "2023-01-15")
        
        # 验证异常处理
        self.assertEqual(result[3][1], "")
        self.assertIsNone(result[3][2])
        self.assertIsNone(result[3][3])
    
    def test_data_cleaning(self):
        # 执行数据清洗
        cleaned_df = self.df \
            .filter(col("name") != "") \
            .withColumn("cleaned_name", regexp_replace(col("name"), " ", "_"))
        
        # 收集结果
        result = cleaned_df.collect()
        
        # 验证清洗结果
        self.assertEqual(len(result), 3)  # 空字符串记录已被过滤
        self.assertEqual(result[0][4], "john_doe")  # 空格已替换为下划线

if __name__ == "__main__":
    unittest.main()
