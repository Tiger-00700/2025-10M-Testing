# 报告生成器示例
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os

class TestReportGenerator:
    
    def __init__(self, output_dir='reports'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(self, test_results, suite_name='TestSuite'):
        """生成测试报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"{self.output_dir}/report_{suite_name}_{timestamp}.html"
        
        # 计算统计信息
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results.values() if r['status'] == 'success')
        failed_tests = sum(1 for r in test_results.values() if r['status'] in ['failed', 'error'])
        timeout_tests = sum(1 for r in test_results.values() if r['status'] == 'timeout')
        
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # 生成图表
        self._generate_charts(test_results, timestamp)
        
        # 生成HTML报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self._get_report_html(test_results, suite_name, timestamp, 
                                         total_tests, passed_tests, failed_tests, 
                                         timeout_tests, pass_rate))
        
        return report_file
    
    def _generate_charts(self, test_results, timestamp):
        """生成测试结果图表"""
        # 提取执行时间数据
        execution_times = [r.get('execution_time', 0) for r in test_results.values() if 'execution_time' in r]
        test_names = list(test_results.keys())
        
        # 创建执行时间柱状图
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(execution_times)), execution_times)
        plt.xlabel('测试用例')
        plt.ylabel('执行时间 (秒)')
        plt.title('测试用例执行时间')
        plt.xticks(range(len(test_names)), test_names, rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/execution_times_{timestamp}.png")
        plt.close()
    
    def _get_report_html(self, test_results, suite_name, timestamp, total, passed, failed, timeout, pass_rate):
        """生成HTML报告内容"""
        # 简化的HTML报告模板
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>测试报告 - {suite_name}</title>
            <style>body {{ font-family: Arial; margin: 20px; }} .summary {{ background: #f0f0f0; padding: 10px; }} .success {{ color: green; }} .failed {{ color: red; }} .timeout {{ color: orange; }}</style>
        </head>
        <body>
            <h1>测试报告 - {suite_name}</h1>
            <p>生成时间: {timestamp}</p>
            
            <div class="summary">
                <h2>测试摘要</h2>
                <p>总测试数: {total}</p>
                <p>通过: <span class="success">{passed}</span></p>
                <p>失败: <span class="failed">{failed}</span></p>
                <p>超时: <span class="timeout">{timeout}</span></p>
                <p>通过率: {pass_rate:.2f}%</p>
            </div>
            
            <h2>详细结果</h2>
            <table border="1" width="100%">
                <tr><th>测试用例</th><th>状态</th><th>执行时间</th><th>详情</th></tr>
        """
        
        # 添加详细结果
        for test_name, result in test_results.items():
            status = result['status']
            time_info = f"{result.get('execution_time', 'N/A')}秒" if 'execution_time' in result else 'N/A'
            details = result.get('result', '') if status == 'success' else result.get('error', '')
            status_class = 'success' if status == 'success' else 'failed' if status in ['failed', 'error'] else 'timeout'
            
            html += f"""
            <tr>
                <td>{test_name}</td>
                <td class="{status_class}">{status}</td>
                <td>{time_info}</td>
                <td>{details}</td>
            </tr>
            """
        
        html += """
            </table>
            
            <h2>图表分析</h2>
            <img src="execution_times_{timestamp}.png" alt="执行时间图表">
        </body>
        </html>
        """
        
        return html
