"""第5篇-第14章-14.2节：数据存储测试用例 - 本地模拟示例

示例演示如何用本地文件系统模拟“写入/读取”存储测试逻辑，避免依赖 HDFS。
"""
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent / 'data_tmp'
TEST_DIR.mkdir(exist_ok=True)


def write_to_storage(data, filename='test_data.csv'):
    path = TEST_DIR / filename
    with path.open('w', encoding='utf-8') as f:
        for rec in data:
            f.write(f"{rec.get('id')},{rec.get('value')}\n")
    return path


def read_from_storage(path):
    with path.open('r', encoding='utf-8') as f:
        return [line.strip() for line in f]


def test_hdfs_data_storage():
    data = [{'id': i, 'value': i * 3} for i in range(3)]
    p = write_to_storage(data, 'sample.csv')
    lines = read_from_storage(p)
    assert len(lines) == len(data)


if __name__ == '__main__':
    test_hdfs_data_storage()
    print('第14章 14.2节 示例运行成功')
