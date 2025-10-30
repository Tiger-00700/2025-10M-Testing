# 数据质量抽样测试策略示例代码
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

class DataSamplingStrategy:
    """数据抽样策略类"""
    
    @staticmethod
    def random_sampling(data, sample_size, random_state=None):
        """随机抽样"""
        # 如果样本量大于数据总量，返回全部数据
        if sample_size >= len(data):
            return data.copy()
        
        return data.sample(n=sample_size, random_state=random_state)
    
    @staticmethod
    def stratified_sampling(data, stratify_col, sample_size, random_state=None):
        """分层抽样"""
        # 计算每个分层的比例
        stratify_counts = data[stratify_col].value_counts()
        total_count = len(data)
        
        # 确保每个分层至少有一个样本
        min_samples_per_stratum = 1
        total_min_samples = len(stratify_counts) * min_samples_per_stratum
        
        if sample_size < total_min_samples:
            raise ValueError(f"样本量 {sample_size} 小于最小所需样本量 {total_min_samples}")
        
        # 计算每个分层的样本量
        samples = []
        remaining_samples = sample_size
        
        # 首先为每个分层分配最小样本量
        for stratum in stratify_counts.index:
            samples.append(data[data[stratify_col] == stratum].sample(
                n=min_samples_per_stratum, random_state=random_state))
            remaining_samples -= min_samples_per_stratum
        
        # 分配剩余样本量
        for stratum in stratify_counts.index:
            stratum_size = stratify_counts[stratum]
            # 按比例分配剩余样本，但不超过该分层的实际数量
            proportional_size = int(remaining_samples * (stratum_size / total_count))
            max_possible = stratum_size - min_samples_per_stratum
            actual_size = min(proportional_size, max_possible)
            
            if actual_size > 0:
                additional_samples = data[data[stratify_col] == stratum].sample(
                    n=actual_size, random_state=random_state + 1 if random_state is not None else None)
                samples.append(additional_samples)
                remaining_samples -= actual_size
        
        # 如果还有剩余样本，随机分配给各分层
        while remaining_samples > 0:
            for stratum in stratify_counts.index:
                stratum_data = data[data[stratify_col] == stratum]
                # 找出尚未被采样的记录
                already_sampled_indices = set()
                for s in samples:
                    already_sampled_indices.update(s.index)
                
                available = stratum_data[~stratum_data.index.isin(already_sampled_indices)]
                
                if len(available) > 0:
                    samples.append(available.sample(n=1, random_state=random_state + 2 if random_state is not None else None))
                    remaining_samples -= 1
                    if remaining_samples <= 0:
                        break
        
        return pd.concat(samples)
    
    @staticmethod
    def importance_sampling(data, importance_col, sample_size, random_state=None):
        """重要性抽样 - 基于某列值的重要性进行抽样"""
        # 假设越大的值越重要，使用值的相对大小作为权重
        weights = data[importance_col] / data[importance_col].sum()
        
        # 确保权重总和为1
        weights = weights / weights.sum()
        
        # 基于权重进行抽样
        sample_indices = np.random.choice(data.index, size=sample_size, replace=False, p=weights)
        return data.loc[sample_indices]
    
    @staticmethod
    def systematic_sampling(data, sample_size, random_state=None):
        """系统抽样"""
        np.random.seed(random_state)
        
        population_size = len(data)
        interval = population_size / sample_size
        
        # 随机选择起始点
        start = np.random.randint(0, interval)
        
        # 按照固定间隔选择样本
        indices = [int(start + i * interval) for i in range(sample_size)]
        
        # 确保索引在有效范围内
        indices = [i for i in indices if i < population_size]
        
        return data.iloc[indices]
    
    @staticmethod
    def time_series_sampling(data, time_col, sample_size, frequency='D', random_state=None):
        """时间序列抽样"""
        # 确保时间列是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(data[time_col]):
            data = data.copy()
            data[time_col] = pd.to_datetime(data[time_col])
        
        # 按指定频率重采样并计算每个时间段的记录数
        time_groups = data.groupby(pd.Grouper(key=time_col, freq=frequency))
        time_periods = list(time_groups.groups.keys())
        
        # 如果时间段数少于样本量，直接返回所有时间段的样本
        if len(time_periods) <= sample_size:
            samples = []
            for period in time_periods:
                # 每个时间段取一个样本
                period_data = time_groups.get_group(period)
                if len(period_data) > 0:
                    samples.append(period_data.sample(1, random_state=random_state))
            return pd.concat(samples) if samples else pd.DataFrame()
        
        # 否则，随机选择时间段
        selected_periods = np.random.choice(time_periods, size=sample_size, replace=False)
        
        samples = []
        for period in selected_periods:
            period_data = time_groups.get_group(period)
            if len(period_data) > 0:
                samples.append(period_data.sample(1, random_state=random_state))
        
        return pd.concat(samples) if samples else pd.DataFrame()

