import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# 创建包含质量问题的交易数据集
def create_transaction_data():
    np.random.seed(42)
    
    # 基本数据
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    n_records = 1000
    
    # 生成随机交易数据
    transaction_ids = [f'TX{i:06d}' for i in range(1, n_records + 1)]
    dates = np.random.choice(dates, n_records)
    customer_ids = np.random.randint(1000, 9999, n_records)
    amounts = np.random.normal(5000, 2000, n_records).round(2)  # 正态分布的交易金额
    products = np.random.choice(['A', 'B', 'C', 'D', 'E'], n_records)
    statuses = np.random.choice(['completed', 'pending', 'failed'], n_records, p=[0.85, 0.1, 0.05])
    
    # 创建DataFrame
    df = pd.DataFrame({
        'transaction_id': transaction_ids,
        'date': dates,
        'customer_id': customer_ids,
        'amount': amounts,
        'product': products,
        'status': statuses
    })
    
    # 引入质量问题
    # 1. 添加缺失值
    df.loc[np.random.choice(df.index, 50), 'amount'] = np.nan
    df.loc[np.random.choice(df.index, 30), 'product'] = np.nan
    
    # 2. 添加异常值
    df.loc[np.random.choice(df.index, 20), 'amount'] = np.random.uniform(20000, 50000, 20).round(2)
    
    # 3. 添加错误值
    df.loc[np.random.choice(df.index, 15), 'amount'] = -abs(df.loc[np.random.choice(df.index, 15), 'amount'])
    
    # 4. 添加重复记录
    duplicate_indices = np.random.choice(df.index, 25)
    duplicates = df.loc[duplicate_indices].copy()
    df = pd.concat([df, duplicates]).reset_index(drop=True)
    
    # 5. 添加格式问题
    invalid_ids = np.random.choice(df.index, 20)
    df.loc[invalid_ids, 'transaction_id'] = df.loc[invalid_ids, 'transaction_id'].str.replace('TX', 'XX')
    
    return df

# 数据质量问题诊断
def diagnose_data_quality(df):
    print("=== 数据质量问题诊断报告 ===\n")
    
    # 1. 基本统计审计
    print("1. 数据审计基础统计:")
    print(f"   - 总记录数: {len(df)}")
    print(f"   - 唯一交易ID数: {df['transaction_id'].nunique()}")
    print(f"   - 唯一客户数: {df['customer_id'].nunique()}")
    print(f"   - 日期范围: {df['date'].min().strftime('%Y-%m-%d')} 至 {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"   - 产品类型: {', '.join(df['product'].dropna().unique())}")
    print(f"   - 交易状态分布: {dict(df['status'].value_counts())}")
    
    # 2. 缺失值分析
    missing_values = df.isnull().sum()
    print("\n2. 缺失值分析:")
    for column, count in missing_values.items():
        if count > 0:
            percent = (count / len(df)) * 100
            print(f"   - {column}: {count}个缺失值 ({percent:.2f}%)")
    
    # 3. 异常值检测
    print("\n3. 异常值检测:")
    # 使用Z-score检测异常
    if df['amount'].notnull().sum() > 0:  # 确保有非空值
        z_scores = stats.zscore(df['amount'].dropna())
        outliers = (abs(z_scores) > 3).sum()
        print(f"   - 金额异常值（Z-score > 3）: {outliers}个")
        
        # 检测负值
        negative_values = (df['amount'] < 0).sum()
        print(f"   - 负交易金额: {negative_values}个")
    
    # 4. 重复记录分析
    duplicate_rows = df.duplicated().sum()
    duplicate_transactions = df.duplicated(subset=['transaction_id']).sum()
    print("\n4. 重复记录分析:")
    print(f"   - 完全重复记录: {duplicate_rows}条")
    print(f"   - 交易ID重复: {duplicate_transactions}条")
    
    # 5. 格式问题分析
    print("\n5. 格式问题分析:")
    # 检查交易ID格式
    invalid_tx_ids = df[~df['transaction_id'].str.startswith('TX')]['transaction_id'].count()
    print(f"   - 无效交易ID格式: {invalid_tx_ids}个")
    
    # 6. 模式分析
    print("\n6. 业务模式分析:")
    # 按产品分析交易金额
    if df['amount'].notnull().sum() > 0:
        product_stats = df.groupby('product')['amount'].agg(['mean', 'std', 'count']).round(2)
        print(f"   - 各产品平均交易金额:")
        print(product_stats)
    
    # 按月分析交易数量和金额
    df['month'] = df['date'].dt.to_period('M')
    monthly_stats = df.groupby('month').agg({
        'transaction_id': 'count',
        'amount': 'sum'
    }).rename(columns={'transaction_id': 'count', 'amount': 'total_amount'})
    
    print(f"\n   - 月度交易趋势:")
    print(monthly_stats.head())
    
    # 7. 根因分析
    print("\n7. 潜在根因分析:")
    
    # 分析缺失值是否集中在特定时间段或产品
    missing_by_product = df.groupby('product')['amount'].apply(lambda x: x.isnull().sum())
    if missing_by_product.sum() > 0:
        print(f"   - 金额缺失值按产品分布:")
        print(missing_by_product[missing_by_product > 0])
    
    # 分析异常值是否集中在特定状态
    if df['amount'].notnull().sum() > 0:
        z_scores = stats.zscore(df['amount'].dropna())
        df_clean = df[df['amount'].notnull()].copy()
        df_clean['is_outlier'] = abs(z_scores) > 3
        outlier_by_status = df_clean.groupby('status')['is_outlier'].sum()
        print(f"\n   - 异常值按交易状态分布:")
        print(outlier_by_status)
    
    # 8. 影响分析
    print("\n8. 业务影响分析:")
    
    # 计算缺失数据的潜在财务影响
    if df['amount'].notnull().sum() > 0:
        avg_valid_amount = df['amount'].mean()
        missing_amount_records = df['amount'].isnull().sum()
        potential_missing_value = avg_valid_amount * missing_amount_records
        print(f"   - 缺失金额数据的潜在财务影响: {potential_missing_value:.2f}")
    
    # 计算异常值的影响
    if df['amount'].notnull().sum() > 0:
        outlier_threshold = df['amount'].mean() + 3 * df['amount'].std()
        outliers = df[df['amount'] > outlier_threshold]['amount']
        if len(outliers) > 0:
            outlier_impact = outliers.sum() - (outlier_threshold * len(outliers))
            print(f"   - 异常大额交易的影响: {outlier_impact:.2f}")
    
    return {
        'basic_stats': {'total_records': len(df), 'unique_tx': df['transaction_id'].nunique()},
        'missing_values': missing_values,
        'outliers': outliers.sum() if 'outliers' in locals() else 0,
        'duplicates': {'rows': duplicate_rows, 'transactions': duplicate_transactions},
        'format_issues': {'invalid_tx_ids': invalid_tx_ids}
    }

# 运行诊断示例
tx_df = create_transaction_data()
results = diagnose_data_quality(tx_df)
