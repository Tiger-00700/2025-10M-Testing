"""
AdaptiveAssertionEngine

Extracted from book (Chapter 20). Example of adaptive assertions using history.
"""
import statistics
from collections import deque


class AdaptiveAssertionEngine:
    def __init__(self, window_size=100, confidence=0.95):
        self.metrics_history = {}
        self.window_size = window_size
        self.confidence = confidence

    def record_metric(self, metric_name, value):
        if metric_name not in self.metrics_history:
            self.metrics_history[metric_name] = deque(maxlen=self.window_size)
        self.metrics_history[metric_name].append(value)

    def assert_metric(self, metric_name, value, assertion_type="range"):
        if metric_name not in self.metrics_history or len(self.metrics_history[metric_name]) < 10:
            # 历史数据不足，使用默认断言
            return self._default_assertion(value, assertion_type)

        history = list(self.metrics_history[metric_name])
        mean = statistics.mean(history)
        stdev = statistics.stdev(history) if len(history) > 1 else 0

        if assertion_type == "range":
            lower_bound = mean - 3 * stdev
            upper_bound = mean + 3 * stdev
            is_valid = lower_bound <= value <= upper_bound
            return is_valid, f"值 {value} 应在 [{lower_bound:.2f}, {upper_bound:.2f}] 范围内"

        elif assertion_type == "trend":
            recent_mean = statistics.mean(history[-10:])
            older_mean = statistics.mean(history[:-10]) if len(history) > 10 else recent_mean
            change_percent = (recent_mean - older_mean) / older_mean * 100 if older_mean != 0 else 0
            is_valid = abs(change_percent) < 20
            return is_valid, f"趋势变化 {change_percent:.2f}% 应小于20%"

        return False, "未知的断言类型"

    def _default_assertion(self, value, assertion_type):
        if assertion_type == "range":
            if isinstance(value, (int, float)):
                return value >= 0, "值应大于等于0"
        return True, "无法进行智能断言，默认通过"


if __name__ == "__main__":
    engine = AdaptiveAssertionEngine()
    for i in range(100):
        engine.record_metric("query_latency", 100 + i % 10)
    result, message = engine.assert_metric("query_latency", 150)
    print(f"断言结果: {result}, 消息: {message}")
