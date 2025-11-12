
     // 大数据性能数据收集器示例
     import org.apache.spark.SparkConf;
     import org.apache.spark.api.java.JavaSparkContext;
     import org.apache.spark.scheduler.*;
     import java.util.HashMap;
     import java.util.Map;
     import java.time.LocalDateTime;
     import java.time.format.DateTimeFormatter;
     import java.io.FileWriter;
     import java.io.IOException;

     public class PerformanceDataCollector implements SparkListener {
         private Map<String, JobMetrics> jobMetricsMap = new HashMap<>();
         private String outputDir;

         public PerformanceDataCollector(String outputDir) {
             this.outputDir = outputDir;
         }

         @Override
         public void onJobStart(SparkListenerJobStart jobStart) {
             String jobId = String.valueOf(jobStart.jobId());
             JobMetrics metrics = new JobMetrics();
             metrics.setStartTime(System.currentTimeMillis());
             metrics.setStageIds(jobStart.stageInfos().stream()
                     .map(stageInfo -> String.valueOf(stageInfo.stageId()))
                     .toArray(String[]::new));
             jobMetricsMap.put(jobId, metrics);
         }

         @Override
         public void onJobEnd(SparkListenerJobEnd jobEnd) {
             String jobId = String.valueOf(jobEnd.jobId());
             JobMetrics metrics = jobMetricsMap.get(jobId);
             if (metrics != null) {
                 metrics.setEndTime(System.currentTimeMillis());
                 metrics.setDuration(metrics.getEndTime() - metrics.getStartTime());
                 metrics.setStatus(jobEnd.jobResult().toString());

                 // 保存指标数据
                 saveJobMetrics(jobId, metrics);
             }
         }

         private void saveJobMetrics(String jobId, JobMetrics metrics) {
             try (FileWriter writer = new FileWriter(
                     outputDir + "/job_metrics_" + LocalDateTime.now().format(
                             DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")) + ".csv", true)) {
                 writer.write(jobId + "," +
                             metrics.getStartTime() + "," +
                             metrics.getEndTime() + "," +
                             metrics.getDuration() + "," +
                             metrics.getStatus() + "\n");
             } catch (IOException e) {
                 e.printStackTrace();
             }
         }

         // JobMetrics 类定义
         private static class JobMetrics {
             private long startTime;
             private long endTime;
             private long duration;
             private String status;
             private String[] stageIds;

             // Getters and setters
             public long getStartTime() { return startTime; }
             public void setStartTime(long startTime) { this.startTime = startTime; }
             public long getEndTime() { return endTime; }
             public void setEndTime(long endTime) { this.endTime = endTime; }
             public long getDuration() { return duration; }
             public void setDuration(long duration) { this.duration = duration; }
             public String getStatus() { return status; }
             public void setStatus(String status) { this.status = status; }
             public String[] getStageIds() { return stageIds; }
             public void setStageIds(String[] stageIds) { this.stageIds = stageIds; }
         }

         // 使用示例
         public static void main(String[] args) {
             SparkConf conf = new SparkConf().setAppName("PerformanceTesting");
             JavaSparkContext sc = new JavaSparkContext(conf);

             // 添加性能监听器
             sc.sc().addSparkListener(new PerformanceDataCollector("/path/to/metrics"));

             // 执行Spark作业...

             sc.close();
         }
     }
