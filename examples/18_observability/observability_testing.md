# 可观测性测试框架与方法

## 测试策略概述

### 测试目标
**功能完整性：**
- 验证三大支柱的完整实现
- 确保数据收集的准确性
- 确认可视化和告警功能

**性能表现：**
- 评估可观测性系统的性能影响
- 验证高负载下的稳定性
- 确认资源使用效率

**可靠性保证：**
- 测试系统故障场景
- 验证数据持久性和一致性
- 确认备份和恢复能力

### 测试类型
**单元测试：**
- 单个组件的功能测试
- 指标收集器的准确性验证
- 日志处理逻辑的正确性检查

**集成测试：**
- 组件间的协作测试
- 数据流转的完整性验证
- 端到端的数据管道测试

**系统测试：**
- 完整可观测性系统的功能测试
- 性能和负载测试
- 故障恢复和容错测试

## 指标测试

### 指标收集测试
**收集器功能测试：**
```python
class MetricsCollectorTest(unittest.TestCase):
    def test_cpu_metrics_collection(self):
        """测试CPU指标收集"""
        collector = SystemMetricsCollector()

        # 收集指标
        metrics = collector.collect_cpu_metrics()

        # 验证指标存在
        self.assertIn('cpu_usage_percent', metrics)
        self.assertIn('cpu_load_average', metrics)

        # 验证指标范围
        self.assertGreaterEqual(metrics['cpu_usage_percent'], 0)
        self.assertLessEqual(metrics['cpu_usage_percent'], 100)

    def test_memory_metrics_collection(self):
        """测试内存指标收集"""
        collector = SystemMetricsCollector()
        metrics = collector.collect_memory_metrics()

        # 验证关键指标
        required_metrics = ['total_bytes', 'used_bytes', 'free_bytes', 'usage_percent']
        for metric in required_metrics:
            self.assertIn(metric, metrics)

        # 验证数据一致性
        self.assertEqual(
            metrics['used_bytes'] + metrics['free_bytes'],
            metrics['total_bytes']
        )
```

**指标准确性测试：**
```python
def test_metrics_accuracy():
    """测试指标准确性"""
    # 创建测试环境
    test_env = MetricsTestEnvironment()

    # 生成已知负载
    test_env.generate_cpu_load(50)  # 50% CPU负载

    # 等待指标收集
    time.sleep(10)

    # 获取收集的指标
    collected_metrics = test_env.get_collected_metrics()

    # 验证准确性（允许5%误差）
    expected_cpu = 50
    actual_cpu = collected_metrics['cpu_usage_percent']
    accuracy = abs(actual_cpu - expected_cpu) / expected_cpu

    assert accuracy < 0.05, f"CPU metrics accuracy too low: {accuracy}"
```

### 指标存储测试
**存储持久性测试：**
```python
def test_metrics_persistence():
    """测试指标存储持久性"""
    storage = MetricsStorage()

    # 存储测试指标
    test_metrics = {
        'timestamp': datetime.now(),
        'cpu_usage': 75.5,
        'memory_usage': 60.2
    }
    storage.store_metrics(test_metrics)

    # 模拟系统重启
    storage.simulate_restart()

    # 验证数据持久性
    retrieved_metrics = storage.retrieve_metrics(
        start_time=test_metrics['timestamp'] - timedelta(minutes=1),
        end_time=test_metrics['timestamp'] + timedelta(minutes=1)
    )

    assert len(retrieved_metrics) > 0, "Metrics not persisted after restart"
```

**查询性能测试：**
```python
def test_metrics_query_performance():
    """测试指标查询性能"""
    storage = MetricsStorage()
    query_engine = MetricsQueryEngine(storage)

    # 生成大量测试数据
    generate_test_metrics(storage, count=100000)

    # 测试查询性能
    start_time = time.time()
    results = query_engine.query_range(
        metric_name='cpu_usage',
        start_time=datetime.now() - timedelta(hours=1),
        end_time=datetime.now()
    )
    query_time = time.time() - start_time

    # 验证性能要求（查询时间 < 1秒）
    assert query_time < 1.0, f"Query too slow: {query_time}s"

    # 验证结果正确性
    assert len(results) > 0, "No results returned"
```

