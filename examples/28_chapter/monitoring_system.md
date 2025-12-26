# 监控体系建设与指标管理

## 概述

本文档详细介绍大数据测试系统的监控体系建设，包括基础设施监控、应用性能监控、业务指标监控等核心内容。

## 基础设施监控

### 系统资源监控

#### CPU监控
- **使用率监控**: 整体CPU使用率和各核心使用率
- **负载监控**: 系统负载平均值和队列长度
- **上下文切换**: 进程上下文切换频率
- **中断统计**: 硬件和软件中断统计

#### 内存监控
- **物理内存**: 已用内存、可用内存、缓存内存
- **虚拟内存**: Swap使用情况和页面交换统计
- **内存压力**: PSI(Pressure Stall Information)指标
- **OOM事件**: Out of Memory事件检测

#### 磁盘监控
- **I/O性能**: 读写速度、IOPS、延迟时间
- **存储空间**: 磁盘使用率、inode使用情况
- **磁盘健康**: SMART状态、坏块检测
- **文件系统**: 挂载点状态、文件系统类型

#### 网络监控
- **带宽使用**: 进出流量、带宽利用率
- **连接状态**: TCP连接数、UDP数据包统计
- **网络延迟**: RTT(Round Trip Time)测量
- **错误统计**: 丢包率、重传率、错误包统计

### 容器监控

#### Docker容器监控
```yaml
# docker-compose监控配置
version: '3.8'
services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    devices:
      - /dev/kmsg
    privileged: true

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
```

#### Kubernetes监控
```yaml
# Kubernetes监控配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    rule_files:
      - /etc/prometheus/prometheus.rules

    alerting:
      alertmanagers:
        - static_configs:
            - targets:
              - alertmanager:9093

    scrape_configs:
      - job_name: 'kubernetes-apiservers'
        kubernetes_sd_configs:
          - role: endpoints
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
          - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
            action: keep
            regex: default;kubernetes;https

      - job_name: 'kubernetes-nodes'
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        kubernetes_sd_configs:
          - role: node
        relabel_configs:
          - action: labelmap
            regex: __meta_kubernetes_node_label_(.+)
          - target_label: __address__
            replacement: kubernetes.default.svc:443
          - source_labels: [__meta_kubernetes_node_name]
            regex: (.+)
            target_label: __metrics_path__
            replacement: /api/v1/nodes/${1}/proxy/metrics
```

## 应用性能监控

### Web应用监控

#### HTTP接口监控
```python
from prometheus_client import Counter, Histogram, Gauge
import time
import functools

# HTTP请求计数器
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

# HTTP请求延迟直方图
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# 活跃请求数量
http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['endpoint']
)

def monitor_http_request(method, endpoint):
    """HTTP请求监控装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            # 增加活跃请求计数
            http_requests_in_progress.labels(endpoint=endpoint).inc()

            try:
                result = func(*args, **kwargs)

                # 记录请求计数和延迟
                status_code = getattr(result, 'status_code', 200)
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()

                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(time.time() - start_time)

                return result

            finally:
                # 减少活跃请求计数
                http_requests_in_progress.labels(endpoint=endpoint).dec()

        return wrapper
    return decorator

# 使用示例
@app.route('/api/test')
@monitor_http_request('GET', '/api/test')
def test_endpoint():
    # 业务逻辑
    return jsonify({'status': 'success'})
```

#### 数据库连接监控
```python
import psycopg2
from prometheus_client import Gauge, Counter
import time

# 数据库连接池指标
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections',
    ['database']
)

db_connections_idle = Gauge(
    'db_connections_idle',
    'Number of idle database connections',
    ['database']
)

db_connections_total = Gauge(
    'db_connections_total',
    'Total number of database connections',
    ['database']
)

# 数据库查询指标
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type', 'table']
)

db_query_errors_total = Counter(
    'db_query_errors_total',
    'Total number of database query errors',
    ['query_type', 'error_type']
)

class DatabaseConnectionPool:
    """数据库连接池监控"""

    def __init__(self, dsn, max_connections=10):
        self.dsn = dsn
        self.max_connections = max_connections
        self.connections = []
        self.database = dsn.split('/')[-1] if '/' in dsn else 'unknown'

    def get_connection(self):
        """获取数据库连接"""
        start_time = time.time()

        try:
            if len(self.connections) < self.max_connections:
                conn = psycopg2.connect(self.dsn)
                self.connections.append(conn)

            # 返回现有连接
            conn = self.connections.pop(0)

            # 更新连接池指标
            db_connections_active.labels(database=self.database).inc()
            db_connections_total.labels(database=self.database).set(len(self.connections))

            return conn

        except Exception as e:
            db_query_errors_total.labels(
                query_type='connection',
                error_type=type(e).__name__
            ).inc()
            raise

    def release_connection(self, conn):
        """释放数据库连接"""
        self.connections.append(conn)

        # 更新连接池指标
        db_connections_active.labels(database=self.database).dec()
        db_connections_idle.labels(database=self.database).set(len(self.connections))

    def execute_query(self, query, params=None):
        """执行数据库查询"""
        conn = self.get_connection()

        try:
            start_time = time.time()

            with conn.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()

            # 记录查询性能
            query_type = query.strip().split()[0].upper()
            db_query_duration_seconds.labels(
                query_type=query_type,
                table='unknown'  # 可以从查询中解析表名
            ).observe(time.time() - start_time)

            return results

        except Exception as e:
            db_query_errors_total.labels(
                query_type='unknown',
                error_type=type(e).__name__
            ).inc()
            raise

        finally:
            self.release_connection(conn)
```

