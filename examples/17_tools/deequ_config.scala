// examples/17_tools/deequ_config.scala
import com.amazon.deequ.{VerificationSuite, VerificationResult}
import com.amazon.deequ.checks.{Check, CheckLevel}
import com.amazon.deequ.constraints.ConstraintStatus
import org.apache.spark.sql.{SparkSession, DataFrame}

// 创建Spark会话
val spark = SparkSession.builder()
  .appName("DataQualityValidation")
  .config("spark.sql.adaptive.enabled", "true")
  .getOrCreate()

// 读取测试数据
val df: DataFrame = spark.read
  .option("header", "true")
  .option("inferSchema", "true")
  .csv("/data/input/customer_data.csv")

// 创建验证套件
val verificationSuite = VerificationSuite()
  .onData(df)
  .addCheck(
    Check(CheckLevel.Error, "Data Quality Checks")
      .hasSize(_ >= 1000)  // 数据行数不少于1000
      .isComplete("customer_id")  // customer_id列无空值
      .isUnique("customer_id")  // customer_id列唯一
      .isNonNegative("age")  // age列非负
      .isContainedIn("status", Array("active", "inactive", "pending"))  // status列值域检查
      .hasPattern("email", "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$".r)  // email格式检查
      .hasMaxLength("phone", 20)  // phone列最大长度
  )
  .addCheck(
    Check(CheckLevel.Warning, "Data Distribution Checks")
      .hasApproxQuantile("age", 0.5, _ <= 65.0)  // 年龄中位数不超过65
      .hasApproxCountDistinct("city", _ >= 50)  // 城市数量不少于50
  )

// 执行验证
val verificationResult: VerificationResult = verificationSuite.run()

// 输出验证结果
println("=== Data Quality Verification Results ===")
verificationResult.checkResults.foreach { case (check, result) =>
  println(s"Check: ${check.description}")
  println(s"Status: ${result.status}")
  result.constraintResults.foreach { constraintResult =>
    println(s"  Constraint: ${constraintResult.constraint}")
    println(s"  Status: ${constraintResult.status}")
    if (constraintResult.status != ConstraintStatus.Success) {
      println(s"  Message: ${constraintResult.message.getOrElse("N/A")}")
    }
  }
  println()
}

// 保存验证结果
verificationResult.checkResults
  .map { case (check, result) => (check.description, result.status.toString) }
  .toSeq
  .toDF("check_description", "status")
  .write
  .mode("overwrite")
  .json("/data/output/deequ_results.json")

println("Deequ validation completed successfully!")