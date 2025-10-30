import org.apache.nifi.util.TestRunner;
import org.apache.nifi.util.TestRunners;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class NiFiFlowTest {
    private TestRunner testRunner;

    @BeforeEach
    public void init() {
        // 创建TestRunner实例，指定要测试的处理器
        testRunner = TestRunners.newTestRunner(MyCustomProcessor.class);
        
        // 配置处理器属性
        testRunner.setProperty(MyCustomProcessor.INPUT_DIRECTORY, "/tmp/input");
        testRunner.setProperty(MyCustomProcessor.OUTPUT_DIRECTORY, "/tmp/output");
        
        // 添加关系
        testRunner.enqueue("test content", null, "test.json");
    }

    @Test
    public void testProcessor() {
        // 运行处理器
        testRunner.run();
        
        // 验证输出
        testRunner.assertTransferCount(MyCustomProcessor.REL_SUCCESS, 1);
        testRunner.assertTransferCount(MyCustomProcessor.REL_FAILURE, 0);
        
        // 获取处理后的结果并验证
        MockFlowFile out = testRunner.getFlowFilesForRelationship(MyCustomProcessor.REL_SUCCESS).get(0);
        out.assertContentEquals("expected output content");
    }
}