## 日志测试

### 日志格式测试
**结构化日志测试：**
```python
def test_log_structuring():
    """测试日志结构化"""
    log_processor = LogProcessor()

    # 测试不同格式的日志
    test_logs = [
        '2024-01-01 10:00:00 INFO User login successful: user_id=123',
        '{"timestamp": "2024-01-01T10:00:00Z", "level": "INFO", "message": "User login"}',
        'ERROR Database connection failed: timeout'
    ]

    for log_line in test_logs:
        structured_log = log_processor.parse_log(log_line)

        # 验证必需字段
        required_fields = ['timestamp', 'level', 'message']
        for field in required_fields:
            assert field in structured_log, f"Missing field: {field}"

        # 验证时间戳格式
        try:
            datetime.fromisoformat(structured_log['timestamp'])
        except ValueError:
            pytest.fail("Invalid timestamp format")
```

**日志字段提取测试：**
```python
def test_log_field_extraction():
    """测试日志字段提取"""
    extractor = LogFieldExtractor()

    test_log = '2024-01-01 10:00:00 INFO [UserService] Login attempt: user=john, ip=192.168.1.100, result=success'

    fields = extractor.extract_fields(test_log)

    # 验证提取的字段
    expected_fields = {
        'service': 'UserService',
        'user': 'john',
        'ip': '192.168.1.100',
        'result': 'success'
    }

    for field, expected_value in expected_fields.items():
        assert fields.get(field) == expected_value, f"Field extraction failed for {field}"
```

### 日志传输测试
**传输可靠性测试：**
```python
def test_log_transport_reliability():
    """测试日志传输可靠性"""
    sender = LogSender()
    receiver = LogReceiver()

    # 发送测试日志
    test_logs = [f"Test log message {i}" for i in range(1000)]
    sent_count = sender.send_logs(test_logs)

    # 等待传输完成
    time.sleep(5)

    # 验证接收到的日志
    received_logs = receiver.get_received_logs()
    received_count = len(received_logs)

    # 验证传输完整性（允许1%丢失）
    loss_rate = (sent_count - received_count) / sent_count
    assert loss_rate < 0.01, f"Log transport loss rate too high: {loss_rate}"

    # 验证日志顺序
    for i, log in enumerate(received_logs[:100]):  # 检查前100条
        assert f"Test log message {i}" == log, f"Log order incorrect at position {i}"
```

**传输性能测试：**
```python
def test_log_transport_performance():
    """测试日志传输性能"""
    sender = LogSender()
    receiver = LogReceiver()

    # 测试不同负载下的性能
    test_loads = [100, 1000, 10000]

    for load in test_loads:
        start_time = time.time()

        # 发送日志
        test_logs = [f"Performance test log {i}" for i in range(load)]
        sender.send_logs(test_logs)

        # 等待传输
        time.sleep(1)

        # 验证接收
        received_count = len(receiver.get_received_logs())

        transmission_time = time.time() - start_time
        throughput = received_count / transmission_time

        print(f"Load {load}: {throughput} logs/second")

        # 验证最小吞吐量要求
        assert throughput > 100, f"Throughput too low for load {load}: {throughput}"
```

## 追踪测试

### 追踪注入测试
**上下文传播测试：**
```python
def test_trace_context_propagation():
    """测试追踪上下文传播"""
    tracer = TestTracer()

    # 创建根span
    with tracer.start_span("root_operation") as root_span:
        root_trace_id = root_span.get_span_context().trace_id

        # 模拟服务调用
        result = simulate_service_call(tracer)

        # 验证上下文传播
        assert result['trace_id'] == root_trace_id, "Trace ID not propagated"

        # 验证span层级
        spans = tracer.get_finished_spans()
        assert len(spans) >= 2, "Should have at least root and child spans"

        # 验证父子关系
        child_span = next(span for span in spans if span != root_span)
        assert child_span.parent_span_id == root_span.span_id, "Parent-child relationship incorrect"
```

