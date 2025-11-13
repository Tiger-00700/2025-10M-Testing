"""第5篇-第14章-14.1节：测试案例设计原则 - 轻量示例

此示例为占位符，演示如何组织一个可运行的单元测试函数。
"""

def prepare_source_data(record_count=10, with_edge_cases=False):
    """生成简单的测试数据（字典列表）"""
    data = []
    for i in range(record_count):
        rec = {'id': i, 'value': i * 2}
        data.append(rec)
    if with_edge_cases:
        data.append({'id': record_count, 'value': None})
    return data


def test_batch_data_collection():
    # 1. 准备测试数据
    source_data = prepare_source_data(record_count=5, with_edge_cases=True)

    # 2. 模拟加载并校验
    assert isinstance(source_data, list)
    assert len(source_data) >= 5


if __name__ == '__main__':
    test_batch_data_collection()
    print('第14章 14.1节 示例运行成功')
