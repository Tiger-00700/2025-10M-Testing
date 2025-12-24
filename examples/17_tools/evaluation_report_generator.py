# examples/17_tools/evaluation_report_generator.py
import yaml
import json
import pandas as pd
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import os

@dataclass
class EvaluationResult:
    tool_name: str
    evaluator: str
    evaluation_date: str
    scores: Dict[str, float]
    total_score: float
    recommendation: str
    strengths: List[str]
    weaknesses: List[str]
    risks: List[str]

class ToolEvaluationReport:
    """Generate comprehensive tool evaluation reports"""

    def __init__(self, checklist_file: str):
        with open(checklist_file, 'r', encoding='utf-8') as f:
            self.checklist = yaml.safe_load(f)

        self.results: List[EvaluationResult] = []

    def add_evaluation_result(self, result: EvaluationResult):
        """Add an evaluation result"""
        self.results.append(result)

    def calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted total score"""
        total_score = 0.0

        for dimension, dimension_config in self.checklist['evaluation_dimensions']:
            dimension_name = dimension_config['name']
            dimension_weight = dimension_config['weight']

            if dimension_name in scores:
                dimension_score = scores[dimension_name]
                total_score += dimension_score * dimension_weight

        return round(total_score, 2)

    def generate_comparison_report(self, output_dir: str = "reports"):
        """Generate comparison report for all evaluated tools"""
        os.makedirs(output_dir, exist_ok=True)

        # Prepare data for analysis
        comparison_data = []
        for result in self.results:
            row = {
                'Tool': result.tool_name,
                'Total Score': result.total_score,
                'Recommendation': result.recommendation,
                'Evaluator': result.evaluator,
                'Date': result.evaluation_date
            }

            # Add dimension scores
            for dimension in self.checklist['evaluation_dimensions']:
                dim_name = dimension['name']
                if dim_name in result.scores:
                    row[dim_name.title()] = result.scores[dim_name]

            comparison_data.append(row)

        df = pd.DataFrame(comparison_data)

        # Generate reports
        self._generate_summary_report(df, output_dir)
        self._generate_detailed_report(df, output_dir)
        self._generate_visualizations(df, output_dir)

    def _generate_summary_report(self, df: pd.DataFrame, output_dir: str):
        """Generate summary report"""
        summary_file = os.path.join(output_dir, "evaluation_summary.md")

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# 工具评估总结报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 评估概览\n\n")
            f.write(f"- 评估工具数量: {len(df)}\n")
            f.write(f"- 最高评分: {df['Total Score'].max():.2f}\n")
            f.write(f"- 最低评分: {df['Total Score'].min():.2f}\n")
            f.write(f"- 平均评分: {df['Total Score'].mean():.2f}\n\n")

            f.write("## 工具排名\n\n")
            f.write("| 排名 | 工具名称 | 总评分 | 推荐等级 | 评估人 |\n")
            f.write("|------|---------|--------|---------|--------|\n")

            sorted_df = df.sort_values('Total Score', ascending=False)
            for idx, row in sorted_df.iterrows():
                rank = idx + 1
                f.write(f"| {rank} | {row['Tool']} | {row['Total Score']:.2f} | {row['Recommendation']} | {row['Evaluator']} |\n")

            f.write("\n## 维度分析\n\n")

            dimensions = [d['name'].title() for d in self.checklist['evaluation_dimensions']]
            for dim in dimensions:
                if dim in df.columns:
                    f.write(f"### {dim}\n\n")
                    dim_stats = df[dim].describe()
                    f.write(f"- 平均分: {dim_stats['mean']:.2f}\n")
                    f.write(f"- 最高分: {dim_stats['max']:.2f}\n")
                    f.write(f"- 最低分: {dim_stats['min']:.2f}\n\n")

    def _generate_detailed_report(self, df: pd.DataFrame, output_dir: str):
        """Generate detailed report for each tool"""
        for _, row in df.iterrows():
            tool_name = row['Tool'].replace(' ', '_')
            detail_file = os.path.join(output_dir, f"{tool_name}_detailed.md")

            with open(detail_file, 'w', encoding='utf-8') as f:
                f.write(f"# {row['Tool']} 详细评估报告\n\n")
                f.write(f"评估人: {row['Evaluator']}\n")
                f.write(f"评估日期: {row['Date']}\n")
                f.write(f"总评分: {row['Total Score']:.2f}\n")
                f.write(f"推荐等级: {row['Recommendation']}\n\n")

                # Find the result object for this tool
                result = next((r for r in self.results if r.tool_name == row['Tool']), None)
                if result:
                    f.write("## 维度评分详情\n\n")
                    for dimension in self.checklist['evaluation_dimensions']:
                        dim_name = dimension['name']
                        if dim_name in result.scores:
                            score = result.scores[dim_name]
                            f.write(f"- **{dim_name.title()}**: {score:.2f}/5.0\n")

                    f.write("\n## 优势\n\n")
                    for strength in result.strengths:
                        f.write(f"- {strength}\n")

                    f.write("\n## 劣势\n\n")
                    for weakness in result.weaknesses:
                        f.write(f"- {weakness}\n")

                    f.write("\n## 风险评估\n\n")
                    for risk in result.risks:
                        f.write(f"- {risk}\n")

    def _generate_visualizations(self, df: pd.DataFrame, output_dir: str):
        """Generate visualization charts"""
        plt.style.use('default')
        sns.set_palette("husl")

        # Radar chart for dimension comparison
        dimensions = [d['name'].title() for d in self.checklist['evaluation_dimensions']]
        available_dims = [d for d in dimensions if d in df.columns]

        if len(df) > 1 and available_dims:
            # Create radar chart
            fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))

            angles = [n / float(len(available_dims)) * 2 * 3.14159 for n in range(len(available_dims))]
            angles += angles[:1]

            for _, row in df.iterrows():
                values = [row[dim] for dim in available_dims]
                values += values[:1]

                ax.plot(angles, values, 'o-', linewidth=2, label=row['Tool'])
                ax.fill(angles, values, alpha=0.25)

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(available_dims)
            ax.set_ylim(0, 5)
            ax.set_title("工具评估维度对比", size=16, fontweight='bold')
            ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
            ax.grid(True)

            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "dimension_comparison_radar.png"), dpi=300, bbox_inches='tight')
            plt.close()

        # Bar chart for total scores
        if len(df) > 1:
            plt.figure(figsize=(12, 6))
            bars = plt.bar(df['Tool'], df['Total Score'])
            plt.title('工具总评分对比', fontsize=16, fontweight='bold')
            plt.xlabel('工具名称', fontsize=12)
            plt.ylabel('总评分', fontsize=12)
            plt.ylim(0, 5)

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                        f'{height:.2f}', ha='center', va='bottom')

            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "total_score_comparison.png"), dpi=300, bbox_inches='tight')
            plt.close()

def main():
    """Main function to demonstrate report generation"""
    # Initialize report generator
    generator = ToolEvaluationReport("examples/17_tools/tool_evaluation_checklist.yml")

    # Add sample evaluation results
    sample_results = [
        EvaluationResult(
            tool_name="Great Expectations",
            evaluator="张三",
            evaluation_date="2024-01-15",
            scores={
                "functionality": 4.5,
                "performance": 4.0,
                "usability": 3.5,
                "integration": 4.5,
                "cost": 5.0,
                "vendor_support": 4.0,
                "security": 4.0
            },
            total_score=4.35,
            recommendation="强烈推荐",
            strengths=["功能完整", "社区活跃", "开源免费"],
            weaknesses=["学习曲线较陡", "文档需要改进"],
            risks=["版本更新频繁", "社区依赖"]
        ),
        EvaluationResult(
            tool_name="Informatica Data Validation",
            evaluator="李四",
            evaluation_date="2024-01-15",
            scores={
                "functionality": 4.8,
                "performance": 4.5,
                "usability": 4.5,
                "integration": 4.2,
                "cost": 2.5,
                "vendor_support": 4.5,
                "security": 4.5
            },
            total_score=4.2,
            recommendation="推荐",
            strengths=["企业级功能", "专业支持", "用户界面友好"],
            weaknesses=["成本较高", "定制化复杂"],
            risks=["供应商锁定", "许可费用上涨"]
        )
    ]

    for result in sample_results:
        generator.add_evaluation_result(result)

    # Generate reports
    generator.generate_comparison_report("examples/17_tools/evaluation_reports")

    print("评估报告生成完成！")

if __name__ == "__main__":
    main()