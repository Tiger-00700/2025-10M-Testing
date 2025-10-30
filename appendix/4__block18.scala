import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class SparkRestApiSimulation extends Simulation {
  // 配置HTTP协议
  val httpConf = http
    .baseUrl("http://spark-cluster:8080")
    .acceptHeader("application/json")
    .contentTypeHeader("application/json")
    .userAgentHeader("Gatling/3.9")
  
  // 定义测试场景
  val scn = scenario("Spark REST API Test")
    .exec(
      http("Submit Spark Job")
        .post("/api/v1/submit")
        .body(StringBody("""{
          "jobName": "${jobName}",
          "parameters": {
            "input": "/data/input",
            "output": "/data/output",
            "partitions": ${partitions}
          }
        }"""
        )).asJson
        .check(status.is(200))
        .check(jsonPath("$.jobId").saveAs("jobId"))
    )
    .pause(2 seconds)
    .exec(
      http("Check Job Status")
        .get("/api/v1/job/${jobId}/status")
        .check(status.is(200))
        .check(jsonPath("$.status").is("RUNNING"))
    )
  
  // 设置数据生成器
  val feeder = Iterator.continually(Map(
    "jobName" -> s"test-job-${scala.util.Random.nextInt(10000)}",
    "partitions" -> scala.util.Random.nextInt(100) + 1
  ))
  
  // 注入用户
  setUp(
    scn
      .feed(feeder)
      .inject(
        rampUsers(100) during (60 seconds),
        constantUsersPerSec(10) during (5 minutes)
      )
      .protocols(httpConf)
  )
}
