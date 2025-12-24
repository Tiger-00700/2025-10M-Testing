# 链路追踪与性能分析

## 分布式追踪基础

### 追踪概念
**Span（跨度）：**
- 单个操作的追踪单元
- 包含操作名称、开始时间、持续时间
- 关联的标签和日志
- 父子关系构成调用树

**Trace（追踪）：**
- 端到端请求的完整调用链
- 由多个Span组成的有向无环图
- 包含全局唯一的Trace ID
- 跨越多个服务和组件

**Context（上下文）：**
- 追踪状态的传播载体
- 包含Trace ID和Span ID
- 在服务间传递追踪信息
- 支持分布式调用关联

### 采样策略
**头部采样(Head Sampling)：**
- 在请求开始时决定是否采样
- 采样决策影响整个调用链
- 实现简单，性能开销小
- 可能丢失重要异常信息

**尾部采样(Tail Sampling)：**
- 收集完整追踪后再决定采样
- 基于完整信息做智能决策
- 可以优先保留异常和慢请求
- 存储和处理开销较大

**自适应采样：**
- 根据系统负载动态调整采样率
- 结合业务规则和性能指标
- 平衡观测性和系统性能
- 需要复杂的决策算法

## OpenTelemetry标准

### 数据模型
**资源(Resource)：**
- 描述服务实例的属性
- 包括服务名称、版本、环境等
- 在整个追踪生命周期中保持不变

**Span属性：**
```go
span.SetAttribute("http.method", "GET")
span.SetAttribute("http.url", "https://api.example.com/users")
span.SetAttribute("http.status_code", 200)
span.SetAttribute("db.statement", "SELECT * FROM users")
```

**事件(Events)：**
```go
span.AddEvent("Starting database query")
span.AddEvent("Query completed", attributes)
```

### 传播机制
**W3C Trace Context：**
```
traceparent: 00-12345678901234567890123456789012-1234567890123456-01
```

**B3 Propagation：**
```
X-B3-TraceId: 12345678901234567890123456789012
X-B3-SpanId: 1234567890123456
X-B3-ParentSpanId: 1234567890123450
X-B3-Sampled: 1
```

### 自动插桩
**框架支持：**
- HTTP客户端/服务器
- 数据库连接池
- 消息队列客户端
- RPC框架

**语言SDK：**
- Java: OpenTelemetry Java Agent
- Python: opentelemetry-distro
- Go: go.opentelemetry.io
- Node.js: @opentelemetry/auto-instrumentations-node

## 追踪系统架构

### Jaeger架构
**组件组成：**
- **Jaeger Client**: 应用端库
- **Jaeger Agent**: 本地代理，接收Span
- **Jaeger Collector**: 收集器，处理和存储
- **Jaeger Query**: 查询服务
- **Jaeger UI**: Web界面

**存储后端：**
- Cassandra: 分布式存储
- Elasticsearch: 全文搜索
- Memory: 内存存储（测试用）

### Zipkin架构
**简化架构：**
- **Collector**: 收集追踪数据
- **Storage**: 存储组件
- **API**: 查询接口
- **UI**: 用户界面

**特点：**
- 轻量级实现
- 多种语言支持
- 丰富的存储选项

### OpenTelemetry Collector
**接收器(Receivers)：**
- OTLP (OpenTelemetry Protocol)
- Jaeger格式
- Zipkin格式
- Prometheus指标

**处理器(Processors)：**
- 批处理(batch)
- 采样(sampling)
- 属性处理(attributes)
- 过滤(filtering)

**导出器(Exporters)：**
- Jaeger
- Zipkin
- Elasticsearch
- Kafka

## 性能分析方法

### 延迟分析
**响应时间分解：**
- 网络延迟
- 序列化/反序列化时间
- 数据库查询时间
- 业务逻辑处理时间

**关键路径识别：**
- 找出调用链中的瓶颈
- 识别串行vs并行操作
- 计算关键路径长度

### 错误追踪
**异常传播分析：**
- 异常在调用链中的传递
- 错误处理逻辑的执行
- 降级和熔断机制的触发

**错误模式识别：**
- 常见错误类型的统计
- 错误发生的时间模式
- 错误影响的范围分析

### 依赖分析
**服务依赖图：**
- 服务间的调用关系
- 调用频率和成功率
- 依赖的健康状态

**性能影响评估：**
- 下游服务对上游的影响
- 级联故障的传播路径
- 依赖关系的强弱程度

