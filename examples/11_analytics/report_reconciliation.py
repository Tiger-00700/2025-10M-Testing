#!/usr/bin/env python3
"""
报表与事实表一致性对账脚本
用于自动化验证BI报表数据与源数据的一致性

作者: 数据质量保障团队
版本: 1.0.0
更新时间: 2025-12-24
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import argparse
import sys
from typing import Dict, List, Tuple, Optional
import sqlalchemy as sa
from sqlalchemy import create_engine, text
import yaml
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('report_reconciliation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ReportReconciliation:
    """报表对账工具类"""

    def __init__(self, config_path: str):
        """初始化对账工具

        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # 数据库连接
        self.source_engine = create_engine(self.config['database']['source'])
        self.report_engine = create_engine(self.config['database']['report'])

        # 对账配置
        self.tolerance = self.config.get('tolerance', 0.001)
        self.date_column = self.config.get('date_column', 'dt')

        logger.info("报表对账工具初始化完成")

    def get_date_range(self, days_back: int = 7) -> Tuple[str, str]:
        """获取对账日期范围

        Args:
            days_back: 回溯天数

        Returns:
            (开始日期, 结束日期) 格式: YYYY-MM-DD
        """
        end_date = datetime.now() - timedelta(days=1)
        start_date = end_date - timedelta(days=days_back-1)

        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

    def execute_query(self, engine, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """执行SQL查询

        Args:
            engine: 数据库引擎
            query: SQL查询语句
            params: 查询参数

        Returns:
            查询结果DataFrame
        """
        try:
            with engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                return pd.DataFrame(result.fetchall(), columns=result.keys())
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            raise

    def calculate_metrics(self, source_df: pd.DataFrame, report_df: pd.DataFrame,
                         metrics_config: Dict) -> Dict:
        """计算对账指标

        Args:
            source_df: 源数据
            report_df: 报表数据
            metrics_config: 指标配置

        Returns:
            对账结果字典
        """
        results = {}

        for metric in metrics_config:
            metric_name = metric['name']
            source_col = metric['source_column']
            report_col = metric['report_column']
            aggregation = metric.get('aggregation', 'sum')

            try:
                # 计算源数据指标
                if aggregation == 'sum':
                    source_value = source_df[source_col].sum()
                elif aggregation == 'count':
                    source_value = len(source_df)
                elif aggregation == 'avg':
                    source_value = source_df[source_col].mean()
                else:
                    source_value = source_df[source_col].sum()

                # 计算报表数据指标
                if aggregation == 'sum':
                    report_value = report_df[report_col].sum()
                elif aggregation == 'count':
                    report_value = len(report_df)
                elif aggregation == 'avg':
                    report_value = report_df[report_col].mean()
                else:
                    report_value = report_df[report_col].sum()

                # 计算差异
                diff = abs(source_value - report_value)
                diff_pct = diff / abs(source_value) if source_value != 0 else 0

                # 判断是否通过
                passed = diff_pct <= self.tolerance

                results[metric_name] = {
                    'source_value': float(source_value),
                    'report_value': float(report_value),
                    'difference': float(diff),
                    'difference_pct': float(diff_pct),
                    'passed': passed,
                    'tolerance': self.tolerance
                }

            except Exception as e:
                logger.error(f"计算指标 {metric_name} 失败: {e}")
                results[metric_name] = {
                    'error': str(e),
                    'passed': False
                }

        return results

    def generate_report(self, results: Dict, output_path: str):
        """生成对账报告

        Args:
            results: 对账结果
            output_path: 报告输出路径
        """
        report = {
            'execution_time': datetime.now().isoformat(),
            'summary': {
                'total_metrics': len(results),
                'passed_metrics': sum(1 for r in results.values() if r.get('passed', False)),
                'failed_metrics': sum(1 for r in results.values() if not r.get('passed', False)),
                'pass_rate': sum(1 for r in results.values() if r.get('passed', False)) / len(results)
            },
            'details': results
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"对账报告已生成: {output_path}")

    def run_reconciliation(self, report_name: str, start_date: str, end_date: str) -> bool:
        """执行对账

        Args:
            report_name: 报表名称
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            对账是否通过
        """
        logger.info(f"开始对账: {report_name}, 日期范围: {start_date} 至 {end_date}")

        # 获取报表配置
        report_config = self.config['reports'][report_name]

        # 执行源数据查询
        source_query = report_config['source_query']
        source_df = self.execute_query(
            self.source_engine,
            source_query,
            {'start_date': start_date, 'end_date': end_date}
        )

        # 执行报表数据查询
        report_query = report_config['report_query']
        report_df = self.execute_query(
            self.report_engine,
            report_query,
            {'start_date': start_date, 'end_date': end_date}
        )

        # 计算对账指标
        results = self.calculate_metrics(source_df, report_df, report_config['metrics'])

        # 生成报告
        output_path = f"reconciliation_report_{report_name}_{end_date}.json"
        self.generate_report(results, output_path)

        # 判断整体结果
        all_passed = all(r.get('passed', False) for r in results.values())

        if all_passed:
            logger.info(f"对账通过: {report_name}")
        else:
            logger.warning(f"对账失败: {report_name}")
            failed_metrics = [k for k, v in results.items() if not v.get('passed', False)]
            logger.warning(f"失败指标: {failed_metrics}")

        return all_passed

def main():
    parser = argparse.ArgumentParser(description='报表对账工具')
    parser.add_argument('--config', required=True, help='配置文件路径')
    parser.add_argument('--report', required=True, help='报表名称')
    parser.add_argument('--days', type=int, default=7, help='对账天数')
    parser.add_argument('--start-date', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='结束日期 (YYYY-MM-DD)')

    args = parser.parse_args()

    try:
        # 初始化对账工具
        reconciler = ReportReconciliation(args.config)

        # 确定日期范围
        if args.start_date and args.end_date:
            start_date, end_date = args.start_date, args.end_date
        else:
            start_date, end_date = reconciler.get_date_range(args.days)

        # 执行对账
        success = reconciler.run_reconciliation(args.report, start_date, end_date)

        # 返回状态码
        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"对账执行失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()