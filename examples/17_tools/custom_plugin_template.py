# examples/17_tools/custom_plugin_template.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    config_schema: Dict[str, Any]

@dataclass
class PluginContext:
    config: Dict[str, Any]
    runtime_env: Dict[str, Any]
    shared_state: Dict[str, Any]

class PluginInterface(ABC):
    """Abstract base class for all plugins"""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass

    @abstractmethod
    def initialize(self, context: PluginContext) -> bool:
        """Initialize the plugin with context"""
        pass

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Execute the plugin's main logic"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources"""
        pass

class DataQualityPlugin(PluginInterface):
    """Custom data quality validation plugin"""

    def __init__(self):
        self._metadata = PluginMetadata(
            name="custom_data_quality",
            version="1.0.0",
            description="Custom data quality validation rules",
            author="Enterprise Team",
            dependencies=["pandas", "numpy"],
            config_schema={
                "rules": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["range", "pattern", "uniqueness"]},
                            "column": {"type": "string"},
                            "params": {"type": "object"}
                        }
                    }
                }
            }
        )
        self.rules = []

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    def initialize(self, context: PluginContext) -> bool:
        try:
            self.rules = context.config.get("rules", [])
            logger.info(f"Initialized {len(self.rules)} data quality rules")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize plugin: {e}")
            return False

    def execute(self, input_data: Any) -> Any:
        """Execute data quality validation"""
        if not isinstance(input_data, dict) or "dataframe" not in input_data:
            raise ValueError("Input must contain 'dataframe' key")

        df = input_data["dataframe"]
        results = {
            "passed": True,
            "violations": [],
            "summary": {}
        }

        for rule in self.rules:
            rule_name = rule["name"]
            rule_type = rule["type"]
            column = rule["column"]
            params = rule.get("params", {})

            if column not in df.columns:
                results["violations"].append({
                    "rule": rule_name,
                    "error": f"Column '{column}' not found in dataframe"
                })
                results["passed"] = False
                continue

            violation_count = self._validate_rule(df[column], rule_type, params)

            if violation_count > 0:
                results["violations"].append({
                    "rule": rule_name,
                    "column": column,
                    "violations": violation_count
                })
                results["passed"] = False

        results["summary"] = {
            "total_rows": len(df),
            "total_rules": len(self.rules),
            "failed_rules": len(results["violations"])
        }

        return results

    def _validate_rule(self, series, rule_type: str, params: Dict[str, Any]) -> int:
        """Validate a single rule"""
        if rule_type == "range":
            min_val = params.get("min")
            max_val = params.get("max")
            if min_val is not None and max_val is not None:
                return ((series < min_val) | (series > max_val)).sum()

        elif rule_type == "pattern":
            pattern = params.get("pattern")
            if pattern:
                import re
                return (~series.astype(str).str.match(pattern)).sum()

        elif rule_type == "uniqueness":
            return series.duplicated().sum()

        return 0

    def cleanup(self) -> None:
        """Cleanup resources"""
        self.rules = []
        logger.info("Plugin cleaned up")

