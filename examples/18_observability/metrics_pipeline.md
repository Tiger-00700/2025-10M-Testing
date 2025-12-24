# 指标体系设计与数据管道

## 指标分类体系

### 系统指标(Infrastructure Metrics)
**服务器指标：**
- CPU使用率、负载平均值
- 内存总量、使用量、可用量
- 磁盘读写IOPS、吞吐量
- 网络收发包数、带宽利用率

**容器指标：**
- 容器CPU/内存限制和使用
- 磁盘I/O统计
- 网络流量监控
- 重启次数、健康状态

### 应用指标(Application Metrics)
**性能指标：**
- 请求响应时间分布
- 吞吐量(QPS/TPS)
- 并发连接数
- 线程池状态

**错误指标：**
- 错误率、异常计数
- HTTP状态码分布
- 业务错误分类
- 超时统计

### 业务指标(Business Metrics)
**核心KPI：**
- 用户注册数、活跃用户
- 订单量、转化率
- 营收指标、ARPU值
- 客户满意度评分

**运营指标：**
- 页面访问量、停留时间
- 功能使用统计
- A/B测试效果
- 用户行为路径

## 指标命名规范

### Prometheus命名约定
```
<namespace>_<subsystem>_<name>_<suffix>
```

**示例：**
- `http_requests_total` - HTTP请求总数
- `cpu_usage_percent` - CPU使用百分比
- `memory_bytes_used` - 已用内存字节数
- `disk_io_bytes_total` - 磁盘I/O总字节数

### 标签体系
**基础标签：**
- `instance` - 实例标识
- `job` - 作业名称
- `service` - 服务名称
- `environment` - 环境标识

**业务标签：**
- `region` - 地域
- `cluster` - 集群
- `version` - 版本号
- `user_type` - 用户类型

## 数据管道架构

### 数据收集层
**收集器类型：**
- **Exporter**: 专用指标导出器
- **Agent**: 通用数据收集代理
- **SDK**: 应用内埋点收集
- **Push Gateway**: 推送网关

**收集协议：**
- Prometheus格式
- StatsD协议
- JMX接口
- HTTP API

### 数据处理层
**预处理：**
- 数据验证和清洗
- 格式标准化
- 异常值检测
- 缺失值补全

**聚合计算：**
- 时间序列聚合
- 多维度汇总
- 统计指标计算
- 趋势分析

### 数据存储层
**存储引擎选择：**
- **时序数据库**: Prometheus、InfluxDB、VictoriaMetrics
- **列式存储**: ClickHouse、Druid
- **对象存储**: S3、MinIO (用于归档)

**存储优化：**
- 数据压缩
- 分层存储
- 索引优化
- 缓存策略

## 指标管道实现

### Prometheus生态
**核心组件：**
- **Prometheus Server**: 指标收集和存储
- **AlertManager**: 告警管理
- **Push Gateway**: 指标推送
- **Service Discovery**: 服务发现

**配置示例：**
```yaml
scrape_configs:
  - job_name: 'application'
    static_configs:
      - targets: ['app:8080']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Telegraf集成
**输入插件：**
- 系统指标收集
- 容器监控
- 网络设备监控
- 数据库性能指标

**输出插件：**
- InfluxDB存储
- Prometheus格式
- Kafka消息队列
- 文件输出

### 自定义指标收集
**Python实现：**
```python
from prometheus_client import Gauge, Counter, Histogram, start_http_server
import time
import psutil

# 定义指标
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('memory_usage_percent', 'Memory usage percentage')
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])

# 收集系统指标
def collect_system_metrics():
    cpu_usage.set(psutil.cpu_percent())
    memory_usage.set(psutil.virtual_memory().percent)

# HTTP请求计数
def record_request(method, endpoint):
    request_count.labels(method=method, endpoint=endpoint).inc()
```

## 数据质量保证

### 指标准确性
**校验机制：**
- 数据范围检查
- 单位一致性验证
- 时间戳准确性
- 标签完整性

### 指标完整性
**监控覆盖：**
- 关键指标完备性检查
- 数据采集成功率
- 异常指标检测
- 缺失数据补全

### 指标时效性
**延迟控制：**
- 采集间隔优化
- 传输延迟监控
- 处理时间统计
- 存储写入延迟

## 查询与分析

### PromQL查询语言
**基础查询：**
- `cpu_usage_percent` - 当前CPU使用率
- `cpu_usage_percent{instance="web01"}` - 指定实例CPU使用率
- `rate(http_requests_total[5m])` - 5分钟请求率

**聚合查询：**
- `sum(rate(http_requests_total[5m])) by (method)` - 按方法聚合请求率
- `avg(cpu_usage_percent) by (cluster)` - 按集群平均CPU使用率
- `histogram_quantile(0.95, rate(http_request_duration_bucket[5m]))` - 95分位响应时间

### 性能优化
**查询优化：**
- 选择器优化
- 时间范围控制
- 聚合函数选择
- 缓存利用

## 扩展与集成

### 多数据源集成
**异构数据源：**
- 关系型数据库指标
- NoSQL数据库统计
- 消息队列监控
- 外部API数据

### 联邦集群
**水平扩展：**
- 数据分片存储
- 查询负载均衡
- 跨集群聚合
- 全局视图

### 云服务集成
**云监控API：**
- AWS CloudWatch
- Azure Monitor
- Google Cloud Monitoring
- 阿里云监控

## 最佳实践

### 指标设计原则
- **可测量性**: 能够量化衡量的指标
- **可操作性**: 对问题诊断有帮助的指标
- **相关性**: 与业务目标相关的指标
- **经济性**: 采集和存储成本合理

### 管道运维
- **监控监控系统**: 自身健康状态监控
- **容量规划**: 存储和计算资源规划
- **备份恢复**: 数据备份和灾难恢复
- **升级策略**: 平滑升级和回滚方案

### 成本控制
- **数据采样**: 降低采集频率或精度
- **存储优化**: 数据压缩和清理策略
- **查询限制**: 防止过度查询消耗资源
- **资源监控**: 监控系统自身资源使用