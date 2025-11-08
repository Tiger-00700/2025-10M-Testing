# 大数据处理系统的高级指标监控实现


from prometheus_client import Counter, Gauge, Histogram, Summary, start_http_server, Info, Enum
import time
import random
import threading
from contextlib import contextmanager
from functools import wraps
import psutil  # 用于获取真实系统资源指标

# ================ 1. 基础指标定义 ================



# 数据处理计数器 - 带标签增强


PROCESSING_COUNTER = Counter(
    'bigdata_processing_total',
    'Total number of data records processed',
    ['pipeline', 'stage', 'status', 'data_source', 'job_type']
)

# 错误计数器 - 按错误类型分类


ERROR_COUNTER = Counter(
    'bigdata_errors_total',
    'Total number of errors by type',
    ['pipeline', 'stage', 'error_type', 'severity']
)

# 数据处理延迟直方图 - 优化的桶配置


PROCESSING_HISTOGRAM = Histogram(
    'bigdata_processing_seconds',
    'Time spent processing data',
    ['pipeline', 'stage', 'data_volume'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0)
)

# 数据质量摘要 - 多维度评估


DATA_QUALITY_SUMMARY = Summary(
    'bigdata_data_quality_score',
    'Data quality score for processed data',
    ['pipeline', 'data_type', 'quality_dimension']  # 质量维度：完整性、准确性、一致性等
)

# 系统资源仪表盘 - 增强版


RESOURCE_GAUGE = Gauge(
    'bigdata_resource_usage',
    'Resource usage for big data processing',
    ['resource_type', 'component', 'host', 'instance']
)

# 队列长度仪表盘


QUEUE_LENGTH_GAUGE = Gauge(
    'bigdata_queue_length',
    'Length of processing queues',
    ['queue_name', 'priority']
)

# 并行度仪表盘


PARALLELISM_GAUGE = Gauge(
    'bigdata_task_parallelism',
    'Current parallelism level of tasks',
    ['pipeline', 'resource_pool']
)

# 版本信息指标


VERSION_INFO = Info(
    'bigdata_pipeline_version',
    'Version information about the data pipeline'
)

# 任务状态枚举


TASK_STATUS_ENUM = Enum(
    'bigdata_task_status',
    'Current status of data processing tasks',
    states=['idle', 'running', 'succeeded', 'failed', 'retrying'],
    labelnames=['pipeline', 'task_id']
)

# 数据量大小直方图 - 跟踪不同大小的数据批次


DATA_VOLUME_HISTOGRAM = Histogram(
    'bigdata_batch_size_bytes',
    'Size of data batches processed',
    ['pipeline', 'stage'],
    buckets=(1024, 10240, 102400, 1048576, 10485760, 104857600, 1048576000)
)

# 缓存命中率计数器


CACHE_HIT_COUNTER = Counter(
    'bigdata_cache_operations_total',
    'Cache hit/miss operations',
    ['cache_name', 'operation_type']  # operation_type: hit, miss, evict
)

# ================ 2. 工具函数与装饰器 ================



@contextmanager
def measure_processing_time(pipeline, stage, data_volume='medium'):
    """用于测量和记录处理时间的上下文管理器"""
    start_time = time.time()
    try:
        yield
    finally:
        PROCESSING_HISTOGRAM.labels(
            pipeline=pipeline,
            stage=stage,
            data_volume=data_volume
        ).observe(time.time() - start_time)

