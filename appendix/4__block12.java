import org.apache.beam.sdk.testing.PAssert;
import org.apache.beam.sdk.testing.TestPipeline;
import org.apache.beam.sdk.transforms.Create;
import org.apache.beam.sdk.transforms.MapElements;
import org.apache.beam.sdk.values.KV;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.TypeDescriptors;
import org.junit.Rule;
import org.junit.Test;

public class BeamBatchTest {
    @Rule
    public final TestPipeline pipeline = TestPipeline.create();

    @Test
    public void testTransform() {
        // 创建测试数据
        PCollection<String> input = pipeline.apply(Create.of("apple", "banana", "cherry"));
        
        // 应用转换
        PCollection<KV<String, Integer>> output = input.apply(
            MapElements.into(TypeDescriptors.kvs(TypeDescriptors.strings(), TypeDescriptors.integers()))
                       .via(s -> KV.of(s, s.length()))
        );
        
        // 验证结果
        PAssert.that(output).containsInAnyOrder(
            KV.of("apple", 5),
            KV.of("banana", 6),
            KV.of("cherry", 6)
        );
        
        // 运行测试
        pipeline.run().waitUntilFinish();
    }
}
