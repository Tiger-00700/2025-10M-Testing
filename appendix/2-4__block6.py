import pandas as pd
import numpy as np
import sqlite3
import hashlib
import time

def setup_test_data():
    """设置测试数据和数据库"""
    # 创建内存数据库连接
    source_conn = sqlite3.connect(':memory:')
    target_conn = sqlite3.connect(':memory:')
    
    # 创建源表并插入测试数据
    source_cursor = source_conn.cursor()
    source_cursor.execute('''
        CREATE TABLE source_sales (
            transaction_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            sale_date TEXT,
            amount REAL,
            currency TEXT,
            status TEXT
        )
    ''')
    
    # 插入测试数据
    test_data = [
        (1, 101, 201, '2023-01-01', 100.50, 'USD', 'COMPLETED'),
        (2, 102, 202, '2023-01-02', 200.75, 'USD', 'COMPLETED'),
        (3, 103, 203, '2023-01-03', 300.25, 'EUR', 'COMPLETED'),
        (4, 101, 201, '2023-01-04', 400.00, 'USD', 'CANCELLED'),
        (5, 104, 202, '2023-01-05', 500.00, 'USD', 'COMPLETED')
    ]
    
    source_cursor.executemany(
        "INSERT INTO source_sales VALUES (?, ?, ?, ?, ?, ?, ?)", 
        test_data
    )
    source_conn.commit()
    
    # 创建目标表
    target_cursor = target_conn.cursor()
    target_cursor.execute('''
        CREATE TABLE dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date TEXT,
            year INTEGER,
            quarter INTEGER,
            month INTEGER,
            day INTEGER
        )
    ''')
    
    target_cursor.execute('''
        CREATE TABLE fact_sales (
            fact_id INTEGER PRIMARY KEY,
            transaction_id INTEGER,
            customer_id INTEGER,
            product_id INTEGER,
            date_key INTEGER,
            amount_usd REAL,
            status TEXT,
            etl_timestamp TEXT
        )
    ''')
    
    return source_conn, target_conn

