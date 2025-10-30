import org.apache.spark.sql.Row
import org.apache.spark.sql.types._
import com.holdenkarau.spark.testing._
import org.scalatest.FunSuite

class SparkDataFrameTest extends FunSuite with DataFrameSuiteBase {
  test("test dataframe transformation") {
    // 创建测试数据
    val schema = StructType(Array(
      StructField("name", StringType),
      StructField("age", IntegerType)
    ))
    
    val data = Seq(
      Row("Alice", 30),
      Row("Bob", 25),
      Row("Charlie", 35)
    )
    
    val df = spark.createDataFrame(spark.sparkContext.parallelize(data), schema)
    
    // 应用转换
    val result = df.filter(df("age") > 28)
    
    // 创建预期结果
    val expectedData = Seq(
      Row("Alice", 30),
      Row("Charlie", 35)
    )
    val expected = spark.createDataFrame(spark.sparkContext.parallelize(expectedData), schema)
    
    // 验证结果
    assertDataFrameEquals(expected, result)
  }
}
