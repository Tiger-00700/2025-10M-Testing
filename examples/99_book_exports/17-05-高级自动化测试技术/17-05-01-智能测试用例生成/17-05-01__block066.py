> 【章节重点难点总结】

- 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准
- 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡

> 【课后思考/练习题】

1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。

## 基于机器学习的智能测试用例生成示例

> 【阅读提示】本篇聚焦：基于机器学习的智能测试用例生成示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from deap import base, creator, tools, algorithms
import random

class SmartTestCaseGenerator:
    def __init__(self, historical_test_data):
        self.historical_data = historical_test_data
        self.model = None
        self.feature_columns = None
        self._prepare_data()
        self._train_model()

    def _prepare_data(self):
        """准备历史测试数据"""
        # 假设历史数据包含以下列：各种测试参数和是否发现缺陷的标签
        # 提取特征列（排除标签列）
        self.feature_columns = [col for col in self.historical_data.columns if col != 'found_bug']
        self.X = self.historical_data[self.feature_columns]
        self.y = self.historical_data['found_bug']

    def _train_model(self):
        """训练机器学习模型"""
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )

        # 训练随机森林模型
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        # 评估模型性能
        y_pred = self.model.predict(X_test)
        print("模型性能:")
        print(classification_report(y_test, y_pred))

        # 输出特征重要性
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        print("特征重要性:")
        print(feature_importance)

    def predict_defect_probability(self, test_case):
        """预测测试用例发现缺陷的概率"""
        # 将测试用例转换为模型输入格式
        test_df = pd.DataFrame([test_case])

        # 确保列顺序一致
        test_df = test_df[self.feature_columns]

        # 预测概率
        prob = self.model.predict_proba(test_df)[0][1]  # 第二类的概率（发现缺陷）
        return prob

    def generate_test_cases_with_genetic_algorithm(self, num_cases=10, generations=50, population_size=100):
        """使用遗传算法生成高价值测试用例"""
        # 定义适应度函数：最大化发现缺陷的概率
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        # 工具集初始化
        toolbox = base.Toolbox()

        # 获取每个特征的范围
        feature_ranges = {}
        for col in self.feature_columns:
            min_val = self.historical_data[col].min()
            max_val = self.historical_data[col].max()
            feature_ranges[col] = (min_val, max_val)

        # 生成随机个体（测试用例）
        def generate_individual():
            individual = []
            for col in self.feature_columns:
                min_val, max_val = feature_ranges[col]
                # 根据特征类型生成随机值
                if self.historical_data[col].dtype == 'int64':
                    val = random.randint(min_val, max_val)
                elif self.historical_data[col].dtype == 'float64':
                    val = random.uniform(min_val, max_val)
                else:  # 分类特征
                    unique_vals = self.historical_data[col].unique()
                    val = random.choice(unique_vals)
                individual.append(val)
            return creator.Individual(individual)

        # 注册生成器
        toolbox.register("individual", generate_individual)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # 评估函数
        def evaluate(individual):
            # 将个体转换为测试用例字典
            test_case = {}
            for i, col in enumerate(self.feature_columns):
                test_case[col] = individual[i]

            # 预测缺陷发现概率
            prob = self.predict_defect_probability(test_case)
            return (prob,)

        toolbox.register("evaluate", evaluate)
        toolbox.register("mate", tools.cxTwoPoint)

        # 变异操作
        def mutate(individual, indpb=0.2):
            for i, col in enumerate(self.feature_columns):
                if random.random() < indpb:
                    min_val, max_val = feature_ranges[col]
                    # 根据特征类型生成新值
                    if self.historical_data[col].dtype == 'int64':
                        individual[i] = random.randint(min_val, max_val)
                    elif self.historical_data[col].dtype == 'float64':
                        individual[i] = random.uniform(min_val, max_val)
                    else:  # 分类特征
                        unique_vals = self.historical_data[col].unique()
                        individual[i] = random.choice(unique_vals)
            return (individual,)

        toolbox.register("mutate", mutate)
        toolbox.register("select", tools.selTournament, tournsize=3)

        # 创建初始种群
        population = toolbox.population(n=population_size)

        # 进化
        algorithms.eaSimple(
            population, toolbox, cxpb=0.5, mutpb=0.2,
            ngen=generations, verbose=True
        )

        # 选择最优的测试用例
        top_individuals = tools.selBest(population, k=num_cases)

        # 转换为测试用例列表
        test_cases = []
        for individual in top_individuals:
            test_case = {}
            for i, col in enumerate(self.feature_columns):
                test_case[col] = individual[i]
            # 添加预测的缺陷发现概率
            test_case['defect_probability'] = self.predict_defect_probability(test_case)
            test_cases.append(test_case)

        # 按缺陷发现概率排序
        test_cases.sort(key=lambda x: x['defect_probability'], reverse=True)

        return test_cases

    def generate_edge_cases(self, num_cases=5):
        """生成边缘情况测试用例"""
        edge_cases = []

        # 获取特征重要性
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        # 选择最重要的几个特征
        top_features = feature_importance.head(3)['feature'].tolist()

        # 为每个重要特征生成边缘值
        for feature in top_features:
            # 获取特征的最小值和最大值
            min_val = self.historical_data[feature].min()
            max_val = self.historical_data[feature].max()

            # 生成基于数据分布的边缘值
            if self.historical_data[feature].dtype in ['int64', 'float64']:
                # 数值型特征：最小值、最大值、均值±3倍标准差
                mean_val = self.historical_data[feature].mean()
                std_val = self.historical_data[feature].std()

                edge_values = [min_val, max_val, mean_val - 3*std_val, mean_val + 3*std_val]

                for val in edge_values:
                    # 创建测试用例，设置当前特征为边缘值，其他特征为均值
                    test_case = {}
                    for col in self.feature_columns:
                        if col == feature:
                            test_case[col] = val
                        else:
                            # 非数值型特征使用众数
                            if self.historical_data[col].dtype in ['int64', 'float64']:
                                test_case[col] = self.historical_data[col].mean()
                            else:
                                test_case[col] = self.historical_data[col].mode()[0]

                    # 计算缺陷发现概率
                    test_case['defect_probability'] = self.predict_defect_probability(test_case)
                    edge_cases.append(test_case)

        # 按缺陷发现概率排序并返回前N个
        edge_cases.sort(key=lambda x: x['defect_probability'], reverse=True)
        return edge_cases[:num_cases]