class SampleSizeCalculator:
    """样本量计算器"""
    
    @staticmethod
    def calculate_sample_size(population_size, confidence_level=0.95, margin_of_error=0.05):
        """计算所需样本量
        
        使用有限总体校正的样本量计算公式
        
        参数:
        population_size: 总体大小
        confidence_level: 置信水平
        margin_of_error: 边际误差
        
        返回:
        所需样本量
        """
        # 标准正态分布的z值
        z_score = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}.get(confidence_level, 1.96)
        
        # 假设总体比例为0.5（最保守的估计）
        p = 0.5
        
        # 无限总体的样本量
        n0 = (z_score ** 2 * p * (1 - p)) / (margin_of_error ** 2)
        
        # 应用有限总体校正
        n = n0 / (1 + (n0 - 1) / population_size)
        
        # 返回向上取整的样本量
        return max(1, int(np.ceil(n)))

# 抽样效果评估函数
def evaluate_sampling_quality(original_data, sample_data, numeric_cols):
    """评估抽样质量"""
    results = {
        'original_size': len(original_data),
        'sample_size': len(sample_data),
        'sampling_rate': len(sample_data) / len(original_data),
        'distribution_comparison': {}
    }
    
    for col in numeric_cols:
        # 计算原始数据和样本数据的统计量
        orig_mean = original_data[col].mean()
        orig_std = original_data[col].std()
        sample_mean = sample_data[col].mean()
        sample_std = sample_data[col].std()
        
        # 计算均值差异百分比
        mean_diff_pct = abs(orig_mean - sample_mean) / orig_mean * 100 if orig_mean != 0 else 0
        
        # 执行t检验，检查样本均值是否与总体均值显著不同
        try:
            t_stat, p_value = stats.ttest_ind_from_stats(
                mean1=orig_mean, std1=orig_std, nobs1=len(original_data),
                mean2=sample_mean, std2=sample_std, nobs2=len(sample_data),
                equal_var=False
            )
        except:
            t_stat, p_value = 0, 1.0
        
        results['distribution_comparison'][col] = {
            'original_mean': orig_mean,
            'sample_mean': sample_mean,
            'mean_diff_percent': mean_diff_pct,
            'original_std': orig_std,
            'sample_std': sample_std,
            't_statistic': t_stat,
            'p_value': p_value,
            'distributions_similar': p_value > 0.05  # 95%置信水平
        }
    
    # 计算整体抽样质量评分（基于分布相似性）
    similar_count = sum(1 for col_stats in results['distribution_comparison'].values() 
                      if col_stats['distributions_similar'])
    total_cols = len(results['distribution_comparison'])
    
    if total_cols > 0:
        quality_score = (similar_count / total_cols) * 100
        results['overall_quality_score'] = quality_score
        results['quality_rating'] = '良好' if quality_score >= 80 else '一般' if quality_score >= 60 else '较差'
    
    return results

