import java.lang.management.ManagementFactory;
import java.lang.management.OperatingSystemMXBean;
import java.lang.reflect.Method;
import java.util.concurrent.TimeUnit;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.SparkSession;
import java.util.ArrayList;
import java.util.List;

public class ResourceUtilizationTest {
    private final SparkSession spark;
    private final JavaSparkContext jsc;
    private final OperatingSystemMXBean osBean;
    
    public ResourceUtilizationTest() {
        this.spark = SparkSession.builder()
                .appName("ResourceUtilizationTest")
                .master("local[*]")
                .config("spark.memory.fraction", 0.8)  // 调整Spark内存配置
                .getOrCreate();
        
        this.jsc = new JavaSparkContext(spark.sparkContext());
        this.osBean = ManagementFactory.getOperatingSystemMXBean();
    }
    
    public void testCPUUtilization(int dataSize) {
        System.out.println("\n开始CPU利用率测试");
        
        // 获取测试开始前的CPU使用率基线
        double baselineCPU = getCPUUsage();
        System.out.println(String.format("基线CPU使用率: %.2f%%", baselineCPU));
        
        // 生成测试数据
        List<String> testData = generateTestData(dataSize);
        JavaRDD<String> rdd = jsc.parallelize(testData);
        
        // 创建一个线程监控CPU使用率
        Thread monitorThread = new Thread(() -> {
            try {
                for (int i = 0; i < 30; i++) {
                    double cpuUsage = getCPUUsage();
                    System.out.println(String.format("CPU使用率: %.2f%%", cpuUsage));
                    TimeUnit.SECONDS.sleep(1);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        // 启动监控
        monitorThread.start();
        
        // 执行CPU密集型操作
        long startTime = System.currentTimeMillis();
        
        // 执行复杂的字符串操作和聚合
        rdd.map(s -> {
            // 模拟CPU密集型计算
            String result = "";
            for (int i = 0; i < 100; i++) {
                result = s + result;
                result = result.substring(0, Math.min(result.length(), 1000));
            }
            return result.hashCode() % 1000;
        })
        .countByValue();
        
        long endTime = System.currentTimeMillis();
        
        // 等待监控线程完成
        try {
            monitorThread.join(5000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        System.out.println(String.format("CPU密集型操作完成，耗时: %d毫秒", endTime - startTime));
    }
    
    public void testMemoryUtilization(int dataSize) {
        System.out.println("\n开始内存利用率测试");
        
        // 记录初始内存使用
        Runtime runtime = Runtime.getRuntime();
        long initialMemory = runtime.totalMemory() - runtime.freeMemory();
        System.out.println(String.format("初始内存使用: %.2f MB", initialMemory / (1024.0 * 1024.0)));
        
        // 生成并缓存大量数据
        List<String> testData = generateTestData(dataSize);
        
        // 记录数据生成后的内存使用
        long dataGeneratedMemory = runtime.totalMemory() - runtime.freeMemory();
        System.out.println(String.format("数据生成后内存使用: %.2f MB", dataGeneratedMemory / (1024.0 * 1024.0)));
        System.out.println(String.format("数据占用内存: %.2f MB", (dataGeneratedMemory - initialMemory) / (1024.0 * 1024.0)));
        
        // 使用Spark缓存数据
        JavaRDD<String> rdd = jsc.parallelize(testData).cache();
        long cacheStart = System.currentTimeMillis();
        
        // 触发缓存
        long count = rdd.count();
        
        long cacheEnd = System.currentTimeMillis();
        System.out.println(String.format("缓存 %d 条记录，耗时: %d毫秒", count, cacheEnd - cacheStart));
        
        // 记录缓存后的内存使用
        long cachedMemory = runtime.totalMemory() - runtime.freeMemory();
        System.out.println(String.format("缓存后内存使用: %.2f MB", cachedMemory / (1024.0 * 1024.0)));
        
        // 执行内存密集型操作
        System.out.println("执行内存密集型操作...");
        rdd.flatMap(s -> {
            List<String> result = new ArrayList<>();
            // 生成更大的数据结构
            for (int i = 0; i < 10; i++) {
                result.add(s + "_processed_" + i);
            }
            return result.iterator();
        }).count();
        
        // 记录操作后的内存使用
        long afterOpMemory = runtime.totalMemory() - runtime.freeMemory();
        System.out.println(String.format("操作后内存使用: %.2f MB", afterOpMemory / (1024.0 * 1024.0)));
        
        // 释放缓存
        rdd.unpersist(true);
        
        // 强制GC（仅用于测试）
        System.gc();
        
        // 记录释放后的内存使用
        long finalMemory = runtime.totalMemory() - runtime.freeMemory();
        System.out.println(String.format("释放缓存后内存使用: %.2f MB", finalMemory / (1024.0 * 1024.0)));
    }
    
    public void testIOUtilization(String tempDir, int dataSize) {
        System.out.println("\n开始I/O利用率测试");
        
        // 生成测试数据
        List<String> testData = generateTestData(dataSize);
        JavaRDD<String> rdd = jsc.parallelize(testData);
        
        // 测试写入性能
        long writeStart = System.currentTimeMillis();
        String outputPath = tempDir + "/test_output";
        rdd.saveAsTextFile(outputPath);
        long writeEnd = System.currentTimeMillis();
        
        long writeTime = writeEnd - writeStart;
        double writeThroughput = (dataSize * 1000.0) / writeTime; // 假设每条记录约1KB
        
        System.out.println(String.format("写入时间: %d毫秒", writeTime));
        System.out.println(String.format("写入吞吐量: %.2f KB/秒", writeThroughput));
        
        // 测试读取性能
        long readStart = System.currentTimeMillis();
        JavaRDD<String> readRDD = jsc.textFile(outputPath);
        long readCount = readRDD.count();
        long readEnd = System.currentTimeMillis();
        
        long readTime = readEnd - readStart;
        double readThroughput = (dataSize * 1000.0) / readTime; // 假设每条记录约1KB
        
        System.out.println(String.format("读取记录数: %d", readCount));
        System.out.println(String.format("读取时间: %d毫秒", readTime));
        System.out.println(String.format("读取吞吐量: %.2f KB/秒", readThroughput));
    }
    
    // 获取CPU使用率（需要使用反射获取操作系统MXBean的扩展方法）
    private double getCPUUsage() {
        try {
            Method method = osBean.getClass().getMethod("getSystemCpuLoad");
            method.setAccessible(true);
            double cpuLoad = (double) method.invoke(osBean);
            return cpuLoad * 100.0;
        } catch (Exception e) {
            return -1.0; // 返回-1表示无法获取CPU使用率
        }
    }
    
    private List<String> generateTestData(int size) {
        List<String> data = new ArrayList<>(size);
        for (int i = 0; i < size; i++) {
            data.add("test_data_" + i + "_" + generateRandomString(1000));
        }
        return data;
    }
    
    private String generateRandomString(int length) {
        StringBuilder sb = new StringBuilder(length);
        String chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        for (int i = 0; i < length; i++) {
            sb.append(chars.charAt((int) (Math.random() * chars.length())));
        }
        return sb.toString();
    }
    
    public void close() {
        if (jsc != null) {
            jsc.close();
        }
        if (spark != null) {
            spark.stop();
        }
    }
    
    public static void main(String[] args) {
        ResourceUtilizationTest test = new ResourceUtilizationTest();
        try {
            // 测试CPU利用率
            test.testCPUUtilization(100000);
            
            // 测试内存利用率
            test.testMemoryUtilization(500000);
            
            // 测试I/O利用率（需要提供临时目录路径）
            String tempDir = System.getProperty("java.io.tmpdir");
            test.testIOUtilization(tempDir, 200000);
        } finally {
            test.close();
        }
    }
}
