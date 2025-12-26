# 大数据简单流水线示例

这是一个入门级的大数据处理流水线示例，使用Python和Pandas进行数据处理。

## 示例代码

```python
import pandas as pd
from datetime import datetime

def simple_data_pipeline(input_file, output_file):
    """
    简单的数据处理流水线
    1. 读取数据
    2. 数据清洗
    3. 基本统计
    4. 输出结果
    """
    # 1. 读取数据
    df = pd.read_csv(input_file)
    print(f"读取了 {len(df)} 行数据")

    # 2. 数据清洗
    df = df.dropna()  # 删除缺失值
    df = df.drop_duplicates()  # 删除重复行

    # 3. 基本统计
    stats = {
        'total_rows': len(df),
        'columns': list(df.columns),
        'timestamp': datetime.now().isoformat()
    }

    # 4. 输出结果
    df.to_csv(output_file, index=False)
    print(f"处理完成，结果保存到 {output_file}")

    return stats

# 使用示例
if __name__ == "__main__":
    stats = simple_data_pipeline("input.csv", "output.csv")
    print("流水线统计:", stats)
```

## 说明

这个示例展示了大数据处理的基本步骤：
- 数据摄入
- 数据清洗和预处理
- 基本分析
- 结果输出

在实际的大数据系统中，这些步骤会使用Spark、Flink等框架进行分布式处理。