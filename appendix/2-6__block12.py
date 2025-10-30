# 实时数据质量监控系统示例
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from collections import deque

class RealTimeDataQualityMonitor:
    """实时数据质量监控系统"""
    
    def __init__(self, config):
        """初始化监控系统
        
        参数:
        config: 监控配置，包含阈值、告警规则等
        """
        self.config = config
        self.metrics_history = {}
        self.alerts = []
        self.anomalies = []
        self.initialize_metrics_history()
        print("实时数据质量监控系统已初始化")
    
    def initialize_metrics_history(self):
        """初始化指标历史记录"""
        for metric in self.config.get('metrics', {}):
            self.metrics_history[metric] = deque(maxlen=self.config.get('history_size', 100))
    
    def process_data_stream(self, data_batch):
        """处理数据流批次，执行质量检查"""
        timestamp = datetime.now()
        metrics = self.calculate_metrics(data_batch)
        self.update_metrics_history(metrics, timestamp)
        
        # 执行监控检查
        alerts = []
        alerts.extend(self.check_thresholds(metrics, timestamp))
        alerts.extend(self.check_trends(metrics, timestamp))
        alerts.extend(self.detect_anomalies(data_batch, timestamp))
        
        # 记录告警
        if alerts:
            self.alerts.extend(alerts)
            self.trigger_alerts(alerts)
        
        return {
            'timestamp': timestamp,
            'metrics': metrics,
            'alerts_count': len(alerts)
        }
    
    def calculate_metrics(self, data_batch):
        """计算数据质量指标"""
        metrics = {}
        
        # 计算完整性指标
        total_cells = len(data_batch) * len(data_batch.columns)
        missing_cells = data_batch.isnull().sum().sum()
        metrics['completeness'] = 100.0 - (missing_cells / total_cells * 100)
        
        # 计算每列的缺失率
        for col in data_batch.columns:
            metrics[f'{col}_missing_rate'] = data_batch[col].isnull().mean() * 100
        
        # 计算唯一性指标（针对主键）
        if 'primary_key' in self.config:
            pk_col = self.config['primary_key']
            if pk_col in data_batch.columns:
                metrics['uniqueness'] = (data_batch[pk_col].nunique() / len(data_batch)) * 100
        
        # 计算准确性指标（如果有验证规则）
        if 'validation_rules' in self.config:
            validations = 0
            total_checks = 0
            for col, rules in self.config['validation_rules'].items():
                if col in data_batch.columns:
                    if 'range' in rules:
                        min_val, max_val = rules['range']
                        validations += ((data_batch[col] >= min_val) & (data_batch[col] <= max_val)).sum()
                        total_checks += len(data_batch)
                    if 'pattern' in rules:
                        # 简化的模式检查，实际应用中可使用正则表达式
                        pass
            if total_checks > 0:
                metrics['accuracy'] = (validations / total_checks) * 100
        
        return metrics
    
    def update_metrics_history(self, metrics, timestamp):
        """更新指标历史记录"""
        for metric, value in metrics.items():
            if metric in self.metrics_history:
                self.metrics_history[metric].append((timestamp, value))
    
    def check_thresholds(self, metrics, timestamp):
        """检查阈值告警"""
        alerts = []
        thresholds = self.config.get('thresholds', {})
        
        for metric, value in metrics.items():
            if metric in thresholds:
                threshold = thresholds[metric]
                if isinstance(threshold, dict):
                    # 支持多级阈值
                    if 'critical' in threshold and value < threshold['critical']:
                        alerts.append({
                            'timestamp': timestamp,
                            'metric': metric,
                            'value': value,
                            'threshold': threshold['critical'],
                            'severity': 'critical',
                            'message': f"关键告警: {metric} = {value:.2f}, 低于临界阈值 {threshold['critical']}"
                        })
                    elif 'warning' in threshold and value < threshold['warning']:
                        alerts.append({
                            'timestamp': timestamp,
                            'metric': metric,
                            'value': value,
                            'threshold': threshold['warning'],
                            'severity': 'warning',
                            'message': f"警告: {metric} = {value:.2f}, 低于警告阈值 {threshold['warning']}"
                        })
                else:
                    # 单一阈值
                    if value < threshold:
                        alerts.append({
                            'timestamp': timestamp,
                            'metric': metric,
                            'value': value,
                            'threshold': threshold,
                            'severity': 'warning',
                            'message': f"警告: {metric} = {value:.2f}, 低于阈值 {threshold}"
                        })
        
        return alerts
    
    def check_trends(self, metrics, timestamp):
        """检查趋势告警"""
        alerts = []
        
        # 检查是否有足够的历史数据
        for metric, history in self.metrics_history.items():
            if len(history) >= 5 and metric in metrics:
                # 计算最近5个点的趋势
                values = [h[1] for h in history[-5:]]
                recent_value = metrics[metric]
                
                # 简单趋势检测：检查是否连续下降
                if len(values) >= 3:
                    if all(values[i] > values[i+1] for i in range(len(values)-1)) and recent_value < values[-1]:
                        alerts.append({
                            'timestamp': timestamp,
                            'metric': metric,
                            'value': recent_value,
                            'severity': 'warning',
                            'message': f"趋势告警: {metric} 连续下降，当前值 {recent_value:.2f}"
                        })
        
        return alerts
    
    def detect_anomalies(self, data_batch, timestamp):
        """检测数据异常"""
        anomalies = []
        anomaly_config = self.config.get('anomaly_detection', {})
        
        # 对配置的列执行异常检测
        for col, config in anomaly_config.items():
            if col in data_batch.columns and data_batch[col].dtype in ['int64', 'float64']:
                method = config.get('method', 'zscore')
                threshold = config.get('threshold', 3.0)
                
                if method == 'zscore':
                    # Z-score异常检测
                    mean_val = data_batch[col].mean()
                    std_val = data_batch[col].std()
                    if std_val > 0:  # 避免除以零
                        z_scores = np.abs((data_batch[col] - mean_val) / std_val)
                        outliers = data_batch[z_scores > threshold]
                        
                        for idx, row in outliers.iterrows():
                            anomaly_info = {
                                'timestamp': timestamp,
                                'column': col,
                                'value': row[col],
                                'anomaly_type': 'zscore',
                                'severity': 'warning',
                                'message': f"异常值: {col} = {row[col]} (Z-score: {z_scores[idx]:.2f})
                            }
                            anomalies.append(anomaly_info)
                            self.anomalies.append(anomaly_info)
        
        return anomalies
    
    def trigger_alerts(self, alerts):
        """触发告警通知"""
        # 在实际应用中，这里会调用告警系统发送邮件、短信等
        for alert in alerts:
            print(f"[{alert['severity'].upper()}] {alert['timestamp']} - {alert['message']}")
    
    def generate_dashboard_data(self):
        """生成仪表盘数据"""
        dashboard = {}
        
        # 整理最新的指标数据
        dashboard['latest_metrics'] = {}
        dashboard['metric_trends'] = {}
        
        for metric, history in self.metrics_history.items():
            if history:
                # 最新指标值
                latest_timestamp, latest_value = history[-1]
                dashboard['latest_metrics'][metric] = {
                    'timestamp': latest_timestamp,
                    'value': latest_value
                }
                
                # 指标趋势数据
                dashboard['metric_trends'][metric] = {
                    'timestamps': [h[0] for h in history],
                    'values': [h[1] for h in history]
                }
        
        # 最近的告警
        dashboard['recent_alerts'] = sorted(self.alerts[-20:], key=lambda x: x['timestamp'], reverse=True)
        
        return dashboard

