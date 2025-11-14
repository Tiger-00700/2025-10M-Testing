# 测试报告生成器示例
import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

class TestReportGenerator:
    def __init__(self, config):
        self.config = config
        self.report_dir = config.get('report_directory', './reports')
        # 确保报告目录存在
        import os
        os.makedirs(self.report_dir, exist_ok=True)

    def generate_report(self, test_results):
        """生成测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_id = f"test_report_{timestamp}"

        # 生成摘要信息
        summary = self._generate_summary(test_results)

        # 生成详细报告
        detailed_report = self._generate_detailed_report(test_results)

        # 生成图表
        charts = self._generate_charts(test_results, report_id)

        # 生成HTML报告
        html_report = self._generate_html_report(summary, detailed_report, charts, report_id)

        # 保存JSON格式报告
        report_data = {
            'report_id': report_id,
            'timestamp': timestamp,
            'summary': summary,
            'detailed_results': detailed_report,
            'charts': charts
        }

        json_report_path = os.path.join(self.report_dir, f"{report_id}.json")
        with open(json_report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        # 保存HTML报告
        html_report_path = os.path.join(self.report_dir, f"{report_id}.html")
        with open(html_report_path, 'w') as f:
            f.write(html_report)

        # 更新历史报告索引
        self._update_history(report_data)

        return {
            'report_id': report_id,
            'json_report': json_report_path,
            'html_report': html_report_path,
            'summary': summary
        }

    def _generate_summary(self, test_results):
        """生成测试摘要"""
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r['status'] == 'passed')
        failed_tests = sum(1 for r in test_results if r['status'] == 'failed')
        skipped_tests = sum(1 for r in test_results if r['status'] == 'skipped')

        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        # 计算执行时间
        total_duration = sum(r.get('duration', 0) for r in test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0

        # 按类型统计
        type_stats = {}
        for result in test_results:
            test_type = result.get('type', 'unknown')
            if test_type not in type_stats:
                type_stats[test_type] = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}

            type_stats[test_type]['total'] += 1
            if result['status'] == 'passed':
                type_stats[test_type]['passed'] += 1
            elif result['status'] == 'failed':
                type_stats[test_type]['failed'] += 1
            elif result['status'] == 'skipped':
                type_stats[test_type]['skipped'] += 1

        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'pass_rate': pass_rate,
            'total_duration': total_duration,
            'average_duration': avg_duration,
            'type_statistics': type_stats
        }

    def _generate_detailed_report(self, test_results):
        """生成详细报告"""
        # 按状态和类型组织结果
        organized_results = {
            'passed': [],
            'failed': [],
            'skipped': []
        }

        for result in test_results:
            status = result['status']
            if status in organized_results:
                organized_results[status].append(result)

        return organized_results

    def _generate_charts(self, test_results, report_id):
        """生成可视化图表"""
        charts = []

        # 生成饼图：测试结果分布
        plt.figure(figsize=(8, 6))
        labels = ['Passed', 'Failed', 'Skipped']
        summary = self._generate_summary(test_results)
        sizes = [summary['passed_tests'], summary['failed_tests'], summary['skipped_tests']]
        colors = ['#4CAF50', '#F44336', '#FFC107']

        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        plt.axis('equal')  # 保证饼图为圆形
        plt.title('Test Results Distribution')

        pie_chart_path = os.path.join(self.report_dir, f"{report_id}_pie_chart.png")
        plt.savefig(pie_chart_path)
        plt.close()

        charts.append({
            'type': 'pie_chart',
            'title': 'Test Results Distribution',
            'path': pie_chart_path
        })

        # 生成柱状图：按类型的测试结果
        plt.figure(figsize=(10, 6))

        types = list(summary['type_statistics'].keys())
        passed_counts = [summary['type_statistics'][t]['passed'] for t in types]
        failed_counts = [summary['type_statistics'][t]['failed'] for t in types]

        x = range(len(types))
        width = 0.35

        plt.bar([i - width/2 for i in x], passed_counts, width, label='Passed', color='#4CAF50')
        plt.bar([i + width/2 for i in x], failed_counts, width, label='Failed', color='#F44336')

        plt.xlabel('Test Type')
        plt.ylabel('Count')
        plt.title('Test Results by Type')
        plt.xticks(x, types)
        plt.legend()

        bar_chart_path = os.path.join(self.report_dir, f"{report_id}_bar_chart.png")
        plt.savefig(bar_chart_path)
        plt.close()

        charts.append({
            'type': 'bar_chart',
            'title': 'Test Results by Type',
            'path': bar_chart_path
        })

        return charts

    def _generate_html_report(self, summary, detailed_report, charts, report_id):
        """生成HTML格式报告"""
        # HTML模板
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Big Data Test Report - {report_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #333; }}
                .summary {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-box {{ text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px; flex: 1; margin: 0 10px; }}
                .passed {{ background-color: #e8f5e9; border-color: #4CAF50; }}
                .failed {{ background-color: #ffebee; border-color: #F44336; }}
                .skipped {{ background-color: #fff8e1; border-color: #FFC107; }}
                .charts {{ display: flex; flex-wrap: wrap; margin: 20px 0; }}
                .chart {{ flex: 1; min-width: 400px; margin: 10px; text-align: center; }}
                .chart img {{ max-width: 100%; height: auto; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .error-message {{ color: #F44336; font-family: monospace; }}
            </style>
        </head>
        <body>
            <h1>Big Data Test Report</h1>
            <p>Report ID: {report_id}</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <div class="summary">
                <h2>Summary</h2>
                <div class="stats">
                    <div class="stat-box">
                        <h3>Total Tests</h3>
                        <p style="font-size: 24px;">{summary['total_tests']}</p>
                    </div>
                    <div class="stat-box passed">
                        <h3>Passed</h3>
                        <p style="font-size: 24px;">{summary['passed_tests']}</p>
                    </div>
                    <div class="stat-box failed">
                        <h3>Failed</h3>
                        <p style="font-size: 24px;">{summary['failed_tests']}</p>
                    </div>
                    <div class="stat-box skipped">
                        <h3>Skipped</h3>
                        <p style="font-size: 24px;">{summary['skipped_tests']}</p>
                    </div>
                </div>
                <p>Pass Rate: {summary['pass_rate']:.2f}%</p>
                <p>Total Duration: {summary['total_duration']:.2f} seconds</p>
                <p>Average Duration: {summary['average_duration']:.2f} seconds per test</p>
            </div>

            <div class="charts">
                <h2>Visualizations</h2>
                {self._generate_chart_html(charts)}
            </div>

            <div class="detailed-results">
                <h2>Detailed Results</h2>

                <h3>Failed Tests</h3>
                {self._generate_test_table(detailed_report['failed'])}

                <h3>Passed Tests</h3>
                {self._generate_test_table(detailed_report['passed'])}

                <h3>Skipped Tests</h3>
                {self._generate_test_table(detailed_report['skipped'])}
            </div>
        </body>
        </html>
        """

        return html_template

    def _generate_chart_html(self, charts):
        """生成图表HTML部分"""
        chart_html = ""
        for chart in charts:
            chart_html += f"""
            <div class="chart">
                <h3>{chart['title']}</h3>
                <img src="{os.path.basename(chart['path'])}" alt="{chart['title']}">
            </div>
            """
        return chart_html

    def _generate_test_table(self, test_results):
        """生成测试结果表格HTML"""
        if not test_results:
            return "<p>No tests to display.</p>"

        table_html = """
        <table>
            <tr>
                <th>Test Name</th>
                <th>Type</th>
                <th>Duration (s)</th>
                <th>Status</th>
                <th>Message</th>
            </tr>
        """

        for result in test_results:
            message = result.get('message', '')
            message_html = f"<div class='error-message'>{message}</div>" if result['status'] == 'failed' else message

            table_html += f"""
            <tr>
                <td>{result.get('name', 'Unknown')}</td>
                <td>{result.get('type', 'Unknown')}</td>
                <td>{result.get('duration', 'N/A')}</td>
                <td>{result['status']}</td>
                <td>{message_html}</td>
            </tr>
            """

        table_html += "</table>"
        return table_html

    def _update_history(self, report_data):
        """更新历史报告索引"""
        history_file = os.path.join(self.report_dir, "report_history.json")

        try:
            # 读取现有历史
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []

            # 添加新报告
            history.append({
                'report_id': report_data['report_id'],
                'timestamp': report_data['timestamp'],
                'summary': report_data['summary']
            })

            # 只保留最近的100个报告
            if len(history) > 100:
                history = history[-100:]

            # 保存更新后的历史
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error updating report history: {e}")