**跨服务追踪测试：**
```python
def test_cross_service_tracing():
    """测试跨服务追踪"""
    service_a = MockService("service-a")
    service_b = MockService("service-b")
    service_c = MockService("service-c")

    # 模拟请求链：A -> B -> C
    with service_a.tracer.start_span("request") as span:
        # 服务A调用服务B
        response_b = service_a.call_service(service_b)

        # 服务B调用服务C
        response_c = service_b.call_service(service_c)

    # 验证完整追踪
    all_spans = []
    for service in [service_a, service_b, service_c]:
        all_spans.extend(service.tracer.get_finished_spans())

    # 按开始时间排序
    all_spans.sort(key=lambda s: s.start_time)

    # 验证追踪连续性
    for i in range(len(all_spans) - 1):
        current_span = all_spans[i]
        next_span = all_spans[i + 1]

        # 验证时间连续性（允许1ms误差）
        time_gap = next_span.start_time - (current_span.start_time + current_span.duration)
        assert abs(time_gap) < 1000, f"Time gap too large between spans: {time_gap}μs"
```

### 追踪查询测试
**追踪检索测试：**
```python
def test_trace_retrieval():
    """测试追踪检索"""
    trace_storage = TraceStorage()
    trace_query = TraceQuery(trace_storage)

    # 存储测试追踪
    test_trace = generate_test_trace()
    trace_storage.store_trace(test_trace)

    # 按Trace ID查询
    retrieved_trace = trace_query.get_trace_by_id(test_trace.trace_id)
    assert retrieved_trace is not None, "Trace not found by ID"

    # 按服务查询
    service_traces = trace_query.get_traces_by_service("test-service")
    assert len(service_traces) > 0, "No traces found for service"

    # 按时间范围查询
    time_range_traces = trace_query.get_traces_by_time_range(
        start_time=datetime.now() - timedelta(hours=1),
        end_time=datetime.now()
    )
    assert len(time_range_traces) > 0, "No traces found in time range"
```

**追踪分析测试：**
```python
def test_trace_analysis():
    """测试追踪分析"""
    analyzer = TraceAnalyzer()

    # 生成测试追踪数据
    traces = generate_multiple_traces(count=100)

    # 分析响应时间
    latency_stats = analyzer.analyze_latency(traces)
    assert 'avg' in latency_stats, "Average latency not calculated"
    assert 'p95' in latency_stats, "95th percentile not calculated"
    assert 'p99' in latency_stats, "99th percentile not calculated"

    # 分析错误率
    error_stats = analyzer.analyze_errors(traces)
    assert 'total_requests' in error_stats, "Total requests not counted"
    assert 'error_rate' in error_stats, "Error rate not calculated"

    # 分析服务依赖
    dependency_graph = analyzer.analyze_dependencies(traces)
    assert len(dependency_graph.nodes) > 0, "No services found in dependency graph"
    assert len(dependency_graph.edges) > 0, "No dependencies found in dependency graph"
```

## 告警测试

### 告警规则测试
**规则触发测试：**
```python
def test_alert_rule_triggering():
    """测试告警规则触发"""
    rule_engine = AlertRuleEngine()

    # 定义测试规则
    cpu_rule = AlertRule(
        name="HighCPU",
        query="cpu_usage_percent > 80",
        duration="5m",
        severity="warning"
    )

    rule_engine.add_rule(cpu_rule)

    # 模拟指标数据
    metrics_data = [
        {"timestamp": "2024-01-01T10:00:00Z", "cpu_usage_percent": 70},
        {"timestamp": "2024-01-01T10:01:00Z", "cpu_usage_percent": 85},
        {"timestamp": "2024-01-01T10:02:00Z", "cpu_usage_percent": 90},
        {"timestamp": "2024-01-01T10:03:00Z", "cpu_usage_percent": 95},
        {"timestamp": "2024-01-01T10:04:00Z", "cpu_usage_percent": 88},
        {"timestamp": "2024-01-01T10:05:00Z", "cpu_usage_percent": 92},
    ]

    # 处理指标数据
    alerts = []
    for metric in metrics_data:
        new_alerts = rule_engine.process_metric(metric)
        alerts.extend(new_alerts)

    # 验证告警触发
    cpu_alerts = [a for a in alerts if a.name == "HighCPU"]
    assert len(cpu_alerts) > 0, "CPU alert should have been triggered"

    # 验证告警属性
    alert = cpu_alerts[0]
    assert alert.severity == "warning", "Alert severity incorrect"
    assert alert.labels["value"] > 80, "Alert threshold not met"
```