## 使用示例 （来自：第5篇-第17章-大数据测试自动化【进阶】）

> 【阅读提示】本篇聚焦：使用示例 （来自：第5篇-第17章-大数据测试自动化【进阶】）。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

def demo_smart_test_case_generation():
    # 模拟历史测试数据
    np.random.seed(42)
    n_samples = 1000

    # 生成特征数据
    data = {
        'data_volume_gb': np.random.uniform(1, 1000, n_samples),
        'num_nodes': np.random.randint(1, 100, n_samples),
        'concurrency': np.random.randint(1, 1000, n_samples),
        'query_complexity': np.random.uniform(1, 10, n_samples),
        'data_skew': np.random.uniform(0, 1, n_samples),
        'network_latency': np.random.uniform(0, 100, n_samples)
    }

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 生成标签：缺陷发现与否
    # 模拟：数据量过大、并发过高、数据倾斜严重时更容易发现缺陷
    df['found_bug'] = 0

    # 数据量大于800GB时更容易出问题
    df.loc[df['data_volume_gb'] > 800, 'found_bug'] = 1

    # 并发大于800时更容易出问题
    df.loc[df['concurrency'] > 800, 'found_bug'] = 1

    # 数据倾斜严重时更容易出问题
    df.loc[df['data_skew'] > 0.8, 'found_bug'] = 1

    # 复杂查询在高并发时更容易出问题
    df.loc[(df['query_complexity'] > 7) & (df['concurrency'] > 500), 'found_bug'] = 1

    # 初始化智能测试用例生成器
    generator = SmartTestCaseGenerator(df)

    # 生成基于遗传算法的高价值测试用例
    high_value_cases = generator.generate_test_cases_with_genetic_algorithm(
        num_cases=5, generations=30, population_size=50
    )

    print("\n基于遗传算法的高价值测试用例:")
    for i, case in enumerate(high_value_cases, 1):
        print(f"\n测试用例 {i} (缺陷发现概率: {case['defect_probability']:.4f}):")
        for key, value in case.items():
            if key != 'defect_probability':
                print(f"  {key}: {value}")

    # 生成边缘情况测试用例
    edge_cases = generator.generate_edge_cases(num_cases=5)

    print("\n边缘情况测试用例:")
    for i, case in enumerate(edge_cases, 1):
        print(f"\n测试用例 {i} (缺陷发现概率: {case['defect_probability']:.4f}):")
        for key, value in case.items():
            if key != 'defect_probability':
                print(f"  {key}: {value}")