# 使用示例 （来自：第5篇-第17章-大数据测试自动化【进阶】）
def generate_test_report():
    # 模拟测试结果数据
    test_results = [
        {'name': 'test_hdfs_read_write', 'type': 'hadoop', 'status': 'passed', 'duration': 2.3},
        {'name': 'test_mapreduce_wordcount', 'type': 'hadoop', 'status': 'passed', 'duration': 15.6},
        {'name': 'test_spark_sql', 'type': 'spark', 'status': 'failed', 'duration': 8.9, 'message': 'Query execution failed: Table not found'},
        {'name': 'test_spark_streaming', 'type': 'spark', 'status': 'passed', 'duration': 12.3},
        {'name': 'test_cassandra_read', 'type': 'nosql', 'status': 'passed', 'duration': 3.1},
        {'name': 'test_cassandra_write', 'type': 'nosql', 'status': 'skipped', 'duration': 0, 'message': 'Skipped due to environment issue'},
        {'name': 'test_kafka_produce_consume', 'type': 'streaming', 'status': 'passed', 'duration': 5.7}
    ]

    # 生成报告
    config = {'report_directory': './reports'}
    generator = TestReportGenerator(config)
    report = generator.generate_report(test_results)

    print(f"Report generated: {report['html_report']}")
    print(f"Summary: {report['summary']}")

    return report