**告警抑制测试：**
```python
def test_alert_suppression():
    """测试告警抑制"""
    alert_manager = AlertManager()

    # 配置抑制规则
    suppression_rule = {
        "source_alert": "NodeDown",
        "target_alerts": ["ServiceUnavailable", "HighLatency"],
        "equal_labels": ["node"]
    }
    alert_manager.add_suppression_rule(suppression_rule)

    # 触发源告警
    node_down_alert = Alert(
        name="NodeDown",
        labels={"node": "worker-01", "cluster": "production"}
    )
    alert_manager.process_alert(node_down_alert)

    # 尝试触发目标告警
    service_alert = Alert(
        name="ServiceUnavailable",
        labels={"node": "worker-01", "service": "web-api"}
    )
    alert_manager.process_alert(service_alert)

    # 验证抑制生效
    active_alerts = alert_manager.get_active_alerts()
    service_alerts = [a for a in active_alerts if a.name == "ServiceUnavailable"]

    assert len(service_alerts) == 0, "Service alert should have been suppressed"
```

### 告警通知测试
**通知发送测试：**
```python
def test_alert_notification():
    """测试告警通知"""
    notification_system = AlertNotificationSystem()

    # 配置通知渠道
    email_config = {
        "type": "email",
        "recipients": ["alerts@company.com"],
        "smtp_server": "smtp.company.com"
    }
    notification_system.add_channel("email", email_config)

    # 创建测试告警
    test_alert = Alert(
        name="TestAlert",
        severity="critical",
        description="This is a test alert",
        labels={"service": "test-service"}
    )

    # 发送通知
    result = notification_system.send_notification(test_alert, "email")

    # 验证发送成功
    assert result["success"], f"Notification failed: {result.get('error')}"

    # 验证通知内容
    sent_notifications = notification_system.get_sent_notifications()
    assert len(sent_notifications) > 0, "No notifications were sent"

    notification = sent_notifications[0]
    assert test_alert.name in notification["subject"], "Alert name not in subject"
    assert test_alert.description in notification["body"], "Alert description not in body"
```

## 集成测试

### 端到端测试
**完整数据流测试：**
```python
def test_end_to_end_observability():
    """端到端可观测性测试"""
    test_env = ObservabilityTestEnvironment()

    try:
        # 1. 启动可观测性系统
        test_env.start_observability_stack()

        # 2. 部署测试应用
        test_env.deploy_test_application()

        # 3. 生成测试流量
        test_env.generate_test_traffic(duration_minutes=5)

        # 4. 验证指标收集
        metrics_collected = test_env.verify_metrics_collection()
        assert metrics_collected, "Metrics collection failed"

        # 5. 验证日志收集
        logs_collected = test_env.verify_logs_collection()
        assert logs_collected, "Logs collection failed"

        # 6. 验证追踪完整性
        traces_collected = test_env.verify_traces_collection()
        assert traces_collected, "Traces collection failed"

        # 7. 验证告警触发
        alerts_triggered = test_env.verify_alerts_triggering()
        assert alerts_triggered, "Alerts triggering failed"

        # 8. 验证可视化
        dashboards_accessible = test_env.verify_dashboards()
        assert dashboards_accessible, "Dashboards not accessible"

    finally:
        # 清理测试环境
        test_env.cleanup()
```

