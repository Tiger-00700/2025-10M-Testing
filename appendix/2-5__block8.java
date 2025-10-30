import org.apache.flink.api.common.functions.RichMapFunction;
import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.util.KeyedOneInputStreamOperatorTestHarness;
import org.apache.flink.streaming.util.ProcessFunctionTestHarnesses;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class StateManagementTest {
    
    private static class StatefulMapFunction extends RichMapFunction<String, String> {
        private ValueState<Integer> countState;
        
        @Override
        public void open(Configuration config) {
            ValueStateDescriptor<Integer> descriptor = 
                new ValueStateDescriptor<>("count", Types.INT);
            countState = getRuntimeContext().getState(descriptor);
        }
        
        @Override
        public String map(String value) throws Exception {
            Integer count = countState.value();
            if (count == null) {
                count = 0;
            }
            count++;
            countState.update(count);
            return value + ":" + count;
        }
    }
    
    private KeyedOneInputStreamOperatorTestHarness<String, String, String> testHarness;
    
    @BeforeEach
    void setUp() throws Exception {
        // 创建测试的有状态函数
        StatefulMapFunction statefulFunction = new StatefulMapFunction();
        
        // 创建测试Harness
        testHarness = ProcessFunctionTestHarnesses
                .forKeyedFunction(statefulFunction, String::valueOf);
        
        // 初始化测试Harness
        testHarness.open();
    }
    
    @Test
    void testStatePersistence() throws Exception {
        // 为不同的key发送数据
        testHarness.processElement("hello", "key1", 100L);
        testHarness.processElement("world", "key1", 200L);
        testHarness.processElement("flink", "key2", 300L);
        
        // 获取结果
        List<String> results = new ArrayList<>();
        for (String result : testHarness.extractOutputValues()) {
            results.add(result);
        }
        
        // 验证状态计数结果
        assertEquals(3, results.size());
        assertEquals("hello:1", results.get(0));
        assertEquals("world:2", results.get(1));
        assertEquals("flink:1", results.get(2));
    }
    
    @Test
    void testStateRecovery() throws Exception {
        // 发送数据
        testHarness.processElement("test1", "key1", 100L);
        testHarness.processElement("test2", "key1", 200L);
        
        // 创建检查点
        long checkpointId = 100L;
        testHarness.snapshotCheckpoint(checkpointId);
        
        // 恢复检查点
        testHarness.restore();
        
        // 继续处理数据
        testHarness.processElement("test3", "key1", 300L);
        
        // 获取结果 - 只包含恢复后的新数据
        List<String> results = new ArrayList<>();
        for (String result : testHarness.extractOutputValues()) {
            results.add(result);
        }
        
        // 验证状态是否正确恢复 - 计数应该从3开始
        assertEquals(1, results.size());
        assertEquals("test3:3", results.get(0));
    }
    
    @Test
    void testStateConsistency() throws Exception {
        // 模拟多个并行处理
        for (int i = 0; i < 5; i++) {
            testHarness.processElement("value" + i, "consistent-key", (long)(i * 100));
        }
        
        // 获取结果
        List<String> results = new ArrayList<>();
        for (String result : testHarness.extractOutputValues()) {
            results.add(result);
        }
        
        // 验证状态一致性 - 计数应该是连续的
        assertEquals(5, results.size());
        for (int i = 0; i < 5; i++) {
            assertTrue(results.contains("value" + i + ":" + (i + 1)));
        }
    }
}
