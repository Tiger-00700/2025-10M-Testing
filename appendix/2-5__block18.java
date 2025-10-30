import org.apache.kafka.common.serialization.*;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.test.*;
import org.junit.jupiter.api.*;
import java.util.*;

import static org.junit.jupiter.api.Assertions.assertEquals;

class KafkaStreamsProcessorTest {
    private TopologyTestDriver testDriver;
    private TestInputTopic<String, String> inputTopic;
    private TestOutputTopic<String, String> outputTopic;
    
    @BeforeEach
    void setUp() {
        // 配置Serde
        Serde<String> stringSerde = Serdes.String();
        
        // 创建拓扑
        StreamsBuilder builder = new StreamsBuilder();
        KStream<String, String> input = builder.stream("input-topic");
        
        // 定义处理逻辑：简单的字符串转换
        KStream<String, String> processed = input
            .filter((key, value) -> value != null && value.contains("test"))
            .mapValues(value -> value.toUpperCase());
        
        // 将结果写入输出主题
        processed.to("output-topic");
        
        // 创建TopologyTestDriver
        Properties props = new Properties();
        props.setProperty(StreamsConfig.APPLICATION_ID_CONFIG, "test-application");
        props.setProperty(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "dummy:9092");
        
        testDriver = new TopologyTestDriver(builder.build(), props);
        
        // 创建测试主题
        inputTopic = testDriver.createInputTopic("input-topic", stringSerde.serializer(), stringSerde.serializer());
        outputTopic = testDriver.createOutputTopic("output-topic", stringSerde.deserializer(), stringSerde.deserializer());
    }
    
    @AfterEach
    void tearDown() {
        // 关闭测试驱动，避免资源泄漏
        if (testDriver != null) {
            testDriver.close();
        }
    }
    
    @Test
    void testStringProcessing() {
        // 输入测试数据
        inputTopic.pipeInput("key1", "this is a test message");
        inputTopic.pipeInput("key2", "this message should be filtered out");
        inputTopic.pipeInput("key3", "another TEST case");
        
        // 验证输出结果
        assertEquals(2, outputTopic.getQueueSize(), "应该有两条消息被处理");
        
        // 检查每条输出消息
        KeyValue<String, String> record1 = outputTopic.readKeyValue();
        assertEquals("key1", record1.key);
        assertEquals("THIS IS A TEST MESSAGE", record1.value);
        
        KeyValue<String, String> record2 = outputTopic.readKeyValue();
        assertEquals("key3", record2.key);
        assertEquals("ANOTHER TEST CASE", record2.value);
        
        // 确保没有更多的输出
        assertTrue(outputTopic.isEmpty());
    }
    
    @Test
    void testStateStore() {
        // 创建带状态存储的拓扑
        StreamsBuilder builder = new StreamsBuilder();
        
        // 创建状态存储
        StoreBuilder<KeyValueStore<String, Long>> storeBuilder = 
            Stores.keyValueStoreBuilder(
                Stores.persistentKeyValueStore("word-count-store"),
                Serdes.String(),
                Serdes.Long());
        builder.addStateStore(storeBuilder);
        
        // 实现单词计数逻辑
        KStream<String, String> input = builder.stream("input-topic");
        input.flatMapValues(value -> Arrays.asList(value.toLowerCase().split("\\W+")))
            .groupBy((key, word) -> word)
            .count(Materialized.as("word-count-store"));
        
        // 更新测试驱动
        Properties props = new Properties();
        props.setProperty(StreamsConfig.APPLICATION_ID_CONFIG, "test-application");
        props.setProperty(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "dummy:9092");
        
        testDriver = new TopologyTestDriver(builder.build(), props);
        inputTopic = testDriver.createInputTopic("input-topic", Serdes.String().serializer(), Serdes.String().serializer());
        
        // 输入测试数据
        inputTopic.pipeInput("key1", "hello world hello");
        
        // 访问状态存储验证结果
        ReadOnlyKeyValueStore<String, Long> store = testDriver.getKeyValueStore("word-count-store");
        assertEquals(2L, store.get("hello"), "'hello'应该出现两次");
        assertEquals(1L, store.get("world"), "'world'应该出现一次");
    }
}
