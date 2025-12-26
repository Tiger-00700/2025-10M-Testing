# 质量摘要工具

这个模块提供了数据质量检查和摘要报告功能。

```python
import pandas as pd
import numpy as np
from datetime import datetime

class QualitySummary:
    """数据质量摘要工具"""

    def __init__(self):
        self.summary_stats = {}

    def analyze_dataframe(self, df, name="dataset"):
        """
        分析DataFrame的质量指标
        """
        analysis = {
            'dataset_name': name,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'column_info': {},
            'overall_quality': {}
        }

        # 逐列分析
        for col in df.columns:
            col_info = {
                'dtype': str(df[col].dtype),
                'non_null_count': df[col].notna().sum(),
                'null_count': df[col].isna().sum(),
                'null_percentage': round(df[col].isna().sum() / len(df) * 100, 2),
                'unique_count': df[col].nunique()
            }

            # 数值型列的统计
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info.update({
                    'mean': round(df[col].mean(), 2) if df[col].notna().any() else None,
                    'std': round(df[col].std(), 2) if df[col].notna().any() else None,
                    'min': df[col].min() if df[col].notna().any() else None,
                    'max': df[col].max() if df[col].notna().any() else None,
                    'zeros_count': (df[col] == 0).sum(),
                    'negative_count': (df[col] < 0).sum() if pd.api.types.is_numeric_dtype(df[col]) else 0
                })

            # 字符串列的统计
            elif pd.api.types.is_object_dtype(df[col]):
                col_info.update({
                    'avg_length': round(df[col].str.len().mean(), 2) if df[col].notna().any() else None,
                    'empty_strings': (df[col] == '').sum(),
                    'whitespace_only': df[col].str.match(r'^\s*$').sum() if df[col].notna().any() else 0
                })

            analysis['column_info'][col] = col_info

        # 整体质量指标
        total_nulls = sum(info['null_count'] for info in analysis['column_info'].values())
        analysis['overall_quality'] = {
            'total_null_percentage': round(total_nulls / (len(df) * len(df.columns)) * 100, 2),
            'columns_with_nulls': sum(1 for info in analysis['column_info'].values() if info['null_count'] > 0),
            'completeness_score': round((1 - total_nulls / (len(df) * len(df.columns))) * 100, 2),
            'analysis_timestamp': datetime.now().isoformat()
        }

        self.summary_stats[name] = analysis
        return analysis

    def generate_report(self, name=None):
        """
        生成质量报告
        """
        if name and name in self.summary_stats:
            stats = self.summary_stats[name]
        elif self.summary_stats:
            stats = list(self.summary_stats.values())[0]
        else:
            return "无质量分析数据"

        report = f"""
# 数据质量分析报告

## 数据集概览
- 数据集名称: {stats['dataset_name']}
- 总行数: {stats['total_rows']}
- 总列数: {stats['total_columns']}
- 分析时间: {stats['overall_quality']['analysis_timestamp']}

## 整体质量指标
- 完整性评分: {stats['overall_quality']['completeness_score']}%
- 总空值率: {stats['overall_quality']['total_null_percentage']}%
- 包含空值的列数: {stats['overall_quality']['columns_with_nulls']}

## 列级质量详情
"""

        for col, info in stats['column_info'].items():
            report += f"""
### {col}
- 数据类型: {info['dtype']}
- 非空数量: {info['non_null_count']}
- 空值数量: {info['null_count']} ({info['null_percentage']}%)
- 唯一值数量: {info['unique_count']}
"""
            if 'mean' in info and info['mean'] is not None:
                report += f"- 均值: {info['mean']}\n"
                report += f"- 标准差: {info['std']}\n"
                report += f"- 最小值: {info['min']}\n"
                report += f"- 最大值: {info['max']}\n"
                report += f"- 零值数量: {info['zeros_count']}\n"
                report += f"- 负值数量: {info['negative_count']}\n"

        return report

    def compare_datasets(self, name1, name2):
        """
        比较两个数据集的质量
        """
        if name1 not in self.summary_stats or name2 not in self.summary_stats:
            return "数据集不存在"

        stats1 = self.summary_stats[name1]['overall_quality']
        stats2 = self.summary_stats[name2]['overall_quality']

        comparison = f"""
# 数据集质量对比报告

## {name1} vs {name2}

| 指标 | {name1} | {name2} | 差异 |
|------|---------|---------|------|
| 完整性评分 | {stats1['completeness_score']}% | {stats2['completeness_score']}% | {stats1['completeness_score'] - stats2['completeness_score']:+.2f}% |
| 总空值率 | {stats1['total_null_percentage']}% | {stats2['total_null_percentage']}% | {stats1['total_null_percentage'] - stats2['total_null_percentage']:+.2f}% |
| 包含空值的列数 | {stats1['columns_with_nulls']} | {stats2['columns_with_nulls']} | {stats1['columns_with_nulls'] - stats2['columns_with_nulls']:+} |
"""

        return comparison

# 使用示例
if __name__ == "__main__":
    qa = QualitySummary()

    # 创建示例数据
    sample_data = pd.DataFrame({
        'id': range(1, 101),
        'name': ['User' + str(i) for i in range(1, 101)],
        'age': np.random.randint(18, 80, 100),
        'score': np.random.uniform(0, 100, 100),
        'email': ['user' + str(i) + '@example.com' for i in range(1, 101)]
    })

    # 引入一些缺失值
    sample_data.loc[10:15, 'age'] = np.nan
    sample_data.loc[20:25, 'score'] = np.nan

    # 分析质量
    analysis = qa.analyze_dataframe(sample_data, "user_sample")
    print("质量分析完成")

    # 生成报告
    report = qa.generate_report("user_sample")
    print(report)
```