def monitor_method(pipeline, stage):
    """用于监控方法执行的装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 记录方法开始执行
            TASK_STATUS_ENUM.labels(pipeline=pipeline, task_id=f"{stage}-{id(func)}").state('running')

            try:
                # 测量执行时间
                with measure_processing_time(pipeline, stage):
                    result = func(*args, **kwargs)

                # 记录成功状态
                TASK_STATUS_ENUM.labels(pipeline=pipeline, task_id=f"{stage}-{id(func)}").state('succeeded')
                return result
            except Exception as e:
                # 记录错误
                error_type = type(e).__name__
                ERROR_COUNTER.labels(
                    pipeline=pipeline,
                    stage=stage,
                    error_type=error_type,
                    severity='critical' if 'fatal' in str(e).lower() else 'warning'
                ).inc()

                # 更新任务状态为失败
                TASK_STATUS_ENUM.labels(pipeline=pipeline, task_id=f"{stage}-{id(func)}").state('failed')
                raise
        return wrapper
    return decorator

# ================ 3. 数据处理模拟与监控 ================



class DataPipelineMonitor:
    """数据流水线监控类"""

    def __init__(self, pipeline_name):
        self.pipeline_name = pipeline_name
        # 设置版本信息
        VERSION_INFO.info({
            'pipeline': pipeline_name,
            'version': '1.2.3',
            'build_date': '2023-10-23',
            'environment': 'production'
        })

    @monitor_method(pipeline='etl_pipeline', stage='extract')
    def extract_data(self, source_type, record_count):
        """提取数据阶段"""
        # 模拟提取延迟
        time.sleep(random.uniform(0.2, 1.0))

        # 模拟不同的数据量
        batch_size_bytes = random.randint(10240, 104857600)
        DATA_VOLUME_HISTOGRAM.labels(
            pipeline=self.pipeline_name,
            stage='extract'
        ).observe(batch_size_bytes)

        # 模拟成功率
        success_rate = random.uniform(0.9, 0.99)
        successful_records = int(record_count * success_rate)
        failed_records = record_count - successful_records

        # 更新计数器
        PROCESSING_COUNTER.labels(
            pipeline=self.pipeline_name,
            stage='extract',
            status='success',
            data_source=source_type,
            job_type='batch'
        ).inc(successful_records)

        if failed_records > 0:
            PROCESSING_COUNTER.labels(
                pipeline=self.pipeline_name,
                stage='extract',
                status='failure',
                data_source=source_type,
                job_type='batch'
            ).inc(failed_records)

        # 更新数据质量指标 - 完整性
        DATA_QUALITY_SUMMARY.labels(
            pipeline=self.pipeline_name,
            data_type=source_type,
            quality_dimension='completeness'
        ).observe(success_rate)

        return {"status": "success", "processed": successful_records, "failed": failed_records}

    @monitor_method(pipeline='etl_pipeline', stage='transform')
    def transform_data(self, input_data, transformations=None):
        """转换数据阶段"""
        # 模拟转换延迟
        time.sleep(random.uniform(0.5, 2.0))

        # 模拟不同转换操作的成功率
        transformations = transformations or ['clean', 'normalize', 'enrich', 'validate']
        for transform in transformations:
            # 为每个转换操作记录质量指标
            quality_score = random.uniform(0.85, 1.0)
            DATA_QUALITY_SUMMARY.labels(
                pipeline=self.pipeline_name,
                data_type='transformed',
                quality_dimension=transform
            ).observe(quality_score)

        # 模拟整体转换成功率
        success_rate = random.uniform(0.92, 0.98)
        successful_records = int(input_data['processed'] * success_rate)
        failed_records = input_data['processed'] - successful_records

        # 更新计数器
        PROCESSING_COUNTER.labels(
            pipeline=self.pipeline_name,
            stage='transform',
            status='success',
            data_source='internal',
            job_type='batch'
        ).inc(successful_records)

        if failed_records > 0:
            PROCESSING_COUNTER.labels(
                pipeline=self.pipeline_name,
                stage='transform',
                status='failure',
                data_source='internal',
                job_type='batch'
            ).inc(failed_records)

        return {"status": "success", "processed": successful_records, "failed": failed_records}

    @monitor_method(pipeline='etl_pipeline', stage='load')
    def load_data(self, input_data, target_type):
        """加载数据阶段"""
        # 模拟加载延迟
        time.sleep(random.uniform(0.3, 1.5))

        # 模拟加载成功率
        success_rate = random.uniform(0.95, 1.0)
        successful_records = int(input_data['processed'] * success_rate)
        failed_records = input_data['processed'] - successful_records

        # 更新计数器
        PROCESSING_COUNTER.labels(
            pipeline=self.pipeline_name,
            stage='load',
            status='success',
            data_source='internal',
            job_type='batch'
        ).inc(successful_records)

        if failed_records > 0:
            PROCESSING_COUNTER.labels(
                pipeline=self.pipeline_name,
                stage='load',
                status='failure',
                data_source='internal',
                job_type='batch'
            ).inc(failed_records)

        # 更新数据质量指标 - 一致性
        DATA_QUALITY_SUMMARY.labels(
            pipeline=self.pipeline_name,
            data_type=target_type,
            quality_dimension='consistency'
        ).observe(success_rate)

        return {"status": "success", "processed": successful_records, "failed": failed_records}

def update_system_resources(interval=5):
    """更新系统资源指标的后台线程函数"""
    def _update_loop():
        while True:
            # 获取真实系统资源指标
            try:
                # CPU使用率
                cpu_usage = psutil.cpu_percent(interval=0.1)
                RESOURCE_GAUGE.labels(
                    resource_type='cpu',
                    component='spark_executor',
                    host='localhost',
                    instance='executor-1'
                ).set(cpu_usage)

                # 内存使用率
                memory = psutil.virtual_memory()
                RESOURCE_GAUGE.labels(
                    resource_type='memory',
                    component='spark_executor',
                    host='localhost',
                    instance='executor-1'
                ).set(memory.percent)

                # 磁盘I/O
                disk_io = psutil.disk_io_counters()
                # 转换为每秒读写字节数
                # 注意：这里需要计算速率，简化处理
                RESOURCE_GAUGE.labels(
                    resource_type='disk_read_bytes',
                    component='hdfs_datanode',
                    host='localhost',
                    instance='datanode-1'
                ).set(disk_io.read_bytes / (interval * 1024 * 1024))  # MB

                RESOURCE_GAUGE.labels(
                    resource_type='disk_write_bytes',
                    component='hdfs_datanode',
                    host='localhost',
                    instance='datanode-1'
                ).set(disk_io.write_bytes / (interval * 1024 * 1024))  # MB

                # 网络流量
                net_io = psutil.net_io_counters()
                RESOURCE_GAUGE.labels(
                    resource_type='network_recv_bytes',
                    component='cluster',
                    host='localhost',
                    instance='network-1'
                ).set(net_io.bytes_recv / (interval * 1024 * 1024))  # MB

                RESOURCE_GAUGE.labels(
                    resource_type='network_sent_bytes',
                    component='cluster',
                    host='localhost',
                    instance='network-1'
                ).set(net_io.bytes_sent / (interval * 1024 * 1024))  # MB

                # 模拟队列长度
                QUEUE_LENGTH_GAUGE.labels(
                    queue_name='ingestion_queue',
                    priority='high'
                ).set(random.randint(0, 1000))

                # 模拟并行度
                PARALLELISM_GAUGE.labels(
                    pipeline='etl_pipeline',
                    resource_pool='default'
                ).set(random.randint(1, 32))

                # 模拟缓存操作
                if random.random() < 0.7:  # 70%概率缓存命中
                    CACHE_HIT_COUNTER.labels(
                        cache_name='data_lookup_cache',
                        operation_type='hit'
                    ).inc()
                else:
                    CACHE_HIT_COUNTER.labels(
                        cache_name='data_lookup_cache',
                        operation_type='miss'
                    ).inc()

                # 偶尔模拟缓存驱逐
                if random.random() < 0.05:
                    CACHE_HIT_COUNTER.labels(
                        cache_name='data_lookup_cache',
                        operation_type='evict'
                    ).inc()

            except Exception as e:
                print(f"更新资源指标失败: {e}")
                # 记录错误但继续运行
                ERROR_COUNTER.labels(
                    pipeline='monitoring',
                    stage='resource_collection',
                    error_type=type(e).__name__,
                    severity='warning'
                ).inc()

            time.sleep(interval)

    # 启动后台线程
    thread = threading.Thread(target=_update_loop, daemon=True)
    thread.start()
    return thread

# ================ 4. 主执行逻辑 ================



def main():
    # 启动指标HTTP服务器
    start_http_server(8000)
    print("指标服务器启动在 http://localhost:8000/metrics")

    # 启动资源监控线程
    resource_thread = update_system_resources(interval=5)

    # 创建监控实例
    monitor = DataPipelineMonitor('etl_pipeline')

    # 模拟持续的数据处理
    pipeline_runs = 0
    try:
        while True:
            pipeline_runs += 1
            print(f"\n执行流水线运行 #{pipeline_runs}")

            # 模拟数据提取
            extract_result = monitor.extract_data(
                source_type=random.choice(['kafka', 'hdfs', 'database', 'api']),
                record_count=random.randint(5000, 20000)
            )
            print(f"提取结果: 成功={extract_result['processed']}, 失败={extract_result['failed']}")

            # 模拟数据转换
            transform_result = monitor.transform_data(
                input_data=extract_result,
                transformations=random.sample(['clean', 'normalize', 'enrich', 'validate', 'aggregate'],
                                            k=random.randint(2, 5))
            )
            print(f"转换结果: 成功={transform_result['processed']}, 失败={transform_result['failed']}")

            # 模拟数据加载
            load_result = monitor.load_data(
                input_data=transform_result,
                target_type=random.choice(['hive', 'elasticsearch', 'data_lake', 'data_mart'])
            )
            print(f"加载结果: 成功={load_result['processed']}, 失败={load_result['failed']}")

            # 随机模拟异常情况
            if random.random() < 0.1:  # 10%概率触发异常
                print("模拟异常情况...")
                # 故意调用一个会失败的方法
                with measure_processing_time(pipeline='etl_pipeline', stage='error_test'):
                    raise Exception("模拟的数据处理错误")

            # 等待一段时间再执行下一次
            sleep_time = random.uniform(2, 5)
            print(f"等待 {sleep_time:.2f} 秒...")
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n接收到中断信号，正在退出...")
    finally:
        print("程序已退出")

if __name__ == "__main__":
    # 在实际环境中，psutil需要安装: pip install psutil
    main()
