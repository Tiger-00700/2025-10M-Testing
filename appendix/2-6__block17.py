import pandas as pd
import numpy as np
import re
from datetime import datetime

# 创建包含质量问题的样本数据
def create_dirty_data():
    # 客户数据
    customers = {
        'customer_id': [101, 102, 103, 104, 105, 102, 107],  # 重复ID
        'name': ['John Doe', 'Jane Smith', 'Bob Johnson', np.nan, 'Alice Brown', 'Jane Smith', 'Charlie Davis'],  # 缺失值
        'email': ['john.doe@example.com', 'jane.smith@', 'bob.johnson@example.com', 'invalid-email', 'alice@example.com', 'jane.smith@example.com', 'charlie@example.com'],  # 格式错误
        'phone': ['123-456-7890', '234-567-8901', '345-678-9012', '456-789-0123', '567-8901234', '234-567-8901', '678-901-2345'],  # 格式不一致
        'birth_date': ['1985-05-15', '1990/08/22', '1975.12.10', '1995-03-01', np.nan, '1990-08-22', '1988-07-19'],  # 格式不一致和缺失值
        'income': [50000, 60000, 1500000, 45000, -5000, 60000, 75000]  # 异常值和负值
    }
    
    return pd.DataFrame(customers)

# 数据清洗函数
def clean_data(df):
    print("=== 数据清洗过程 ===\n")
    
    # 创建数据副本以避免修改原始数据
    cleaned_df = df.copy()
    print("原始数据:")
    print(cleaned_df)
    print(f"\n原始记录数: {len(cleaned_df)}")
    
    # 1. 处理缺失值
    print("\n1. 处理缺失值:")
    
    # 统计缺失值
    missing_before = cleaned_df.isnull().sum()
    print(f"   清洗前缺失值: {missing_before}")
    
    # 对于'name'列的缺失值，使用'Unknown'
    cleaned_df['name'].fillna('Unknown', inplace=True)
    
    # 对于'birth_date'列的缺失值，暂时保留为NaT（后面会转换为日期类型）
    # 实际业务中可能需要其他处理方式
    
    # 2. 处理异常值
    print("\n2. 处理异常值:")
    
    # 识别income列的异常值（使用IQR方法）
    Q1 = cleaned_df['income'].quantile(0.25)
    Q3 = cleaned_df['income'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = cleaned_df[(cleaned_df['income'] < lower_bound) | (cleaned_df['income'] > upper_bound)]
    print(f"   识别到的异常值: {len(outliers)}")
    print(f"   异常值范围: 小于{lower_bound}或大于{upper_bound}")
    
    # 处理income列的负值和异常值
    # 对于负值，设置为0
    cleaned_df.loc[cleaned_df['income'] < 0, 'income'] = 0
    
    # 对于超出上界的异常值，使用上界值
    cleaned_df.loc[cleaned_df['income'] > upper_bound, 'income'] = upper_bound
    
    # 3. 处理重复值
    print("\n3. 处理重复值:")
    
    # 检测重复行
    duplicates = cleaned_df.duplicated().sum()
    print(f"   重复行数量: {duplicates}")
    
    # 根据customer_id删除重复记录，保留第一条
    cleaned_df.drop_duplicates(subset=['customer_id'], keep='first', inplace=True)
    print(f"   删除重复后记录数: {len(cleaned_df)}")
    
    # 4. 格式标准化
    print("\n4. 格式标准化:")
    
    # 标准化email格式（简单验证）
    def is_valid_email(email):
        if pd.isna(email):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email)))
    
    invalid_emails = cleaned_df[~cleaned_df['email'].apply(is_valid_email)]
    print(f"   无效邮箱数量: {len(invalid_emails)}")
    
    # 标记无效邮箱
    cleaned_df.loc[~cleaned_df['email'].apply(is_valid_email), 'email'] = 'invalid-email@example.com'
    
    # 标准化电话号码格式
    def standardize_phone(phone):
        if pd.isna(phone):
            return phone
        # 提取所有数字
        digits = re.sub(r'\D', '', str(phone))
        # 假设都是10位电话号码，格式化为xxx-xxx-xxxx
        if len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        return phone
    
    cleaned_df['phone'] = cleaned_df['phone'].apply(standardize_phone)
    
    # 标准化出生日期格式
    def standardize_date(date_str):
        if pd.isna(date_str):
            return pd.NaT
        
        # 尝试多种日期格式
        formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d']
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt)
            except ValueError:
                continue
        return pd.NaT
    
    cleaned_df['birth_date'] = cleaned_df['birth_date'].apply(standardize_date)
    
    # 5. 数据转换
    print("\n5. 数据转换:")
    
    # 计算年龄（基于生日）
    today = datetime.now()
    cleaned_df['age'] = cleaned_df['birth_date'].apply(
        lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day)) if pd.notna(x) else pd.NA
    )
    
    # 收入分类
    def categorize_income(income):
        if income < 30000:
            return 'Low'
        elif income < 70000:
            return 'Medium'
        else:
            return 'High'
    
    cleaned_df['income_category'] = cleaned_df['income'].apply(categorize_income)
    
    # 6. 应用业务规则
    print("\n6. 应用业务规则:")
    
    # 业务规则1: 确保所有客户都有有效的标识符
    cleaned_df['customer_id'] = cleaned_df['customer_id'].astype(int)
    
    # 业务规则2: 验证年龄的合理性（18-120岁）
    age_invalid = cleaned_df[(cleaned_df['age'] < 18) | (cleaned_df['age'] > 120)]
    print(f"   无效年龄记录数量: {len(age_invalid)}")
    
    # 标记无效年龄
    cleaned_df.loc[(cleaned_df['age'] < 18) | (cleaned_df['age'] > 120), 'age'] = pd.NA
    
    print("\n清洗后的数据:")
    print(cleaned_df)
    
    # 7. 验证清洗结果
    print("\n7. 清洗结果验证:")
    
    # 检查剩余缺失值
    missing_after = cleaned_df.isnull().sum()
    print(f"   清洗后缺失值: {missing_after}")
    
    # 检查是否还有负值收入
    negative_income = (cleaned_df['income'] < 0).sum()
    print(f"   负值收入记录: {negative_income}")
    
    # 检查重复客户ID
    duplicate_ids = cleaned_df['customer_id'].duplicated().sum()
    print(f"   重复客户ID: {duplicate_ids}")
    
    return cleaned_df

# 运行数据清洗示例
dirty_df = create_dirty_data()
cleaned_data = clean_data(dirty_df)
