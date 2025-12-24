# examples/17_tools/api_extension.py
from typing import Dict, Any, List, Optional
import requests
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """API响应数据类"""
    status_code: int
    data: Any
    headers: Dict[str, str]
    success: bool
    error_message: Optional[str] = None

class ToolAPIExtension(ABC):
    """工具API扩展基类"""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})

    def _make_request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """统一的HTTP请求方法"""
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', self.timeout)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            # 尝试解析JSON响应
            try:
                data = response.json()
            except ValueError:
                data = response.text

            return APIResponse(
                status_code=response.status_code,
                data=data,
                headers=dict(response.headers),
                success=True
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return APIResponse(
                status_code=getattr(e.response, 'status_code', 0),
                data=None,
                headers={},
                success=False,
                error_message=str(e)
            )

    def get(self, endpoint: str, params: Optional[Dict] = None) -> APIResponse:
        """GET请求"""
        return self._make_request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Any] = None, json_data: Optional[Dict] = None) -> APIResponse:
        """POST请求"""
        kwargs = {}
        if json_data:
            kwargs['json'] = json_data
        elif data:
            kwargs['data'] = data if isinstance(data, str) else json.dumps(data)
            kwargs['headers'] = {'Content-Type': 'application/json'}

        return self._make_request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, data: Optional[Any] = None, json_data: Optional[Dict] = None) -> APIResponse:
        """PUT请求"""
        kwargs = {}
        if json_data:
            kwargs['json'] = json_data
        elif data:
            kwargs['data'] = data if isinstance(data, str) else json.dumps(data)
            kwargs['headers'] = {'Content-Type': 'application/json'}

        return self._make_request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str) -> APIResponse:
        """DELETE请求"""
        return self._make_request('DELETE', endpoint)

class GreatExpectationsAPI(ToolAPIExtension):
    """Great Expectations API扩展"""

    def __init__(self, base_url: str = "http://localhost:5000", api_key: Optional[str] = None):
        super().__init__(base_url, api_key)

    def list_expectation_suites(self) -> List[str]:
        """列出所有期望套件"""
        response = self.get("/api/v1/expectation_suites")
        if response.success:
            return [suite['name'] for suite in response.data.get('expectation_suites', [])]
        return []

    def run_checkpoint(self, checkpoint_name: str, batch_request: Optional[Dict] = None) -> APIResponse:
        """运行检查点"""
        data = {"checkpoint_name": checkpoint_name}
        if batch_request:
            data["batch_request"] = batch_request

        return self.post("/api/v1/checkpoints/run", json_data=data)

    def get_validation_results(self, suite_name: str, limit: int = 10) -> APIResponse:
        """获取验证结果"""
        return self.get(f"/api/v1/expectation_suites/{suite_name}/validation_results",
                       params={"limit": limit})

class JMeterAPI(ToolAPIExtension):
    """JMeter API扩展"""

    def __init__(self, base_url: str = "http://localhost:9270", api_key: Optional[str] = None):
        super().__init__(base_url, api_key)

    def start_test(self, test_plan_path: str, properties: Optional[Dict] = None) -> APIResponse:
        """启动测试"""
        data = {
            "test_plan_path": test_plan_path,
            "properties": properties or {}
        }
        return self.post("/api/v1/test/start", json_data=data)

    def stop_test(self, test_id: str) -> APIResponse:
        """停止测试"""
        return self.post(f"/api/v1/test/{test_id}/stop")

    def get_test_status(self, test_id: str) -> APIResponse:
        """获取测试状态"""
        return self.get(f"/api/v1/test/{test_id}/status")

    def get_test_results(self, test_id: str) -> APIResponse:
        """获取测试结果"""
        return self.get(f"/api/v1/test/{test_id}/results")