### 性能测试
**负载测试：**
```python
def test_observability_under_load():
    """负载下的可观测性测试"""
    load_tester = ObservabilityLoadTester()

    # 测试不同负载级别
    load_levels = [100, 500, 1000, 2000]  # RPS

    results = {}
    for load in load_levels:
        print(f"Testing load: {load} RPS")

        # 生成负载
        load_tester.generate_load(rps=load, duration_minutes=2)

        # 收集性能指标
        performance_metrics = load_tester.measure_performance()

        # 验证可观测性系统稳定性
        stability_metrics = load_tester.check_stability()

        results[load] = {
            "performance": performance_metrics,
            "stability": stability_metrics
        }

        # 验证性能阈值
        assert performance_metrics["response_time_p95"] < 500, f"P95 too high at {load} RPS"
        assert stability_metrics["data_loss_rate"] < 0.01, f"Data loss too high at {load} RPS"

    return results
```

### 故障恢复测试
**系统故障测试：**
```python
def test_fault_recovery():
    """故障恢复测试"""
    fault_tester = FaultRecoveryTester()

    # 测试不同故障场景
    fault_scenarios = [
        "prometheus_restart",
        "elasticsearch_node_failure",
        "network_partition",
        "disk_full"
    ]

    for scenario in fault_scenarios:
        print(f"Testing fault scenario: {scenario}")

        # 注入故障
        fault_tester.inject_fault(scenario)

        # 等待系统响应
        time.sleep(30)

        # 验证系统恢复
        recovery_status = fault_tester.verify_recovery()

        # 验证数据完整性
        data_integrity = fault_tester.check_data_integrity()

        assert recovery_status["system_up"] == True, f"System not recovered from {scenario}"
        assert data_integrity["data_preserved"] == True, f"Data lost during {scenario}"

        # 清理故障
        fault_tester.cleanup_fault(scenario)
```

## 测试自动化

### CI/CD集成
**测试流水线：**
```yaml
# .github/workflows/observability-tests.yml
name: Observability Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run unit tests
        run: python -m pytest tests/unit/ -v

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Docker
        run: docker-compose up -d
      - name: Wait for services
        run: sleep 60
      - name: Run integration tests
        run: python -m pytest tests/integration/ -v

  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup test environment
        run: ./setup-performance-test.sh
      - name: Run performance tests
        run: python -m pytest tests/performance/ -v
      - name: Generate performance report
        run: python generate-performance-report.py
```

### 测试报告生成
**自动化报告：**
```python
def generate_test_report(test_results):
    """生成测试报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": len(test_results),
            "passed": sum(1 for r in test_results.values() if r["success"]),
            "failed": sum(1 for r in test_results.values() if not r["success"])
        },
        "details": test_results,
        "recommendations": generate_recommendations(test_results)
    }

    # 生成HTML报告
    html_report = generate_html_report(report)

    # 生成JSON报告
    json_report = json.dumps(report, indent=2, ensure_ascii=False)

    return {
        "html": html_report,
        "json": json_report
    }

def generate_recommendations(test_results):
    """生成改进建议"""
    recommendations = []

    # 分析失败模式
    failed_tests = [name for name, result in test_results.items() if not result["success"]]

    if any("performance" in test for test in failed_tests):
        recommendations.append("性能测试失败，建议优化系统资源配置")

    if any("reliability" in test for test in failed_tests):
        recommendations.append("可靠性测试失败，建议加强故障恢复机制")

    if any("accuracy" in test for test in failed_tests):
        recommendations.append("准确性测试失败，建议校准指标收集逻辑")

    return recommendations
```

## 最佳实践

### 测试策略
**分层测试：**
- 单元测试：验证单个组件
- 集成测试：验证组件协作
- 系统测试：验证完整系统
- 验收测试：验证业务需求

**持续测试：**
- 提交前测试
- 合并前测试
- 部署前测试
- 生产环境监控

### 测试数据管理
**测试数据生成：**
- 合成数据生成
- 生产数据采样
- 历史数据回放
- 异常场景模拟

**数据清理：**
- 自动清理机制
- 数据隔离策略
- 隐私保护措施
- 存储成本控制

### 测试环境管理
**环境标准化：**
- 基础设施即代码
- 配置管理
- 版本控制
- 自动化部署

**环境隔离：**
- 命名空间隔离
- 网络隔离
- 数据隔离
- 权限隔离