
     # 大数据量测试数据生成框架
     from pyspark.sql import SparkSession
     import random
     from datetime import datetime, timedelta

     def generate_test_data(spark, num_records, output_path):
         # 定义数据生成函数
         def create_record(_):
             user_id = random.randint(1, 1000000)
             # 模拟用户活跃度分布（长尾分布）
             activity_prob = 0.8 if user_id <= 200000 else 0.2
             active = random.random() < activity_prob

             # 生成时间戳（近一年的数据）
             base_date = datetime(2024, 1, 1)
             random_days = random.randint(0, 365)
             timestamp = base_date + timedelta(days=random_days, hours=random.randint(0, 23))

             # 生成其他字段
             transaction_amount = random.uniform(10.0, 10000.0)
             product_category = random.choice(['electronics', 'clothing', 'food', 'home', 'sports'])

             return (
                 user_id,
                 active,
                 timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                 round(transaction_amount, 2),
                 product_category
             )

         # 使用Spark并行生成数据
         rdd = spark.sparkContext.parallelize(range(num_records))
             .map(create_record)
             .toDF(["user_id", "is_active", "transaction_time", "amount", "category"])

         # 保存数据
         rdd.write.parquet(output_path)
         print(f"生成了 {num_records} 条测试数据，保存在 {output_path}")

     # 示例调用
     spark = SparkSession.builder.appName("TestDataGenerator").getOrCreate()
     generate_test_data(spark, 100000000, "/data/test/sales_data.parquet")