### 微服务监控

#### 服务健康检查
```python
from flask import Flask, jsonify
from prometheus_client import Gauge, generate_latest
import requests
import time

app = Flask(__name__)

# 服务健康状态指标
service_health_status = Gauge(
    'service_health_status',
    'Service health status (1=healthy, 0=unhealthy)',
    ['service_name', 'check_type']
)

# 服务响应时间
service_response_time = Gauge(
    'service_response_time_seconds',
    'Service response time in seconds',
    ['service_name', 'endpoint']
)

# 依赖服务状态
dependency_health_status = Gauge(
    'dependency_health_status',
    'Dependency service health status',
    ['dependency_name', 'dependency_type']
)

class ServiceHealthChecker:
    """服务健康检查器"""

    def __init__(self, service_name):
        self.service_name = service_name
        self.dependencies = {
            'database': 'postgresql://localhost:5432/mydb',
            'redis': 'redis://localhost:6379',
            'external_api': 'https://api.external.com/health'
        }

    def check_own_health(self):
        """检查自身健康状态"""
        try:
            # 检查应用端口
            response = requests.get('http://localhost:5000/health', timeout=5)
            is_healthy = response.status_code == 200

            service_health_status.labels(
                service_name=self.service_name,
                check_type='application'
            ).set(1 if is_healthy else 0)

            return is_healthy

        except Exception as e:
            service_health_status.labels(
                service_name=self.service_name,
                check_type='application'
            ).set(0)
            return False

    def check_dependencies(self):
        """检查依赖服务健康状态"""
        results = {}

        # 检查数据库连接
        try:
            import psycopg2
            conn = psycopg2.connect(self.dependencies['database'])
            conn.close()
            dependency_health_status.labels(
                dependency_name='database',
                dependency_type='postgresql'
            ).set(1)
            results['database'] = True
        except:
            dependency_health_status.labels(
                dependency_name='database',
                dependency_type='postgresql'
            ).set(0)
            results['database'] = False

        # 检查Redis连接
        try:
            import redis
            r = redis.Redis.from_url(self.dependencies['redis'])
            r.ping()
            dependency_health_status.labels(
                dependency_name='redis',
                dependency_type='redis'
            ).set(1)
            results['redis'] = True
        except:
            dependency_health_status.labels(
                dependency_name='redis',
                dependency_type='redis'
            ).set(0)
            results['redis'] = False

        # 检查外部API
        try:
            response = requests.get(self.dependencies['external_api'], timeout=10)
            is_healthy = response.status_code == 200
            dependency_health_status.labels(
                dependency_name='external_api',
                dependency_type='api'
            ).set(1 if is_healthy else 0)
            results['external_api'] = is_healthy
        except:
            dependency_health_status.labels(
                dependency_name='external_api',
                dependency_type='api'
            ).set(0)
            results['external_api'] = False

        return results

    def measure_response_time(self, endpoint='/api/v1/test'):
        """测量响应时间"""
        try:
            start_time = time.time()
            response = requests.get(f'http://localhost:5000{endpoint}', timeout=10)
            response_time = time.time() - start_time

            service_response_time.labels(
                service_name=self.service_name,
                endpoint=endpoint
            ).set(response_time)

            return response_time

        except Exception as e:
            service_response_time.labels(
                service_name=self.service_name,
                endpoint=endpoint
            ).set(-1)  # -1表示请求失败
            return None

# Flask路由
@app.route('/health')
def health_check():
    checker = ServiceHealthChecker('bigdata-testing-service')

    own_health = checker.check_own_health()
    dependencies = checker.check_dependencies()
    response_time = checker.measure_response_time()

    health_status = {
        'service': 'healthy' if own_health else 'unhealthy',
        'dependencies': dependencies,
        'response_time': response_time,
        'timestamp': time.time()
    }

    status_code = 200 if own_health and all(dependencies.values()) else 503
    return jsonify(health_status), status_code

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 业务指标监控

### 用户行为监控

#### 用户会话跟踪
```python
from prometheus_client import Counter, Gauge, Histogram
import time
import uuid

