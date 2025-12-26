#!/usr/bin/env python3
"""
数据质量规则驱动检查Runner示例
用于演示如何实现规则驱动的数据质量自动化检查

作者: 数据质量测试框架
版本: 1.0
更新时间: 2025-12-24
"""

import yaml
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2  # 或其他数据库连接库

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class QualityRule:
    """数据质量规则定义"""
    name: str
    rule_type: str  # accuracy, completeness, consistency, etc.
    table_name: str
    column_name: Optional[str] = None
    condition: str
    threshold: float
    severity: str  # critical, major, minor
    description: str

@dataclass
class QualityCheckResult:
    """质量检查结果"""
    rule_name: str
    passed: bool
    actual_value: float
    threshold: float
    severity: str
    details: Dict[str, Any]
    timestamp: datetime

class DataQualityRunner:
    """数据质量检查执行器"""

    def __init__(self, config_path: str, db_connection_string: str):
        """
        初始化质量检查执行器

        Args:
            config_path: 规则配置文件路径
            db_connection_string: 数据库连接字符串
        """
        self.config_path = config_path
        self.db_connection_string = db_connection_string
        self.engine = create_engine(db_connection_string)
        self.rules = self._load_rules()
        self.results = []

    def _load_rules(self) -> List[QualityRule]:
        """加载质量规则配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            rules = []
            for rule_config in config.get('quality_rules', []):
                rule = QualityRule(
                    name=rule_config['name'],
                    rule_type=rule_config['type'],
                    table_name=rule_config['table'],
                    column_name=rule_config.get('column'),
                    condition=rule_config['condition'],
                    threshold=rule_config['threshold'],
                    severity=rule_config.get('severity', 'major'),
                    description=rule_config.get('description', '')
                )
                rules.append(rule)

            logger.info(f"成功加载 {len(rules)} 条质量规则")
            return rules

        except Exception as e:
            logger.error(f"加载规则配置失败: {e}")
            raise

    def run_quality_checks(self) -> List[QualityCheckResult]:
        """执行所有质量检查"""
        logger.info("开始执行数据质量检查...")

        for rule in self.rules:
            try:
                result = self._execute_single_check(rule)
                self.results.append(result)
                logger.info(f"规则 '{rule.name}' 检查完成: {'通过' if result.passed else '失败'}")

            except Exception as e:
                logger.error(f"执行规则 '{rule.name}' 失败: {e}")
                # 创建失败结果
                failed_result = QualityCheckResult(
                    rule_name=rule.name,
                    passed=False,
                    actual_value=0.0,
                    threshold=rule.threshold,
                    severity=rule.severity,
                    details={'error': str(e)},
                    timestamp=datetime.now()
                )
                self.results.append(failed_result)

        logger.info(f"质量检查完成，共执行 {len(self.results)} 项检查")
        return self.results

    def _execute_single_check(self, rule: QualityRule) -> QualityCheckResult:
        """执行单个质量检查"""
        # 构建SQL查询
        sql = self._build_check_sql(rule)

        # 执行查询
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            row = result.fetchone()

        actual_value = float(row[0]) if row else 0.0

        # 判断是否通过
        passed = self._evaluate_result(actual_value, rule.threshold, rule.condition)

        # 构建结果详情
        details = {
            'table': rule.table_name,
            'column': rule.column_name,
            'condition': rule.condition,
            'sql_executed': sql,
            'description': rule.description
        }

        return QualityCheckResult(
            rule_name=rule.name,
            passed=passed,
            actual_value=actual_value,
            threshold=rule.threshold,
            severity=rule.severity,
            details=details,
            timestamp=datetime.now()
        )

    def _build_check_sql(self, rule: QualityRule) -> str:
        """根据规则构建SQL查询"""
        table = rule.table_name
        column = rule.column_name

        if rule.rule_type == 'completeness':
            # 完整性检查：计算非空值比例
            if column:
                sql = f"SELECT (COUNT({column}) * 1.0 / COUNT(*)) FROM {table}"
            else:
                sql = f"SELECT 1.0 FROM {table} LIMIT 1"  # 简化示例

        elif rule.rule_type == 'uniqueness':
            # 唯一性检查：计算唯一值比例
            if column:
                sql = f"SELECT (COUNT(DISTINCT {column}) * 1.0 / COUNT(*)) FROM {table}"
            else:
                sql = f"SELECT 1.0 FROM {table} LIMIT 1"

        elif rule.rule_type == 'accuracy':
            # 准确性检查：自定义条件
            sql = f"SELECT AVG(CASE WHEN {rule.condition} THEN 1 ELSE 0 END) FROM {table}"

        elif rule.rule_type == 'consistency':
            # 一致性检查：跨表或自定义逻辑
            sql = rule.condition  # 直接使用条件作为SQL

        else:
            # 默认查询
            sql = f"SELECT COUNT(*) FROM {table}"

        return sql

    def _evaluate_result(self, actual: float, threshold: float, condition: str) -> bool:
        """评估检查结果是否通过"""
        if condition.startswith('>'):
            return actual > threshold
        elif condition.startswith('<'):
            return actual < threshold
        elif condition.startswith('>='):
            return actual >= threshold
        elif condition.startswith('<='):
            return actual <= threshold
        elif condition == '=':
            return abs(actual - threshold) < 0.001  # 浮点数比较
        else:
            return actual >= threshold  # 默认大于等于

    def generate_report(self) -> Dict[str, Any]:
        """生成质量检查报告"""
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r.passed)
        failed_checks = total_checks - passed_checks

        # 按严重程度统计失败
        critical_failures = sum(1 for r in self.results if not r.passed and r.severity == 'critical')
        major_failures = sum(1 for r in self.results if not r.passed and r.severity == 'major')

        report = {
            'summary': {
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': failed_checks,
                'pass_rate': passed_checks / total_checks if total_checks > 0 else 0,
                'critical_failures': critical_failures,
                'major_failures': major_failures
            },
            'timestamp': datetime.now().isoformat(),
            'results': [
                {
                    'rule_name': r.rule_name,
                    'passed': r.passed,
                    'actual_value': r.actual_value,
                    'threshold': r.threshold,
                    'severity': r.severity,
                    'details': r.details,
                    'timestamp': r.timestamp.isoformat()
                }
                for r in self.results
            ]
        }

        return report

    def save_report(self, output_path: str):
        """保存报告到文件"""
        report = self.generate_report()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"质量检查报告已保存到: {output_path}")

# 使用示例
if __name__ == "__main__":
    # 配置数据库连接（示例）
    DB_CONNECTION = "postgresql://user:password@localhost:5432/data_quality_db"

    # 规则配置文件路径
    RULES_CONFIG = "examples/09_quality/quality_rules.yml"

    # 创建执行器
    runner = DataQualityRunner(RULES_CONFIG, DB_CONNECTION)

    # 执行检查
    results = runner.run_quality_checks()

    # 生成并保存报告
    runner.save_report("quality_check_report.json")

    # 打印摘要
    report = runner.generate_report()
    summary = report['summary']
    print("
=== 数据质量检查报告 ===")
    print(f"总检查数: {summary['total_checks']}")
    print(f"通过数: {summary['passed_checks']}")
    print(f"失败数: {summary['failed_checks']}")
    print(".2%")
    print(f"严重失败: {summary['critical_failures']}")
    print(f"主要失败: {summary['major_failures']}")