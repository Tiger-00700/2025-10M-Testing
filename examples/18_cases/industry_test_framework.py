# examples/18_cases/industry_test_framework.py
"""
行业大数据测试框架
提供统一的测试框架，支持各行业的测试场景和验证需求
"""

import json
import yaml
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict, field
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from pathlib import Path
import sqlite3
import hashlib
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestConfiguration:
    """测试配置"""
    config_id: str
    industry: str
    test_type: str
    parameters: Dict[str, Any]
    thresholds: Dict[str, float]
    data_sources: List[str]
    validation_rules: Dict[str, Any]
    created_date: str
    updated_date: str

@dataclass
class TestResult:
    """测试结果"""
    test_id: str
    config_id: str
    status: str  # 'passed', 'failed', 'warning', 'error'
    score: float
    metrics: Dict[str, float]
    details: Dict[str, Any]
    execution_time: float
    start_time: str
    end_time: str
    error_message: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)

@dataclass
class TestSuite:
    """测试套件"""
    suite_id: str
    name: str
    description: str
    industry: str
    test_configs: List[str]  # 配置ID列表
    execution_order: List[str]
    parallel_execution: bool
    timeout_minutes: int
    created_date: str
    updated_date: str

class IndustryTestFramework(ABC):
    """行业测试框架基类"""

    def __init__(self, industry: str, config_path: Optional[str] = None):
        self.industry = industry
        self.config_path = config_path or f"{industry}_test_config.yml"
        self.configurations: Dict[str, TestConfiguration] = {}
        self.test_results: List[TestResult] = []
        self.db_path = f"{industry}_test_results.db"
        self._init_database()
        self._load_configurations()

    def _init_database(self):
        """初始化结果数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    test_id TEXT PRIMARY KEY,
                    config_id TEXT,
                    status TEXT,
                    score REAL,
                    metrics TEXT,
                    details TEXT,
                    execution_time REAL,
                    start_time TEXT,
                    end_time TEXT,
                    error_message TEXT,
                    recommendations TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_suites (
                    suite_id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    industry TEXT,
                    test_configs TEXT,
                    execution_order TEXT,
                    parallel_execution INTEGER,
                    timeout_minutes INTEGER,
                    created_date TEXT,
                    updated_date TEXT
                )
            ''')

    def _load_configurations(self):
        """加载测试配置"""
        if Path(self.config_path).exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            for config_id, config in config_data.get('configurations', {}).items():
                test_config = TestConfiguration(
                    config_id=config_id,
                    industry=self.industry,
                    test_type=config['test_type'],
                    parameters=config['parameters'],
                    thresholds=config['thresholds'],
                    data_sources=config['data_sources'],
                    validation_rules=config['validation_rules'],
                    created_date=config.get('created_date', datetime.now().isoformat()),
                    updated_date=config.get('updated_date', datetime.now().isoformat())
                )
                self.configurations[config_id] = test_config

    def save_configuration(self, config: TestConfiguration):
        """保存测试配置"""
        self.configurations[config.config_id] = config

        # 保存到文件
        config_data = {
            'configurations': {
                cid: {
                    'test_type': c.test_type,
                    'parameters': c.parameters,
                    'thresholds': c.thresholds,
                    'data_sources': c.data_sources,
                    'validation_rules': c.validation_rules,
                    'created_date': c.created_date,
                    'updated_date': c.updated_date
                }
                for cid, c in self.configurations.items()
            }
        }

        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)

    def execute_test(self, config_id: str, data: pd.DataFrame,
                    context: Dict[str, Any] = None) -> TestResult:
        """执行单个测试"""
        if config_id not in self.configurations:
            raise ValueError(f"Configuration {config_id} not found")

        config = self.configurations[config_id]
        start_time = datetime.now()

        try:
            # 执行测试逻辑
            result = self._execute_test_logic(config, data, context or {})

            # 评估结果
            evaluation = self._evaluate_test_result(config, result)

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            test_result = TestResult(
                test_id=f"{config_id}_{int(start_time.timestamp())}",
                config_id=config_id,
                status=evaluation['status'],
                score=evaluation['score'],
                metrics=result.get('metrics', {}),
                details=result,
                execution_time=execution_time,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                error_message=None,
                recommendations=evaluation.get('recommendations', [])
            )

        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            test_result = TestResult(
                test_id=f"{config_id}_{int(start_time.timestamp())}",
                config_id=config_id,
                status='error',
                score=0.0,
                metrics={},
                details={},
                execution_time=execution_time,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                error_message=str(e),
                recommendations=[]
            )

            logger.error(f"Test execution failed for {config_id}: {str(e)}")

        # 保存结果
        self._save_test_result(test_result)
        self.test_results.append(test_result)

        return test_result

    @abstractmethod
    def _execute_test_logic(self, config: TestConfiguration, data: pd.DataFrame,
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """执行测试逻辑的具体实现"""
        pass

    def _evaluate_test_result(self, config: TestConfiguration,
                            result: Dict[str, Any]) -> Dict[str, Any]:
        """评估测试结果"""
        score = 0.0
        status = 'passed'
        recommendations = []

        # 检查阈值
        for metric_name, threshold in config.thresholds.items():
            if metric_name in result.get('metrics', {}):
                metric_value = result['metrics'][metric_name]

                if metric_value < threshold:
                    status = 'failed'
                    recommendations.append(
                        f"{metric_name} ({metric_value:.3f}) 低于阈值 {threshold}"
                    )
                elif metric_value < threshold * 1.1:  # 警告阈值
                    if status == 'passed':
                        status = 'warning'
                    recommendations.append(
                        f"{metric_name} ({metric_value:.3f}) 接近阈值 {threshold}"
                    )
                else:
                    score += 1.0

        # 计算综合评分
        total_metrics = len(config.thresholds)
        if total_metrics > 0:
            score = score / total_metrics

        return {
            'status': status,
            'score': score,
            'recommendations': recommendations
        }

    def execute_test_suite(self, suite: TestSuite, data: pd.DataFrame,
                          context: Dict[str, Any] = None) -> List[TestResult]:
        """执行测试套件"""
        results = []
        context = context or {}

        if suite.parallel_execution:
            # 并行执行
            with ThreadPoolExecutor(max_workers=len(suite.test_configs)) as executor:
                futures = {}
                for config_id in suite.test_configs:
                    future = executor.submit(
                        self.execute_test, config_id, data, context
                    )
                    futures[future] = config_id

                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=suite.timeout_minutes * 60)
                        results.append(result)
                    except Exception as e:
                        config_id = futures[future]
                        logger.error(f"Test {config_id} failed: {str(e)}")
                        # 创建错误结果
                        error_result = TestResult(
                            test_id=f"{config_id}_error",
                            config_id=config_id,
                            status='error',
                            score=0.0,
                            metrics={},
                            details={},
                            execution_time=0.0,
                            start_time=datetime.now().isoformat(),
                            end_time=datetime.now().isoformat(),
                            error_message=str(e),
                            recommendations=[]
                        )
                        results.append(error_result)
        else:
            # 顺序执行
            for config_id in suite.execution_order:
                try:
                    result = self.execute_test(config_id, data, context)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Test {config_id} failed: {str(e)}")
                    error_result = TestResult(
                        test_id=f"{config_id}_error",
                        config_id=config_id,
                        status='error',
                        score=0.0,
                        metrics={},
                        details={},
                        execution_time=0.0,
                        start_time=datetime.now().isoformat(),
                        end_time=datetime.now().isoformat(),
                        error_message=str(e),
                        recommendations=[]
                    )
                    results.append(error_result)

        return results

    def _save_test_result(self, result: TestResult):
        """保存测试结果到数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO test_results
                (test_id, config_id, status, score, metrics, details,
                 execution_time, start_time, end_time, error_message, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.test_id, result.config_id, result.status, result.score,
                json.dumps(result.metrics), json.dumps(result.details),
                result.execution_time, result.start_time, result.end_time,
                result.error_message, json.dumps(result.recommendations)
            ))

    def save_test_suite(self, suite: TestSuite):
        """保存测试套件"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO test_suites
                (suite_id, name, description, industry, test_configs,
                 execution_order, parallel_execution, timeout_minutes,
                 created_date, updated_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                suite.suite_id, suite.name, suite.description, suite.industry,
                json.dumps(suite.test_configs), json.dumps(suite.execution_order),
                1 if suite.parallel_execution else 0, suite.timeout_minutes,
                suite.created_date, suite.updated_date
            ))

    def load_test_suite(self, suite_id: str) -> Optional[TestSuite]:
        """加载测试套件"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM test_suites WHERE suite_id = ?', (suite_id,))
            row = cursor.fetchone()

        if row:
            return TestSuite(
                suite_id=row[0], name=row[1], description=row[2], industry=row[3],
                test_configs=json.loads(row[4]), execution_order=json.loads(row[5]),
                parallel_execution=bool(row[6]), timeout_minutes=row[7],
                created_date=row[8], updated_date=row[9]
            )

        return None

    def generate_test_report(self, test_results: List[TestResult],
                           output_format: str = 'markdown') -> str:
        """生成测试报告"""
        if output_format == 'markdown':
            return self._generate_markdown_report(test_results)
        elif output_format == 'json':
            return json.dumps([asdict(r) for r in test_results], indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

    def _generate_markdown_report(self, test_results: List[TestResult]) -> str:
        """生成Markdown格式的测试报告"""
        report = f"# {self.industry}行业测试报告\n\n"
        report += f"生成时间: {datetime.now().isoformat()}\n\n"

        # 统计信息
        total_tests = len(test_results)
        passed = sum(1 for r in test_results if r.status == 'passed')
        failed = sum(1 for r in test_results if r.status == 'failed')
        warning = sum(1 for r in test_results if r.status == 'warning')
        error = sum(1 for r in test_results if r.status == 'error')

        report += "## 测试统计\n\n"
        report += f"- 总测试数: {total_tests}\n"
        report += f"- 通过: {passed} ({passed/total_tests*100:.1f}%)\n"
        report += f"- 失败: {failed} ({failed/total_tests*100:.1f}%)\n"
        report += f"- 警告: {warning} ({warning/total_tests*100:.1f}%)\n"
        report += f"- 错误: {error} ({error/total_tests*100:.1f}%)\n\n"

        # 平均分数
        avg_score = sum(r.score for r in test_results) / total_tests if total_tests > 0 else 0
        report += f"- 平均分数: {avg_score:.3f}\n\n"

        # 详细结果
        report += "## 详细结果\n\n"
        for result in test_results:
            status_emoji = {
                'passed': '✅',
                'failed': '❌',
                'warning': '⚠️',
                'error': '💥'
            }.get(result.status, '❓')

            report += f"### {status_emoji} {result.config_id}\n\n"
            report += f"- **状态**: {result.status}\n"
            report += f"- **分数**: {result.score:.3f}\n"
            report += f"- **执行时间**: {result.execution_time:.2f}秒\n"
            report += f"- **开始时间**: {result.start_time}\n"
            report += f"- **结束时间**: {result.end_time}\n\n"

            if result.metrics:
                report += "**指标**:\n"
                for key, value in result.metrics.items():
                    report += f"- {key}: {value:.3f}\n"
                report += "\n"

            if result.recommendations:
                report += "**建议**:\n"
                for rec in result.recommendations:
                    report += f"- {rec}\n"
                report += "\n"

            if result.error_message:
                report += f"**错误信息**: {result.error_message}\n\n"

        return report

    def get_test_history(self, config_id: Optional[str] = None,
                        days: int = 30) -> List[TestResult]:
        """获取测试历史"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            if config_id:
                cursor = conn.execute('''
                    SELECT * FROM test_results
                    WHERE config_id = ? AND start_time >= ?
                    ORDER BY start_time DESC
                ''', (config_id, cutoff_date))
            else:
                cursor = conn.execute('''
                    SELECT * FROM test_results
                    WHERE start_time >= ?
                    ORDER BY start_time DESC
                ''', (cutoff_date,))

            rows = cursor.fetchall()

        results = []
        for row in rows:
            result = TestResult(
                test_id=row[0], config_id=row[1], status=row[2], score=row[3],
                metrics=json.loads(row[4]), details=json.loads(row[5]),
                execution_time=row[6], start_time=row[7], end_time=row[8],
                error_message=row[9], recommendations=json.loads(row[10])
            )
            results.append(result)

        return results

# 使用示例
if __name__ == "__main__":
    # 创建金融行业测试框架实例
    framework = IndustryTestFramework("financial_services")

    # 创建测试配置
    config = TestConfiguration(
        config_id="fraud_detection_test",
        industry="financial_services",
        test_type="fraud_detection",
        parameters={
            "model_path": "models/fraud_model.pkl",
            "feature_columns": ["amount", "frequency", "location_score"],
            "threshold": 0.8
        },
        thresholds={
            "accuracy": 0.85,
            "precision": 0.80,
            "recall": 0.75,
            "f1_score": 0.77
        },
        data_sources=["transaction_data.csv", "user_profiles.csv"],
        validation_rules={
            "data_quality": "high",
            "model_version": "latest"
        },
        created_date=datetime.now().isoformat(),
        updated_date=datetime.now().isoformat()
    )

    framework.save_configuration(config)

    # 创建测试套件
    suite = TestSuite(
        suite_id="financial_comprehensive_test",
        name="金融综合测试套件",
        description="涵盖风控、合规、性能等方面的全面测试",
        industry="financial_services",
        test_configs=["fraud_detection_test", "compliance_test", "performance_test"],
        execution_order=["fraud_detection_test", "compliance_test", "performance_test"],
        parallel_execution=True,
        timeout_minutes=30,
        created_date=datetime.now().isoformat(),
        updated_date=datetime.now().isoformat()
    )

    framework.save_test_suite(suite)

    # 模拟测试数据
    test_data = pd.DataFrame({
        'amount': np.random.normal(100, 50, 1000),
        'frequency': np.random.poisson(5, 1000),
        'location_score': np.random.uniform(0, 1, 1000),
        'is_fraud': np.random.choice([0, 1], 1000, p=[0.95, 0.05])
    })

    # 执行单个测试
    result = framework.execute_test("fraud_detection_test", test_data)
    print(f"测试结果: {result.status}, 分数: {result.score:.3f}")

    # 生成报告
    report = framework.generate_test_report([result])
    with open('test_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print("行业测试框架演示完成")