# 用户会话指标
user_sessions_active = Gauge(
    'user_sessions_active',
    'Number of active user sessions'
)

user_sessions_total = Counter(
    'user_sessions_total',
    'Total number of user sessions created'
)

# 用户行为指标
user_actions_total = Counter(
    'user_actions_total',
    'Total number of user actions',
    ['action_type', 'user_type', 'page']
)

user_page_views_total = Counter(
    'user_page_views_total',
    'Total number of page views',
    ['page', 'user_type', 'device_type']
)

# 用户性能指标
page_load_time_seconds = Histogram(
    'page_load_time_seconds',
    'Page load time in seconds',
    ['page', 'device_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

class UserBehaviorTracker:
    """用户行为跟踪器"""

    def __init__(self):
        self.active_sessions = set()

    def start_session(self, user_id=None, user_type='anonymous', device_type='desktop'):
        """开始用户会话"""
        session_id = str(uuid.uuid4())

        self.active_sessions.add(session_id)
        user_sessions_active.set(len(self.active_sessions))
        user_sessions_total.inc()

        return {
            'session_id': session_id,
            'user_id': user_id,
            'user_type': user_type,
            'device_type': device_type,
            'start_time': time.time()
        }

    def end_session(self, session_id):
        """结束用户会话"""
        if session_id in self.active_sessions:
            self.active_sessions.remove(session_id)
            user_sessions_active.set(len(self.active_sessions))

    def track_action(self, session_id, action_type, page, user_type='anonymous'):
        """跟踪用户行为"""
        user_actions_total.labels(
            action_type=action_type,
            user_type=user_type,
            page=page
        ).inc()

    def track_page_view(self, page, user_type='anonymous', device_type='desktop', load_time=None):
        """跟踪页面访问"""
        user_page_views_total.labels(
            page=page,
            user_type=user_type,
            device_type=device_type
        ).inc()

        if load_time is not None:
            page_load_time_seconds.labels(
                page=page,
                device_type=device_type
            ).observe(load_time)

# JavaScript前端跟踪代码
FRONTEND_TRACKING_CODE = """
// 用户行为跟踪JavaScript代码
class UserTracker {
    constructor() {
        this.sessionId = null;
        this.userType = 'anonymous';
        this.deviceType = this.detectDeviceType();
        this.initSession();
        this.bindEvents();
    }

    detectDeviceType() {
        const ua = navigator.userAgent;
        if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
            return 'tablet';
        }
        if (/Mobile|iP(hone|od|ad)|Android|BlackBerry|IEMobile|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
            return 'mobile';
        }
        return 'desktop';
    }

    async initSession() {
        try {
            const response = await fetch('/api/session/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    userType: this.userType,
                    deviceType: this.deviceType
                })
            });

            const data = await response.json();
            this.sessionId = data.session_id;

            // 页面加载时间跟踪
            const loadTime = performance.now();
            this.trackPageView(window.location.pathname, loadTime);

        } catch (error) {
            console.error('Failed to initialize session:', error);
        }
    }

    bindEvents() {
        // 跟踪用户点击行为
        document.addEventListener('click', (event) => {
            const target = event.target;
            const actionType = target.tagName.toLowerCase();

            if (target.hasAttribute('data-track')) {
                this.trackAction(target.getAttribute('data-track'), window.location.pathname);
            } else if (['button', 'a', 'input'].includes(actionType)) {
                this.trackAction(`${actionType}_click`, window.location.pathname);
            }
        });

        // 跟踪页面离开
        window.addEventListener('beforeunload', () => {
            this.endSession();
        });
    }

    async trackAction(actionType, page) {
        if (!this.sessionId) return;

        try {
            await fetch('/api/track/action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sessionId: this.sessionId,
                    actionType: actionType,
                    page: page,
                    userType: this.userType
                })
            });
        } catch (error) {
            console.error('Failed to track action:', error);
        }
    }

    async trackPageView(page, loadTime) {
        if (!this.sessionId) return;

        try {
            await fetch('/api/track/pageview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sessionId: this.sessionId,
                    page: page,
                    userType: this.userType,
                    deviceType: this.deviceType,
                    loadTime: loadTime / 1000  // 转换为秒
                })
            });
        } catch (error) {
            console.error('Failed to track page view:', error);
        }
    }

    async endSession() {
        if (!this.sessionId) return;

        try {
            await fetch('/api/session/end', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sessionId: this.sessionId
                })
            });
        } catch (error) {
            console.error('Failed to end session:', error);
        }
    }
}

// 初始化跟踪器
document.addEventListener('DOMContentLoaded', () => {
    window.userTracker = new UserTracker();
});
"""
```

#### 业务流程监控
```python
from prometheus_client import Counter, Gauge, Histogram
from enum import Enum
import time

class BusinessProcessStatus(Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# 业务流程指标
business_process_total = Counter(
    'business_process_total',
    'Total number of business processes',
    ['process_type', 'status']
)

business_process_active = Gauge(
    'business_process_active',
    'Number of active business processes',
    ['process_type']
)

business_process_duration_seconds = Histogram(
    'business_process_duration_seconds',
    'Business process duration in seconds',
    ['process_type', 'outcome'],
    buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600]
)

# 业务步骤指标
business_step_total = Counter(
    'business_step_total',
    'Total number of business steps executed',
    ['process_type', 'step_name', 'status']
)

business_step_duration_seconds = Histogram(
    'business_step_duration_seconds',
    'Business step duration in seconds',
    ['process_type', 'step_name'],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60]
)

class BusinessProcessMonitor:
    """业务流程监控器"""

    def __init__(self):
        self.active_processes = {}

    def start_process(self, process_id, process_type, metadata=None):
        """开始业务流程"""
        start_time = time.time()

        process_info = {
            'process_id': process_id,
            'process_type': process_type,
            'start_time': start_time,
            'status': BusinessProcessStatus.STARTED,
            'steps': [],
            'metadata': metadata or {}
        }

        self.active_processes[process_id] = process_info
        business_process_active.labels(process_type=process_type).inc()

        business_process_total.labels(
            process_type=process_type,
            status=BusinessProcessStatus.STARTED.value
        ).inc()

        return process_info

    def record_step(self, process_id, step_name, status='completed', duration=None):
        """记录业务步骤"""
        if process_id not in self.active_processes:
            return False

        process_info = self.active_processes[process_id]

        step_info = {
            'step_name': step_name,
            'status': status,
            'timestamp': time.time(),
            'duration': duration
        }

        process_info['steps'].append(step_info)

        business_step_total.labels(
            process_type=process_info['process_type'],
            step_name=step_name,
            status=status
        ).inc()

        if duration is not None:
            business_step_duration_seconds.labels(
                process_type=process_info['process_type'],
                step_name=step_name
            ).observe(duration)

        return True

    def end_process(self, process_id, outcome='completed'):
        """结束业务流程"""
        if process_id not in self.active_processes:
            return False

        process_info = self.active_processes[process_id]
        end_time = time.time()
        duration = end_time - process_info['start_time']

        process_info['status'] = BusinessProcessStatus(outcome)
        process_info['end_time'] = end_time
        process_info['duration'] = duration

        business_process_total.labels(
            process_type=process_info['process_type'],
            status=outcome
        ).inc()

        business_process_duration_seconds.labels(
            process_type=process_info['process_type'],
            outcome=outcome
        ).observe(duration)

        business_process_active.labels(
            process_type=process_info['process_type']
        ).dec()

        # 清理已完成流程
        del self.active_processes[process_id]

        return process_info

    def get_process_status(self, process_id):
        """获取流程状态"""
        return self.active_processes.get(process_id)

    def get_active_processes(self, process_type=None):
        """获取活跃流程"""
        if process_type:
            return {pid: info for pid, info in self.active_processes.items()
                   if info['process_type'] == process_type}
        return self.active_processes

# 使用示例
monitor = BusinessProcessMonitor()

# 开始用户注册流程
process = monitor.start_process('user_reg_001', 'user_registration')

# 记录各个步骤
monitor.record_step('user_reg_001', 'email_validation', 'completed', 0.5)
monitor.record_step('user_reg_001', 'password_check', 'completed', 0.2)
monitor.record_step('user_reg_001', 'user_creation', 'completed', 1.8)
monitor.record_step('user_reg_001', 'welcome_email', 'completed', 0.3)

# 结束流程
final_status = monitor.end_process('user_reg_001', 'completed')
print(f"Process completed in {final_status['duration']:.2f} seconds")
```

## 监控数据可视化

### Grafana仪表板配置

#### 系统资源仪表板
```json
{
  "dashboard": {
    "title": "系统资源监控",
    "tags": ["infrastructure", "system"],
    "timezone": "browser",
    "panels": [
      {
        "title": "CPU使用率",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "内存使用率",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "磁盘使用率",
        "type": "table",
        "targets": [
          {
            "expr": "(node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100",
            "legendFormat": "{{instance}} - {{mountpoint}}"
          }
        ]
      }
    ]
  }
}
```

#### 应用性能仪表板
```json
{
  "dashboard": {
    "title": "应用性能监控",
    "tags": ["application", "performance"],
    "timezone": "browser",
    "panels": [
      {
        "title": "HTTP请求率",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "HTTP响应时间",
        "type": "heatmap",
        "targets": [
          {
            "expr": "http_request_duration_seconds",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "错误率",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status_code=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "5xx错误率"
          }
        ]
      }
    ]
  }
}
```

#### 业务指标仪表板
```json
{
  "dashboard": {
    "title": "业务指标监控",
    "tags": ["business", "metrics"],
    "timezone": "browser",
    "panels": [
      {
        "title": "活跃用户会话",
        "type": "stat",
        "targets": [
          {
            "expr": "user_sessions_active",
            "legendFormat": "活跃会话数"
          }
        ]
      },
      {
        "title": "用户行为趋势",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(user_actions_total[5m])",
            "legendFormat": "{{action_type}}"
          }
        ]
      },
      {
        "title": "业务流程成功率",
        "type": "gauge",
        "targets": [
          {
            "expr": "rate(business_process_total{status=\"completed\"}[1h]) / rate(business_process_total[1h]) * 100",
            "legendFormat": "成功率"
          }
        ]
      }
    ]
  }
}
```

## 告警配置

### Prometheus告警规则

#### 系统资源告警
```yaml
groups:
  - name: system_alerts
    rules:
      - alert: HighCpuUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value }}% on {{ $labels.instance }}"

      - alert: HighMemoryUsage
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is {{ $value }}% on {{ $labels.instance }}"

      - alert: LowDiskSpace
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk usage is {{ $value }}% on {{ $labels.instance }} mountpoint {{ $labels.mountpoint }}"
```

#### 应用性能告警
```yaml
groups:
  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"[4-5].."}[5m]) / rate(http_requests_total[5m]) * 100 > 5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.endpoint }}"
          description: "Error rate is {{ $value }}% on {{ $labels.endpoint }}"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time on {{ $labels.endpoint }}"
          description: "95th percentile response time is {{ $value }}s on {{ $labels.endpoint }}"

      - alert: HighActiveConnections
        expr: http_requests_in_progress > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High number of active connections"
          description: "Active connections is {{ $value }} on {{ $labels.endpoint }}"
