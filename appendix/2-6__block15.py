import pandas as pd
import numpy as np
import re
from datetime import datetime

# 创建示例数据集
def create_sample_data():
    # 创建包含各类数据质量问题的示例数据
    data = {
        'customer_id': [1, 2, 3, 4, 5, 2, 7],  # 重复的customer_id=2
        'name': ['张三', '李四', '王五', np.nan, '赵六', '李四', '钱七'],  # 缺失值
        'phone': ['13812345678', '139abcdefgh', '13709876543', '13612345678', None, '13909876543', '13512345678'],  # 格式错误和缺失值
        'email': ['zhangsan@example.com', 'lisi@example', 'wangwu@example.com', 'invalid-email', 'zhaoliu@example.com', 'lisi@example.com', 'qianqi@example.com'],  # 格式错误
        'address': ['北京市朝阳区', None, '上海市浦东新区', '广州市天河区', '深圳市南山区', '北京市海淀区', '杭州市西湖区'],  # 缺失值和不一致（李四有两个地址）
        'registration_date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05', '2021-12-01', '2023-02-20', '2023-05-15'],  # 可能的过时数据
        'last_login': ['2023-12-01', '2023-11-15', '2023-12-10', '2022-06-20', '2023-12-05', '2023-11-15', '2023-12-08']  # 可能的过时数据
    }
    
    return pd.DataFrame(data)

# 检测数据质量问题
def detect_data_quality_issues(df):
    print("=== 数据质量问题检测报告 ===\n")
    
    # 1. 检测缺失数据
    missing_data = df.isnull().sum()
    print("1. 缺失数据检测:")
    for column, count in missing_data.items():
        if count > 0:
            percent = (count / len(df)) * 100
            print(f"   - {column}: {count}条记录缺失 ({percent:.2f}%)")
    
    # 2. 检测重复数据
    duplicate_rows = df.duplicated().sum()
    print(f"\n2. 重复记录检测:")
    print(f"   - 发现{duplicate_rows}条完全重复的记录")
    
    # 检测特定字段的重复值
    duplicate_customer_ids = df['customer_id'].duplicated().sum()
    print(f"   - customer_id字段: 发现{duplicate_customer_ids}个重复值")
    
    # 3. 检测错误数据
    print("\n3. 错误数据检测:")
    
    # 手机号格式验证（中国大陆手机号）
    valid_phone_pattern = r'^1[3-9]\d{9}$'
    invalid_phones = df[~df['phone'].str.match(valid_phone_pattern, na=False)]['phone'].count()
    print(f"   - 手机号格式错误: {invalid_phones}条记录")
    
    # 邮箱格式验证
    valid_email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    invalid_emails = df[~df['email'].str.match(valid_email_pattern, na=False)]['email'].count()
    print(f"   - 邮箱格式错误: {invalid_emails}条记录")
    
    # 4. 检测不一致数据
    print("\n4. 不一致数据检测:")
    
    # 检查同一客户是否有不同地址
    customer_addresses = df.groupby('customer_id')['address'].nunique()
    inconsistent_customers = customer_addresses[customer_addresses > 1].count()
    print(f"   - 发现{inconsistent_customers}个客户存在多个不同的地址")
    
    # 5. 检测过时数据
    print("\n5. 过时数据检测:")
    
    current_date = datetime.now()
    df['registration_date'] = pd.to_datetime(df['registration_date'])
    df['last_login'] = pd.to_datetime(df['last_login'])
    
    # 注册时间超过2年的数据
    outdated_registration = (current_date.year - df['registration_date'].dt.year > 2).sum()
    print(f"   - 注册时间超过2年: {outdated_registration}条记录")
    
    # 超过6个月未登录的数据
    six_months_ago = current_date - pd.DateOffset(months=6)
    inactive_accounts = (df['last_login'] < six_months_ago).sum()
    print(f"   - 超过6个月未登录: {inactive_accounts}条记录")
    
    # 6. 格式错误汇总
    print("\n6. 格式错误汇总:")
    print(f"   - 手机号格式错误: {invalid_phones}条记录")
    print(f"   - 邮箱格式错误: {invalid_emails}条记录")
    
    # 返回问题检测结果，便于后续处理
    return {
        'missing_data': missing_data,
        'duplicate_rows': duplicate_rows,
        'duplicate_customer_ids': duplicate_customer_ids,
        'invalid_phones': invalid_phones,
        'invalid_emails': invalid_emails,
        'inconsistent_customers': inconsistent_customers,
        'outdated_registration': outdated_registration,
        'inactive_accounts': inactive_accounts
    }

# 运行示例
df = create_sample_data()
issues = detect_data_quality_issues(df)
print("\n=== 数据示例 ===")
print(df)
