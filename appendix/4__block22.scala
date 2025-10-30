import org.apache.spark.sql.SparkSession
import org.apache.griffin.measure.context._

val spark = SparkSession.builder()
  .appName("Griffin Data Quality")
  .enableHiveSupport()
  .getOrCreate()

// 创建测量上下文
val contextParam = MeasureContextParam(
  spark = spark,
  config = MeasureConfig.load(configPath),
  env = EnvironmentContext(
    spark.sparkContext.hadoopConfiguration,
    System.currentTimeMillis()
  )
)

val measureContext = MeasureContext(contextParam)

// 执行数据质量测量
measureContext.execute()

// 处理结果
val result = measureContext.getResult
result.save(outputPath)

spark.stop()
