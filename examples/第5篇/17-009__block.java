// Apache Kafka自动化测试示例
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class KafkaTest {
    private static final String TOPIC = "test_topic";
    private static final String BOOTSTRAP_SERVERS = "localhost:9092";

    private KafkaProducer<String, String> producer;
    private KafkaConsumer<String, String> consumer;

    @BeforeEach
    public void setup() {
        // 设置生产者配置
        Properties producerProps = new Properties();
        producerProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
        producerProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        producerProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        producerProps.put(ProducerConfig.ACKS_CONFIG, "all");

        // 创建生产者
        producer = new KafkaProducer<>(producerProps);

        // 设置消费者配置
        Properties consumerProps = new Properties();
        consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
        consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, "test-consumer-group" + System.currentTimeMillis());
        consumerProps.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        consumerProps.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        consumerProps.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        // 创建消费者
        consumer = new KafkaConsumer<>(consumerProps);
        consumer.subscribe(Collections.singletonList(TOPIC));

        // 清除初始消息
        ConsumerRecords<String, String> initialRecords = consumer.poll(Duration.ofMillis(100));
    }

    @AfterEach
    public void teardown() {
        if (producer != null) {
            producer.close();
        }
        if (consumer != null) {
            consumer.close();
        }
    }

    @Test
    public void testBasicProduceConsume() throws InterruptedException {
        // 准备测试数据
        int numMessages = 10;

        // 发送消息
        for (int i = 0; i < numMessages; i++) {
            String key = "key-" + i;
            String value = "value-" + i;
            ProducerRecord<String, String> record = new ProducerRecord<>(TOPIC, key, value);
            producer.send(record);
        }

        // 刷新生产者，确保消息被发送
        producer.flush();

        // 等待消息传播
        TimeUnit.SECONDS.sleep(1);

        // 消费消息
        int receivedCount = 0;
        long endTime = System.currentTimeMillis() + 5000; // 5秒超时

        while (receivedCount < numMessages && System.currentTimeMillis() < endTime) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            receivedCount += records.count();
        }

        // 验证接收到的消息数量
        assertEquals(numMessages, receivedCount, "未收到预期数量的消息");
    }

    @Test
    public void testMessageOrdering() throws InterruptedException {
        // 发送有序消息
        int numMessages = 5;
        for (int i = 0; i < numMessages; i++) {
            ProducerRecord<String, String> record = new ProducerRecord<>(TOPIC, "order-key", "message-" + i);
            producer.send(record);
        }

        producer.flush();
        TimeUnit.SECONDS.sleep(1);

        // 消费并验证顺序
        StringBuilder receivedOrder = new StringBuilder();
        long endTime = System.currentTimeMillis() + 5000;

        while (receivedOrder.length() < numMessages && System.currentTimeMillis() < endTime) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            records.forEach(record -> {
                if (record.key().equals("order-key")) {
                    receivedOrder.append(record.value().substring(8)); // 提取数字部分
                }
            });
        }

        // 验证消息顺序
        assertEquals("01234", receivedOrder.toString(), "消息顺序不正确");
    }

    @Test
    public void testPerformance() throws InterruptedException {
        // 性能测试参数
        int numMessages = 1000;
        int messageSize = 1024; // 1KB消息

        // 创建固定大小的消息
        StringBuilder messageBuilder = new StringBuilder(messageSize);
        for (int i = 0; i < messageSize; i++) {
            messageBuilder.append('X');
        }
        String message = messageBuilder.toString();

        // 测量生产性能
        long startTime = System.currentTimeMillis();
        for (int i = 0; i < numMessages; i++) {
            ProducerRecord<String, String> record = new ProducerRecord<>(TOPIC, "perf-key-" + i, message);
            producer.send(record);
        }
        producer.flush();
        long produceTime = System.currentTimeMillis() - startTime;

        // 等待消息传播
        TimeUnit.SECONDS.sleep(1);

        // 测量消费性能
        startTime = System.currentTimeMillis();
        int receivedCount = 0;
        long endTime = System.currentTimeMillis() + 10000; // 10秒超时

        while (receivedCount < numMessages && System.currentTimeMillis() < endTime) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            receivedCount += records.count();
        }

        long consumeTime = System.currentTimeMillis() - startTime;

        // 验证接收到所有消息
        assertEquals(numMessages, receivedCount, "未收到所有性能测试消息");

        // 计算性能指标
        double produceRate = numMessages * 1000.0 / produceTime;
        double consumeRate = numMessages * 1000.0 / consumeTime;

        System.out.printf("生产性能: %.2f 消息/秒\n", produceRate);
        System.out.printf("消费性能: %.2f 消息/秒\n", consumeRate);

        // 验证性能满足要求（示例阈值）
        assertTrue(produceRate > 100, "生产性能不满足要求");
        assertTrue(consumeRate > 100, "消费性能不满足要求");
    }
}
