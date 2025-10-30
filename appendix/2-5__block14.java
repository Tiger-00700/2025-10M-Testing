import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

public class LatencyTest {
    private final SparkSession spark;
    
    public LatencyTest() {
        this.spark = SparkSession.builder()
                .appName("LatencyTest")
                .master("local[*]")
                .getOrCreate();
    }
    
    public void testBatchProcessingLatency(int dataSize) {
        // 准备测试数据
        List<String> testData = generateTestData(dataSize);
        
        // 测量批处理延迟
        long startTime = System.currentTimeMillis();
        
        // 执行数据处理操作
        Dataset<Row> df = spark.createDataset(testData, org.apache.spark.sql.Encoders.STRING())
                .toDF("data")
                .filter("data LIKE '%test%'")
                .groupBy("data")
                .count();
        
        // 执行action触发计算
        df.count();
        
        long endTime = System.currentTimeMillis();
        long latency = endTime - startTime;
        
        System.out.println(String.format("批处理延迟测试: 数据量=%d, 延迟=%d毫秒", dataSize, latency));
    }
    
    public void testComponentLevelLatency() {
        // 准备测试数据
        List<String> testData = generateTestData(100000);
        
        // 测量数据加载延迟
        long loadStart = System.currentTimeMillis();
        Dataset<Row> df = spark.createDataset(testData, org.apache.spark.sql.Encoders.STRING())
                .toDF("data");
        long loadEnd = System.currentTimeMillis();
        
        // 测量过滤操作延迟
        long filterStart = System.currentTimeMillis();
        Dataset<Row> filtered = df.filter("data LIKE '%test%'");
        filtered.count();  // 触发执行
        long filterEnd = System.currentTimeMillis();
        
        // 测量聚合操作延迟
        long aggregateStart = System.currentTimeMillis();
        Dataset<Row> aggregated = filtered.groupBy("data").count();
        aggregated.count();  // 触发执行
        long aggregateEnd = System.currentTimeMillis();
        
        System.out.println(String.format("数据加载延迟: %d毫秒", loadEnd - loadStart));
        System.out.println(String.format("过滤操作延迟: %d毫秒", filterEnd - filterStart));
        System.out.println(String.format("聚合操作延迟: %d毫秒", aggregateEnd - aggregateStart));
    }
    
    public void testColdStartLatency() {
        // 关闭现有Spark会话模拟冷启动
        spark.stop();
        
        // 测量冷启动延迟
        long start = System.currentTimeMillis();
        SparkSession newSpark = SparkSession.builder()
                .appName("ColdStartTest")
                .master("local[*]")
                .getOrCreate();
        
        // 执行简单操作验证启动完成
        newSpark.range(100).count();
        
        long end = System.currentTimeMillis();
        System.out.println(String.format("冷启动延迟: %d毫秒", end - start));
        
        // 重新初始化spark引用
        this.spark = newSpark;
    }
    
    private List<String> generateTestData(int size) {
        List<String> data = new ArrayList<>(size);
        for (int i = 0; i < size; i++) {
            data.add("test_data_" + i);
        }
        return data;
    }
    
    public void close() {
        if (spark != null) {
            spark.stop();
        }
    }
    
    public static void main(String[] args) {
        LatencyTest test = new LatencyTest();
        try {
            // 测试不同数据量的批处理延迟
            test.testBatchProcessingLatency(10000);
            test.testBatchProcessingLatency(100000);
            test.testBatchProcessingLatency(1000000);
            
            // 测试组件级延迟
            test.testComponentLevelLatency();
            
            // 测试冷启动延迟
            test.testColdStartLatency();
        } finally {
            test.close();
        }
    }
}
