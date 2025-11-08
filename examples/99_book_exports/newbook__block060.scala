// Spark SQL自动化测试示例
import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._
import org.scalatest._

class SparkSqlTest extends FlatSpec with Matchers with BeforeAndAfter {
  private var spark: SparkSession = _
  private val testDataPath = "/tmp/spark_test_data"

  // 测试前准备
  before {
    // 创建SparkSession
    spark = SparkSession.builder()
      .appName("Spark SQL Test")
      .master("local[*]")
      .config("spark.sql.shuffle.partitions", "1")
      .getOrCreate()

    // 准备测试数据
    import spark.implicits._

    val testData = Seq(
      (1, "Alice", 30, "New York"),
      (2, "Bob", 35, "Boston"),
      (3, "Charlie", 40, "Chicago"),
      (4, "David", 25, "Dallas"),
      (5, "Eva", 45, "Los Angeles")
    )

    val df = testData.toDF("id", "name", "age", "city")
    df.write.mode("overwrite").parquet(testDataPath)
  }

  // 测试后清理
  after {
    // 停止SparkSession
    spark.stop()

    // 清理测试数据
    import java.io.File
    val dir = new File(testDataPath)
    if (dir.exists()) {
      dir.listFiles().foreach(_.delete())
      dir.delete()
    }
  }

  // 测试DataFrame读取
  "Spark DataFrame" should "correctly read parquet data" in {
    val df = spark.read.parquet(testDataPath)

    // 验证数据条数
    df.count() should be (5)

    // 验证数据结构
    df.columns should contain allOf ("id", "name", "age", "city")

    // 验证数据内容
    val firstRow = df.first()
    firstRow.getAs[Int]("id") should be (1)
    firstRow.getAs[String]("name") should be ("Alice")
  }

  // 测试SQL查询
  "Spark SQL" should "correctly execute SQL queries" in {
    // 创建临时表
    val df = spark.read.parquet(testDataPath)
    df.createOrReplaceTempView("users")

    // 执行SQL查询
    val result = spark.sql("""
      SELECT name, age
      FROM users
      WHERE age > 30
      ORDER BY age DESC
    """)

    // 验证查询结果
    result.count() should be (2)

    val rows = result.collect()
    rows(0).getAs[String]("name") should be ("Charlie")
    rows(0).getAs[Int]("age") should be (40)
    rows(1).getAs[String]("name") should be ("Bob")
    rows(1).getAs[Int]("age") should be (35)
  }

  // 测试DataFrame操作
  "DataFrame operations" should "produce correct results" in {
    val df = spark.read.parquet(testDataPath)

    // 测试过滤和聚合
    val result = df
      .filter(col("age") > 30)
      .groupBy("city")
      .agg(avg("age").as("avg_age"))
      .orderBy(desc("avg_age"))

    // 验证结果
    result.count() should be (2)

    val rows = result.collect()
    rows(0).getAs[Double]("avg_age") should be (40.0)
    rows(1).getAs[Double]("avg_age") should be (35.0)
  }

  // 测试UDF
  "Spark UDF" should "work correctly" in {
    val df = spark.read.parquet(testDataPath)

    // 注册UDF
    spark.udf.register("calculate_birth_year", (age: Int) => 2023 - age)

    // 使用UDF
    val result = df.select(
      col("name"),
      col("age"),
      expr("calculate_birth_year(age) as birth_year")
    )

    // 验证UDF结果
    val aliceRow = result.filter(col("name") === "Alice").first()
    aliceRow.getAs[Int]("birth_year") should be (1993)
  }
}

> 【小结】

- 用 3~5 条项目化要点复盘本章内容
- 指出易错点/反模式与纠正建议
- 给出可延伸阅读或下一步实践方向