## 追踪数据存储

### 时序存储
**ClickHouse：**
- 列式存储，查询性能高
- 支持复杂SQL查询
- 分布式部署能力
- 适合大规模追踪数据

**表结构设计：**
```sql
CREATE TABLE traces (
    trace_id String,
    span_id String,
    parent_span_id String,
    service_name String,
    operation_name String,
    start_time DateTime64(9),
    duration UInt64,
    tags Map(String, String),
    logs Array(Tuple(String, Map(String, String)))
) ENGINE = MergeTree()
ORDER BY (service_name, start_time, trace_id)
```

### 图数据库
**Neo4j：**
- 原生图存储
- 复杂关系查询
- 路径分析能力
- 适合依赖关系分析

**数据建模：**
```
(Service:Service)-[:CALLS]->(Service:Service)
(Span:Span)-[:BELONGS_TO]->(Trace:Trace)
(Span:Span)-[:PRECEDES]->(Span:Span)
```

### 搜索存储
**Elasticsearch：**
- 全文搜索能力
- 聚合分析功能
- 可视化集成
- 适合日志关联分析

## 采样优化

### 确定性采样
**固定比例采样：**
```python
if random.random() < 0.1:  # 10%采样率
    create_span()
```

**基于规则采样：**
```python
if request.path.startswith('/api/v1/'):
    sample = True
elif request.user.is_premium:
    sample = True
else:
    sample = random.random() < 0.01
```

### 概率采样
**一致性哈希采样：**
- 基于Trace ID的哈希值采样
- 保证相同Trace的完整性
- 支持动态调整采样率

**自适应采样：**
- 基于系统负载调整采样率
- 优先采样异常和慢请求
- 使用机器学习优化采样决策

## 性能监控

### 追踪开销
**CPU开销：**
- Span创建和属性设置
- 上下文传播
- 序列化处理

**内存开销：**
- Span对象存储
- 上下文对象
- 缓冲区管理

**网络开销：**
- 数据上报流量
- 压缩传输
- 批量发送优化

### 优化策略
**异步处理：**
- 后台线程上报数据
- 非阻塞Span操作
- 批量数据发送

**采样控制：**
- 动态采样率调整
- 基于优先级的采样
- 异常路径全采样

**资源限制：**
- 内存缓冲区大小限制
- 上报频率控制
- 超时和重试机制

## 集成实践

### 微服务架构集成
**服务网格集成：**
- Istio集成
- Linkerd集成
- Envoy代理

**框架集成：**
- Spring Cloud Sleuth
- Micronaut Tracing
- Quarkus OpenTelemetry

### 大数据系统集成
**Spark应用追踪：**
```python
from pyspark.sql import SparkSession
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# 初始化追踪
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent",
    agent_port=14268,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)

# 在Spark作业中添加追踪
with tracer.start_as_span("spark_job") as span:
    span.set_attribute("spark.app_name", "data_processing")
    span.set_attribute("spark.executor_count", 4)

    # Spark处理逻辑
    df = spark.read.parquet("input/")
    result = df.groupBy("category").count()
    result.write.parquet("output/")
```

**Kafka流处理追踪：**
```java
// Kafka Streams集成
StreamsBuilder builder = new StreamsBuilder();
KStream<String, String> stream = builder.stream("input-topic");

// 添加追踪
stream.mapValues(value -> {
    Span span = tracer.startSpan("process_message");
    try (Scope scope = tracer.activateSpan(span)) {
        span.setAttribute("kafka.topic", "input-topic");
        // 处理逻辑
        return processValue(value);
    } finally {
        span.end();
    }
});
```

## 最佳实践

### 追踪策略
**关键路径追踪：**
- 用户请求入口
- 数据库操作
- 外部服务调用
- 业务关键逻辑

**异常全追踪：**
- 所有错误和异常
- 超时操作
- 降级和熔断触发

### 标签标准化
**通用标签：**
- `service.name`: 服务名称
- `service.version`: 服务版本
- `deployment.environment`: 部署环境
- `host.name`: 主机名称

**业务标签：**
- `user.id`: 用户ID
- `request.id`: 请求ID
- `business.operation`: 业务操作
- `data.size`: 数据大小

### 监控与告警
**追踪质量监控：**
- 采样率达成
- 数据完整性
- 处理延迟
- 错误率统计

**性能监控：**
- 追踪系统资源使用
- 查询响应时间
- 存储增长率
- 系统可用性