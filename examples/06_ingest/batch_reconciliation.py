# batch_reconciliation.py
# 批采集完整性对账脚本示例

import pandas as pd
from sqlalchemy import create_engine

def reconcile_batch_ingestion(source_table, target_table, key_column, db_url):
    """
    对账批采集完整性
    :param source_table: 源表名
    :param target_table: 目标表名
    :param key_column: 主键列名
    :param db_url: 数据库连接URL
    :return: 对账结果字典
    """
    engine = create_engine(db_url)

    # 查询源端记录数和主键集合
    source_query = f"SELECT COUNT(*) as count, ARRAY_AGG({key_column}) as keys FROM {source_table}"
    source_df = pd.read_sql(source_query, engine)

    # 查询目标端记录数和主键集合
    target_query = f"SELECT COUNT(*) as count, ARRAY_AGG({key_column}) as keys FROM {target_table}"
    target_df = pd.read_sql(target_query, engine)

    # 计算差异
    source_count = source_df['count'].iloc[0]
    target_count = target_df['count'].iloc[0]
    count_diff = source_count - target_count

    # 简单主键集合比较（实际中可能需要更复杂的集合运算）
    source_keys = set(source_df['keys'].iloc[0] or [])
    target_keys = set(target_df['keys'].iloc[0] or [])
    missing_keys = source_keys - target_keys
    extra_keys = target_keys - source_keys

    return {
        'source_count': source_count,
        'target_count': target_count,
        'count_diff': count_diff,
        'missing_keys_count': len(missing_keys),
        'extra_keys_count': len(extra_keys),
        'is_complete': count_diff == 0 and len(missing_keys) == 0
    }

# 示例使用
if __name__ == "__main__":
    result = reconcile_batch_ingestion('source_orders', 'target_orders', 'order_id', 'postgresql://user:pass@localhost/db')
    print(f"对账结果: {result}")