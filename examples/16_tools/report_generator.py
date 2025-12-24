# Report Generation Module
# Generates comprehensive test reports with visualization

import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from jinja2 import Template
import pdfkit
from pathlib import Path

@dataclass
class TestExecutionSummary:
    """Test execution summary"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    success_rate: float
    total_duration: float
    avg_duration: float

@dataclass
class QualityMetrics:
    """Quality metrics"""
    completeness_score: float
    accuracy_score: float
    timeliness_score: float
    consistency_score: float
    overall_score: float

@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    response_time_p50: float
    response_time_p95: float
    response_time_p99: float
    throughput: float
    error_rate: float

class ReportGenerator:
    """Comprehensive test report generator"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.templates_dir = Path(config.get('templates_dir', 'templates'))
        self.output_dir = Path(config.get('output_dir', 'reports'))

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Set up plotting style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)

    def generate_comprehensive_report(self,
                                   execution_results: List[Dict[str, Any]],
                                   quality_metrics: Optional[QualityMetrics] = None,
                                   performance_metrics: Optional[PerformanceMetrics] = None,
                                   historical_data: Optional[List[Dict[str, Any]]] = None) -> str:
        """Generate comprehensive test report"""

        # Calculate summary
        summary = self._calculate_summary(execution_results)

        # Prepare report data
        report_data = {
            'summary': asdict(summary),
            'execution_results': execution_results,
            'quality_metrics': asdict(quality_metrics) if quality_metrics else None,
            'performance_metrics': asdict(performance_metrics) if performance_metrics else None,
            'historical_trends': historical_data,
            'generated_at': datetime.now().isoformat(),
            'report_config': self.config
        }

        # Generate different report formats
        report_files = {}

        if 'html' in self.config.get('formats', ['html']):
            report_files['html'] = self._generate_html_report(report_data)

        if 'pdf' in self.config.get('formats', []):
            report_files['pdf'] = self._generate_pdf_report(report_data)

        if 'json' in self.config.get('formats', []):
            report_files['json'] = self._generate_json_report(report_data)

        # Generate charts
        self._generate_charts(report_data)

        return str(self.output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    def _calculate_summary(self, results: List[Dict[str, Any]]) -> TestExecutionSummary:
        """Calculate execution summary"""
        total_tests = len(results)
        passed_tests = len([r for r in results if r.get('status') == 'PASSED'])
        failed_tests = len([r for r in results if r.get('status') == 'FAILED'])
        skipped_tests = len([r for r in results if r.get('status') == 'SKIPPED'])

        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        total_duration = sum(r.get('duration', 0) for r in results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0

        return TestExecutionSummary(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            success_rate=success_rate,
            total_duration=total_duration,
            avg_duration=avg_duration
        )

    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report"""
        template_path = self.templates_dir / 'report_template.html'

        if not template_path.exists():
            # Create default template
            self._create_default_html_template()

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        template = Template(template_content)
        html_content = template.render(**report_data)

        output_file = self.output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def _generate_pdf_report(self, report_data: Dict[str, Any]) -> str:
        """Generate PDF report"""
        html_file = self._generate_html_report(report_data)

        pdf_file = html_file.replace('.html', '.pdf')
        pdfkit.from_file(html_file, pdf_file)

        return pdf_file

    def _generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """Generate JSON report"""
        output_file = self.output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        return str(output_file)

    def _generate_charts(self, report_data: Dict[str, Any]):
        """Generate visualization charts"""
        charts_dir = self.output_dir / 'charts'
        charts_dir.mkdir(exist_ok=True)

        # Test status distribution pie chart
        self._generate_status_pie_chart(report_data['execution_results'], charts_dir)

        # Execution time histogram
        self._generate_execution_time_histogram(report_data['execution_results'], charts_dir)

        # Success rate trend (if historical data available)
        if report_data.get('historical_trends'):
            self._generate_success_rate_trend(report_data['historical_trends'], charts_dir)

        # Quality metrics radar chart
        if report_data.get('quality_metrics'):
            self._generate_quality_radar_chart(report_data['quality_metrics'], charts_dir)

    def _generate_status_pie_chart(self, results: List[Dict[str, Any]], output_dir: Path):
        """Generate test status distribution pie chart"""
        status_counts = {}
        for result in results:
            status = result.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1

        plt.figure()
        plt.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%')
        plt.title('Test Status Distribution')
        plt.savefig(output_dir / 'status_distribution.png')
        plt.close()

    def _generate_execution_time_histogram(self, results: List[Dict[str, Any]], output_dir: Path):
        """Generate execution time histogram"""
        durations = [r.get('duration', 0) for r in results]

        plt.figure()
        plt.hist(durations, bins=20, edgecolor='black')
        plt.xlabel('Execution Time (seconds)')
        plt.ylabel('Frequency')
        plt.title('Test Execution Time Distribution')
        plt.savefig(output_dir / 'execution_time_histogram.png')
        plt.close()

    def _generate_success_rate_trend(self, historical_data: List[Dict[str, Any]], output_dir: Path):
        """Generate success rate trend chart"""
        dates = [d['date'] for d in historical_data]
        rates = [d['success_rate'] for d in historical_data]

        plt.figure()
        plt.plot(dates, rates, marker='o')
        plt.xlabel('Date')
        plt.ylabel('Success Rate')
        plt.title('Success Rate Trend')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / 'success_rate_trend.png')
        plt.close()

    def _generate_quality_radar_chart(self, quality_metrics: Dict[str, Any], output_dir: Path):
        """Generate quality metrics radar chart"""
        categories = ['Completeness', 'Accuracy', 'Timeliness', 'Consistency']
        values = [
            quality_metrics.get('completeness_score', 0),
            quality_metrics.get('accuracy_score', 0),
            quality_metrics.get('timeliness_score', 0),
            quality_metrics.get('consistency_score', 0)
        ]

        # Close the polygon
        values += values[:1]
        categories += categories[:1]

        angles = [n / float(len(categories[:-1])) * 2 * 3.14159 for n in range(len(categories[:-1]))]
        angles += angles[:1]

        plt.figure()
        ax = plt.subplot(111, polar=True)
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.3)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories[:-1])
        ax.set_title('Quality Metrics Radar Chart')
        plt.savefig(output_dir / 'quality_radar.png')
        plt.close()

    def _create_default_html_template(self):
        """Create default HTML report template"""
        template_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .metric { display: inline-block; margin: 10px; text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; color: #2e7d32; }
        .metric-label { font-size: 14px; color: #666; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .passed { color: #2e7d32; }
        .failed { color: #d32f2f; }
        .chart { margin: 20px 0; text-align: center; }
    </style>
</head>
<body>
    <h1>大数据测试自动化框架 - 测试报告</h1>

    <div class="summary">
        <h2>执行摘要</h2>
        <div class="metric">
            <div class="metric-value">{{ summary.total_tests }}</div>
            <div class="metric-label">总测试数</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ summary.passed_tests }}</div>
            <div class="metric-label">通过测试</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ summary.failed_tests }}</div>
            <div class="metric-label">失败测试</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ "%.1f"|format(summary.success_rate * 100) }}%</div>
            <div class="metric-label">成功率</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ "%.1f"|format(summary.total_duration) }}s</div>
            <div class="metric-label">总耗时</div>
        </div>
    </div>

    {% if quality_metrics %}
    <h2>质量指标</h2>
    <div class="chart">
        <img src="charts/quality_radar.png" alt="Quality Metrics" />
    </div>
    {% endif %}

    <h2>测试结果详情</h2>
    <table>
        <tr>
            <th>测试ID</th>
            <th>状态</th>
            <th>耗时(s)</th>
            <th>错误信息</th>
        </tr>
        {% for result in execution_results %}
        <tr>
            <td>{{ result.test_id }}</td>
            <td class="{{ 'passed' if result.status == 'PASSED' else 'failed' }}">{{ result.status }}</td>
            <td>{{ "%.2f"|format(result.duration) }}</td>
            <td>{{ result.error_message or '-' }}</td>
        </tr>
        {% endfor %}
    </table>

    <div class="chart">
        <img src="charts/status_distribution.png" alt="Status Distribution" />
    </div>

    <div class="chart">
        <img src="charts/execution_time_histogram.png" alt="Execution Time Distribution" />
    </div>

    {% if historical_trends %}
    <div class="chart">
        <img src="charts/success_rate_trend.png" alt="Success Rate Trend" />
    </div>
    {% endif %}

    <p><small>报告生成时间: {{ generated_at }}</small></p>
</body>
</html>
        """

        template_file = self.templates_dir / 'report_template.html'
        self.templates_dir.mkdir(exist_ok=True)

        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)

# Example usage
if __name__ == "__main__":
    config = {
        'templates_dir': 'templates',
        'output_dir': 'reports',
        'formats': ['html', 'json']
    }

    generator = ReportGenerator(config)

    # Mock test results
    mock_results = [
        {'test_id': 'test_001', 'status': 'PASSED', 'duration': 2.5, 'error_message': None},
        {'test_id': 'test_002', 'status': 'FAILED', 'duration': 1.8, 'error_message': 'Assertion failed'},
        {'test_id': 'test_003', 'status': 'PASSED', 'duration': 3.2, 'error_message': None},
    ]

    quality_metrics = QualityMetrics(
        completeness_score=0.98,
        accuracy_score=0.95,
        timeliness_score=0.92,
        consistency_score=0.96,
        overall_score=0.95
    )

    report_path = generator.generate_comprehensive_report(
        execution_results=mock_results,
        quality_metrics=quality_metrics
    )

    print(f"Report generated at: {report_path}")