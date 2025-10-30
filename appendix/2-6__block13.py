# 数据质量指标体系和阈值管理示例
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

class DataQualityMetricsSystem:
    """数据质量指标体系和阈值管理系统"""
    
    def __init__(self):
        self.metrics_definitions = {}
        self.metrics_weights = {}
        self.thresholds = {}
        self.baseline_metrics = {}
        self.sla_definitions = {}
        self.history_data = {}
    
    def define_metric(self, metric_name, description, calculation_func, data_type='numeric'):
        """定义质量指标
        
        参数:
        metric_name: 指标名称
        description: 指标描述
        calculation_func: 计算函数，接收数据并返回指标值
        data_type: 数据类型
        """
        self.metrics_definitions[metric_name] = {
            'description': description,
            'calculation_func': calculation_func,
            'data_type': data_type
        }
        print(f"已定义指标: {metric_name} - {description}")
    
    def set_metric_weight(self, metric_name, weight):
        """设置指标权重
        
        参数:
        metric_name: 指标名称
        weight: 权重值，应为0-1之间的小数，所有指标权重之和应为1
        """
        if metric_name in self.metrics_definitions:
            self.metrics_weights[metric_name] = weight
            print(f"已设置指标 {metric_name} 的权重: {weight}")
        else:
            print(f"警告: 指标 {metric_name} 未定义")
    
    def set_thresholds(self, metric_name, thresholds):
        """设置告警阈值
        
        参数:
        metric_name: 指标名称
        thresholds: 阈值配置，可以是单一值或包含warning和critical的字典
        """
        if metric_name in self.metrics_definitions:
            self.thresholds[metric_name] = thresholds
            print(f"已设置指标 {metric_name} 的阈值: {thresholds}")
        else:
            print(f"警告: 指标 {metric_name} 未定义")
    
    def calculate_metrics(self, data, context=None):
        """计算所有定义的指标
        
        参数:
        data: 要评估的数据
        context: 上下文信息（可选）
        
        返回:
        包含所有指标值的字典
        """
        results = {}
        
        for metric_name, definition in self.metrics_definitions.items():
            try:
                value = definition['calculation_func'](data, context)
                results[metric_name] = value
            except Exception as e:
                print(f"计算指标 {metric_name} 时出错: {str(e)}")
                results[metric_name] = None
        
        # 计算综合质量得分
        if self.metrics_weights:
            weighted_score = 0
            weight_sum = 0
            for metric, weight in self.metrics_weights.items():
                if metric in results and results[metric] is not None:
                    weighted_score += results[metric] * weight
                    weight_sum += weight
            
            if weight_sum > 0:
                results['overall_score'] = weighted_score / weight_sum
        
        return results
    
    def update_baseline(self, metric_name, baseline_value):
        """更新指标基准值
        
        参数:
        metric_name: 指标名称
        baseline_value: 基准值
        """
        if metric_name in self.metrics_definitions:
            self.baseline_metrics[metric_name] = baseline_value
            print(f"已更新指标 {metric_name} 的基准值: {baseline_value}")
        else:
            print(f"警告: 指标 {metric_name} 未定义")
    
    def define_sla(self, data_domain, metrics, targets, response_times):
        """定义服务水平协议
        
        参数:
        data_domain: 数据域
        metrics: 指标列表
        targets: 目标值字典 {metric: target}
        response_times: 响应时间字典 {severity: time_in_hours}
        """
        self.sla_definitions[data_domain] = {
            'metrics': metrics,
            'targets': targets,
            'response_times': response_times
        }
        print(f"已定义数据域 {data_domain} 的SLA")
    
    def calculate_dynamic_thresholds(self, metric_name, history_data, sensitivity=0.9):
        """计算动态阈值
        
        参数:
        metric_name: 指标名称
        history_data: 历史数据列表
        sensitivity: 灵敏度参数，值越大阈值越宽松
        
        返回:
        计算得到的动态阈值
        """
        if not history_data:
            return None
        
        # 使用历史数据的统计特性计算阈值
        mean_val = np.mean(history_data)
        std_val = np.std(history_data)
        
        # 计算动态阈值（考虑数据的分布特性）
        # 对于完整性、准确性等越高越好的指标，阈值应略低于平均值
        # 这里使用可调的灵敏度参数来控制阈值的严格程度
        threshold = mean_val - (sensitivity * std_val)
        
        return threshold
    
    def evaluate_against_thresholds(self, metrics_results):
        """评估指标结果是否超过阈值
        
        参数:
        metrics_results: 指标计算结果
        
        返回:
        告警列表
        """
        alerts = []
        
        for metric_name, value in metrics_results.items():
            if metric_name in self.thresholds and value is not None:
                thresholds = self.thresholds[metric_name]
                
                if isinstance(thresholds, dict):
                    # 多级阈值
                    if 'critical' in thresholds and value < thresholds['critical']:
                        alerts.append({
                            'metric': metric_name,
                            'value': value,
                            'threshold': thresholds['critical'],
                            'severity': 'critical',
                            'message': f"关键告警: {metric_name} = {value:.2f} 低于临界阈值 {thresholds['critical']}"
                        })
                    elif 'warning' in thresholds and value < thresholds['warning']:
                        alerts.append({
                            'metric': metric_name,
                            'value': value,
                            'threshold': thresholds['warning'],
                            'severity': 'warning',
                            'message': f"警告: {metric_name} = {value:.2f} 低于警告阈值 {thresholds['warning']}"
                        })
                else:
                    # 单一阈值
                    if value < thresholds:
                        alerts.append({
                            'metric': metric_name,
                            'value': value,
                            'threshold': thresholds,
                            'severity': 'warning',
                            'message': f"警告: {metric_name} = {value:.2f} 低于阈值 {thresholds}"
                        })
        
        return alerts
    
    def compare_with_baseline(self, metrics_results):
        """与基准值进行比较
        
        参数:
        metrics_results: 指标计算结果
        
        返回:
        比较结果字典
        """
        comparisons = {}
        
        for metric_name, value in metrics_results.items():
            if metric_name in self.baseline_metrics and value is not None:
                baseline = self.baseline_metrics[metric_name]
                if baseline > 0:  # 避免除以零
                    change_percent = ((value - baseline) / baseline) * 100
                    comparisons[metric_name] = {
                        'current': value,
                        'baseline': baseline,
                        'change_percent': change_percent,
                        'status': 'improved' if change_percent > 0 else 'degraded' if change_percent < 0 else 'unchanged'
                    }
        
        return comparisons
    
    def generate_metrics_report(self, metrics_results, comparisons=None, alerts=None):
        """生成指标报告
        
        参数:
        metrics_results: 指标计算结果
        comparisons: 与基准的比较结果（可选）
        alerts: 告警列表（可选）
        
        返回:
        格式化的报告
        """
        report = {
            'report_time': datetime.now(),
            'metrics_summary': {},
            'comparison_summary': {},
            'alerts_summary': {},
            'overall_evaluation': ''
        }
        
        # 整理指标摘要
        for metric_name, value in metrics_results.items():
            if value is not None:
                report['metrics_summary'][metric_name] = {
                    'value': value,
                    'description': self.metrics_definitions.get(metric_name, {}).get('description', '')
                }
        
        # 整理比较摘要
        if comparisons:
            report['comparison_summary'] = comparisons
        
        # 整理告警摘要
        if alerts:
            report['alerts_summary'] = {
                'total_alerts': len(alerts),
                'critical_alerts': len([a for a in alerts if a['severity'] == 'critical']),
                'warning_alerts': len([a for a in alerts if a['severity'] == 'warning']),
                'alert_details': alerts
            }
        
        # 总体评估
        if 'overall_score' in metrics_results and metrics_results['overall_score'] is not None:
            score = metrics_results['overall_score']
            if score >= 95:
                evaluation = "优秀: 数据质量符合最高标准"
            elif score >= 90:
                evaluation = "良好: 数据质量基本符合要求"
            elif score >= 80:
                evaluation = "一般: 数据质量需要关注和改进"
            else:
                evaluation = "较差: 数据质量存在严重问题，需要立即处理"
            report['overall_evaluation'] = evaluation
        
        return report

