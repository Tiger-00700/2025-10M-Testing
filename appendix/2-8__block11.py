def run_mining_model_test_suite():
    # 创建测试套件
    test_suite = DataAnalysisTestSuite()
    
    # 准备测试数据
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    
    # 生成分类测试数据
    def generate_classification_data(n_samples=1000):
        from sklearn.datasets import make_classification
        X, y = make_classification(
            n_samples=n_samples,
            n_features=10,
            n_informative=5,
            n_redundant=2,
            random_state=42
        )
        
        columns = [f'feature_{i}' for i in range(X.shape[1])]
        df = pd.DataFrame(X, columns=columns)
        df['target'] = y
        
        return df
    
    # 生成回归测试数据
    def generate_regression_data(n_samples=1000):
        from sklearn.datasets import make_regression
        X, y = make_regression(
            n_samples=n_samples,
            n_features=10,
            n_informative=5,
            noise=0.1,
            random_state=42
        )
        
        columns = [f'feature_{i}' for i in range(X.shape[1])]
        df = pd.DataFrame(X, columns=columns)
        df['target'] = y
        
        return df
    
    # 分类问题测试
    print("=== 执行分类模型测试 ===")
    class_data = generate_classification_data()
    
    # 划分训练集和测试集
    from sklearn.model_selection import train_test_split
    train_data, test_data = train_test_split(class_data, test_size=0.3, random_state=42)
    
    # 训练模型
    class_model = RandomForestClassifier(n_estimators=100, random_state=42)
    X_train = train_data.drop('target', axis=1)
    y_train = train_data['target']
    class_model.fit(X_train, y_train)
    
    # 添加模型准确性测试
    accuracy_test = MiningModelAccuracyTest(
        "分类模型准确性测试",
        class_model,
        test_data,
        'target'
    )
    test_suite.add_test(accuracy_test)
    
    # 添加交叉验证测试
    cv_test = CrossValidationTest(
        "分类模型交叉验证测试",
        RandomForestClassifier,
        class_data,
        'target',
        params={'n_estimators': 100, 'random_state': 42},
        cv=5
    )
    test_suite.add_test(cv_test)
    
    # 添加稳定性测试
    stability_test = ModelStabilityTest(
        "分类模型稳定性测试",
        RandomForestClassifier,
        class_data,
        'target',
        stability_tests=stability_test_configs,
        params={'n_estimators': 100, 'random_state': 42}
    )
    test_suite.add_test(stability_test)
    
    # 回归问题测试
    print("=== 执行回归模型测试 ===")
    reg_data = generate_regression_data()
    train_data, test_data = train_test_split(reg_data, test_size=0.3, random_state=42)
    
    # 训练模型
    reg_model = RandomForestRegressor(n_estimators=100, random_state=42)
    X_train = train_data.drop('target', axis=1)
    y_train = train_data['target']
    reg_model.fit(X_train, y_train)
    
    # 添加模型准确性测试
    accuracy_test = MiningModelAccuracyTest(
        "回归模型准确性测试",
        reg_model,
        test_data,
        'target'
    )
    test_suite.add_test(accuracy_test)
    
    # 添加交叉验证测试
    cv_test = CrossValidationTest(
        "回归模型交叉验证测试",
        RandomForestRegressor,
        reg_data,
        'target',
        params={'n_estimators': 100, 'random_state': 42},
        cv=5
    )
    test_suite.add_test(cv_test)
    
    # 添加稳定性测试
    stability_test = ModelStabilityTest(
        "回归模型稳定性测试",
        RandomForestRegressor,
        reg_data,
        'target',
        stability_tests=stability_test_configs,
        params={'n_estimators': 100, 'random_state': 42}
    )
    test_suite.add_test(stability_test)
    
    # 运行测试
    print("=== 运行所有测试 ===")
    summary = test_suite.run_all(parallel=True)
    
    # 生成报告
    report = test_suite.generate_report("mining_model_test_report.txt")
    print(report)
    
    return summary

## 8.5 AI分析模型测试

