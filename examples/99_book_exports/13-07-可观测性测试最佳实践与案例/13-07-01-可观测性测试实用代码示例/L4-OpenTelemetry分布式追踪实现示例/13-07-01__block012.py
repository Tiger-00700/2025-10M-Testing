## OpenTelemetry追踪实现示例


from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

## 配置追踪器


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
