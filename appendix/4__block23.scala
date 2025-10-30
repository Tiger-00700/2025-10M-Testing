import com.amazon.deequ.{VerificationSuite, VerificationResult}
import com.amazon.deequ.checks.{Check, CheckLevel}
import com.amazon.deequ.constraints.ConstrainableDataTypes
import com.amazon.deequ.profiles.ColumnProfilerRunner
import org.apache.spark.sql.{DataFrame, SparkSession}

// 初始化Spark会话
val spark = SparkSession.builder()
  .appName("Deequ Data Quality")
  .master("local[*]")
  .getOrCreate()

// 加载测试数据
val df = spark.read
  .option("header", "true")
  .option("inferSchema", "true")
  .csv("/path/to/test_data.csv")

// 执行数据验证
val verificationResult: VerificationResult = {
  VerificationSuite()
    // 指定要验证的DataFrame
    .onData(df)
    // 添加检查
    .addCheck(
      Check(CheckLevel.Error, "Customer Data Validation")
        // 检查customer_id列的唯一性
        .isUnique("customer_id")
        // 检查email列的格式
        .matchesRegex("email", "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")
        // 检查age列的值范围
        .isBetween("age", 18, 100)
        // 检查status列的值集合
        .isContainedIn("status", Seq("active", "inactive", "pending"))
        // 检查name列的非空性
        .isComplete("name")
    )
    .run()
}

// 分析验证结果
if (verificationResult.status == VerificationResult.Status.Success) {
  println("数据质量检查通过！")
} else {
  println("数据质量检查失败：")
  verificationResult.checkResults.foreach {
    case (_, checkResult) => checkResult.constraintResults.foreach {
      case constraintResult if !constraintResult.status =>
        println(s"  - 约束失败: ${constraintResult.constraint}")
        println(s"    消息: ${constraintResult.message.getOrElse("")}")
      case _ =>
    }
  }
}

// 数据特征分析
val result = ColumnProfilerRunner()
  .onData(df)
  .run()

// 输出分析结果
result.profiles.foreach {
  case (columnName, profile) =>
    println(s"列名: $columnName")
    println(s"  数据类型: ${profile.dataType}")
    println(s"  完整性: ${profile.completeness}")
    println(s"  近似唯一值数量: ${profile.approximateNumDistinctValues}")
    
    // 如果是数值类型，输出数值统计信息
    if (profile.isNumeric) {
      println(s"  最小值: ${profile.minimum}")
      println(s"  最大值: ${profile.maximum}")
      println(s"  平均值: ${profile.mean}")
      println(s"  标准差: ${profile.stdDev}")
    }
}

spark.stop()
