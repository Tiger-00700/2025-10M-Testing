# 质量摘要工具 (工具版本)

这个工具版本提供了命令行接口的数据质量检查功能。

```python
#!/usr/bin/env python3
"""
数据质量摘要工具 - 命令行版本
用于大数据测试环境中的数据质量检查
"""

import argparse
import pandas as pd
import numpy as np
import json
import sys
from datetime import datetime
from pathlib import Path

class QualityAnalyzer:
    """数据质量分析器"""

    def __init__(self):
        self.results = {}

    def load_data(self, file_path, file_format='csv', **kwargs):
        """
        加载数据文件
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if file_format.lower() == 'csv':
            df = pd.read_csv(file_path, **kwargs)
        elif file_format.lower() == 'json':
            df = pd.read_json(file_path, **kwargs)
        elif file_format.lower() == 'parquet':
            df = pd.read_parquet(file_path, **kwargs)
        else:
            raise ValueError(f"不支持的文件格式: {file_format}")

        return df

    def analyze_quality(self, df, dataset_name="dataset"):
        """
        执行质量分析
        """
        analysis = {
            'dataset_name': dataset_name,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'total_cells': len(df) * len(df.columns)
            },
            'quality_metrics': {}
        }

        # 计算质量指标
        total_nulls = df.isnull().sum().sum()
        analysis['quality_metrics'] = {
            'completeness': {
                'score': round((1 - total_nulls / analysis['summary']['total_cells']) * 100, 2),
                'total_nulls': int(total_nulls),
                'null_percentage': round(total_nulls / analysis['summary']['total_cells'] * 100, 2)
            },
            'validity': {
                'columns_with_nulls': int((df.isnull().sum() > 0).sum()),
                'columns_completely_null': int((df.isnull().sum() == len(df)).sum())
            },
            'uniqueness': {
                'duplicate_rows': int(df.duplicated().sum()),
                'duplicate_percentage': round(df.duplicated().sum() / len(df) * 100, 2)
            }
        }

        # 列级分析
        analysis['column_analysis'] = {}
        for col in df.columns:
            col_stats = {
                'dtype': str(df[col].dtype),
                'null_count': int(df[col].isnull().sum()),
                'null_percentage': round(df[col].isnull().sum() / len(df) * 100, 2),
                'unique_count': int(df[col].nunique()),
                'unique_percentage': round(df[col].nunique() / len(df) * 100, 2)
            }

            # 数据类型特定的统计
            if pd.api.types.is_numeric_dtype(df[col]):
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    col_stats['numeric_stats'] = {
                        'mean': round(non_null_values.mean(), 2),
                        'std': round(non_null_values.std(), 2),
                        'min': float(non_null_values.min()),
                        'max': float(non_null_values.max()),
                        'zeros': int((non_null_values == 0).sum()),
                        'negatives': int((non_null_values < 0).sum())
                    }

            analysis['column_analysis'][col] = col_stats

        self.results[dataset_name] = analysis
        return analysis

    def generate_report(self, dataset_name=None, output_format='text'):
        """
        生成质量报告
        """
        if dataset_name and dataset_name in self.results:
            analysis = self.results[dataset_name]
        elif self.results:
            analysis = list(self.results.values())[0]
        else:
            return "无分析结果"

        if output_format == 'json':
            return json.dumps(analysis, indent=2, ensure_ascii=False)
        elif output_format == 'text':
            return self._format_text_report(analysis)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

    def _format_text_report(self, analysis):
        """
        格式化文本报告
        """
        report = f"""
数据质量分析报告
================

数据集: {analysis['dataset_name']}
分析时间: {analysis['timestamp']}

数据集概览:
- 总行数: {analysis['summary']['total_rows']:,}
- 总列数: {analysis['summary']['total_columns']}
- 总单元格数: {analysis['summary']['total_cells']:,}

质量指标:
- 完整性评分: {analysis['quality_metrics']['completeness']['score']}%
- 总空值数: {analysis['quality_metrics']['completeness']['total_nulls']:,}
- 空值率: {analysis['quality_metrics']['completeness']['null_percentage']}%
- 包含空值的列数: {analysis['quality_metrics']['validity']['columns_with_nulls']}
- 完全为空的列数: {analysis['quality_metrics']['validity']['columns_completely_null']}
- 重复行数: {analysis['quality_metrics']['uniqueness']['duplicate_rows']:,}
- 重复行百分比: {analysis['quality_metrics']['uniqueness']['duplicate_percentage']}%

列级分析:
"""

        for col, stats in analysis['column_analysis'].items():
            report += f"\n{col}:\n"
            report += f"  - 类型: {stats['dtype']}\n"
            report += f"  - 空值数: {stats['null_count']:,} ({stats['null_percentage']}%)\n"
            report += f"  - 唯一值数: {stats['unique_count']:,} ({stats['unique_percentage']}%)\n"

            if 'numeric_stats' in stats:
                ns = stats['numeric_stats']
                report += f"  - 数值统计: 均值={ns['mean']}, 标准差={ns['std']}, 范围=[{ns['min']}, {ns['max']}]\n"
                report += f"  - 特殊值: 零值={ns['zeros']}, 负值={ns['negatives']}\n"

        return report

def main():
    parser = argparse.ArgumentParser(description='数据质量分析工具')
    parser.add_argument('input_file', help='输入数据文件路径')
    parser.add_argument('-f', '--format', choices=['csv', 'json', 'parquet'],
                       default='csv', help='输入文件格式 (默认: csv)')
    parser.add_argument('-n', '--name', default='dataset',
                       help='数据集名称 (默认: dataset)')
    parser.add_argument('-o', '--output', choices=['text', 'json'],
                       default='text', help='输出格式 (默认: text)')
    parser.add_argument('--output-file', help='输出文件路径 (默认: 标准输出)')

    args = parser.parse_args()

    try:
        analyzer = QualityAnalyzer()

        # 加载数据
        df = analyzer.load_data(args.input_file, args.format)

        # 分析质量
        analysis = analyzer.analyze_quality(df, args.name)

        # 生成报告
        report = analyzer.generate_report(args.name, args.output)

        # 输出结果
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已保存到: {args.output_file}")
        else:
            print(report)

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 使用方法

```bash
# 分析CSV文件
python qa_summary.py data.csv

# 分析JSON文件
python qa_summary.py data.json -f json

# 输出JSON格式报告
python qa_summary.py data.csv -o json

# 保存报告到文件
python qa_summary.py data.csv --output-file report.txt
```