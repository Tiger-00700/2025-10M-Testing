"""
RootCauseAnalyzer

Extracted from book (Chapter 20). Lightweight example for root-cause suggestion.
"""


class RootCauseAnalyzer:
    def __init__(self):
        self.knowledge_base = {}
        self.load_knowledge_base()

    def load_knowledge_base(self):
        # 加载知识库（简化为硬编码示例）
        self.knowledge_base = {
            "数据格式错误": {
                "patterns": ["schema validation", "format error", "type mismatch"],
                "possible_causes": ["数据生成逻辑错误", "源数据变更", "序列化/反序列化问题"],
            },
            "性能下降": {
                "patterns": ["timeout", "latency", "slow response"],
                "possible_causes": ["资源不足", "查询优化问题", "数据量增长", "死锁"],
            },
            "内存泄漏": {
                "patterns": ["OutOfMemoryError", "memory usage increasing"],
                "possible_causes": ["未释放资源", "缓存过大", "递归过深"],
            },
        }

    def analyze(self, error_message, test_results):
        possible_causes = []
        for issue, details in self.knowledge_base.items():
            for pattern in details["patterns"]:
                if pattern.lower() in error_message.lower():
                    possible_causes.extend(details["possible_causes"])
                    break

        possible_causes = list(set(possible_causes))
        return {
            "error": error_message,
            "possible_causes": possible_causes,
            "suggested_actions": self._generate_actions(possible_causes),
        }

    def _generate_actions(self, causes):
        actions = []
        for cause in causes:
            if "数据" in cause:
                actions.append("检查数据格式和内容")
            elif "资源" in cause:
                actions.append("增加资源配额或优化资源使用")
            elif "查询" in cause:
                actions.append("检查并优化查询语句")
        return actions


if __name__ == "__main__":
    analyzer = RootCauseAnalyzer()
    result = analyzer.analyze("测试失败: Schema validation error in field 'timestamp'", {})
    print(f"可能的根本原因: {result['possible_causes']}")
    print(f"建议行动: {result['suggested_actions']}")
