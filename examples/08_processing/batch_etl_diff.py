#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
batch_etl_diff.py
批处理ETL前后差异对比脚本示例

此脚本用于比较ETL作业输入和输出数据的差异，
支持记录数、主键、业务指标的自动化校验。
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text
import json
import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_etl_diff.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BatchETLDiffChecker:
    """
    批处理ETL差异对比检查器
    """

    def __init__(self, config_path: str):
        """
        初始化检查器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.source_engine = None
        self.target_engine = None
        self._setup_connections()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise

    def _setup_connections(self):
        """设置数据库连接"""
        try:
            # 源数据库连接
            if 'source_db' in self.config:
                source_config = self.config['source_db']
                source_url = self._build_db_url(source_config)
                self.source_engine = create_engine(source_url)

            # 目标数据库连接
            if 'target_db' in self.config:
                target_config = self.config['target_db']
                target_url = self._build_db_url(target_config)
                self.target_engine = create_engine(target_url)

            logger.info("数据库连接设置完成")
        except Exception as e:
            logger.error(f"数据库连接设置失败: {e}")
            raise

    def _build_db_url(self, db_config: Dict[str, Any]) -> str:
        """构建数据库URL"""
        db_type = db_config.get('type', 'postgresql')
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 5432)
        database = db_config.get('database', '')
        username = db_config.get('username', '')
        password = db_config.get('password', '')

        if db_type == 'postgresql':
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        elif db_type == 'mysql':
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        elif db_type == 'oracle':
            return f"oracle://{username}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

    def run_comparison(self, job_name: str, batch_date: str) -> Dict[str, Any]:
        """
        运行ETL差异对比

        Args:
            job_name: 作业名称
            batch_date: 批次日期 (YYYY-MM-DD)

        Returns:
            对比结果字典
        """
        logger.info(f"开始ETL差异对比 - 作业: {job_name}, 批次: {batch_date}")

        try:
            # 获取作业配置
            job_config = self.config['jobs'][job_name]

            # 执行各项检查
            results = {
                'job_name': job_name,
                'batch_date': batch_date,
                'timestamp': datetime.now().isoformat(),
                'checks': {}
            }

            # 1. 记录数对比
            results['checks']['record_count'] = self._check_record_count(job_config, batch_date)

            # 2. 主键一致性检查
            results['checks']['primary_key_consistency'] = self._check_primary_key_consistency(job_config, batch_date)

            # 3. 业务指标对比
            results['checks']['business_metrics'] = self._check_business_metrics(job_config, batch_date)

            # 4. 数据质量检查
            results['checks']['data_quality'] = self._check_data_quality(job_config, batch_date)

            # 计算总体状态
            results['overall_status'] = self._calculate_overall_status(results['checks'])

            logger.info(f"ETL差异对比完成 - 状态: {results['overall_status']}")
            return results

        except Exception as e:
            logger.error(f"ETL差异对比失败: {e}")
            return {
                'job_name': job_name,
                'batch_date': batch_date,
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'ERROR',
                'error_message': str(e)
            }

    def _check_record_count(self, job_config: Dict[str, Any], batch_date: str) -> Dict[str, Any]:
        """检查记录数"""
        try:
            source_query = job_config['source']['record_count_query'].format(batch_date=batch_date)
            target_query = job_config['target']['record_count_query'].format(batch_date=batch_date)

            source_count = self._execute_scalar_query(self.source_engine, source_query)
            target_count = self._execute_scalar_query(self.target_engine, target_query)

            diff = abs(source_count - target_count)
            tolerance = job_config.get('tolerances', {}).get('record_count', 0)

            status = 'PASS' if diff <= tolerance else 'FAIL'

            return {
                'status': status,
                'source_count': source_count,
                'target_count': target_count,
                'difference': diff,
                'tolerance': tolerance
            }

        except Exception as e:
            logger.error(f"记录数检查失败: {e}")
            return {'status': 'ERROR', 'error': str(e)}

    def _check_primary_key_consistency(self, job_config: Dict[str, Any], batch_date: str) -> Dict[str, Any]:
        """检查主键一致性"""
        try:
            source_query = job_config['source']['primary_key_query'].format(batch_date=batch_date)
            target_query = job_config['target']['primary_key_query'].format(batch_date=batch_date)

            source_keys = set(self._execute_query(self.source_engine, source_query))
            target_keys = set(self._execute_query(self.target_engine, target_query))

            missing_in_target = source_keys - target_keys
            extra_in_target = target_keys - source_keys

            status = 'PASS' if len(missing_in_target) == 0 and len(extra_in_target) == 0 else 'FAIL'

            return {
                'status': status,
                'source_unique_keys': len(source_keys),
                'target_unique_keys': len(target_keys),
                'missing_in_target': len(missing_in_target),
                'extra_in_target': len(extra_in_target),
                'sample_missing': list(missing_in_target)[:10] if missing_in_target else []
            }

        except Exception as e:
            logger.error(f"主键一致性检查失败: {e}")
            return {'status': 'ERROR', 'error': str(e)}

    def _check_business_metrics(self, job_config: Dict[str, Any], batch_date: str) -> Dict[str, Any]:
        """检查业务指标"""
        try:
            results = {}
            metrics_config = job_config.get('business_metrics', {})

            for metric_name, metric_config in metrics_config.items():
                source_query = metric_config['source_query'].format(batch_date=batch_date)
                target_query = metric_config['target_query'].format(batch_date=batch_date)

                source_value = self._execute_scalar_query(self.source_engine, source_query)
                target_value = self._execute_scalar_query(self.target_engine, target_query)

                diff = abs(source_value - target_value)
                tolerance = metric_config.get('tolerance', 0)

                status = 'PASS' if diff <= tolerance else 'FAIL'

                results[metric_name] = {
                    'status': status,
                    'source_value': source_value,
                    'target_value': target_value,
                    'difference': diff,
                    'tolerance': tolerance
                }

            return results

        except Exception as e:
            logger.error(f"业务指标检查失败: {e}")
            return {'status': 'ERROR', 'error': str(e)}

    def _check_data_quality(self, job_config: Dict[str, Any], batch_date: str) -> Dict[str, Any]:
        """检查数据质量"""
        try:
            results = {}
            quality_config = job_config.get('data_quality', {})

            for check_name, check_config in quality_config.items():
                query = check_config['query'].format(batch_date=batch_date)
                result = self._execute_scalar_query(self.target_engine, query)

                expected = check_config.get('expected', 0)
                status = 'PASS' if result == expected else 'FAIL'

                results[check_name] = {
                    'status': status,
                    'actual': result,
                    'expected': expected
                }

            return results

        except Exception as e:
            logger.error(f"数据质量检查失败: {e}")
            return {'status': 'ERROR', 'error': str(e)}

    def _execute_scalar_query(self, engine, query: str) -> Any:
        """执行标量查询"""
        with engine.connect() as conn:
            result = conn.execute(text(query))
            return result.scalar()

    def _execute_query(self, engine, query: str) -> List[Any]:
        """执行查询并返回结果列表"""
        with engine.connect() as conn:
            result = conn.execute(text(query))
            return [row[0] for row in result.fetchall()]

    def _calculate_overall_status(self, checks: Dict[str, Any]) -> str:
        """计算总体状态"""
        has_failures = False
        has_errors = False

        def check_status_recursive(check_dict):
            nonlocal has_failures, has_errors
            for key, value in check_dict.items():
                if isinstance(value, dict):
                    if 'status' in value:
                        if value['status'] == 'FAIL':
                            has_failures = True
                        elif value['status'] == 'ERROR':
                            has_errors = True
                    else:
                        check_status_recursive(value)

        check_status_recursive(checks)

        if has_errors:
            return 'ERROR'
        elif has_failures:
            return 'FAIL'
        else:
            return 'PASS'

    def save_results(self, results: Dict[str, Any], output_path: str):
        """保存结果到文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"结果已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存结果失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批处理ETL差异对比工具')
    parser.add_argument('--config', required=True, help='配置文件路径')
    parser.add_argument('--job', required=True, help='作业名称')
    parser.add_argument('--batch-date', required=True, help='批次日期 (YYYY-MM-DD)')
    parser.add_argument('--output', default='etl_diff_results.json', help='输出文件路径')

    args = parser.parse_args()

    try:
        # 创建检查器
        checker = BatchETLDiffChecker(args.config)

        # 运行对比
        results = checker.run_comparison(args.job, args.batch_date)

        # 保存结果
        checker.save_results(results, args.output)

        # 输出摘要
        print(f"ETL差异对比完成 - 状态: {results['overall_status']}")
        if results['overall_status'] != 'PASS':
            print("发现差异，请检查详细结果")

        sys.exit(0 if results['overall_status'] == 'PASS' else 1)

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()