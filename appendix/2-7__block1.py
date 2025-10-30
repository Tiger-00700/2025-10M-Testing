# 大数据安全风险分析示例 - 数据访问控制风险评估
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# 模拟用户访问权限数据集
def generate_access_data(num_users=100, num_resources=50):
    """生成模拟的用户访问权限数据"""
    # 用户信息
    users = [f"user_{i}" for i in range(num_users)]
    departments = np.random.choice(['IT', 'Finance', 'HR', 'Marketing', 'Operations'], size=num_users)
    roles = np.random.choice(['Admin', 'Manager', 'Analyst', 'Developer', 'Viewer'], size=num_users)
    
    # 资源信息
    resources = [f"resource_{i}" for i in range(num_resources)]
    resource_sensitivity = np.random.choice(['Low', 'Medium', 'High', 'Critical'], size=num_resources)
    
    # 生成访问矩阵
    access_matrix = np.random.choice([0, 1], size=(num_users, num_resources), p=[0.7, 0.3])
    
    # 创建数据框
    df = pd.DataFrame(columns=['user', 'department', 'role', 'resource', 'resource_sensitivity', 'access'])
    
    records = []
    for i, user in enumerate(users):
        for j, resource in enumerate(resources):
            records.append({
                'user': user,
                'department': departments[i],
                'role': roles[i],
                'resource': resource,
                'resource_sensitivity': resource_sensitivity[j],
                'access': access_matrix[i, j]
            })
    
    return pd.DataFrame(records)

# 风险评估函数
def assess_access_risks(df):
    """评估数据访问控制风险"""
    # 1. 敏感资源访问风险分析
    sensitive_access = df[df['resource_sensitivity'].isin(['High', 'Critical']) & (df['access'] == 1)]
    risk_by_role = sensitive_access.groupby('role').size().reset_index(name='risk_count')
    
    # 2. 异常访问模式检测
    # 将用户-资源访问矩阵转换为特征向量
    pivot_df = df.pivot(index='user', columns='resource', values='access').fillna(0)
    
    # 使用K-means聚类检测异常访问模式
    kmeans = KMeans(n_clusters=5, random_state=42)
    user_clusters = kmeans.fit_predict(pivot_df)
    
    # 计算轮廓系数评估聚类质量
    silhouette_avg = silhouette_score(pivot_df, user_clusters)
    
    # 识别异常用户（离群点）
    distances = np.min(kmeans.transform(pivot_df), axis=1)
    threshold = np.percentile(distances, 95)  # 95百分位作为异常阈值
    anomalous_users = pivot_df.index[distances > threshold].tolist()
    
    # 3. 最小权限原则违反检测
    # 计算每个用户的平均访问权限数
    user_access_counts = df.groupby('user')['access'].sum()
    avg_access_per_user = user_access_counts.mean()
    
    # 识别过度授权的用户（访问权限显著高于平均值）
    overprivileged_users = user_access_counts[user_access_counts > 2 * avg_access_per_user].index.tolist()
    
    # 返回评估结果
    return {
        'risk_by_role': risk_by_role,
        'anomalous_users': anomalous_users,
        'overprivileged_users': overprivileged_users,
        'silhouette_score': silhouette_avg
    }

# 可视化风险评估结果
def visualize_risks(assessment_results):
    """可视化风险评估结果"""
    # 1. 按角色显示敏感资源访问风险
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    risk_by_role = assessment_results['risk_by_role']
    plt.bar(risk_by_role['role'], risk_by_role['risk_count'])
    plt.title('敏感资源访问风险（按角色）')
    plt.xlabel('角色')
    plt.ylabel('敏感资源访问次数')
    plt.xticks(rotation=45)
    
    # 2. 风险概览
    plt.subplot(1, 2, 2)
    risk_categories = ['异常访问模式', '过度授权用户']
    risk_counts = [len(assessment_results['anomalous_users']), len(assessment_results['overprivileged_users'])]
    plt.bar(risk_categories, risk_counts)
    plt.title('安全风险概览')
    plt.ylabel('风险实例数量')
    
    plt.tight_layout()
    plt.savefig('data_access_security_risk_assessment.png')
    plt.close()

# 主函数
def main():
    # 生成模拟数据
    access_data = generate_access_data()
    
    # 评估风险
    assessment_results = assess_access_risks(access_data)
    
    # 可视化结果
    visualize_risks(assessment_results)
    
    # 输出风险摘要
    print(f"\n安全风险评估摘要:")
    print(f"1. 异常访问模式检测到 {len(assessment_results['anomalous_users'])} 个异常用户")
    print(f"2. 最小权限原则违反检测到 {len(assessment_results['overprivileged_users'])} 个过度授权用户")
    print(f"3. 聚类质量（轮廓系数）: {assessment_results['silhouette_score']:.2f}")
    print(f"\n敏感资源访问风险（按角色）:")
    print(assessment_results['risk_by_role'])

if __name__ == "__main__":
    main()