def etl_process(source_conn, target_conn, eur_to_usd_rate=1.10):
    """模拟ETL过程"""
    source_df = pd.read_sql_query("SELECT * FROM source_sales", source_conn)
    
    # 提取日期维度数据
    date_dim = source_df[['sale_date']].drop_duplicates()
    date_dim['date_datetime'] = pd.to_datetime(date_dim['sale_date'])
    date_dim['year'] = date_dim['date_datetime'].dt.year
    date_dim['quarter'] = date_dim['date_datetime'].dt.quarter
    date_dim['month'] = date_dim['date_datetime'].dt.month
    date_dim['day'] = date_dim['date_datetime'].dt.day
    date_dim['date_key'] = date_dim['date_datetime'].dt.strftime('%Y%m%d').astype(int)
    date_dim = date_dim[['date_key', 'sale_date', 'year', 'quarter', 'month', 'day']]
    date_dim = date_dim.rename(columns={'sale_date': 'full_date'})
    
    # 转换销售事实数据
    fact_df = source_df.copy()
    fact_df['date_datetime'] = pd.to_datetime(fact_df['sale_date'])
    fact_df['date_key'] = fact_df['date_datetime'].dt.strftime('%Y%m%d').astype(int)
    
    # 转换货币为USD
    fact_df['amount_usd'] = np.where(
        fact_df['currency'] == 'EUR',
        fact_df['amount'] * eur_to_usd_rate,
        fact_df['amount']
    )
    
    # 仅保留已完成交易
    fact_df = fact_df[fact_df['status'] == 'COMPLETED']
    
    fact_df['etl_timestamp'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    fact_df = fact_df[[
        'transaction_id', 'customer_id', 'product_id', 
        'date_key', 'amount_usd', 'status', 'etl_timestamp'
    ]]
    fact_df['fact_id'] = range(1, len(fact_df) + 1)
    
    # 加载到目标表
    date_dim.to_sql('dim_date', target_conn, if_exists='append', index=False)
    fact_df.to_sql('fact_sales', target_conn, if_exists='append', index=False)
    target_conn.commit()
    
    return source_df, fact_df

def test_extraction_completeness(source_df, fact_df):
    """测试数据提取的完整性"""
    print("=== 测试数据提取完整性 ===")
    
    # 检查已完成交易的数量
    source_completed_count = len(source_df[source_df['status'] == 'COMPLETED'])
    target_record_count = len(fact_df)
    
    print(f"源系统已完成交易数: {source_completed_count}")
    print(f"目标系统记录数: {target_record_count}")
    
    assert source_completed_count == target_record_count, \
        f"数据提取不完整，源系统{source_completed_count}条已完成交易，但目标系统只有{target_record_count}条记录"
    
    print("数据提取完整性测试通过")

def test_transformation_rules(source_df, fact_df):
    """测试数据转换规则"""
    print("=== 测试数据转换规则 ===")
    
    # 检查USD金额转换
    test_usd_record = source_df[(source_df['transaction_id'] == 1) & (source_df['currency'] == 'USD')]
    test_target_record = fact_df[fact_df['transaction_id'] == 1]
    
    assert test_target_record['amount_usd'].iloc[0] == test_usd_record['amount'].iloc[0], \
        "USD金额未正确转换"
    
    # 检查EUR金额转换（汇率为1.10）
    test_eur_record = source_df[(source_df['transaction_id'] == 3) & (source_df['currency'] == 'EUR')]
    test_eur_target_record = fact_df[fact_df['transaction_id'] == 3]
    expected_usd_amount = test_eur_record['amount'].iloc[0] * 1.10
    
    assert abs(test_eur_target_record['amount_usd'].iloc[0] - expected_usd_amount) < 0.001, \
        "EUR金额转换不正确"
    
    # 检查已取消交易是否被过滤
    cancelled_in_target = fact_df[fact_df['status'] == 'CANCELLED']
    assert len(cancelled_in_target) == 0, "已取消的交易未被正确过滤"
    
    print("数据转换规则测试通过")

def test_data_consistency(source_conn, target_conn):
    """测试数据一致性"""
    print("=== 测试数据一致性 ===")
    
    # 计算源系统已完成交易的总金额
    source_cursor = source_conn.cursor()
    source_cursor.execute("""
        SELECT SUM(CASE WHEN currency = 'EUR' THEN amount * 1.10 ELSE amount END) 
        FROM source_sales 
        WHERE status = 'COMPLETED'
    """)
    source_total = source_cursor.fetchone()[0]
    
    # 计算目标系统的总金额
    target_cursor = target_conn.cursor()
    target_cursor.execute("SELECT SUM(amount_usd) FROM fact_sales")
    target_total = target_cursor.fetchone()[0]
    
    print(f"源系统已转换总金额: {source_total}")
    print(f"目标系统总金额: {target_total}")
    
    assert abs(source_total - target_total) < 0.001, \
        f"数据不一致，源系统总金额{source_total}与目标系统总金额{target_total}不匹配"
    
    print("数据一致性测试通过")

def test_performance(source_conn, target_conn):
    """测试ETL性能"""
    print("=== 测试ETL性能 ===")
    
    # 测量ETL处理时间
    start_time = time.time()
    etl_process(source_conn, target_conn)
    elapsed_time = time.time() - start_time
    
    print(f"ETL处理耗时: {elapsed_time:.4f} 秒")
    
    # 在实际测试中，可以设置性能阈值
    # 例如：assert elapsed_time < 1.0, "ETL处理性能未达标"

# 运行测试
if __name__ == "__main__":
    source_conn, target_conn = setup_test_data()
    source_df, fact_df = etl_process(source_conn, target_conn)
    test_extraction_completeness(source_df, fact_df)
    test_transformation_rules(source_df, fact_df)
    test_data_consistency(source_conn, target_conn)
    test_performance(source_conn, target_conn)
    
    source_conn.close()
    target_conn.close()
