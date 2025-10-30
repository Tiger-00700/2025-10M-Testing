# 数据探查技术示例代码
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def perform_data_profiling(data):
    """执行数据探查分析"""
    results = {}
    
    # 1. 基本统计分析
    basic_stats = data.describe()
    results['基本统计量'] = basic_stats
    
    # 2. 数据质量概况
    quality_overview = {
        '总行数': len(data),
        '总列数': len(data.columns),
        '每列缺失值统计': data.isnull().sum(),
        '每列缺失值比例': (data.isnull().sum() / len(data) * 100).round(2)
    }
    results['数据质量概况'] = quality_overview
    
    # 3. 异常值检测（针对数值型列）
    numeric_cols = data.select_dtypes(include=['number']).columns
    outliers = {}
    
    for col in numeric_cols:
        # 使用IQR方法检测异常值
        Q1 = data[col].quantile(0.25)
        Q3 = data[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outlier_count = data[(data[col] < lower_bound) | (data[col] > upper_bound)][col].count()
        outliers[col] = {
            '异常值数量': outlier_count,
            '异常值比例(%)': (outlier_count / len(data) * 100).round(2),
            '下界': lower_bound,
            '上界': upper_bound
        }
    
    results['异常值分析'] = outliers
    
    # 4. 相关性分析（仅对数值型列）
    if len(numeric_cols) > 1:
        corr_matrix = data[numeric_cols].corr()
        results['相关性矩阵'] = corr_matrix
    
    # 5. 分类特征分析（针对分类型列）
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns
    category_analysis = {}
    
    for col in categorical_cols:
        value_counts = data[col].value_counts()
        category_analysis[col] = {
            '唯一值数量': data[col].nunique(),
            '值分布': value_counts
        }
    
    results['分类特征分析'] = category_analysis
    
    return results

def visualize_data_quality(data, output_file=None):
    """可视化数据质量状况"""
    # 设置图形风格
    plt.style.use('seaborn-v0_8-whitegrid')
    fig = plt.figure(figsize=(20, 15))
    
    # 1. 缺失值可视化
    plt.subplot(2, 2, 1)
    missing_percent = (data.isnull().sum() / len(data) * 100)
    missing_percent = missing_percent[missing_percent > 0]
    if len(missing_percent) > 0:
        missing_percent.plot(kind='bar', color='skyblue')
        plt.title('各列缺失值比例(%)')
        plt.ylabel('缺失百分比(%)')
        plt.xticks(rotation=45)
    else:
        plt.text(0.5, 0.5, '无缺失值', ha='center', va='center', transform=plt.gca().transAxes)
        plt.title('缺失值分析')
    
    # 2. 数值型数据分布
    numeric_cols = data.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        plt.subplot(2, 2, 2)
        # 选择第一个数值型列进行可视化
        sns.histplot(data[numeric_cols[0]].dropna(), kde=True)
        plt.title(f'{numeric_cols[0]} 分布')
        plt.xlabel(numeric_cols[0])
    
    # 3. 相关性热图
    if len(numeric_cols) > 1:
        plt.subplot(2, 2, 3)
        corr_matrix = data[numeric_cols].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title('数值列相关性矩阵')
    
    # 4. 分类特征可视化
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        plt.subplot(2, 2, 4)
        # 选择第一个分类型列进行可视化
        top_categories = data[categorical_cols[0]].value_counts().head(10)
        top_categories.plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.title(f'{categorical_cols[0]} 分布（前10个类别）')
        plt.ylabel('')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    plt.close()  # 关闭图形以释放内存
    return fig

# 创建示例数据集进行探查
def create_sample_data():
    # 创建一个包含1000行的混合数据集
    np.random.seed(42)
    n = 1000
    
    data = pd.DataFrame({
        # 数值型特征
        'age': np.random.normal(35, 10, n).astype(int),
        'income': np.random.lognormal(10, 0.5, n),
        'spending_score': np.random.normal(50, 15, n),
        'purchase_amount': np.random.exponential(100, n),
        
        # 分类型特征
        'gender': np.random.choice(['Male', 'Female', None], size=n, p=[0.49, 0.49, 0.02]),
        'region': np.random.choice(['North', 'South', 'East', 'West'], size=n),
        'membership_level': np.random.choice(['Bronze', 'Silver', 'Gold', 'Platinum'], 
                                            size=n, p=[0.4, 0.3, 0.2, 0.1]),
        
        # 日期型特征
        'registration_date': pd.date_range(start='2020-01-01', periods=n)
    })
    
    # 引入一些缺失值
    data.loc[np.random.choice(n, 50), 'income'] = np.nan
    data.loc[np.random.choice(n, 30), 'spending_score'] = np.nan
    
    # 引入一些异常值
    data.loc[np.random.choice(n, 10), 'income'] = data['income'].max() * np.random.uniform(2, 5, 10)
    data.loc[np.random.choice(n, 5), 'age'] = [150, 200, -10, -5, 250]  # 不合理的年龄值
    
    return data

# 执行数据探查
sample_data = create_sample_data()
profiling_results = perform_data_profiling(sample_data)

# 打印部分探查结果
print("\n=== 数据探查结果 ===")
print(f"\n数据基本信息: 行数={profiling_results['数据质量概况']['总行数']}, 列数={profiling_results['数据质量概况']['总列数']}")
print("\n缺失值统计:")
print(profiling_results['数据质量概况']['每列缺失值比例'])
print("\n异常值分析:")
for col, stats in profiling_results['异常值分析'].items():
    print(f"{col}: 异常值比例 {stats['异常值比例(%)']}%")

# 生成可视化报告
visualize_data_quality(sample_data, 'data_quality_report.png')
print("\n数据质量可视化报告已生成: data_quality_report.png")
