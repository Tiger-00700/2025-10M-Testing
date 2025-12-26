# 可观测性数据分析平台

## 概述

本文档详细介绍大数据测试系统的可观测性数据分析平台，包括数据采集与预处理、智能分析算法、可视化展示等核心组件。

## 数据采集与预处理

### 数据采集器设计

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
import time
import logging
from concurrent.futures import ThreadPoolExecutor
import queue

logger = logging.getLogger(__name__)

class DataCollector(ABC):
    """数据采集器基类"""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_running = False
        self.collection_interval = config.get('interval', 60)
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 5)

    @abstractmethod
    def collect_data(self) -> List[Dict[str, Any]]:
        """采集数据"""
        pass

    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """验证数据"""
        pass

    def start_collection(self):
        """开始数据采集"""
        self.is_running = True
        logger.info(f"Started data collection for {self.name}")

    def stop_collection(self):
        """停止数据采集"""
        self.is_running = False
        logger.info(f"Stopped data collection for {self.name}")

class MetricsCollector(DataCollector):
    """指标数据采集器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("metrics_collector", config)
        from prometheus_api_client import PrometheusConnect
        self.prometheus = PrometheusConnect(url=config.get('prometheus_url', 'http://localhost:9090'))
        self.metrics_queries = config.get('queries', [])

    def collect_data(self) -> List[Dict[str, Any]]:
        """采集指标数据"""
        data_points = []

        for query_config in self.metrics_queries:
            query_name = query_config['name']
            promql = query_config['query']
            labels = query_config.get('labels', {})

            try:
                result = self.prometheus.custom_query(query=promql)

                for item in result:
                    data_point = {
                        'timestamp': time.time(),
                        'metric_name': query_name,
                        'value': float(item['value'][1]),
                        'labels': {**item['metric'], **labels},
                        'source': 'prometheus',
                        'collector': self.name
                    }

                    if self.validate_data(data_point):
                        data_points.append(data_point)

            except Exception as e:
                logger.error(f"Error collecting metric {query_name}: {e}")

        return data_points

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """验证指标数据"""
        required_fields = ['timestamp', 'metric_name', 'value']
        return all(field in data for field in required_fields) and isinstance(data['value'], (int, float))

class LogCollector(DataCollector):
    """日志数据采集器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("log_collector", config)
        self.log_sources = config.get('sources', [])
        self.parsers = self._init_parsers()

    def _init_parsers(self) -> Dict[str, Callable]:
        """初始化日志解析器"""
        parsers = {}

        # JSON日志解析器
        def parse_json_log(line: str) -> Dict[str, Any]:
            import json
            try:
                return json.loads(line)
            except:
                return {'raw_log': line, 'parse_error': True}

        # Apache访问日志解析器
        def parse_apache_log(line: str) -> Dict[str, Any]:
            import re
            pattern = r'(\S+) - - \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\d+)'
            match = re.match(pattern, line)
            if match:
                return {
                    'ip': match.group(1),
                    'timestamp': match.group(2),
                    'method': match.group(3),
                    'url': match.group(4),
                    'protocol': match.group(5),
                    'status': int(match.group(6)),
                    'size': int(match.group(7))
                }
            return {'raw_log': line, 'parse_error': True}

        parsers['json'] = parse_json_log
        parsers['apache'] = parse_apache_log

        return parsers

    def collect_data(self) -> List[Dict[str, Any]]:
        """采集日志数据"""
        log_entries = []

        for source in self.log_sources:
            source_type = source.get('type', 'file')
            source_config = source.get('config', {})

            try:
                if source_type == 'file':
                    entries = self._collect_from_file(source_config)
                elif source_type == 'kafka':
                    entries = self._collect_from_kafka(source_config)
                elif source_type == 'syslog':
                    entries = self._collect_from_syslog(source_config)
                else:
                    logger.warning(f"Unsupported log source type: {source_type}")
                    continue

                log_entries.extend(entries)

            except Exception as e:
                logger.error(f"Error collecting logs from {source}: {e}")

        return log_entries

    def _collect_from_file(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从文件采集日志"""
        file_path = config['path']
        parser_type = config.get('parser', 'json')
        max_lines = config.get('max_lines', 1000)

        entries = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-max_lines:]  # 读取最后max_lines行

                for line in lines:
                    parsed = self.parsers.get(parser_type, lambda x: {'raw_log': x})(line.strip())
                    if parsed:
                        entry = {
                            'timestamp': time.time(),
                            'source': file_path,
                            'parser': parser_type,
                            'data': parsed,
                            'collector': self.name
                        }
                        entries.append(entry)

        except Exception as e:
            logger.error(f"Error reading log file {file_path}: {e}")

        return entries

    def _collect_from_kafka(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从Kafka采集日志"""
        # 简化实现，实际需要kafka-python库
        logger.warning("Kafka log collection not implemented in this example")
        return []

    def _collect_from_syslog(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从syslog采集日志"""
        # 简化实现
        logger.warning("Syslog collection not implemented in this example")
        return []

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """验证日志数据"""
        return 'timestamp' in data and 'data' in data

class TraceCollector(DataCollector):
    """链路追踪数据采集器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("trace_collector", config)
        self.jaeger_url = config.get('jaeger_url', 'http://localhost:16686')
        self.service_name = config.get('service_name')

    def collect_data(self) -> List[Dict[str, Any]]:
        """采集链路追踪数据"""
        # 简化实现，实际需要jaeger-client或opentelemetry库
        trace_data = []

        # 这里应该调用Jaeger API获取追踪数据
        # 示例数据结构
        sample_trace = {
            'timestamp': time.time(),
            'trace_id': 'abc123',
            'span_id': 'span456',
            'service_name': self.service_name or 'unknown',
            'operation': 'http_request',
            'duration_ms': 150.5,
            'tags': {'http.status_code': 200, 'http.method': 'GET'},
            'collector': self.name
        }

        trace_data.append(sample_trace)
        return trace_data

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """验证追踪数据"""
        required_fields = ['trace_id', 'span_id', 'service_name', 'operation']
        return all(field in data for field in required_fields)
```

### 数据预处理器

```python
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import logging

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """数据预处理器"""

    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.preprocessing_rules = []

    def add_preprocessing_rule(self, rule: Dict[str, Any]):
        """添加预处理规则"""
        self.preprocessing_rules.append(rule)

    def preprocess_batch(self, data_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量预处理数据"""
        if not data_batch:
            return []

        try:
            # 转换为DataFrame进行批量处理
            df = pd.DataFrame(data_batch)

            # 应用预处理规则
            for rule in self.preprocessing_rules:
                rule_type = rule.get('type')
                columns = rule.get('columns', [])

                if rule_type == 'normalize':
                    df = self._normalize_columns(df, columns, rule)
                elif rule_type == 'encode':
                    df = self._encode_columns(df, columns, rule)
                elif rule_type == 'fill_missing':
                    df = self._fill_missing_values(df, columns, rule)
                elif rule_type == 'remove_outliers':
                    df = self._remove_outliers(df, columns, rule)

            # 转换回字典列表
            processed_data = df.to_dict('records')

            return processed_data

        except Exception as e:
            logger.error(f"Error in batch preprocessing: {e}")
            return data_batch  # 返回原始数据

    def _normalize_columns(self, df: pd.DataFrame, columns: List[str], rule: Dict[str, Any]) -> pd.DataFrame:
        """标准化列"""
        method = rule.get('method', 'standard')  # standard, minmax

        for col in columns:
            if col not in df.columns:
                continue

            if method == 'standard':
                scaler_key = f"standard_{col}"
                if scaler_key not in self.scalers:
                    self.scalers[scaler_key] = StandardScaler()
                    # 训练scaler（实际应该在训练数据上进行）
                    self.scalers[scaler_key].fit(df[[col]])

                df[col] = self.scalers[scaler_key].transform(df[[col]]).flatten()

            elif method == 'minmax':
                scaler_key = f"minmax_{col}"
                if scaler_key not in self.scalers:
                    self.scalers[scaler_key] = MinMaxScaler()
                    self.scalers[scaler_key].fit(df[[col]])

                df[col] = self.scalers[scaler_key].transform(df[[col]]).flatten()

        return df

    def _encode_columns(self, df: pd.DataFrame, columns: List[str], rule: Dict[str, Any]) -> pd.DataFrame:
        """编码列"""
        method = rule.get('method', 'label')  # label, onehot

        for col in columns:
            if col not in df.columns:
                continue

            if method == 'label':
                from sklearn.preprocessing import LabelEncoder
                encoder_key = f"label_{col}"
                if encoder_key not in self.encoders:
                    self.encoders[encoder_key] = LabelEncoder()
                    self.encoders[encoder_key].fit(df[col])

                df[f"{col}_encoded"] = self.encoders[encoder_key].transform(df[col])

            elif method == 'onehot':
                # One-hot编码
                dummies = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df, dummies], axis=1)
                df.drop(col, axis=1, inplace=True)

        return df

    def _fill_missing_values(self, df: pd.DataFrame, columns: List[str], rule: Dict[str, Any]) -> pd.DataFrame:
        """填充缺失值"""
        method = rule.get('method', 'mean')  # mean, median, mode, constant

        for col in columns:
            if col not in df.columns:
                continue

            if method == 'mean':
                fill_value = df[col].mean()
            elif method == 'median':
                fill_value = df[col].median()
            elif method == 'mode':
                fill_value = df[col].mode().iloc[0] if not df[col].mode().empty else 0
            elif method == 'constant':
                fill_value = rule.get('value', 0)
            else:
                continue

            df[col] = df[col].fillna(fill_value)

        return df

    def _remove_outliers(self, df: pd.DataFrame, columns: List[str], rule: Dict[str, Any]) -> pd.DataFrame:
        """移除异常值"""
        method = rule.get('method', 'iqr')  # iqr, zscore

        for col in columns:
            if col not in df.columns:
                continue

            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]

            elif method == 'zscore':
                threshold = rule.get('threshold', 3)
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                df = df[z_scores < threshold]

        return df

    def get_preprocessing_stats(self) -> Dict[str, Any]:
        """获取预处理统计信息"""
        return {
            'scalers_count': len(self.scalers),
            'encoders_count': len(self.encoders),
            'rules_count': len(self.preprocessing_rules)
        }
```

## 智能分析算法

### 异常检测算法

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector(ABC):
    """异常检测器基类"""

    @abstractmethod
    def fit(self, data: pd.DataFrame) -> None:
        """训练模型"""
        pass

    @abstractmethod
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """预测异常"""
        pass

    @abstractmethod
    def get_anomaly_score(self, data: pd.DataFrame) -> np.ndarray:
        """获取异常分数"""
        pass

class IsolationForestDetector(AnomalyDetector):
    """孤立森林异常检测器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.contamination = config.get('contamination', 0.1)
        self.n_estimators = config.get('n_estimators', 100)
        self.random_state = config.get('random_state', 42)

    def fit(self, data: pd.DataFrame) -> None:
        """训练孤立森林模型"""
        try:
            self.model = IsolationForest(
                contamination=self.contamination,
                n_estimators=self.n_estimators,
                random_state=self.random_state
            )

            # 选择数值列进行训练
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) == 0:
                raise ValueError("No numeric columns found for anomaly detection")

            X = data[numeric_columns].values
            self.model.fit(X)

            logger.info(f"Trained IsolationForest with {len(numeric_columns)} features")

        except Exception as e:
            logger.error(f"Error training IsolationForest: {e}")
            raise

    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """预测异常"""
        if self.model is None:
            raise ValueError("Model not trained")

        numeric_columns = data.select_dtypes(include=[np.number]).columns
        X = data[numeric_columns].values
        predictions = self.model.predict(X)

        # 转换为-1（异常）和1（正常）
        return predictions

    def get_anomaly_score(self, data: pd.DataFrame) -> np.ndarray:
        """获取异常分数"""
        if self.model is None:
            raise ValueError("Model not trained")

        numeric_columns = data.select_dtypes(include=[np.number]).columns
        X = data[numeric_columns].values
        scores = self.model.decision_function(X)

        # 转换为0-1范围的分数，1表示最异常
        return -scores

class StatisticalAnomalyDetector(AnomalyDetector):
    """统计异常检测器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.baseline_stats = {}
        self.threshold_multiplier = config.get('threshold_multiplier', 3)

    def fit(self, data: pd.DataFrame) -> None:
        """计算基准统计信息"""
        try:
            numeric_columns = data.select_dtypes(include=[np.number]).columns

            for col in numeric_columns:
                values = data[col].dropna()
                if len(values) > 0:
                    self.baseline_stats[col] = {
                        'mean': values.mean(),
                        'std': values.std(),
                        'median': values.median(),
                        'q1': values.quantile(0.25),
                        'q3': values.quantile(0.75)
                    }

            logger.info(f"Calculated baseline stats for {len(numeric_columns)} columns")

        except Exception as e:
            logger.error(f"Error calculating baseline stats: {e}")
            raise

    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """基于统计阈值预测异常"""
        predictions = []

        for _, row in data.iterrows():
            is_anomaly = False

            for col, stats in self.baseline_stats.items():
                if col in row.index and pd.notna(row[col]):
                    value = row[col]
                    mean = stats['mean']
                    std = stats['std']

                    # 使用标准差阈值
                    threshold = self.threshold_multiplier * std
                    if abs(value - mean) > threshold:
                        is_anomaly = True
                        break

            predictions.append(-1 if is_anomaly else 1)

        return np.array(predictions)

    def get_anomaly_score(self, data: pd.DataFrame) -> np.ndarray:
        """获取异常分数"""
        scores = []

        for _, row in data.iterrows():
            max_score = 0

            for col, stats in self.baseline_stats.items():
                if col in row.index and pd.notna(row[col]):
                    value = row[col]
                    mean = stats['mean']
                    std = stats['std']

                    if std > 0:
                        z_score = abs(value - mean) / std
                        max_score = max(max_score, z_score)

            # 归一化到0-1范围
            normalized_score = min(max_score / self.threshold_multiplier, 1.0)
            scores.append(normalized_score)

        return np.array(scores)

class TimeSeriesAnomalyDetector(AnomalyDetector):
    """时间序列异常检测器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.window_size = config.get('window_size', 24)
        self.threshold = config.get('threshold', 2.0)

    def fit(self, data: pd.DataFrame) -> None:
        """训练时间序列模型"""
        # 简化实现：计算移动平均和标准差
        try:
            if 'timestamp' not in data.columns:
                raise ValueError("Timestamp column required for time series anomaly detection")

            data = data.sort_values('timestamp')
            numeric_columns = data.select_dtypes(include=[np.number]).columns

            self.baseline_windows = {}

            for col in numeric_columns:
                if col == 'timestamp':
                    continue

                values = data[col].rolling(window=self.window_size).mean()
                stds = data[col].rolling(window=self.window_size).std()

                self.baseline_windows[col] = {
                    'mean': values,
                    'std': stds
                }

            logger.info(f"Trained time series anomaly detector for {len(numeric_columns)} columns")

        except Exception as e:
            logger.error(f"Error training time series detector: {e}")
            raise

    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """预测时间序列异常"""
        if not hasattr(self, 'baseline_windows'):
            raise ValueError("Model not trained")

        predictions = []

        for idx, row in data.iterrows():
            is_anomaly = False

            for col, windows in self.baseline_windows.items():
                if col in row.index and pd.notna(row[col]):
                    value = row[col]

                    # 使用最近的窗口统计
                    recent_mean = windows['mean'].iloc[min(idx, len(windows['mean'])-1)]
                    recent_std = windows['std'].iloc[min(idx, len(windows['std'])-1)]

                    if pd.notna(recent_mean) and pd.notna(recent_std) and recent_std > 0:
                        z_score = abs(value - recent_mean) / recent_std
                        if z_score > self.threshold:
                            is_anomaly = True
                            break

            predictions.append(-1 if is_anomaly else 1)

        return np.array(predictions)

    def get_anomaly_score(self, data: pd.DataFrame) -> np.ndarray:
        """获取异常分数"""
        if not hasattr(self, 'baseline_windows'):
            raise ValueError("Model not trained")

        scores = []

        for idx, row in data.iterrows():
            max_score = 0

            for col, windows in self.baseline_windows.items():
                if col in row.index and pd.notna(row[col]):
                    value = row[col]

                    recent_mean = windows['mean'].iloc[min(idx, len(windows['mean'])-1)]
                    recent_std = windows['std'].iloc[min(idx, len(windows['std'])-1)]

                    if pd.notna(recent_mean) and pd.notna(recent_std) and recent_std > 0:
                        z_score = abs(value - recent_mean) / recent_std
                        max_score = max(max_score, z_score)

            normalized_score = min(max_score / self.threshold, 1.0)
            scores.append(normalized_score)

        return np.array(scores)
```

### 根因分析算法

```python
from typing import Dict, Any, List, Optional, Set, Tuple
import networkx as nx
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import logging

logger = logging.getLogger(__name__)

class RootCauseAnalyzer:
    """根因分析器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.causal_graph = nx.DiGraph()
        self.correlation_threshold = config.get('correlation_threshold', 0.7)
        self.models = {}

    def build_causal_graph(self, data: pd.DataFrame, relationships: List[Tuple[str, str]]) -> None:
        """构建因果图"""
        try:
            # 添加节点
            nodes = set()
            for rel in relationships:
                nodes.update(rel)
            for col in data.columns:
                if col != 'timestamp':
                    nodes.add(col)

            for node in nodes:
                self.causal_graph.add_node(node)

            # 添加边
            for cause, effect in relationships:
                if cause in data.columns and effect in data.columns:
                    correlation = data[cause].corr(data[effect])
                    if abs(correlation) >= self.correlation_threshold:
                        self.causal_graph.add_edge(cause, effect, weight=correlation)

            logger.info(f"Built causal graph with {len(self.causal_graph.nodes)} nodes and {len(self.causal_graph.edges)} edges")

        except Exception as e:
            logger.error(f"Error building causal graph: {e}")

    def analyze_root_cause(self, anomaly_data: pd.DataFrame, anomaly_columns: List[str]) -> Dict[str, Any]:
        """分析根因"""
        try:
            root_causes = {}

            for anomaly_col in anomaly_columns:
                if anomaly_col not in self.causal_graph.nodes:
                    continue

                # 找到所有可能的根因路径
                paths = []
                for node in self.causal_graph.nodes:
                    if node != anomaly_col:
                        try:
                            paths.extend(list(nx.all_simple_paths(self.causal_graph, node, anomaly_col)))
                        except nx.NetworkXNoPath:
                            continue

                # 计算每个潜在根因的贡献度
                cause_scores = {}
                for path in paths:
                    if len(path) > 1:
                        root_cause = path[0]
                        contribution = self._calculate_contribution(anomaly_data, path)

                        if root_cause not in cause_scores:
                            cause_scores[root_cause] = []
                        cause_scores[root_cause].append(contribution)

                # 聚合贡献度
                for cause, scores in cause_scores.items():
                    root_causes[cause] = {
                        'average_contribution': np.mean(scores),
                        'max_contribution': np.max(scores),
                        'path_count': len(scores)
                    }

            # 排序并返回最可能的根因
            sorted_causes = sorted(root_causes.items(),
                                 key=lambda x: x[1]['average_contribution'],
                                 reverse=True)

            return {
                'primary_root_cause': sorted_causes[0][0] if sorted_causes else None,
                'all_causes': dict(sorted_causes),
                'analysis_timestamp': pd.Timestamp.now()
            }

        except Exception as e:
            logger.error(f"Error in root cause analysis: {e}")
            return {}

    def _calculate_contribution(self, data: pd.DataFrame, path: List[str]) -> float:
        """计算路径贡献度"""
        try:
            if len(path) < 2:
                return 0.0

            # 使用线性回归计算贡献度
            X = data[path[:-1]]  # 原因变量
            y = data[path[-1]]   # 结果变量

            model = LinearRegression()
            model.fit(X, y)

            # 计算R²作为贡献度度量
            r_squared = model.score(X, y)
            return max(0, r_squared)  # 确保非负

        except Exception as e:
            logger.error(f"Error calculating contribution for path {path}: {e}")
            return 0.0

    def predict_impact(self, root_cause_change: Dict[str, float], time_window: int = 24) -> Dict[str, Any]:
        """预测根因变化的影响"""
        try:
            impacts = {}

            # 遍历图中的所有路径，计算传播效应
            for node in self.causal_graph.nodes:
                if node in root_cause_change:
                    change_value = root_cause_change[node]

                    # 使用简单的传播模型
                    impacted_nodes = self._propagate_change(node, change_value)
                    impacts.update(impacted_nodes)

            return {
                'predicted_impacts': impacts,
                'time_window_hours': time_window,
                'prediction_timestamp': pd.Timestamp.now()
            }

        except Exception as e:
            logger.error(f"Error predicting impact: {e}")
            return {}

    def _propagate_change(self, start_node: str, change_value: float) -> Dict[str, float]:
        """传播变化效应"""
        impacts = {}
        visited = set()

        def dfs(node: str, current_change: float, depth: int = 0):
            if node in visited or depth > 5:  # 限制传播深度
                return

            visited.add(node)

            # 获取该节点的传出边
            for successor in self.causal_graph.successors(node):
                edge_data = self.causal_graph.get_edge_data(node, successor)
                weight = edge_data.get('weight', 1.0)

                # 计算传播后的变化
                propagated_change = current_change * weight * 0.8  # 衰减因子

                if abs(propagated_change) > 0.01:  # 阈值过滤
                    impacts[successor] = impacts.get(successor, 0) + propagated_change
                    dfs(successor, propagated_change, depth + 1)

        dfs(start_node, change_value)
        return impacts

    def get_graph_metrics(self) -> Dict[str, Any]:
        """获取图的度量信息"""
        return {
            'node_count': len(self.causal_graph.nodes),
            'edge_count': len(self.causal_graph.edges),
            'average_degree': sum(dict(self.causal_graph.degree()).values()) / len(self.causal_graph.nodes) if self.causal_graph.nodes else 0,
            'is_connected': nx.is_weakly_connected(self.causal_graph) if self.causal_graph.nodes else False
        }
```

### 趋势分析算法

```python
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
import logging

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """趋势分析器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.seasonal_period = config.get('seasonal_period', 24)  # 默认24小时周期
        self.models = {}

    def decompose_time_series(self, data: pd.DataFrame, time_column: str, value_column: str) -> Dict[str, Any]:
        """时间序列分解"""
        try:
            if time_column not in data.columns or value_column not in data.columns:
                raise ValueError(f"Required columns {time_column}, {value_column} not found")

            # 确保时间列是datetime类型
            if not pd.api.types.is_datetime64_any_dtype(data[time_column]):
                data[time_column] = pd.to_datetime(data[time_column])

            # 设置时间索引
            ts_data = data.set_index(time_column)[value_column].dropna()

            if len(ts_data) < 2 * self.seasonal_period:
                raise ValueError("Insufficient data for seasonal decomposition")

            # 执行季节性分解
            decomposition = seasonal_decompose(ts_data, model='additive', period=self.seasonal_period)

            return {
                'trend': decomposition.trend.dropna().tolist(),
                'seasonal': decomposition.seasonal.dropna().tolist(),
                'residual': decomposition.resid.dropna().tolist(),
                'observed': decomposition.observed.dropna().tolist(),
                'trend_strength': self._calculate_trend_strength(decomposition),
                'seasonal_strength': self._calculate_seasonal_strength(decomposition)
            }

        except Exception as e:
            logger.error(f"Error in time series decomposition: {e}")
            return {}

    def _calculate_trend_strength(self, decomposition) -> float:
        """计算趋势强度"""
        try:
            trend_var = np.var(decomposition.trend.dropna())
            residual_var = np.var(decomposition.resid.dropna())
            total_var = trend_var + residual_var

            return trend_var / total_var if total_var > 0 else 0
        except:
            return 0

    def _calculate_seasonal_strength(self, decomposition) -> float:
        """计算季节性强度"""
        try:
            seasonal_var = np.var(decomposition.seasonal.dropna())
            residual_var = np.var(decomposition.resid.dropna())
            total_var = seasonal_var + residual_var

            return seasonal_var / total_var if total_var > 0 else 0
        except:
            return 0

    def detect_trend_changes(self, data: pd.DataFrame, value_column: str, window_size: int = 10) -> List[Dict[str, Any]]:
        """检测趋势变化点"""
        try:
            values = data[value_column].dropna().values
            changes = []

            if len(values) < window_size * 2:
                return changes

            for i in range(window_size, len(values) - window_size):
                # 计算前后窗口的斜率
                prev_window = values[i-window_size:i]
                next_window = values[i:i+window_size]

                prev_slope = self._calculate_slope(prev_window)
                next_slope = self._calculate_slope(next_window)

                # 计算斜率变化
                slope_change = abs(next_slope - prev_slope)

                # 计算统计显著性
                if slope_change > self._calculate_slope_threshold(prev_window, next_window):
                    changes.append({
                        'index': i,
                        'timestamp': data.index[i] if hasattr(data, 'index') else i,
                        'prev_slope': prev_slope,
                        'next_slope': next_slope,
                        'slope_change': slope_change,
                        'significance': slope_change / (abs(prev_slope) + abs(next_slope) + 1e-6)
                    })

            return changes

        except Exception as e:
            logger.error(f"Error detecting trend changes: {e}")
            return []

    def _calculate_slope(self, values: np.ndarray) -> float:
        """计算斜率"""
        if len(values) < 2:
            return 0

        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        return slope

    def _calculate_slope_threshold(self, window1: np.ndarray, window2: np.ndarray) -> float:
        """计算斜率变化阈值"""
        # 使用标准差作为阈值
        combined = np.concatenate([window1, window2])
        std = np.std(combined)

        # 动态阈值：标准差的倍数
        return std * 2.0

    def forecast_trend(self, data: pd.DataFrame, value_column: str, forecast_steps: int = 24) -> Dict[str, Any]:
        """趋势预测"""
        try:
            values = data[value_column].dropna().values

            if len(values) < 10:
                raise ValueError("Insufficient data for forecasting")

            # 训练ARIMA模型
            model = ARIMA(values, order=(1, 1, 1))
            model_fit = model.fit()

            # 生成预测
            forecast = model_fit.forecast(steps=forecast_steps)

            # 计算置信区间
            forecast_obj = model_fit.get_forecast(steps=forecast_steps)
            conf_int = forecast_obj.conf_int()

            return {
                'forecast': forecast.tolist(),
                'lower_bound': conf_int[:, 0].tolist(),
                'upper_bound': conf_int[:, 1].tolist(),
                'model_aic': model_fit.aic,
                'model_bic': model_fit.bic
            }

        except Exception as e:
            logger.error(f"Error in trend forecasting: {e}")
            return {}

    def analyze_seasonality(self, data: pd.DataFrame, value_column: str) -> Dict[str, Any]:
        """分析季节性模式"""
        try:
            values = data[value_column].dropna().values

            if len(values) < 2 * self.seasonal_period:
                return {}

            # 计算自相关函数
            autocorr = []
            for lag in range(1, min(self.seasonal_period + 1, len(values))):
                corr = np.corrcoef(values[:-lag], values[lag:])[0, 1]
                autocorr.append(corr)

            # 找到主要的季节性周期
            seasonal_peaks = []
            for i, corr in enumerate(autocorr):
                if corr > 0.5:  # 相关性阈值
                    seasonal_peaks.append((i + 1, corr))

            seasonal_peaks.sort(key=lambda x: x[1], reverse=True)

            return {
                'autocorrelation': autocorr,
                'seasonal_periods': seasonal_peaks[:5],  # 前5个主要周期
                'dominant_period': seasonal_peaks[0][0] if seasonal_peaks else None,
                'seasonal_strength': seasonal_peaks[0][1] if seasonal_peaks else 0
            }

        except Exception as e:
            logger.error(f"Error in seasonality analysis: {e}")
            return {}

    def get_trend_summary(self, data: pd.DataFrame, value_column: str) -> Dict[str, Any]:
        """获取趋势摘要"""
        try:
            values = data[value_column].dropna()

            # 基本统计
            current_value = values.iloc[-1]
            previous_value = values.iloc[-2] if len(values) > 1 else current_value

            # 计算变化率
            change_rate = (current_value - previous_value) / previous_value if previous_value != 0 else 0

            # 计算移动平均趋势
            ma_short = values.rolling(window=min(7, len(values))).mean().iloc[-1]
            ma_long = values.rolling(window=min(30, len(values))).mean().iloc[-1]

            trend_direction = "stable"
            if ma_short > ma_long * 1.01:
                trend_direction = "increasing"
            elif ma_short < ma_long * 0.99:
                trend_direction = "decreasing"

            return {
                'current_value': current_value,
                'change_rate': change_rate,
                'trend_direction': trend_direction,
                'short_term_ma': ma_short,
                'long_term_ma': ma_long,
                'volatility': values.std() / values.mean() if values.mean() != 0 else 0
            }

        except Exception as e:
            logger.error(f"Error generating trend summary: {e}")
            return {}
```

## 可视化展示平台

### 可视化组件

```python
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ObservabilityDashboard:
    """可观测性仪表板"""

    def __init__(self, title: str = "大数据测试可观测性平台"):
        self.title = title
        self.metrics_data = {}
        self.alerts_data = []
        self.analysis_results = {}

    def render_dashboard(self):
        """渲染主仪表板"""
        st.set_page_config(page_title=self.title, layout="wide")
        st.title(self.title)

        # 创建标签页
        tab1, tab2, tab3, tab4 = st.tabs(["📊 指标监控", "🚨 告警中心", "🔍 智能分析", "📈 趋势预测"])

        with tab1:
            self._render_metrics_tab()

        with tab2:
            self._render_alerts_tab()

        with tab3:
            self._render_analysis_tab()

        with tab4:
            self._render_forecasting_tab()

    def _render_metrics_tab(self):
        """渲染指标监控标签页"""
        st.header("系统指标监控")

        # 时间范围选择器
        col1, col2 = st.columns(2)
        with col1:
            time_range = st.selectbox("时间范围",
                                    ["1小时", "6小时", "24小时", "7天", "30天"],
                                    index=2)
        with col2:
            refresh_interval = st.slider("自动刷新间隔(秒)", 30, 300, 60)

        # 指标选择器
        if self.metrics_data:
            available_metrics = list(self.metrics_data.keys())
            selected_metrics = st.multiselect("选择指标",
                                            available_metrics,
                                            default=available_metrics[:4])

            # 创建子图
            if selected_metrics:
                fig = make_subplots(rows=len(selected_metrics), cols=1,
                                  subplot_titles=selected_metrics,
                                  shared_xaxes=True)

                for i, metric_name in enumerate(selected_metrics):
                    if metric_name in self.metrics_data:
                        data = self.metrics_data[metric_name]
                        df = pd.DataFrame(data)

                        if 'timestamp' in df.columns and 'value' in df.columns:
                            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                            fig.add_trace(
                                go.Scatter(x=df['timestamp'], y=df['value'],
                                         name=metric_name, mode='lines'),
                                row=i+1, col=1
                            )

                fig.update_layout(height=300*len(selected_metrics), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        # 实时指标卡片
        st.subheader("实时指标")
        if self.metrics_data:
            cols = st.columns(4)
            for i, (metric_name, data) in enumerate(list(self.metrics_data.items())[:4]):
                with cols[i]:
                    latest_value = data[-1]['value'] if data else 0
                    st.metric(metric_name, f"{latest_value:.2f}")

    def _render_alerts_tab(self):
        """渲染告警中心标签页"""
        st.header("告警中心")

        # 告警过滤器
        col1, col2, col3 = st.columns(3)
        with col1:
            severity_filter = st.multiselect("严重程度",
                                           ["info", "warning", "error", "critical"],
                                           default=["warning", "error", "critical"])
        with col2:
            status_filter = st.multiselect("状态",
                                         ["firing", "resolved", "acknowledged"],
                                         default=["firing", "acknowledged"])
        with col3:
            source_filter = st.selectbox("数据源", ["全部", "prometheus", "custom", "analysis"])

        # 过滤告警数据
        filtered_alerts = self._filter_alerts(severity_filter, status_filter, source_filter)

        # 告警统计
        if filtered_alerts:
            stats = self._calculate_alert_stats(filtered_alerts)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("活跃告警", stats['active'])
            with col2:
                st.metric("已解决", stats['resolved'])
            with col3:
                st.metric("严重告警", stats['critical'])
            with col4:
                st.metric("警告告警", stats['warning'])

        # 告警列表
        if filtered_alerts:
            st.subheader("告警列表")

            # 转换为DataFrame用于显示
            alerts_df = pd.DataFrame(filtered_alerts)
            if not alerts_df.empty:
                alerts_df['timestamp'] = pd.to_datetime(alerts_df['timestamp'], unit='s')

                # 添加操作按钮
                alerts_df['操作'] = alerts_df.apply(
                    lambda row: f"确认_{row.name}" if row['status'] == 'firing' else "",
                    axis=1
                )

                st.dataframe(alerts_df[['title', 'severity', 'status', 'timestamp', 'source']])

                # 处理确认操作
                for idx, row in alerts_df.iterrows():
                    if st.button(f"确认告警 {idx}", key=f"ack_{idx}"):
                        self._acknowledge_alert(idx)

        # 告警趋势图
        if filtered_alerts:
            st.subheader("告警趋势")
            alerts_df = pd.DataFrame(filtered_alerts)
            alerts_df['timestamp'] = pd.to_datetime(alerts_df['timestamp'], unit='s')
            alerts_df['hour'] = alerts_df['timestamp'].dt.hour

            hourly_alerts = alerts_df.groupby('hour').size().reset_index(name='count')

            fig = px.bar(hourly_alerts, x='hour', y='count',
                        title="每小时告警数量",
                        labels={'hour': '小时', 'count': '告警数量'})
            st.plotly_chart(fig, use_container_width=True)

    def _render_analysis_tab(self):
        """渲染智能分析标签页"""
        st.header("智能分析")

        # 分析类型选择
        analysis_type = st.selectbox("分析类型",
                                   ["异常检测", "根因分析", "相关性分析", "模式识别"])

        if analysis_type == "异常检测":
            self._render_anomaly_analysis()
        elif analysis_type == "根因分析":
            self._render_root_cause_analysis()
        elif analysis_type == "相关性分析":
            self._render_correlation_analysis()
        elif analysis_type == "模式识别":
            self._render_pattern_recognition()

    def _render_anomaly_analysis(self):
        """渲染异常检测分析"""
        st.subheader("异常检测结果")

        if 'anomaly_results' in self.analysis_results:
            results = self.analysis_results['anomaly_results']

            # 异常统计
            total_points = len(results.get('predictions', []))
            anomaly_count = sum(1 for p in results.get('predictions', []) if p == -1)
            anomaly_rate = anomaly_count / total_points if total_points > 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总数据点", total_points)
            with col2:
                st.metric("异常点数", anomaly_count)
            with col3:
                st.metric("异常率", f"{anomaly_rate:.2%}")

            # 异常分数分布
            if 'scores' in results:
                fig = px.histogram(results['scores'],
                                 title="异常分数分布",
                                 labels={'value': '异常分数'})
                st.plotly_chart(fig, use_container_width=True)

            # 时间序列异常标记
            if 'data' in results and 'predictions' in results:
                data = results['data']
                predictions = results['predictions']

                anomaly_indices = [i for i, p in enumerate(predictions) if p == -1]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data['timestamp'] if 'timestamp' in data.columns else list(range(len(data))),
                    y=data['value'] if 'value' in data.columns else data,
                    mode='lines',
                    name='正常值'
                ))

                if anomaly_indices:
                    anomaly_data = data.iloc[anomaly_indices] if hasattr(data, 'iloc') else [data[i] for i in anomaly_indices]
                    fig.add_trace(go.Scatter(
                        x=anomaly_data['timestamp'] if isinstance(anomaly_data, pd.DataFrame) and 'timestamp' in anomaly_data.columns else anomaly_indices,
                        y=anomaly_data['value'] if isinstance(anomaly_data, pd.DataFrame) and 'value' in anomaly_data.columns else anomaly_data,
                        mode='markers',
                        name='异常点',
                        marker=dict(color='red', size=8)
                    ))

                st.plotly_chart(fig, use_container_width=True)

    def _render_root_cause_analysis(self):
        """渲染根因分析"""
        st.subheader("根因分析结果")

        if 'root_cause_results' in self.analysis_results:
            results = self.analysis_results['root_cause_results']

            if 'primary_root_cause' in results and results['primary_root_cause']:
                st.success(f"主要根因: {results['primary_root_cause']}")

                # 显示所有潜在根因
                if 'all_causes' in results:
                    st.subheader("所有潜在根因")
                    causes_df = pd.DataFrame.from_dict(results['all_causes'], orient='index')
                    causes_df = causes_df.sort_values('average_contribution', ascending=False)
                    st.dataframe(causes_df)

                    # 可视化根因贡献
                    fig = px.bar(causes_df.head(10),
                               x=causes_df.head(10).index,
                               y='average_contribution',
                               title="根因贡献度排名",
                               labels={'index': '根因', 'average_contribution': '平均贡献度'})
                    st.plotly_chart(fig, use_container_width=True)

    def _render_correlation_analysis(self):
        """渲染相关性分析"""
        st.subheader("相关性分析")

        if 'correlation_matrix' in self.analysis_results:
            corr_matrix = self.analysis_results['correlation_matrix']

            # 热力图
            fig = px.imshow(corr_matrix,
                          title="指标相关性热力图",
                          labels=dict(color="相关系数"))
            st.plotly_chart(fig, use_container_width=True)

            # 强相关指标对
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = abs(corr_matrix.iloc[i, j])
                    if corr_value > 0.7:  # 强相关阈值
                        strong_correlations.append({
                            'metric1': corr_matrix.columns[i],
                            'metric2': corr_matrix.columns[j],
                            'correlation': corr_matrix.iloc[i, j]
                        })

            if strong_correlations:
                st.subheader("强相关指标对")
                corr_df = pd.DataFrame(strong_correlations)
                corr_df = corr_df.sort_values('correlation', key=abs, ascending=False)
                st.dataframe(corr_df)

    def _render_pattern_recognition(self):
        """渲染模式识别"""
        st.subheader("模式识别结果")

        if 'patterns' in self.analysis_results:
            patterns = self.analysis_results['patterns']

            for pattern in patterns:
                with st.expander(f"模式: {pattern.get('name', '未知模式')}"):
                    st.write(f"置信度: {pattern.get('confidence', 0):.2%}")
                    st.write(f"支持度: {pattern.get('support', 0):.2%}")
                    st.write(f"描述: {pattern.get('description', '无描述')}")

                    if 'visualization' in pattern:
                        st.plotly_chart(pattern['visualization'], use_container_width=True)

    def _render_forecasting_tab(self):
        """渲染趋势预测标签页"""
        st.header("趋势预测")

        # 预测配置
        col1, col2 = st.columns(2)
        with col1:
            forecast_metric = st.selectbox("预测指标",
                                         list(self.metrics_data.keys()) if self.metrics_data else [])
        with col2:
            forecast_steps = st.slider("预测步长", 1, 168, 24)  # 最多7天

        if forecast_metric and forecast_metric in self.metrics_data:
            data = self.metrics_data[forecast_metric]

            if 'forecast_results' in self.analysis_results:
                forecast_data = self.analysis_results['forecast_results']

                # 显示预测结果
                fig = go.Figure()

                # 历史数据
                historical_df = pd.DataFrame(data)
                if 'timestamp' in historical_df.columns and 'value' in historical_df.columns:
                    historical_df['timestamp'] = pd.to_datetime(historical_df['timestamp'], unit='s')
                    fig.add_trace(go.Scatter(
                        x=historical_df['timestamp'],
                        y=historical_df['value'],
                        name='历史数据',
                        mode='lines'
                    ))

                    # 预测数据
                    if 'forecast' in forecast_data:
                        last_timestamp = historical_df['timestamp'].iloc[-1]
                        forecast_timestamps = pd.date_range(
                            start=last_timestamp,
                            periods=len(forecast_data['forecast']) + 1,
                            freq='H'
                        )[1:]

                        fig.add_trace(go.Scatter(
                            x=forecast_timestamps,
                            y=forecast_data['forecast'],
                            name='预测值',
                            mode='lines',
                            line=dict(dash='dash')
                        ))

                        # 置信区间
                        if 'upper_bound' in forecast_data and 'lower_bound' in forecast_data:
                            fig.add_trace(go.Scatter(
                                x=forecast_timestamps.tolist() + forecast_timestamps.tolist()[::-1],
                                y=forecast_data['upper_bound'] + forecast_data['lower_bound'][::-1],
                                fill='toself',
                                fillcolor='rgba(0,100,80,0.2)',
                                line=dict(color='rgba(255,255,255,0)'),
                                name='置信区间'
                            ))

                st.plotly_chart(fig, use_container_width=True)

                # 预测指标
                if 'forecast' in forecast_data:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("预测平均值", f"{np.mean(forecast_data['forecast']):.2f}")
                    with col2:
                        st.metric("预测标准差", f"{np.std(forecast_data['forecast']):.2f}")
                    with col3:
                        trend = "上升" if forecast_data['forecast'][-1] > forecast_data['forecast'][0] else "下降"
                        st.metric("趋势方向", trend)

    def _filter_alerts(self, severity_filter: List[str], status_filter: List[str],
                      source_filter: str) -> List[Dict[str, Any]]:
        """过滤告警数据"""
        filtered = []

        for alert in self.alerts_data:
            if severity_filter and alert.get('severity') not in severity_filter:
                continue
            if status_filter and alert.get('status') not in status_filter:
                continue
            if source_filter != "全部" and alert.get('source') != source_filter:
                continue
            filtered.append(alert)

        return filtered

    def _calculate_alert_stats(self, alerts: List[Dict[str, Any]]) -> Dict[str, int]:
        """计算告警统计"""
        stats = {'active': 0, 'resolved': 0, 'critical': 0, 'warning': 0}

        for alert in alerts:
            if alert.get('status') == 'firing':
                stats['active'] += 1
            elif alert.get('status') == 'resolved':
                stats['resolved'] += 1

            if alert.get('severity') == 'critical':
                stats['critical'] += 1
            elif alert.get('severity') == 'warning':
                stats['warning'] += 1

        return stats

    def _acknowledge_alert(self, alert_index: int):
        """确认告警"""
        if 0 <= alert_index < len(self.alerts_data):
            self.alerts_data[alert_index]['status'] = 'acknowledged'
            st.success(f"告警 {alert_index} 已确认")

    def update_data(self, metrics_data: Dict[str, List[Dict[str, Any]]],
                   alerts_data: List[Dict[str, Any]],
                   analysis_results: Dict[str, Any]):
        """更新仪表板数据"""
        self.metrics_data = metrics_data
        self.alerts_data = alerts_data
        self.analysis_results = analysis_results
```

## 数据分析平台配置

### 平台配置文件

```yaml
# examples/28_chapter/data_analysis.yml
data_collectors:
  - name: system_metrics
    type: MetricsCollector
    config:
      prometheus_url: "http://localhost:9090"
      interval: 60
      queries:
        - name: cpu_usage
          query: "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
          labels:
            service: "system"
        - name: memory_usage
          query: "(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100"
          labels:
            service: "system"
        - name: disk_usage
          query: "(1 - node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100"
          labels:
            service: "system"

  - name: application_logs
    type: LogCollector
    config:
      sources:
        - type: file
          config:
            path: "/var/log/application/app.log"
            parser: "json"
            max_lines: 1000
        - type: kafka
          config:
            topic: "app-logs"
            bootstrap_servers: ["localhost:9092"]
            parser: "json"

  - name: trace_data
    type: TraceCollector
    config:
      jaeger_url: "http://localhost:16686"
      service_name: "data-testing-service"

preprocessing_rules:
  - type: normalize
    columns: ["cpu_usage", "memory_usage", "disk_usage"]
    config:
      method: "standard"
  - type: fill_missing
    columns: ["response_time", "error_rate"]
    config:
      method: "mean"
  - type: remove_outliers
    columns: ["latency", "throughput"]
    config:
      method: "iqr"

anomaly_detectors:
  - name: isolation_forest_detector
    type: IsolationForestDetector
    config:
      contamination: 0.1
      n_estimators: 100
      columns: ["cpu_usage", "memory_usage", "disk_usage", "response_time"]

  - name: statistical_detector
    type: StatisticalAnomalyDetector
    config:
      threshold_multiplier: 3.0
      columns: ["error_rate", "latency"]

  - name: time_series_detector
    type: TimeSeriesAnomalyDetector
    config:
      window_size: 24
      threshold: 2.0
      columns: ["throughput", "connection_count"]

root_cause_analysis:
  relationships:
    - ["cpu_usage", "response_time"]
    - ["memory_usage", "error_rate"]
    - ["disk_usage", "io_latency"]
    - ["network_latency", "response_time"]
  correlation_threshold: 0.7

trend_analysis:
  seasonal_period: 24
  forecast_steps: 24
  metrics:
    - cpu_usage
    - memory_usage
    - response_time
    - error_rate

visualization:
  dashboard_title: "大数据测试可观测性平台"
  refresh_interval: 60
  theme: "light"
  charts:
    - type: "time_series"
      metrics: ["cpu_usage", "memory_usage", "disk_usage"]
      title: "系统资源使用率"
    - type: "heatmap"
      metrics: ["response_time", "error_rate"]
      title: "应用性能指标"
    - type: "alert_summary"
      title: "告警概览"
    - type: "anomaly_timeline"
      title: "异常检测时间线"
```

### 平台启动脚本

```python
#!/usr/bin/env python3
# examples/28_chapter/start_data_analysis.py

import yaml
import logging
from pathlib import Path
from typing import Dict, Any
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# 导入自定义模块
from data_collectors import MetricsCollector, LogCollector, TraceCollector
from preprocessors import DataPreprocessor
from anomaly_detectors import IsolationForestDetector, StatisticalAnomalyDetector, TimeSeriesAnomalyDetector
from root_cause_analyzer import RootCauseAnalyzer
from trend_analyzer import TrendAnalyzer
from visualization import ObservabilityDashboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataAnalysisPlatform:
    """数据分析平台"""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.collectors = []
        self.preprocessor = None
        self.anomaly_detectors = []
        self.root_cause_analyzer = None
        self.trend_analyzer = None
        self.dashboard = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.is_running = False

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def initialize_components(self):
        """初始化平台组件"""
        logger.info("Initializing data analysis platform components...")

        # 初始化数据采集器
        self._init_data_collectors()

        # 初始化预处理器
        self._init_preprocessor()

        # 初始化异常检测器
        self._init_anomaly_detectors()

        # 初始化根因分析器
        self._init_root_cause_analyzer()

        # 初始化趋势分析器
        self._init_trend_analyzer()

        # 初始化可视化仪表板
        self._init_dashboard()

        logger.info("All components initialized successfully")

    def _init_data_collectors(self):
        """初始化数据采集器"""
        collector_configs = self.config.get('data_collectors', [])

        for collector_config in collector_configs:
            collector_type = collector_config.get('type')
            name = collector_config.get('name')
            config = collector_config.get('config', {})

            try:
                if collector_type == 'MetricsCollector':
                    collector = MetricsCollector(config)
                elif collector_type == 'LogCollector':
                    collector = LogCollector(config)
                elif collector_type == 'TraceCollector':
                    collector = TraceCollector(config)
                else:
                    logger.warning(f"Unknown collector type: {collector_type}")
                    continue

                self.collectors.append(collector)
                logger.info(f"Initialized collector: {name}")

            except Exception as e:
                logger.error(f"Error initializing collector {name}: {e}")

    def _init_preprocessor(self):
        """初始化预处理器"""
        try:
            preprocessing_rules = self.config.get('preprocessing_rules', [])
            self.preprocessor = DataPreprocessor()

            for rule in preprocessing_rules:
                self.preprocessor.add_preprocessing_rule(rule)

            logger.info("Initialized data preprocessor")

        except Exception as e:
            logger.error(f"Error initializing preprocessor: {e}")

    def _init_anomaly_detectors(self):
        """初始化异常检测器"""
        detector_configs = self.config.get('anomaly_detectors', [])

        for detector_config in detector_configs:
            detector_type = detector_config.get('type')
            name = detector_config.get('name')
            config = detector_config.get('config', {})

            try:
                if detector_type == 'IsolationForestDetector':
                    detector = IsolationForestDetector(config)
                elif detector_type == 'StatisticalAnomalyDetector':
                    detector = StatisticalAnomalyDetector(config)
                elif detector_type == 'TimeSeriesAnomalyDetector':
                    detector = TimeSeriesAnomalyDetector(config)
                else:
                    logger.warning(f"Unknown detector type: {detector_type}")
                    continue

                self.anomaly_detectors.append(detector)
                logger.info(f"Initialized anomaly detector: {name}")

            except Exception as e:
                logger.error(f"Error initializing detector {name}: {e}")

    def _init_root_cause_analyzer(self):
        """初始化根因分析器"""
        try:
            root_cause_config = self.config.get('root_cause_analysis', {})
            self.root_cause_analyzer = RootCauseAnalyzer(root_cause_config)

            relationships = root_cause_config.get('relationships', [])
            self.root_cause_analyzer.build_causal_graph(pd.DataFrame(), relationships)

            logger.info("Initialized root cause analyzer")

        except Exception as e:
            logger.error(f"Error initializing root cause analyzer: {e}")

    def _init_trend_analyzer(self):
        """初始化趋势分析器"""
        try:
            trend_config = self.config.get('trend_analysis', {})
            self.trend_analyzer = TrendAnalyzer(trend_config)
            logger.info("Initialized trend analyzer")

        except Exception as e:
            logger.error(f"Error initializing trend analyzer: {e}")

    def _init_dashboard(self):
        """初始化可视化仪表板"""
        try:
            viz_config = self.config.get('visualization', {})
            dashboard_title = viz_config.get('dashboard_title', '数据分析平台')
            self.dashboard = ObservabilityDashboard(dashboard_title)
            logger.info("Initialized visualization dashboard")

        except Exception as e:
            logger.error(f"Error initializing dashboard: {e}")

    def start_collection(self):
        """开始数据采集"""
        logger.info("Starting data collection...")
        self.is_running = True

        for collector in self.collectors:
            self.executor.submit(self._run_collector, collector)

    def _run_collector(self, collector):
        """运行数据采集器"""
        while self.is_running:
            try:
                data = collector.collect_data()
                if data:
                    logger.info(f"Collected {len(data)} data points from {collector.name}")
                    # 这里可以将数据发送到预处理器和分析器

                time.sleep(collector.collection_interval)

            except Exception as e:
                logger.error(f"Error in collector {collector.name}: {e}")
                time.sleep(60)  # 错误重试间隔

    def start_analysis(self):
        """开始数据分析"""
        logger.info("Starting data analysis...")

        # 这里可以启动分析任务
        self.executor.submit(self._run_analysis_loop)

    def _run_analysis_loop(self):
        """运行分析循环"""
        while self.is_running:
            try:
                # 收集最新数据
                all_data = {}
                for collector in self.collectors:
                    # 这里应该从数据存储中获取最新数据
                    pass

                # 执行分析
                if all_data:
                    self._perform_analysis(all_data)

                time.sleep(300)  # 每5分钟执行一次分析

            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                time.sleep(60)

    def _perform_analysis(self, data: Dict[str, Any]):
        """执行数据分析"""
        try:
            # 数据预处理
            if self.preprocessor:
                processed_data = self.preprocessor.preprocess_batch(data)
            else:
                processed_data = data

            # 异常检测
            anomaly_results = {}
            for detector in self.anomaly_detectors:
                detector_name = detector.__class__.__name__
                # 这里应该训练和运行检测器
                anomaly_results[detector_name] = {}

            # 根因分析
            root_cause_results = {}
            if self.root_cause_analyzer:
                # 这里应该执行根因分析
                root_cause_results = {}

            # 趋势分析
            trend_results = {}
            if self.trend_analyzer:
                # 这里应该执行趋势分析
                trend_results = {}

            # 更新仪表板
            if self.dashboard:
                self.dashboard.update_data(data, [], {
                    'anomaly_results': anomaly_results,
                    'root_cause_results': root_cause_results,
                    'trend_results': trend_results
                })

        except Exception as e:
            logger.error(f"Error performing analysis: {e}")

    def start_dashboard(self):
        """启动可视化仪表板"""
        if self.dashboard:
            logger.info("Starting visualization dashboard...")
            # 在实际实现中，这里会启动Streamlit服务器
            # self.dashboard.render_dashboard()
            logger.info("Dashboard started")
        else:
            logger.error("Dashboard not initialized")

    def stop(self):
        """停止平台"""
        logger.info("Stopping data analysis platform...")
        self.is_running = False
        self.executor.shutdown(wait=True)
        logger.info("Data analysis platform stopped")

def main():
    """主函数"""
    config_path = "examples/28_chapter/data_analysis.yml"

    if not Path(config_path).exists():
        logger.error(f"Config file not found: {config_path}")
        return

    platform = DataAnalysisPlatform(config_path)

    try:
        # 初始化组件
        platform.initialize_components()

        # 启动数据采集
        platform.start_collection()

        # 启动分析
        platform.start_analysis()

        # 启动仪表板
        platform.start_dashboard()

        # 保持运行
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Error running platform: {e}")
    finally:
        platform.stop()

if __name__ == "__main__":
    main()
```

## 最佳实践与配置建议

### 数据采集最佳实践
- **数据质量保证**: 实施数据验证和清洗机制
- **采集频率优化**: 根据业务需求和系统负载调整采集间隔
- **数据压缩存储**: 对历史数据进行压缩以节省存储空间
- **故障恢复**: 实现数据采集器的自动故障恢复机制

### 分析算法选择建议
- **异常检测**: 对于高维数据使用孤立森林，对于时间序列使用统计方法
- **根因分析**: 建立准确的因果关系图，避免虚假相关性
- **趋势预测**: 使用ARIMA或LSTM模型，根据数据特点选择合适算法
- **实时性要求**: 根据分析需求选择批处理或流处理模式

### 可视化设计原则
- **用户友好**: 界面简洁直观，重点信息突出显示
- **响应式设计**: 支持不同设备和屏幕尺寸
- **交互性**: 提供钻取、过滤、比较等交互功能
- **实时更新**: 关键指标实时更新，历史数据按需加载

### 性能优化策略
- **数据分区**: 按时间和类型对数据进行分区存储
- **缓存机制**: 对频繁查询的数据实施缓存策略
- **并行处理**: 利用分布式计算框架提高分析速度
- **资源管理**: 实施资源使用监控和自动扩缩容

### 安全与合规考虑
- **数据加密**: 对敏感数据进行加密存储和传输
- **访问控制**: 实施基于角色的访问控制机制
- **审计日志**: 记录所有数据访问和分析操作
- **隐私保护**: 遵守数据隐私保护相关法规要求