> 【章节重点难点总结】

- 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准
- 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡

> 【课后思考/练习题】

1. 【入门】 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
2. 【进阶】 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。

> 【See Also】（工具）相关：[OpenTelemetry分布式追踪实现示例](./1022.2025.newbook.cleaned.md#opentelemetry分布式追踪实现示例)


## OpenTelemetry追踪实现示例

> 【阅读提示】本篇聚焦：OpenTelemetry追踪实现示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

## 配置追踪器

> 【阅读提示】本篇聚焦：配置追踪器。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

resource = Resource(attributes={SERVICE_NAME: "bigdata-processing-service"})
provider = TracerProvider(resource=resource)
exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

## 在数据处理函数中使用追踪

> 【阅读提示】本篇聚焦：在数据处理函数中使用追踪。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

def process_data(input_data, data_type):
    with tracer.start_as_current_span("process_data") as span:
        # 添加Span属性
        span.set_attribute("data.type", data_type)
        span.set_attribute("data.size", len(input_data))

        try:
            # 记录处理步骤
            with tracer.start_as_current_span("validate_data") as validate_span:
                validated_data = validate_data(input_data)
                validate_span.set_attribute("validation.success", True)

            with tracer.start_as_current_span("transform_data") as transform_span:
                result = transform_data(validated_data)
                transform_span.set_attribute("transform.rows_processed", len(result))

            # 添加事件
            span.add_event("Data processing completed successfully")
            return result

        except Exception as e:
            # 记录错误
            span.set_status(trace.StatusCode.ERROR)
            span.record_exception(e)
            raise
