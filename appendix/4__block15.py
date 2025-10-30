import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder \
        .master("local[1]") \
        .appName("pytest-pyspark") \
        .getOrCreate()
    yield spark
    spark.stop()

def test_dataframe_transformation(spark):
    # 创建测试数据
    schema = StructType([
        StructField("name", StringType()),
        StructField("age", IntegerType())
    ])
    
    data = [
        ("Alice", 30),
        ("Bob", 25),
        ("Charlie", 35)
    ]
    
    df = spark.createDataFrame(data, schema)
    
    # 应用转换
    result = df.filter(df["age"] > 28)
    
    # 创建预期结果
    expected_data = [
        ("Alice", 30),
        ("Charlie", 35)
    ]
    expected = spark.createDataFrame(expected_data, schema)
    
    # 验证结果
    assert sorted(result.collect()) == sorted(expected.collect())
