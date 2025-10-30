import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.apache.spark.sql.functions.*;

public class ResultAccuracyTest {
    private SparkSession spark;
    private Dataset<Row> inputData;
    
    @Before
    public void setUp() {
        spark = SparkSession.builder()
                .appName("ResultAccuracyTest")
                .master("local[*]")
                .getOrCreate();
        
        // 创建测试数据
        String[] columns = {"id", "department", "salary", "bonus"};
        Object[][] data = {
            {1, "Engineering", 100000, 10000},
            {2, "Marketing", 80000, 8000},
            {3, "Engineering", 120000, 12000},
            {4, "Sales", 75000, 15000},
            {5, null, 90000, null}  // 包含null值的边界情况
        };
        
        inputData = spark.createDataFrame(
            java.util.Arrays.asList(data), 
            java.util.Arrays.asList(columns)
        );
    }
    
    @After
    public void tearDown() {
        spark.stop();
    }
    
    @Test
    public void testAggregationResults() {
        // 计算部门总薪酬（薪资+奖金）
        Dataset<Row> result = inputData
            .withColumn("total_compensation", col("salary").plus(when(col("bonus").isNull(), 0).otherwise(col("bonus"))))
            .groupBy("department")
            .agg(
                sum("total_compensation").alias("total_compensation"),
                count("*").alias("employee_count")
            )
            .orderBy("department");
        
        // 验证结果
        java.util.List<Row> rows = result.collectAsList();
        
        // 检查Engineering部门
        Row engineeringRow = rows.stream()
            .filter(row -> row.getString(0).equals("Engineering"))
            .findFirst()
            .orElseThrow();
        assertEquals(242000.0, engineeringRow.getDouble(1), 0.001);
        assertEquals(2L, engineeringRow.getLong(2));
        
        // 检查Marketing部门
        Row marketingRow = rows.stream()
            .filter(row -> row.getString(0).equals("Marketing"))
            .findFirst()
            .orElseThrow();
        assertEquals(88000.0, marketingRow.getDouble(1), 0.001);
        assertEquals(1L, marketingRow.getLong(2));
        
        // 验证空值处理 - null部门也被正确分组
        Row nullDeptRow = rows.stream()
            .filter(row -> row.isNullAt(0))
            .findFirst()
            .orElseThrow();
        assertEquals(90000.0, nullDeptRow.getDouble(1), 0.001);
        assertEquals(1L, nullDeptRow.getLong(2));
    }
    
    @Test
    public void testDataIntegrity() {
        // 验证记录数一致性
        long inputCount = inputData.count();
        long processedCount = inputData
            .withColumn("processed", lit(true))
            .count();
        
        assertEquals(inputCount, processedCount);
        
        // 验证字段完整性
        long nonNullIdCount = inputData.filter(col("id").isNotNull()).count();
        assertEquals(inputCount, nonNullIdCount);  // id字段不应有null值
    }
}

## 5.3 流处理测试技术

流处理是大数据处理的重要模式，适用于实时数据分析和处理。本节将详细介绍Kafka Streams、Flink、Spark Streaming等主流流处理框架的测试方法和实践。

### 5.3.1 Kafka Streams测试
Kafka Streams是基于Kafka的轻量级流处理库，提供了简单易用的流处理API。Kafka Streams测试主要包括：

- **流拓扑测试**：验证流处理拓扑的正确性，包括源、转换、汇等组件的连接。
- **流转换操作测试**：测试各种流转换操作，如map、filter、groupBy等的正确性。
- **KTable操作测试**：验证表操作的功能，包括JOIN、聚合等操作。
- **状态存储测试**：测试状态存储的持久化，确保状态数据的安全性和可靠性。
- **容错机制测试**：验证Kafka Streams的容错能力，包括任务失败恢复、状态恢复等。
- **Exactly-Once语义**：测试精确一次处理语义的实现，确保数据处理的准确性。

**Kafka Streams测试示例**：
```java
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.Consumed;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.Produced;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Properties;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class KafkaStreamsTest {
    private TopologyTestDriver testDriver;
    private TestInputTopic<String, String> inputTopic;
    private TestOutputTopic<String, String> outputTopic;

    @BeforeEach
    void setUp() {
        // 创建流处理拓扑
        StreamsBuilder builder = new StreamsBuilder();
        KStream<String, String> inputStream = builder.stream("input-topic", 
                Consumed.with(Serdes.String(), Serdes.String()));
        
        // 实现简单的转换：将消息转换为大写
        KStream<String, String> outputStream = inputStream
                .mapValues(value -> value.toUpperCase());
        
        outputStream.to("output-topic", 
                Produced.with(Serdes.String(), Serdes.String()));
        
        // 创建测试配置
        Properties config = new Properties();
        config.put(StreamsConfig.APPLICATION_ID_CONFIG, "test-application");
        config.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "dummy:1234");
        config.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
        config.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
        
        // 初始化测试驱动
        testDriver = new TopologyTestDriver(builder.build(), config);
        
        // 创建测试主题
        inputTopic = testDriver.createInputTopic("input-topic", 
                new StringSerializer(), new StringSerializer());
        outputTopic = testDriver.createOutputTopic("output-topic", 
                new StringDeserializer(), new StringDeserializer());
    }

    @AfterEach
    void tearDown() {
        testDriver.close();
    }

    @Test
    void testSimpleTransformation() {
        // 发送测试数据
        inputTopic.pipeInput("key1", "hello world");
        inputTopic.pipeInput("key2", "kafka streams");
        
        // 验证输出结果
        assertEquals("HELLO WORLD", outputTopic.readValue());
        assertEquals("KAFKA STREAMS", outputTopic.readValue());
        
        // 确保没有更多输出
        assertEquals(0, outputTopic.isEmpty());
    }

    @Test
    void testWithState() {
        // 创建带有状态的拓扑
        StreamsBuilder builder = new StreamsBuilder();
        KStream<String, String> inputStream = builder.stream("input-topic", 
                Consumed.with(Serdes.String(), Serdes.String()));
        
        // 按key分组并计数
        inputStream.groupByKey()
                .count()
                .toStream()
                .mapValues(count -> count.toString())
                .to("output-topic", 
                        Produced.with(Serdes.String(), Serdes.String()));
        
        // 重新初始化测试驱动
        Properties config = new Properties();
        config.put(StreamsConfig.APPLICATION_ID_CONFIG, "test-application");
        config.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "dummy:1234");
        config.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
        config.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
        
        testDriver.close();
        testDriver = new TopologyTestDriver(builder.build(), config);
        
        inputTopic = testDriver.createInputTopic("input-topic", 
                new StringSerializer(), new StringSerializer());
        outputTopic = testDriver.createOutputTopic("output-topic", 
                new StringDeserializer(), new StringDeserializer());
        
        // 发送测试数据
        inputTopic.pipeInput("key1", "value1");
        inputTopic.pipeInput("key1", "value2");
        inputTopic.pipeInput("key2", "value3");
        
        // 验证状态计数结果
        assertEquals("1", outputTopic.readValue());
        assertEquals("2", outputTopic.readValue());
        assertEquals("1", outputTopic.readValue());
    }
}