### 8.5.1 AI分析模型测试的重要性

随着人工智能技术在数据分析领域的广泛应用，AI分析模型已经成为企业决策和业务优化的重要工具。与传统的数据挖掘模型相比，AI分析模型通常更加复杂，可能包含深度学习、强化学习等高级技术，这使得其测试工作面临着新的挑战。

AI分析模型测试不仅关乎模型的准确性，还涉及到模型的公平性、鲁棒性、安全性和可解释性等多个维度。一个经过充分测试的AI分析模型能够在实际业务中发挥更大的价值，同时降低潜在的风险和问题。

### 8.5.2 模型训练过程验证

模型训练过程的验证确保模型能够正确学习数据中的模式，并且训练过程稳定可靠。以下是模型训练过程验证的实现示例：

```python
class ModelTrainingProcessTest(DataAnalysisTestBase):
    """AI模型训练过程验证测试"""
    
    def __init__(self, test_name, model_class, training_data, validation_data, target_column, training_params=None):
        super().__init__(test_name, "验证AI模型训练过程的正确性和稳定性")
        self.model_class = model_class  # 模型类
        self.training_data = training_data  # 训练数据
        self.validation_data = validation_data  # 验证数据
        self.target_column = target_column  # 目标列
        self.training_params = training_params or {}  # 训练参数
        
    def run(self):
        start_time = time.time()
        
        try:
            # 验证输入
            self.validate_input(self.training_data)
            self.validate_input(self.validation_data)
            
            # 准备训练和验证数据
            X_train, y_train = self._prepare_data(self.training_data)
            X_val, y_val = self._prepare_data(self.validation_data)
            
            # 监控训练过程
            training_history = self._monitor_training(X_train, y_train, X_val, y_val)
            
            # 分析训练过程
            analysis = self._analyze_training_history(training_history)
            
            # 判断是否通过
            self.passed = analysis['passed']
            self.results = {
                'training_history': training_history,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"模型训练过程验证失败: {str(e)}")
            self.passed = False
            self.results['error'] = str(e)
        
        self.execution_time = time.time() - start_time
    
    def _prepare_data(self, data):
        """准备特征和目标数据"""
        # 移除目标列和ID列等非特征列
        X = data.drop([self.target_column] + [col for col in data.columns if col.lower() in ['id', 'index']], axis=1)
        
        # 处理缺失值
        X = X.fillna(0)
        
        # 处理类别特征
        for col in X.select_dtypes(include=['object']).columns:
            try:
                X[col] = pd.factorize(X[col])[0]
            except Exception:
                X = X.drop(col, axis=1)
        
        # 获取目标值
        y = data[self.target_column].values
        
        return X, y
    
    def _monitor_training(self, X_train, y_train, X_val, y_val):
        """监控模型训练过程"""
        # 检查是否支持早停或回调
        history = {
            'epochs': [],
            'train_loss': [],
            'val_loss': [],
            'train_metrics': [],
            'val_metrics': [],
            'learning_rates': []
        }
        
        # 对于支持回调或早停的框架（如TensorFlow/Keras）
        try:
            # 尝试检查是否为Keras模型
            import tensorflow as tf
            if issubclass(self.model_class, tf.keras.Model) or hasattr(self.model_class, 'fit'):
                return self._monitor_keras_training(X_train, y_train, X_val, y_val)
        except ImportError:
            pass
        
        # 对于scikit-learn等传统机器学习模型
        try:
            # 为了监控，我们模拟多轮训练过程（例如，使用不同比例的数据）
            import numpy as np
            from sklearn.metrics import mean_squared_error, accuracy_score
            
            # 判断问题类型
            is_classification = len(set(y_train)) <= 2
            
            # 模拟训练轮次
            for epoch in range(1, 6):  # 模拟5轮
                # 使用不同比例的训练数据
                sample_ratio = 0.2 * epoch
                sample_size = int(len(X_train) * min(sample_ratio, 1.0))
                
                # 随机采样
                sample_indices = np.random.choice(len(X_train), sample_size, replace=False)
                X_sample = X_train.iloc[sample_indices] if hasattr(X_train, 'iloc') else X_train[sample_indices]
                y_sample = y_train[sample_indices]
                
                # 训练模型
                model = self.model_class(**self.training_params)
                model.fit(X_sample, y_sample)
                
                # 计算训练损失/指标
                if is_classification:
                    y_train_pred = model.predict(X_sample)
                    train_acc = accuracy_score(y_sample, y_train_pred)
                    train_loss = 1.0 - train_acc  # 简单地使用1-准确率作为损失
                    
                    # 验证集上的指标
                    y_val_pred = model.predict(X_val)
                    val_acc = accuracy_score(y_val, y_val_pred)
                    val_loss = 1.0 - val_acc
                    
                    history['train_metrics'].append({'accuracy': train_acc})
                    history['val_metrics'].append({'accuracy': val_acc})
                else:
                    y_train_pred = model.predict(X_sample)
                    train_loss = mean_squared_error(y_sample, y_train_pred)
                    
                    # 验证集上的指标
                    y_val_pred = model.predict(X_val)
                    val_loss = mean_squared_error(y_val, y_val_pred)
                    
                    # 计算R²作为额外指标
                    from sklearn.metrics import r2_score
                    train_r2 = r2_score(y_sample, y_train_pred)
                    val_r2 = r2_score(y_val, y_val_pred)
                    
                    history['train_metrics'].append({'r2': train_r2})
                    history['val_metrics'].append({'r2': val_r2})
                
                # 记录历史
                history['epochs'].append(epoch)
                history['train_loss'].append(float(train_loss))
                history['val_loss'].append(float(val_loss))
                history['learning_rates'].append(None)  # 对于简单模型，我们不跟踪学习率
        
        except Exception as e:
            logger.error(f"监控训练过程失败: {str(e)}")
            raise
        
        return history
    
    def _monitor_keras_training(self, X_train, y_train, X_val, y_val):
        """监控Keras模型训练过程"""
        import tensorflow as tf
        
        # 创建回调以记录训练历史
        history = {
            'epochs': [],
            'train_loss': [],
            'val_loss': [],
            'train_metrics': [],
            'val_metrics': [],
            'learning_rates': []
        }
        
        # 自定义回调以记录学习率
        class LearningRateLogger(tf.keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs=None):
                optimizer = self.model.optimizer
                lr = float(optimizer.lr.numpy())
                # 应用可能的学习率调度器
                if hasattr(optimizer, 'lr_scheduler'):
                    lr = optimizer.lr_scheduler(lr, epoch)
                history['learning_rates'].append(lr)
        
        # 创建模型实例
        model = self.model_class(**self.training_params)
        
        # 编译模型（如果需要）
        if not hasattr(model, 'compiled') or not model.compiled:
            # 判断问题类型
            is_classification = len(set(y_train)) <= 2
            
            if is_classification:
                model.compile(
                    optimizer='adam',
                    loss='binary_crossentropy' if len(set(y_train)) == 2 else 'categorical_crossentropy',
                    metrics=['accuracy']
                )
            else:
                model.compile(
                    optimizer='adam',
                    loss='mean_squared_error',
                    metrics=['mae']
                )
        
        # 训练模型并记录历史
        keras_history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.training_params.get('epochs', 10),
            batch_size=self.training_params.get('batch_size', 32),
            callbacks=[LearningRateLogger()],
            verbose=1
        )
        
        # 转换Keras历史记录格式
        history['epochs'] = list(range(1, len(keras_history.history['loss']) + 1))
        history['train_loss'] = [float(loss) for loss in keras_history.history['loss']]
        history['val_loss'] = [float(loss) for loss in keras_history.history['val_loss']]
        
        # 提取其他指标
        train_metrics = {}
        val_metrics = {}
        
        for key in keras_history.history:
            if key.startswith('val_'):
                metric_name = key[4:]  # 移除'val_'前缀
                val_metrics[metric_name] = [float(v) for v in keras_history.history[key]]
            elif key != 'loss':
                train_metrics[key] = [float(v) for v in keras_history.history[key]]
        
        # 重新组织指标格式
        num_epochs = len(history['epochs'])
        for i in range(num_epochs):
            epoch_train_metrics = {}
            epoch_val_metrics = {}
            
            for metric, values in train_metrics.items():
                epoch_train_metrics[metric] = values[i]
            for metric, values in val_metrics.items():
                epoch_val_metrics[metric] = values[i]
            
            history['train_metrics'].append(epoch_train_metrics)
            history['val_metrics'].append(epoch_val_metrics)
        
        # 如果没有记录学习率，填充None
        if len(history['learning_rates']) < num_epochs:
            history['learning_rates'].extend([None] * (num_epochs - len(history['learning_rates'])))
        
        return history
    
    def _analyze_training_history(self, history):
        """分析训练历史"""
        analysis = {
            'convergence': {},
            'overfitting': {},
            'learning_progress': {},
            'passed': True
        }
        
        # 检查训练历史是否为空
        if not history['epochs']:
            analysis['passed'] = False
            analysis['error'] = "训练历史为空"
            return analysis
        
        # 分析收敛性
        train_losses = history['train_loss']
        val_losses = history['val_loss']
        
        # 检查损失是否下降
        if len(train_losses) > 1:
            initial_loss = train_losses[0]
            final_loss = train_losses[-1]
            loss_reduction = (initial_loss - final_loss) / initial_loss
            
            analysis['convergence']['loss_reduction'] = loss_reduction
            analysis['convergence']['converged'] = loss_reduction > 0.1  # 损失减少10%以上认为收敛
            
            if not analysis['convergence']['converged']:
                analysis['passed'] = False
                analysis['failure_reason'] = "模型训练过程未收敛"
        
        # 分析过拟合情况
        if len(val_losses) > 1 and len(train_losses) > 1:
            # 最后几轮的训练损失和验证损失
            recent_epochs = min(3, len(train_losses))
            recent_train_loss = sum(train_losses[-recent_epochs:]) / recent_epochs
            recent_val_loss = sum(val_losses[-recent_epochs:]) / recent_epochs
            
            # 计算过拟合指标
            if recent_val_loss > recent_train_loss:
                overfit_ratio = (recent_val_loss - recent_train_loss) / recent_train_loss
            else:
                overfit_ratio = 0
            
            analysis['overfitting']['ratio'] = overfit_ratio
            analysis['overfitting']['is_overfitting'] = overfit_ratio > 0.2  # 验证损失比训练损失高20%以上认为过拟合
            
            if analysis['overfitting']['is_overfitting']:
                analysis['passed'] = False
                analysis['failure_reason'] = "模型存在过拟合问题"
        
        # 分析学习进度的稳定性
        if len(train_losses) > 2:
            # 计算损失下降的标准差
            loss_deltas = []
            for i in range(1, len(train_losses)):
                delta = train_losses[i-1] - train_losses[i]
                loss_deltas.append(delta)
            
            # 计算损失下降率的变化
            loss_delta_std = np.std(loss_deltas) if loss_deltas else 0
            loss_delta_mean = np.mean(loss_deltas) if loss_deltas else 0
            
            # 稳定性指标：标准差与均值的比率
            stability_ratio = loss_delta_std / max(abs(loss_delta_mean), 1e-10)
            
            analysis['learning_progress']['stability_ratio'] = stability_ratio
            analysis['learning_progress']['is_stable'] = stability_ratio < 0.5  # 标准差小于均值的50%认为稳定
            
            if not analysis['learning_progress']['is_stable']:
                analysis['passed'] = False
                analysis['failure_reason'] = "训练过程不稳定"
        
        # 检查是否有NaN或无穷大值
        if any(np.isnan(loss) or np.isinf(loss) for loss in train_losses + val_losses):
            analysis['passed'] = False
            analysis['failure_reason'] = "训练过程中出现NaN或无穷大值"
        
        return analysis
