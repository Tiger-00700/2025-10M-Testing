import unittest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum

class SparkDataFrameTest(unittest.TestCase):
    def setUp(self):
        self.spark = SparkSession.builder \
            .appName("Test") \
            .master("local[*]") \
            .getOrCreate()
        
        # 创建测试数据
        self.data = [
            ("A", 100),
            ("B", 200),
            ("C", 300),
            ("A", 400)
        ]
        self.df = self.spark.createDataFrame(self.data, ["category", "amount"])
    
    def tearDown(self):
        self.spark.stop()
    
    def test_filter_operation(self):
        # 测试过滤操作
        filtered_df = self.df.filter(col("amount") > 200)
        result = filtered_df.collect()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], "C")
        self.assertEqual(result[1][0], "A")
    
    def test_aggregation(self):
        # 测试聚合操作
        agg_df = self.df.groupBy("category").agg(sum("amount").alias("total"))
        result = agg_df.orderBy("category").collect()
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][0], "A")
        self.assertEqual(result[0][1], 500)
        self.assertEqual(result[1][0], "B")
        self.assertEqual(result[1][1], 200)
        self.assertEqual(result[2][0], "C")
        self.assertEqual(result[2][1], 300)
    
    def test_sql_query(self):
        # 测试SQL查询
        self.df.createOrReplaceTempView("test_table")
        result_df = self.spark.sql("""
            SELECT category, SUM(amount) as total 
            FROM test_table 
            GROUP BY category 
            ORDER BY total DESC
        """)
        
        result = result_df.collect()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][0], "A")
        self.assertEqual(result[0][1], 500)

if __name__ == "__main__":
    unittest.main()
