> 【章节重点难点总结】

- 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准
- 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡

> 【课后思考/练习题】

1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。

## 测试数据管理策略实现

> 【阅读提示】本篇聚焦：测试数据管理策略实现。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

class TestDataManager:
    def __init__(self, config):
        self.config = config
        self.data_generators = {
            'structured': StructuredDataGenerator(),
            'unstructured': UnstructuredDataGenerator(),
            'semi_structured': SemiStructuredDataGenerator()
        }
        self.data_storage = DataStorageProvider(config)
        self.data_sampler = DataSampler(config)

    def prepare_test_data(self, data_type, size_gb, characteristics=None):
        """准备测试数据"""
        # 根据数据类型选择生成器
        generator = self.data_generators.get(data_type)
        if not generator:
            raise ValueError(f"Unsupported data type: {data_type}")

        # 生成数据
        if characteristics:
            data = generator.generate(size_gb, characteristics)
        else:
            data = generator.generate_default(size_gb)

        # 存储数据
        data_id = self.data_storage.store(data, data_type)

        return {
            'data_id': data_id,
            'size_gb': size_gb,
            'type': data_type,
            'timestamp': datetime.now().isoformat()
        }

    def sample_from_production(self, source_table, sample_percent, dest_path, anonymize=True):
        """从生产环境采样数据"""
        # 采样数据
        sampled_data = self.data_sampler.sample(source_table, sample_percent)

        # 匿名化处理
        if anonymize:
            anonymizer = DataAnonymizer(self.config)
            sampled_data = anonymizer.anonymize(sampled_data)

        # 存储采样数据
        self.data_storage.save(sampled_data, dest_path)

        return {
            'source_table': source_table,
            'sample_percent': sample_percent,
            'dest_path': dest_path,
            'anonymized': anonymize
        }

    def generate_edge_cases(self, template, variations=10):
        """生成边界条件测试数据"""
        edge_case_generator = EdgeCaseGenerator()
        return edge_case_generator.generate(template, variations)

    def cleanup(self, data_ids=None):
        """清理测试数据"""
        if data_ids:
            for data_id in data_ids:
                self.data_storage.delete(data_id)
        else:
            # 清理所有临时测试数据
            self.data_storage.cleanup_temp_data()

## 结构化数据生成器示例

> 【阅读提示】本篇聚焦：结构化数据生成器示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

class StructuredDataGenerator:
    def generate(self, size_gb, characteristics):
        """生成结构化测试数据"""
        # 实现数据生成逻辑
        pass

    def generate_default(self, size_gb):
        """生成默认结构的测试数据"""
        # 默认数据结构生成
        pass