```

#### 业务指标告警
```yaml
groups:
  - name: business_alerts
    rules:
      - alert: LowConversionRate
        expr: business_conversion_rate < 0.02
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Low conversion rate"
          description: "Conversion rate dropped to {{ $value }}"

      - alert: HighUserSatisfactionDrop
        expr: business_user_satisfaction_score < 3.5
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "User satisfaction dropped"
          description: "User satisfaction score is {{ $value }}/5"

      - alert: BusinessProcessFailure
        expr: rate(business_process_total{status="failed"}[5m]) / rate(business_process_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High business process failure rate"
          description: "Process failure rate is {{ $value }}%"
```

## 监控最佳实践

### 指标设计原则
- **命名规范**: 使用snake_case，包含度量名、标签和单位
- **标签使用**: 避免高基数标签，控制标签数量
- **聚合策略**: 合理设置直方图桶和汇总间隔
- **数据保留**: 根据业务需求设置数据保留策略

### 监控覆盖范围
- **基础设施**: CPU、内存、磁盘、网络、容器
- **应用性能**: 响应时间、吞吐量、错误率、连接数
- **业务指标**: 用户行为、转化率、满意度、流程效率
- **依赖服务**: 数据库、缓存、外部API、消息队列

### 告警管理策略
- **告警分级**: 合理设置告警级别和升级机制
- **抑制规则**: 避免告警风暴和重复告警
- **自动响应**: 实施自动修复和扩缩容机制
- **告警验证**: 定期review告警规则的有效性

### 可观测性成熟度评估
- **Level 1**: 基础监控，反应式问题处理
- **Level 2**: 综合监控，主动问题发现
- **Level 3**: 智能监控，预测性维护
- **Level 4**: 业务洞察，持续优化改进