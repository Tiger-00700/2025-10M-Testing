
# 【章节重点难点总结】

# - 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准
# - 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡

# 【课后思考/练习题】

# 1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
# 2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。

# 大数据处理流水线中的OpenTelemetry追踪实现 - 增强版

# 【阅读提示】本篇聚焦：大数据处理流水线中的OpenTelemetry追踪实现 - 增强版。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

import time
import random
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource, PROCESS_PID, DEPLOYMENT_ENVIRONMENT
from opentelemetry.context import attach, detach
from opentelemetry.propagate import inject, extract
from opentelemetry.trace import Status, StatusCode

# 配置全局追踪器

# 【阅读提示】本篇聚焦：配置全局追踪器。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

resource = Resource(attributes={
    SERVICE_NAME: "bigdata-processing-pipeline",
    DEPLOYMENT_ENVIRONMENT: "production",
    "cluster.name": "data-lake-cluster",
    "team.owner": "data-engineering"
})

# 创建追踪提供者

# 【阅读提示】本篇聚焦：创建追踪提供者。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

provider = TracerProvider(resource=resource)

# 配置多种导出器

# 【阅读提示】本篇聚焦：配置多种导出器。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-collector",
    agent_port=6831,
)

console_exporter = ConsoleSpanExporter()

# 添加批处理处理器（生产环境）

# 【阅读提示】本篇聚焦：添加批处理处理器（生产环境）。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

batch_processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(batch_processor)

# 可选：添加控制台处理器（开发环境调试用）

# 【阅读提示】本篇聚焦：可选：添加控制台处理器（开发环境调试用）。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

# provider.add_span_processor(BatchSpanProcessor(console_exporter))

# 【阅读提示】本篇聚焦：provider.add_span_processor(BatchSpanProcessor(console_exporter))。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。


# 设置全局追踪提供者

# 【阅读提示】本篇聚焦：设置全局追踪提供者。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

trace.set_tracer_provider(provider)

class DataPipelineTracer:
    """大数据流水线专用追踪工具类"""

    @staticmethod
    def create_context():
        """创建新的追踪上下文"""
        context = {}
        inject(context)
        return context

    @staticmethod
    def extract_context(headers):
        """从headers中提取追踪上下文"""
        return extract(headers)

    @staticmethod
    def with_context(context, func, *args, **kwargs):
        """在指定上下文中执行函数"""
        token = attach(context)
        try:
            return func(*args, **kwargs)
        finally:
            detach(token)