class PerformanceTestPlugin(PluginInterface):
    """Custom performance testing plugin"""

    def __init__(self):
        self._metadata = PluginMetadata(
            name="custom_performance_test",
            version="1.0.0",
            description="Custom performance testing scenarios",
            author="Performance Team",
            dependencies=["locust", "requests"],
            config_schema={
                "scenarios": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "endpoint": {"type": "string"},
                            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                            "payload": {"type": "object"},
                            "users": {"type": "integer", "minimum": 1},
                            "spawn_rate": {"type": "number", "minimum": 0.1},
                            "duration": {"type": "integer", "minimum": 1}
                        }
                    }
                }
            }
        )
        self.scenarios = []

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    def initialize(self, context: PluginContext) -> bool:
        try:
            self.scenarios = context.config.get("scenarios", [])
            logger.info(f"Initialized {len(self.scenarios)} performance scenarios")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize plugin: {e}")
            return False

    def execute(self, input_data: Any) -> Any:
        """Execute performance testing scenarios"""
        results = {
            "scenarios": [],
            "summary": {
                "total_scenarios": len(self.scenarios),
                "passed_scenarios": 0,
                "failed_scenarios": 0
            }
        }

        for scenario in self.scenarios:
            scenario_result = self._run_scenario(scenario)
            results["scenarios"].append(scenario_result)

            if scenario_result["passed"]:
                results["summary"]["passed_scenarios"] += 1
            else:
                results["summary"]["failed_scenarios"] += 1

        return results

    def _run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single performance testing scenario"""
        try:
            # Simplified performance test execution
            # In real implementation, this would use Locust or similar
            import time
            import random

            endpoint = scenario["endpoint"]
            method = scenario.get("method", "GET")
            users = scenario.get("users", 10)
            duration = scenario.get("duration", 60)

            start_time = time.time()
            response_times = []

            # Simulate concurrent users
            for i in range(users * 10):  # Simulate requests
                response_time = random.uniform(0.1, 2.0)
                response_times.append(response_time)
                time.sleep(0.01)  # Simulate request delay

            end_time = time.time()

            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)

            # Simple performance criteria
            passed = avg_response_time < 2.0 and max_response_time < 5.0

            return {
                "scenario": scenario["name"],
                "passed": passed,
                "metrics": {
                    "avg_response_time": avg_response_time,
                    "max_response_time": max_response_time,
                    "min_response_time": min_response_time,
                    "total_requests": users,
                    "duration": end_time - start_time
                },
                "error": None
            }

        except Exception as e:
            return {
                "scenario": scenario["name"],
                "passed": False,
                "metrics": {},
                "error": str(e)
            }

    def cleanup(self) -> None:
        """Cleanup resources"""
        self.scenarios = []
        logger.info("Plugin cleaned up")

class PluginManager:
    """Manager for loading and executing plugins"""

    def __init__(self):
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_contexts: Dict[str, PluginContext] = {}

    def register_plugin(self, plugin_class: type, config: Dict[str, Any]) -> bool:
        """Register a plugin class"""
        try:
            plugin_instance = plugin_class()
            plugin_name = plugin_instance.metadata.name

            context = PluginContext(
                config=config,
                runtime_env={},
                shared_state={}
            )

            if plugin_instance.initialize(context):
                self.plugins[plugin_name] = plugin_instance
                self.plugin_contexts[plugin_name] = context
                logger.info(f"Registered plugin: {plugin_name}")
                return True
            else:
                logger.error(f"Failed to initialize plugin: {plugin_name}")
                return False

        except Exception as e:
            logger.error(f"Failed to register plugin: {e}")
            return False

    def execute_plugin(self, plugin_name: str, input_data: Any) -> Any:
        """Execute a registered plugin"""
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin '{plugin_name}' not registered")

        plugin = self.plugins[plugin_name]
        return plugin.execute(input_data)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins"""
        return [
            {
                "name": name,
                "version": plugin.metadata.version,
                "description": plugin.metadata.description,
                "author": plugin.metadata.author
            }
            for name, plugin in self.plugins.items()
        ]

    def cleanup_all(self):
        """Cleanup all plugins"""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up plugin {plugin.metadata.name}: {e}")

        self.plugins.clear()
        self.plugin_contexts.clear()

# Usage example
if __name__ == "__main__":
    # Initialize plugin manager
    manager = PluginManager()

    # Register data quality plugin
    dq_config = {
        "rules": [
            {
                "name": "age_range_check",
                "type": "range",
                "column": "age",
                "params": {"min": 0, "max": 120}
            },
            {
                "name": "email_pattern_check",
                "type": "pattern",
                "column": "email",
                "params": {"pattern": r"^[^@]+@[^@]+\.[^@]+$"}
            }
        ]
    }

    manager.register_plugin(DataQualityPlugin, dq_config)

    # Register performance test plugin
    perf_config = {
        "scenarios": [
            {
                "name": "api_load_test",
                "endpoint": "http://api.example.com/data",
                "method": "GET",
                "users": 50,
                "spawn_rate": 5,
                "duration": 120
            }
        ]
    }

    manager.register_plugin(PerformanceTestPlugin, perf_config)

    # List available plugins
    print("Available plugins:")
    for plugin_info in manager.list_plugins():
        print(f"- {plugin_info['name']}: {plugin_info['description']}")

    # Example execution (would need actual data)
    # dq_result = manager.execute_plugin("custom_data_quality", {"dataframe": df})
    # perf_result = manager.execute_plugin("custom_performance_test", {})

    # Cleanup
    manager.cleanup_all()