class PrometheusAPI(ToolAPIExtension):
    """Prometheus API扩展"""

    def __init__(self, base_url: str = "http://localhost:9090", api_key: Optional[str] = None):
        super().__init__(base_url, api_key)

    def query(self, query: str, time: Optional[str] = None) -> APIResponse:
        """执行查询"""
        params = {"query": query}
        if time:
            params["time"] = time

        return self.get("/api/v1/query", params=params)

    def query_range(self, query: str, start: str, end: str, step: str = "15s") -> APIResponse:
        """执行范围查询"""
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step
        }
        return self.get("/api/v1/query_range", params=params)

    def get_targets(self) -> APIResponse:
        """获取监控目标"""
        return self.get("/api/v1/targets")

    def get_alerts(self) -> APIResponse:
        """获取告警"""
        return self.get("/api/v1/alerts")

class GrafanaAPI(ToolAPIExtension):
    """Grafana API扩展"""

    def __init__(self, base_url: str = "http://localhost:3000", api_key: Optional[str] = None):
        super().__init__(base_url, api_key)
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})

    def create_dashboard(self, dashboard: Dict) -> APIResponse:
        """创建仪表板"""
        return self.post("/api/dashboards/db", json_data=dashboard)

    def update_dashboard(self, dashboard: Dict, overwrite: bool = True) -> APIResponse:
        """更新仪表板"""
        data = dashboard.copy()
        data["overwrite"] = overwrite
        return self.post("/api/dashboards/db", json_data=data)

    def get_dashboard(self, uid: str) -> APIResponse:
        """获取仪表板"""
        return self.get(f"/api/dashboards/uid/{uid}")

    def delete_dashboard(self, uid: str) -> APIResponse:
        """删除仪表板"""
        return self.delete(f"/api/dashboards/uid/{uid}")

    def create_data_source(self, data_source: Dict) -> APIResponse:
        """创建数据源"""
        return self.post("/api/datasources", json_data=data_source)

    def get_data_sources(self) -> APIResponse:
        """获取数据源列表"""
        return self.get("/api/datasources")

class ToolAPIOrchestrator:
    """工具API编排器"""

    def __init__(self):
        self.tools: Dict[str, ToolAPIExtension] = {}

    def register_tool(self, name: str, tool_api: ToolAPIExtension):
        """注册工具API"""
        self.tools[name] = tool_api
        logger.info(f"Registered tool API: {name}")

    def execute_workflow(self, workflow: List[Dict]) -> List[APIResponse]:
        """执行工作流"""
        results = []

        for step in workflow:
            tool_name = step.get('tool')
            action = step.get('action')
            params = step.get('params', {})

            if tool_name not in self.tools:
                logger.error(f"Tool not registered: {tool_name}")
                continue

            tool_api = self.tools[tool_name]

            try:
                if action == 'get':
                    result = tool_api.get(**params)
                elif action == 'post':
                    result = tool_api.post(**params)
                elif action == 'put':
                    result = tool_api.put(**params)
                elif action == 'delete':
                    result = tool_api.delete(**params)
                else:
                    # 自定义方法调用
                    method = getattr(tool_api, action)
                    result = method(**params)

                results.append(result)
                logger.info(f"Executed {tool_name}.{action}: {'SUCCESS' if result.success else 'FAILED'}")

            except Exception as e:
                logger.error(f"Error executing {tool_name}.{action}: {e}")
                results.append(APIResponse(0, None, {}, False, str(e)))

        return results

# 使用示例
if __name__ == "__main__":
    # 创建编排器
    orchestrator = ToolAPIOrchestrator()

    # 注册工具API
    orchestrator.register_tool("prometheus", PrometheusAPI())
    orchestrator.register_tool("grafana", GrafanaAPI(api_key="your-api-key"))
    orchestrator.register_tool("great_expectations", GreatExpectationsAPI())

    # 定义工作流
    workflow = [
        {
            "tool": "prometheus",
            "action": "query",
            "params": {"query": "up"}
        },
        {
            "tool": "great_expectations",
            "action": "list_expectation_suites"
        }
    ]

    # 执行工作流
    results = orchestrator.execute_workflow(workflow)

    for i, result in enumerate(results):
        print(f"Step {i+1}: {'SUCCESS' if result.success else 'FAILED'}")
        if result.success:
            print(f"  Data: {result.data}")
        else:
            print(f"  Error: {result.error_message}")