def data_ingestion_stage(input_source, context=None):
    """数据采集阶段的高级追踪实现"""
    tracer = trace.get_tracer("data.ingestion")

    # 定义子操作的追踪辅助函数
    def _process_source_chunk(chunk_id, chunk_size):
        with tracer.start_as_current_span(f"process_chunk_{chunk_id}") as span:
            span.set_attribute("chunk.id", chunk_id)
            span.set_attribute("chunk.size", chunk_size)

            # 模拟处理延迟
            processing_time = random.uniform(0.1, 0.5)
            time.sleep(processing_time)

            # 模拟可能的错误
            if random.random() < 0.05:  # 5%概率失败
                span.set_status(Status(StatusCode.ERROR))
                span.add_event("chunk_processing_failed", {
                    "error_type": "timeout",
                    "retry_attempt": 1
                })
                raise Exception(f"处理块 {chunk_id} 超时")

            span.set_attribute("processing.time_ms", int(processing_time * 1000))
            span.add_event("chunk_processing_complete")
            return chunk_size

    try:
        if context:
            # 从外部上下文提取追踪信息
            token = attach(DataPipelineTracer.extract_context(context))

        with tracer.start_as_current_span("data_ingestion") as span:
            # 添加关键属性
            span.set_attribute("source.type", input_source["type"])
            span.set_attribute("source.location", input_source["location"])
            span.set_attribute("source.format", input_source.get("format", "unknown"))
            span.set_attribute("source.partition_count", input_source.get("partitions", 1))

            # 记录数据采集开始事件
            span.add_event("ingestion_start")

            # 模拟分块处理数据
            total_records = 0
            chunk_size = 10000
            chunk_count = 10

            for i in range(chunk_count):
                try:
                    # 处理每个数据块
                    processed = _process_source_chunk(i, chunk_size)
                    total_records += processed
                except Exception as e:
                    # 记录块处理失败，但继续处理其他块
                    span.add_event("chunk_failure_skipped", {
                        "chunk_id": i,
                        "error": str(e)
                    })
                    continue

            # 采集完成后记录结果摘要
            span.set_attribute("records.count", total_records)
            span.set_attribute("processing.success_rate",
                              round(total_records / (chunk_count * chunk_size) * 100, 2))

            span.add_event("ingestion_complete", {
                "records_processed": total_records,
                "status": "success",
                "processing_time_ms": int((time.time() - span.start_time) * 1000)
            })

            return {"status": "success", "count": total_records}
    except Exception as e:
        # 记录严重错误
        if 'span' in locals():
            span.set_status(Status(StatusCode.ERROR))
            span.record_exception(e)
            span.add_event("ingestion_failed", {
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
        raise
    finally:
        if context and 'token' in locals():
            detach(token)

def data_transformation_stage(data, context=None):
    """数据转换阶段的高级追踪实现"""
    tracer = trace.get_tracer("data.transformation")

    try:
        if context:
            token = attach(DataPipelineTracer.extract_context(context))

        with tracer.start_as_current_span("data_transformation") as span:
            span.set_attribute("input.records", data["count"])

            # 记录转换开始事件
            span.add_event("transformation_start", {
                "transformations": ["normalize", "enrich", "validate"],
                "parallel_degree": 8
            })

            # 模拟不同的转换操作
            transformations = [
                ("normalize", 0.2),
                ("enrich", 0.5),
                ("validate", 0.3)
            ]

            for transform_name, weight in transformations:
                with tracer.start_as_current_span(f"transformation_{transform_name}") as child_span:
                    child_span.set_attribute("transformation.type", transform_name)

                    # 模拟转换延迟
                    processing_time = random.uniform(0.1 * weight, 0.5 * weight)
                    time.sleep(processing_time)

                    child_span.set_attribute("processing.time_ms", int(processing_time * 1000))

                    # 记录转换特定的属性
                    if transform_name == "validate":
                        validation_rate = random.uniform(0.95, 1.0)
                        child_span.set_attribute("validation.success_rate", round(validation_rate * 100, 2))

                    child_span.add_event(f"{transform_name}_complete")

            # 转换完成后记录结果
            transformed_records = int(data["count"] * random.uniform(0.95, 1.0))  # 模拟少量记录被过滤
            span.set_attribute("output.records", transformed_records)

            # 添加详细的转换指标
            total_time = (time.time() - span.start_time) * 1000
            span.set_attribute("transformation.time_ms", int(total_time))
            span.set_attribute("data.quality.valid", round(random.uniform(95, 99), 2))
            span.set_attribute("records.filtered", data["count"] - transformed_records)

            # 添加数据特征信息
            span.set_attribute("data.schema.version", "1.2.3")
            span.set_attribute("data.compression.ratio", round(random.uniform(0.3, 0.8), 2))

            span.add_event("transformation_complete", {
                "throughput_records_per_sec": int(transformed_records / (total_time / 1000))
            })

            return {"status": "success", "count": transformed_records}
    except Exception as e:
        # 记录错误信息
        if 'span' in locals():
            span.set_status(Status(StatusCode.ERROR))
            span.record_exception(e)
            span.add_event("transformation_failed", {
                "error": str(e),
                "transformation_stage": "unknown"
            })
        raise
    finally:
        if context and 'token' in locals():
            detach(token)

def data_loading_stage(data, target_config, context=None):
    """数据加载阶段的高级追踪实现"""
    tracer = trace.get_tracer("data.loading")

    try:
        if context:
            token = attach(DataPipelineTracer.extract_context(context))

        with tracer.start_as_current_span("data_loading") as span:
            span.set_attribute("input.records", data["count"])
            span.set_attribute("target.type", target_config["type"])
            span.set_attribute("target.location", target_config["location"])
            span.set_attribute("target.format", target_config.get("format", "parquet"))

            span.add_event("loading_start")

            # 模拟加载操作
            loading_time = random.uniform(0.5, 2.0)
            time.sleep(loading_time)

            # 模拟加载结果
            loaded_records = int(data["count"] * random.uniform(0.98, 1.0))

            # 记录加载指标
            span.set_attribute("output.records", loaded_records)
            span.set_attribute("loading.time_ms", int(loading_time * 1000))
            span.set_attribute("loading.success_rate", round(loaded_records / data["count"] * 100, 2))

            # 记录资源使用情况
            span.set_attribute("resource.memory_mb", random.randint(200, 500))
            span.set_attribute("resource.cpu_percent", round(random.uniform(40, 90), 2))

            span.add_event("loading_complete")

            return {"status": "success", "count": loaded_records}
    except Exception as e:
        if 'span' in locals():
            span.set_status(Status(StatusCode.ERROR))
            span.record_exception(e)
            span.add_event("loading_failed", {"error": str(e)})
        raise
    finally:
        if context and 'token' in locals():
            detach(token)

def execute_pipeline(input_source, target_config):
    """执行完整的数据处理流水线，包含高级追踪上下文传递"""
    tracer = trace.get_tracer("pipeline.coordinator")

    # 创建流水线执行ID
    pipeline_execution_id = f"pipeline-{int(time.time())}-{random.randint(1000, 9999)}"

    with tracer.start_as_current_span("pipeline_execution") as root_span:
        # 添加详细的元数据
        root_span.set_attribute("pipeline.name", "daily_data_processing")
        root_span.set_attribute("pipeline.execution_id", pipeline_execution_id)
        root_span.set_attribute("execution.timestamp", str(int(time.time())))
        root_span.set_attribute("execution.priority", "high")

        # 记录流水线配置
        root_span.add_event("pipeline_configured", {
            "input_source_type": input_source["type"],
            "target_type": target_config["type"],
            "pipeline_version": "1.2.0"
        })

        # 创建上下文用于传递追踪信息
        context = DataPipelineTracer.create_context()

        # 记录流水线开始
        root_span.add_event("pipeline_started")

        try:
            # 执行数据采集
            ingestion_start = time.time()
            root_span.add_event("ingestion_stage_started")
            ingestion_result = data_ingestion_stage(input_source, context)
            ingestion_duration = int((time.time() - ingestion_start) * 1000)

            root_span.add_event("ingestion_stage_completed", {
                "records_ingested": ingestion_result["count"],
                "duration_ms": ingestion_duration
            })

            # 执行数据转换
            transform_start = time.time()
            root_span.add_event("transformation_stage_started")
            transform_result = data_transformation_stage(ingestion_result, context)
            transform_duration = int((time.time() - transform_start) * 1000)

            root_span.add_event("transformation_stage_completed", {
                "records_transformed": transform_result["count"],
                "duration_ms": transform_duration
            })

            # 执行数据加载
            load_start = time.time()
            root_span.add_event("loading_stage_started")
            load_result = data_loading_stage(transform_result, target_config, context)
            load_duration = int((time.time() - load_start) * 1000)

            root_span.add_event("loading_stage_completed", {
                "records_loaded": load_result["count"],
                "duration_ms": load_duration
            })

            # 记录流水线性能指标
            total_duration = ingestion_duration + transform_duration + load_duration
            root_span.set_attribute("execution.duration_ms", total_duration)
            root_span.set_attribute("execution.success_rate",
                                  round(load_result["count"] / ingestion_result["count"] * 100, 2))
            root_span.set_attribute("throughput.records_per_sec",
                                  int(load_result["count"] / (total_duration / 1000)))

            # 完成整个流水线
            root_span.add_event("pipeline_completed", {
                "total_records_processed": load_result["count"],
                "status": "success",
                "stages_completed": 3,
                "total_duration_ms": total_duration
            })

            return {
                "status": "success",
                "count": load_result["count"],
                "execution_id": pipeline_execution_id,
                "duration_ms": total_duration
            }

        except Exception as e:
            # 记录流水线失败
            root_span.set_status(Status(StatusCode.ERROR))
            root_span.record_exception(e)
            root_span.add_event("pipeline_failed", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise

# 示例用法

# 【阅读提示】本篇聚焦：示例用法。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

if __name__ == "__main__":
    try:
        # 定义输入源和目标配置
        input_config = {
            "type": "kafka",
            "location": "kafka-broker:9092",
            "format": "json",
            "partitions": 16
        }

        target_config = {
            "type": "hive",
            "location": "hdfs://namenode:8020/data/customer",
            "format": "parquet",
            "partition_by": ["date", "region"]
        }

        # 执行流水线
        result = execute_pipeline(input_config, target_config)
        print(f"流水线执行成功: {result}")

    except Exception as e:
        print(f"流水线执行失败: {e}")
    finally:
        # 确保所有数据都被导出
        provider.force_flush()