import org.apache.beam.sdk.testing.PAssert;
import org.apache.beam.sdk.testing.TestPipeline;
import org.apache.beam.sdk.testing.TestStream;
import org.apache.beam.sdk.transforms.windowing.FixedWindows;
import org.apache.beam.sdk.transforms.windowing.Window;
import org.apache.beam.sdk.values.TimestampedValue;
import org.joda.time.Duration;
import org.joda.time.Instant;
import org.junit.Rule;
import org.junit.Test;

public class BeamStreamTest {
    @Rule
    public final TestPipeline pipeline = TestPipeline.create();

    @Test
    public void testWindowedTransform() {
        // 创建模拟数据流
        TestStream<String> testStream = TestStream.create(TypeDescriptors.strings())
            .addElements(
                TimestampedValue.of("apple", Instant.parse("2023-01-01T12:00:00Z")),
                TimestampedValue.of("banana", Instant.parse("2023-01-01T12:05:00Z")),
                TimestampedValue.of("cherry", Instant.parse("2023-01-01T12:15:00Z"))
            )
            .advanceWatermarkTo(Instant.parse("2023-01-01T12:30:00Z"))
            .addElements(
                TimestampedValue.of("date", Instant.parse("2023-01-01T12:20:00Z"))
            )
            .advanceWatermarkToInfinity();
        
        // 应用窗口和转换
        PCollection<String> output = pipeline.apply(testStream)
            .apply(Window.into(FixedWindows.of(Duration.standardMinutes(10))))
            .apply(SomeTransforms.someTransform());
        
        // 验证结果
        PAssert.that(output).containsInAnyOrder("expected", "results");
        
        // 运行测试
        pipeline.run().waitUntilFinish();
    }
}
