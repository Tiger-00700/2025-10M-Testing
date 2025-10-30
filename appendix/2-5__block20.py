import time
from locust import HttpUser, task, between, events
import json
import numpy as np

# 全局统计数据
latencies = []

# 注册事件处理器
@events.request_success.add_listener
def capture_success(request_type, name, response_time, response_length, **kwargs):
    latencies.append(response_time)

@events.test_stop.add_listener
def on_test_stop(**kwargs):
    if latencies:
        print("\n性能测试统计数据:")
        print(f"请求总数: {len(latencies)}")
        print(f"平均响应时间: {np.mean(latencies):.2f}ms")
        print(f"中位数响应时间: {np.median(latencies):.2f}ms")
        print(f"95% 响应时间: {np.percentile(latencies, 95):.2f}ms")
        print(f"99% 响应时间: {np.percentile(latencies, 99):.2f}ms")
        print(f"最小响应时间: {np.min(latencies):.2f}ms")
        print(f"最大响应时间: {np.max(latencies):.2f}ms")

class DataProcessingUser(HttpUser):
    # 用户思考时间在1到3秒之间
    wait_time = between(1, 3)
    
    def on_start(self):
        """用户初始化时执行"""
        # 可以在这里进行登录或其他初始化操作
        self.client.verify = False  # 在测试环境中禁用SSL验证
        
    @task(3)
    def test_data_transformation(self):
        """测试数据转换API的性能"""
        # 准备测试数据
        payload = {
            "data": [
                {"id": i, "value": np.random.randint(1, 100)} 
                for i in range(100)
            ],
            "operation": "normalize",
            "params": {
                "method": "minmax",
                "range": [0, 1]
            }
        }
        
        # 发送POST请求并验证响应
        with self.client.post(
            "/api/transform",
            json=payload,
            catch_response=True,
            name="数据转换接口"
        ) as response:
            if response.status_code != 200:
                response.failure(f"请求失败: {response.status_code}")
            else:
                try:
                    json_response = response.json()
                    # 验证响应结构
                    if "transformed_data" not in json_response:
                        response.failure("响应中缺少transformed_data字段")
                    elif len(json_response["transformed_data"]) != 100:
                        response.failure(f"数据转换结果数量错误: {len(json_response['transformed_data'])}")
                except json.JSONDecodeError:
                    response.failure("无法解析JSON响应")
    
    @task(2)
    def test_batch_processing(self):
        """测试批处理API的性能"""
        # 准备较小的批处理请求
        payload = {
            "batch_id": f"test-batch-{int(time.time())}",
            "dataset": "sample_data",
            "operations": ["filter", "aggregate", "export"],
            "priority": "medium"
        }
        
        # 发送请求
        with self.client.post(
            "/api/batch/process",
            json=payload,
            catch_response=True,
            name="批处理接口"
        ) as response:
            if response.status_code != 202:
                response.failure(f"请求失败: {response.status_code}")
    
    @task(1)
    def test_complex_query(self):
        """测试复杂查询API的性能"""
        # 构建复杂查询参数
        query_params = {
            "filters": {
                "date_range": {"start": "2023-01-01", "end": "2023-12-31"},
                "category": ["A", "B", "C"],
                "value_min": 100
            },
            "group_by": ["category", "month"],
            "aggregations": ["sum", "avg", "count"],
            "limit": 1000,
            "sort_by": {"field": "sum_value", "order": "desc"}
        }
        
        # 发送GET请求
        with self.client.get(
            "/api/query",
            params={"query": json.dumps(query_params)},
            catch_response=True,
            name="复杂查询接口"
        ) as response:
            if response.status_code != 200:
                response.failure(f"请求失败: {response.status_code}")
            else:
                try:
                    json_response = response.json()
                    if "results" not in json_response:
                        response.failure("响应中缺少results字段")
                except json.JSONDecodeError:
                    response.failure("无法解析JSON响应")

# 命令行运行示例:
# locust -f data_processing_load_test.py --host=http://localhost:8000 --users=100 --spawn-rate=10
# 这将模拟100个用户，以每秒10个的速率增加，访问指定的主机