# 示例：定义和使用数据质量指标体系
def data_quality_metrics_example():
    # 初始化指标系统
    metrics_system = DataQualityMetricsSystem()
    
    # 1. 定义数据质量指标
    metrics_system.define_metric(
        'completeness',
        '数据完整性百分比',
        lambda data, context: 100.0 - (data.isnull().sum().sum() / (len(data) * len(data.columns)) * 100)
    )
    
    metrics_system.define_metric(
        'accuracy',
        '数据准确性百分比',
        lambda data, context: {
            # 假设我们有验证规则
            'numeric_validation': 98.5,
            'format_validation': 99.2,
            'business_rule_validation': 97.8
        }[context.get('validation_type', 'numeric_validation')] if context else 98.0
    )
    
    metrics_system.define_metric(
        'consistency',
        '数据一致性百分比',
        lambda data, context: 99.0  # 简化示例
    )
    
    metrics_system.define_metric(
        'timeliness',
        '数据时效性评分',
        lambda data, context: 95.0  # 简化示例
    )
    
    metrics_system.define_metric(
        'uniqueness',
        '数据唯一性百分比',
        lambda data, context: (data[context.get('unique_key', 'id')].nunique() / len(data)) * 100 if context else 99.5
    )
    
    # 2. 设置指标权重
    metrics_system.set_metric_weight('completeness', 0.25)
    metrics_system.set_metric_weight('accuracy', 0.30)
    metrics_system.set_metric_weight('consistency', 0.20)
    metrics_system.set_metric_weight('timeliness', 0.15)
    metrics_system.set_metric_weight('uniqueness', 0.10)
    
    # 3. 设置阈值
    metrics_system.set_thresholds('completeness', {'warning': 95.0, 'critical': 90.0})
    metrics_system.set_thresholds('accuracy', {'warning': 97.0, 'critical': 95.0})
    metrics_system.set_thresholds('consistency', {'warning': 98.0, 'critical': 96.0})
    metrics_system.set_thresholds('timeliness', {'warning': 90.0, 'critical': 85.0})
    metrics_system.set_thresholds('uniqueness', {'warning': 99.0, 'critical': 98.0})
    
    # 4. 设置基准值
    metrics_system.update_baseline('completeness', 96.5)
    metrics_system.update_baseline('accuracy', 98.2)
    metrics_system.update_baseline('consistency', 98.8)
    metrics_system.update_baseline('timeliness', 94.5)
    metrics_system.update_baseline('uniqueness', 99.5)
    
    # 5. 定义SLA
    metrics_system.define_sla(
        'customer_data',
        ['completeness', 'accuracy', 'consistency', 'uniqueness'],
        {'completeness': 95.0, 'accuracy': 97.0, 'consistency': 98.0, 'uniqueness': 99.0},
        {'critical': 1, 'high': 4, 'medium': 24, 'low': 72}
    )
    
    # 6. 生成模拟数据
    np.random.seed(42)
    data = pd.DataFrame({
        'id': range(1000),
        'name': ['Customer ' + str(i) for i in range(1000)],
        'email': ['customer' + str(i) + '@example.com' for i in range(1000)],
        'phone': ['123-456-789' + str(i).zfill(2) for i in range(1000)],
        'address': ['Address ' + str(i) for i in range(1000)],
        'registration_date': [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(1000)],
        'last_purchase_date': [datetime.now() - timedelta(days=np.random.randint(0, 90)) for _ in range(1000)],
        'total_spend': np.random.normal(1000, 500, 1000)
    })
    
    # 人为引入一些质量问题
    # 添加缺失值
    data.loc[100:149, 'email'] = np.nan
    data.loc[200:229, 'phone'] = np.nan
    
    # 添加重复ID
    data.loc[500:510, 'id'] = range(50)
    
    # 7. 计算指标
    context = {'unique_key': 'id', 'validation_type': 'numeric_validation'}
    metrics_results = metrics_system.calculate_metrics(data, context)
    
    # 8. 评估阈值
    alerts = metrics_system.evaluate_against_thresholds(metrics_results)
    
    # 9. 与基准比较
    comparisons = metrics_system.compare_with_baseline(metrics_results)
    
    # 10. 生成报告
    report = metrics_system.generate_metrics_report(metrics_results, comparisons, alerts)
    
    # 输出报告摘要
    print("\n=== 数据质量指标报告 ===")
    print(f"报告时间: {report['report_time']}")
    print(f"总体评估: {report['overall_evaluation']}")
    print(f"\n指标摘要:")
    for metric, info in report['metrics_summary'].items():
        print(f"  {metric}: {info['value']:.2f} - {info['description']}")
    
    print(f"\n告警摘要:")
    print(f"  总告警数: {report['alerts_summary']['total_alerts']}")
    print(f"  严重告警: {report['alerts_summary']['critical_alerts']}")
    print(f"  警告告警: {report['alerts_summary']['warning_alerts']}")
    
    print(f"\n基准比较:")
    for metric, comparison in report['comparison_summary'].items():
        print(f"  {metric}: 当前 {comparison['current']:.2f}, 基准 {comparison['baseline']:.2f}, "
              f"变化 {comparison['change_percent']:+.2f}% ({comparison['status']})")

# 运行数据质量指标示例
data_quality_metrics_example()
