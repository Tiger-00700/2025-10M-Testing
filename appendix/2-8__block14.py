def run_ai_model_test_suite():
    # 创建测试套件
    test_suite = DataAnalysisTestSuite()
    
    # 准备测试数据
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    
    # 生成示例数据（也可以使用实际业务数据）
    def generate_sample_data(n_samples=1000, n_features=20, n_informative=10, random_state=42):
        from sklearn.datasets import make_classification
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=n_informative,
            n_redundant=5,
            n_classes=2,
            random_state=random_state
        )
        
        columns = [f'feature_{i}' for i in range(X.shape[1])]
        df = pd.DataFrame(X, columns=columns)
        df['target'] = y
        
        # 添加一些类别特征
        for i in range(3):
            df[f'cat_feature_{i}'] = pd.factorize(np.random.choice(['A', 'B', 'C', 'D'], size=n_samples))[0]
        
        return df
    
    # 生成基准数据
    print("=== 生成测试数据 ===")
    base_data = generate_sample_data(n_samples=1500, random_state=42)
    
    # 划分数据集
    train_data, temp_data = train_test_split(base_data, test_size=0.6, random_state=42)
    validation_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)
    
    # 生成漂移数据（模拟时间变化的数据）
    drift_data = generate_sample_data(n_samples=500, random_state=123)
    # 对漂移数据进行一些修改以模拟分布变化
    for col in drift_data.columns:
        if col.startswith('feature_') and pd.api.types.is_numeric_dtype(drift_data[col]):
            # 改变特征分布
            drift_data[col] = drift_data[col] * 1.2 + 0.5
    
    # 训练模型
    print("=== 训练模型 ===")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    
    # 准备训练数据
    X_train = train_data.drop('target', axis=1)
    y_train = train_data['target']
    
    # 处理类别特征
    for col in X_train.select_dtypes(include=['object']).columns:
        X_train[col] = pd.factorize(X_train[col])[0]
    
    # 训练模型
    model.fit(X_train, y_train)
    
    # 添加模型训练过程验证测试
    print("=== 添加训练过程验证测试 ===")
    training_test = ModelTrainingProcessTest(
        "模型训练过程验证",
        RandomForestClassifier,
        train_data,
        validation_data,
        'target',
        training_params={'n_estimators': 100, 'max_depth': 10, 'random_state': 42}
    )
    test_suite.add_test(training_test)
    
    # 添加模型鲁棒性测试
    print("=== 添加模型鲁棒性测试 ===")
    robustness_test = ModelRobustnessTest(
        "模型鲁棒性测试",
        model,
        test_data,
        'target',
        robustness_tests=robustness_test_configs
    )
    test_suite.add_test(robustness_test)
    
    # 添加模型漂移检测测试
    print("=== 添加模型漂移检测测试 ===")
    drift_test = ModelDriftDetectionTest(
        "模型漂移检测",
        model,
        reference_data=test_data,
        current_data=drift_data,
        target_column='target'
    )
    test_suite.add_test(drift_test)
    
    # 运行测试套件
    print("=== 运行所有测试 ===")
    summary = test_suite.run_all(parallel=True)
    
    # 生成测试报告
    report = test_suite.generate_report("ai_model_test_report.txt")
    print(report)
    
    return summary
