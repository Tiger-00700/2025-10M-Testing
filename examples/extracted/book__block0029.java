
     // Java应用集成Jaeger示例
     import io.jaegertracing.internal.JaegerTracer;
     import io.jaegertracing.Configuration;
     import io.opentracing.Span;
     import io.opentracing.util.GlobalTracer;

     public class DistributedTracingExample {
         private static JaegerTracer tracer;

         // 初始化Jaeger追踪器
         public static void initTracer(String serviceName) {
             Configuration.SamplerConfiguration samplerConfig = Configuration.SamplerConfiguration.fromEnv()
                     .withType("const")
                     .withParam(1); // 采样所有请求

             Configuration.ReporterConfiguration reporterConfig = Configuration.ReporterConfiguration.fromEnv()
                     .withLogSpans(true)
                     .withFlushInterval(1000) // 1秒刷新一次
                     .withMaxQueueSize(10000);

             Configuration config = new Configuration(serviceName)
                     .withSampler(samplerConfig)
                     .withReporter(reporterConfig);

             tracer = config.getTracer();
             GlobalTracer.register(tracer);
         }

         // 处理请求并跟踪
         public void processData(String dataId) {
             // 创建根Span
             Span span = tracer.buildSpan("processData").start();

             try {
                 // 添加标签
                 span.setTag("dataId", dataId);

                 // 调用子操作并传递上下文
                 validateData(dataId, span);

                 // 模拟数据处理
                 Thread.sleep(100);

                 // 记录事件
                 span.log("Data processed successfully");

             } catch (Exception e) {
                 // 记录错误
                 span.setTag("error", true);
                 span.log(e.getMessage());
                 throw new RuntimeException("Failed to process data", e);
             } finally {
                 // 完成Span
                 span.finish();
             }
         }

         // 子操作跟踪
         private void validateData(String dataId, Span parentSpan) throws InterruptedException {
             // 创建子Span
             Span childSpan = tracer.buildSpan("validateData")
                     .asChildOf(parentSpan)
                     .start();

             try {
                 // 模拟数据验证
                 Thread.sleep(50);

                 // 记录关键指标
                 childSpan.setTag("validation.duration", 50);

             } finally {
                 // 完成子Span
                 childSpan.finish();
             }
         }

         public static void main(String[] args) {
             // 初始化追踪器
             initTracer("bigdata-processor");

             // 处理数据
             DistributedTracingExample example = new DistributedTracingExample();
             example.processData("data-12345");

             // 关闭追踪器
             tracer.close();
         }
     }
