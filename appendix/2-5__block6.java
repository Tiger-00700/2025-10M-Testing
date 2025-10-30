import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.util.KeyedOneInputStreamOperatorTestHarness;
import org.apache.flink.streaming.util.ProcessFunctionTestHarnesses;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class FlinkStreamTest {
    private KeyedOneInputStreamOperatorTestHarness<String, String, String> testHarness;
    
    @BeforeEach
    void setUp() throws Exception {
        // 创建测试的MapFunction
        MapFunction<String, String> mapFunction = value -> value.toUpperCase();
        
        // 创建测试Harness
        testHarness = ProcessFunctionTestHarnesses
                .forKeyedFunction(mapFunction, String::valueOf);
        
        // 初始化测试Harness
        testHarness.open();
    }
    
    @Test
    void testMapFunction() throws Exception {
        // 发送测试数据
        testHarness.processElement("hello world", 100L);
        testHarness.processElement("flink streaming", 200L);
        
        // 获取结果
        List<String> results = new ArrayList<>();
        for (String result : testHarness.extractOutputValues()) {
            results.add(result);
        }
        
        // 验证结果
        assertEquals(2, results.size());
        assertEquals("HELLO WORLD", results.get(0));
        assertEquals("FLINK STREAMING", results.get(1));
    }
    
    @Test
    void testCheckpointRestore() throws Exception {
        // 发送数据并执行检查点
        testHarness.processElement("test1", 100L);
        testHarness.snapshotCheckpoint(100L);
        
        // 恢复检查点
        testHarness.restore();
        
        // 继续处理数据
        testHarness.processElement("test2", 200L);
        
        // 获取结果
        List<String> results = new ArrayList<>();
        for (String result : testHarness.extractOutputValues()) {
            results.add(result);
        }
        
        // 验证结果 - 只有恢复后的新数据会被处理
        assertEquals(1, results.size());
        assertEquals("TEST2", results.get(0));
    }
    
    @Test
    public void testFlinkJobWithTestStreamEnvironment() throws Exception {
        // 创建测试环境
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(1);
        env.setRuntimeMode(StreamExecutionEnvironment.RuntimeExecutionMode.AUTOMATIC);
        
        // 创建测试数据流
        DataStream<String> input = env.fromElements("hello", "world", "flink");
        
        // 应用转换
        DataStream<String> output = input.map(value -> value.toUpperCase());
        
        // 收集结果
        List<String> results = new ArrayList<>();
        output.executeAndCollect().forEachRemaining(results::add);
        
        // 验证结果
        assertEquals(3, results.size());
        assertEquals("HELLO", results.get(0));
        assertEquals("WORLD", results.get(1));
        assertEquals("FLINK", results.get(2));
    }
}
