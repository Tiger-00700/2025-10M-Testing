class CrossValidationTest(DataAnalysisTestBase):
    """数据挖掘模型交叉验证测试"""
    
    def __init__(self, test_name, model_class, data, target_column, params=None, cv=5):
        super().__init__(test_name, "通过交叉验证评估模型的泛化能力")
        self.model_class = model_class  # 模型类
        self.data = data  # 完整数据集
        self.target_column = target_column  # 目标列
        self.params = params or {}  # 模型参数
        self.cv = cv  # 交叉验证折数
        
    def run(self):
        start_time = time.time()
        
        try:
            # 验证输入
            self.validate_input(self.data)
            
            # 准备特征和目标
            X = self._prepare_features(self.data)
            y = self.data[self.target_column].values
            
            # 执行交叉验证
            cv_results = self._perform_cross_validation(X, y)
            
            # 分析交叉验证结果
            analysis = self._analyze_cv_results(cv_results)
            
            # 判断是否通过
            self.passed = analysis['passed']
            self.results = {
                'cv_results': cv_results,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"交叉验证测试执行失败: {str(e)}")
            self.passed = False
            self.results['error'] = str(e)
        
        self.execution_time = time.time() - start_time
    
    def _prepare_features(self, data):
        """准备特征数据（与前面的方法类似）"""
        # 移除目标列和ID列等非特征列
        X = data.drop([self.target_column] + [col for col in data.columns if col.lower() in ['id', 'index']], axis=1)
        
        # 处理缺失值
        X = X.fillna(0)  # 简单处理，实际应用中应根据具体情况处理
        
        # 处理类别特征
        for col in X.select_dtypes(include=['object']).columns:
            try:
                X[col] = pd.factorize(X[col])[0]
            except Exception as e:
                logger.warning(f"编码特征 {col} 时出错: {str(e)}")
                X = X.drop(col, axis=1)
        
        return X
    
    def _perform_cross_validation(self, X, y):
        """执行交叉验证"""
        from sklearn.model_selection import cross_validate
        
        # 创建模型实例
        model = self.model_class(**self.params)
        
        # 确定评估指标
        is_classification = len(set(y)) <= 2
        
        if is_classification:
            scoring = ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted']
        else:
            scoring = ['neg_mean_squared_error', 'neg_mean_absolute_error', 'r2']
        
        # 执行交叉验证
        cv_results = cross_validate(
            model, 
            X, 
            y, 
            cv=self.cv, 
            scoring=scoring,
            return_train_score=True,
            return_estimator=True
        )
        
        return cv_results
    
    def _analyze_cv_results(self, cv_results):
        """分析交叉验证结果"""
        analysis = {
            'metrics': {},
            'stability': {},
            'overfitting': {}
        }
        
        # 计算每个指标的平均值和标准差
        for key in cv_results:
            if key.startswith('test_') or key.startswith('train_'):
                metric_name = key.replace('test_', '').replace('train_', '')
                results = cv_results[key]
                
                # 确保存储为基本数据类型，方便序列化
                if isinstance(results, np.ndarray):
                    results = results.tolist()
                
                analysis['metrics'][key] = {
                    'values': results,
                    'mean': float(np.mean(results)),
                    'std': float(np.std(results))
                }
        
        # 分析模型稳定性（不同折之间的差异）
        if 'test_accuracy' in analysis['metrics']:
            std_accuracy = analysis['metrics']['test_accuracy']['std']
            analysis['stability']['accuracy_std'] = std_accuracy
            analysis['stability']['is_stable'] = std_accuracy < 0.05  # 标准差小于0.05认为稳定
        elif 'test_r2' in analysis['metrics']:
            std_r2 = analysis['metrics']['test_r2']['std']
            analysis['stability']['r2_std'] = std_r2
            analysis['stability']['is_stable'] = std_r2 < 0.1  # 标准差小于0.1认为稳定
        
        # 分析过拟合情况（训练集和测试集性能差异）
        # 对于分类问题
        if 'train_accuracy' in analysis['metrics'] and 'test_accuracy' in analysis['metrics']:
            train_acc = analysis['metrics']['train_accuracy']['mean']
            test_acc = analysis['metrics']['test_accuracy']['mean']
            diff = train_acc - test_acc
            analysis['overfitting']['accuracy_diff'] = diff
            analysis['overfitting']['is_overfitting'] = diff > 0.1  # 差异大于0.1认为过拟合
        # 对于回归问题
        elif 'train_r2' in analysis['metrics'] and 'test_r2' in analysis['metrics']:
            train_r2 = analysis['metrics']['train_r2']['mean']
            test_r2 = analysis['metrics']['test_r2']['mean']
            diff = train_r2 - test_r2
            analysis['overfitting']['r2_diff'] = diff
            analysis['overfitting']['is_overfitting'] = diff > 0.15  # 差异大于0.15认为过拟合
        
        # 判断整体是否通过
        analysis['passed'] = True
        
        # 检查模型是否稳定
        if 'is_stable' in analysis['stability'] and not analysis['stability']['is_stable']:
            analysis['passed'] = False
            analysis['failure_reason'] = "模型在不同折之间的表现不稳定"
        
        # 检查是否过拟合
        if 'is_overfitting' in analysis['overfitting'] and analysis['overfitting']['is_overfitting']:
            analysis['passed'] = False
            analysis['failure_reason'] = "模型存在过拟合问题"
        
        # 检查性能是否达标
        if 'test_accuracy' in analysis['metrics']:
            test_acc_mean = analysis['metrics']['test_accuracy']['mean']
            if test_acc_mean < 0.7:
                analysis['passed'] = False
                analysis['failure_reason'] = "模型准确率未达标"
        elif 'test_r2' in analysis['metrics']:
            test_r2_mean = analysis['metrics']['test_r2']['mean']
            if test_r2_mean < 0.6:
                analysis['passed'] = False
                analysis['failure_reason'] = "模型R²未达标"
        
        return analysis