# 可视化抽样分布对比
def visualize_sampling_comparison(original_data, sample_data, numeric_cols):
    """可视化原始数据和样本数据的分布对比"""
    n_cols = min(2, len(numeric_cols))
    n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 4 * n_rows))
    axes = axes.flatten() if n_rows > 1 else [axes]
    
    for i, col in enumerate(numeric_cols):
        ax = axes[i]
        
        # 绘制原始数据分布
        ax.hist(original_data[col].dropna(), bins=30, alpha=0.5, label='原始数据', color='blue')
        
        # 绘制样本数据分布
        ax.hist(sample_data[col].dropna(), bins=30, alpha=0.5, label='样本数据', color='red')
        
        ax.set_title(f'{col} 分布对比')
        ax.set_xlabel(col)
        ax.set_ylabel('频率')
        ax.legend()
    
    # 删除多余的子图
    for i in range(len(numeric_cols), len(axes)):
        fig.delaxes(axes[i])
    
    plt.tight_layout()
    plt.savefig('sampling_distribution_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

# 示例：使用不同的抽样策略并评估效果
def sampling_strategy_example():
    # 创建测试数据
    np.random.seed(42)
    n = 10000
    
    # 创建一个包含多种特征的大数据集
    data = pd.DataFrame({
        'id': range(1, n + 1),
        'age': np.random.normal(40, 10, n).astype(int),
        'income': np.random.lognormal(10, 0.5, n),
        'purchase_amount': np.random.exponential(150, n),
        'region': np.random.choice(['North', 'South', 'East', 'West'], size=n, p=[0.3, 0.25, 0.25, 0.2]),
        'customer_segment': np.random.choice(['Low', 'Medium', 'High'], size=n, p=[0.5, 0.3, 0.2]),
        'transaction_date': pd.date_range(start='2023-01-01', periods=n, freq='H') + 
                           pd.to_timedelta(np.random.randint(0, 24, n), unit='h')
    })
    
    # 确保年龄为正数
    data['age'] = np.abs(data['age'])
    
    # 定义数值型列用于评估
    numeric_cols = ['age', 'income', 'purchase_amount']
    
    # 计算所需样本量
    calc = SampleSizeCalculator()
    required_sample_size = calc.calculate_sample_size(len(data), confidence_level=0.95, margin_of_error=0.05)
    print(f"\n总体大小: {len(data)}")
    print(f"建议样本量 (95%置信水平，5%误差): {required_sample_size}")
    
    # 定义抽样策略
    sampling = DataSamplingStrategy()
    strategies = {
        '随机抽样': lambda: sampling.random_sampling(data, required_sample_size, random_state=42),
        '分层抽样(按地区)': lambda: sampling.stratified_sampling(data, 'region', required_sample_size, random_state=42),
        '分层抽样(按客户细分)': lambda: sampling.stratified_sampling(data, 'customer_segment', required_sample_size, random_state=42),
        '重要性抽样(按购买金额)': lambda: sampling.importance_sampling(data, 'purchase_amount', required_sample_size, random_state=42),
        '系统抽样': lambda: sampling.systematic_sampling(data, required_sample_size, random_state=42),
        '时间序列抽样': lambda: sampling.time_series_sampling(data, 'transaction_date', required_sample_size, frequency='D', random_state=42)
    }
    
    # 比较不同抽样策略的效果
    results = {}
    for strategy_name, strategy_func in strategies.items():
        try:
            sample = strategy_func()
            
            # 跳过空样本
            if len(sample) == 0:
                continue
                
            # 评估抽样质量
            quality = evaluate_sampling_quality(data, sample, numeric_cols)
            results[strategy_name] = quality
            
            print(f"\n--- {strategy_name} ---")
            print(f"样本大小: {quality['sample_size']}")
            print(f"抽样率: {quality['sampling_rate']:.2%}")
            print(f"质量评分: {quality.get('overall_quality_score', 0):.1f}% ({quality.get('quality_rating', '未知')})")
            
            print("分布比较:")
            for col, stats in quality['distribution_comparison'].items():
                print(f"  {col}: 均值差异 {stats['mean_diff_percent']:.1f}%, p值 {stats['p_value']:.4f}")
                
            # 为第一个策略生成可视化
            if strategy_name == '随机抽样':
                visualize_sampling_comparison(data, sample, numeric_cols)
                print("\n已生成抽样分布对比图: sampling_distribution_comparison.png")
                
        except Exception as e:
            print(f"\n--- {strategy_name} 执行失败 ---")
            print(f"错误: {str(e)}")
    
    # 找出最佳抽样策略
    best_strategy = None
    best_score = -1
    
    for strategy_name, quality in results.items():
        score = quality.get('overall_quality_score', 0)
        if score > best_score:
            best_score = score
            best_strategy = strategy_name
    
    if best_strategy:
        print(f"\n最佳抽样策略: {best_strategy} (质量评分: {best_score:.1f}%)")

# 运行抽样策略示例
sampling_strategy_example()