# 使用示例
def real_time_monitor_example():
    # 定义监控配置
    config = {
        'metrics': ['completeness', 'accuracy', 'uniqueness'],
        'history_size': 100,
        'primary_key': 'transaction_id',
        'thresholds': {
            'completeness': {'warning': 95.0, 'critical': 90.0},
            'accuracy': {'warning': 98.0, 'critical': 95.0},
            'uniqueness': {'warning': 99.0, 'critical': 98.0}
        },
        'validation_rules': {
            'amount': {'range': (0, 1000000)},
            'quantity': {'range': (1, 1000)}
        },
        'anomaly_detection': {
            'amount': {'method': 'zscore', 'threshold': 3.0},
            'processing_time': {'method': 'zscore', 'threshold': 2.5}
        }
    }
    
    # 初始化监控系统
    monitor = RealTimeDataQualityMonitor(config)
    
    print("开始模拟实时数据流监控...")
    
    # 模拟数据流
    for batch_id in range(10):
        # 生成模拟数据
        np.random.seed(batch_id)  # 确保可重复性
        
        # 正常数据
        data = {
            'transaction_id': range(1000),
            'amount': np.random.normal(1000, 500, 1000),
            'quantity': np.random.randint(1, 10, 1000),
            'customer_id': np.random.randint(10000, 99999, 1000),
            'timestamp': [datetime.now() - timedelta(minutes=i) for i in range(1000)],
            'processing_time': np.random.normal(0.5, 0.1, 1000)
        }
        
        # 人为引入一些异常
        if batch_id == 3:  # 完整性问题
            data['amount'][100:200] = np.nan
        elif batch_id == 5:  # 准确性问题
            data['amount'][50:150] = np.random.normal(20000, 5000, 100)
        elif batch_id == 7:  # 唯一性问题
            data['transaction_id'][200:250] = range(50)  # 重复ID
        
        df = pd.DataFrame(data)
        
        # 处理数据批次
        result = monitor.process_data_stream(df)
        print(f"批次 {batch_id+1} 处理完成: 完整性={result['metrics']['completeness']:.2f}%, "
              f"告警数={result['alerts_count']}")
        
        # 模拟实时延迟
        time.sleep(1)
    
    # 生成仪表盘数据
    dashboard = monitor.generate_dashboard_data()
    print(f"\n监控完成。共检测到 {len(monitor.alerts)} 个告警，{len(monitor.anomalies)} 个异常值")
    print("仪表盘数据已准备就绪")

# 运行实时监控示例
real_time_monitor_example()
