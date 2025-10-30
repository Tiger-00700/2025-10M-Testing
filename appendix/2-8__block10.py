class ModelStabilityTest(DataAnalysisTestBase):
    """数据挖掘模型稳定性测试"""
    
    def __init__(self, test_name, model_class, base_data, target_column, stability_tests, params=None):
        super().__init__(test_name, "测试模型在不同条件下的稳定性")
        self.model_class = model_class  # 模型类
        self.base_data = base_data  # 基础数据集
        self.target_column = target_column  # 目标列
        self.stability_tests = stability_tests  # 稳定性测试配置
        self.params = params or {}  # 模型参数
        
    def run(self):
        start_time = time.time()
        
        try:
            test_results = []
            all_passed = True
            
            # 训练基准模型
            base_model = self._train_base_model()
            base_performance = self._evaluate_model(base_model, self.base_data)
            
            # 执行各项稳定性测试
            for test_config in self.stability_tests:
                test_name = test_config.get('name', 'Unnamed Stability Test')
                test_type = test_config.get('type', '')
                params = test_config.get('params', {})
                
                try:
                    logger.info(f"执行稳定性测试: {test_name} ({test_type})")
                    
                    # 生成测试数据
                    test_data = self._generate_test_data(test_type, params)
                    
                    # 在测试数据上评估模型
                    test_performance = self._evaluate_model(base_model, test_data)
                    
                    # 分析性能变化
                    analysis = self._analyze_performance_change(
                        base_performance, 
                        test_performance, 
                        params.get('threshold', 0.05)
                    )
                    
                    test_results.append({
                        'test_name': test_name,
                        'test_type': test_type,
                        'params': params,
                        'base_performance': base_performance,
                        'test_performance': test_performance,
                        'analysis': analysis,
                        'passed': analysis['passed']
                    })
                    
                    if not analysis['passed']:
                        all_passed = False
                
                except Exception as e:
                    test_results.append({
                        'test_name': test_name,
                        'test_type': test_type,
                        'params': params,
                        'passed': False,
                        'error': str(e)
                    })
                    all_passed = False
                    logger.error(f"稳定性测试执行失败: {test_name}, 错误: {str(e)}")
            
            self.passed = all_passed
            self.results = {
                'base_performance': base_performance,
                'test_results': test_results,
                'passed_count': sum(1 for r in test_results if r['passed']),
                'failed_count': sum(1 for r in test_results if not r['passed'])
            }
            
        except Exception as e:
            logger.error(f"模型稳定性测试执行失败: {str(e)}")
            self.passed = False
            self.results['error'] = str(e)
        
        self.execution_time = time.time() - start_time
    
    def _train_base_model(self):
        """训练基准模型"""
        # 准备特征和目标
        X = self._prepare_features(self.base_data)
        y = self.base_data[self.target_column].values
        
        # 创建并训练模型
        model = self.model_class(**self.params)
        model.fit(X, y)
        
        return model
    
    def _prepare_features(self, data):
        """准备特征数据"""
        X = data.drop([self.target_column] + [col for col in data.columns if col.lower() in ['id', 'index']], axis=1)
        X = X.fillna(0)
        
        for col in X.select_dtypes(include=['object']).columns:
            try:
                X[col] = pd.factorize(X[col])[0]
            except Exception:
                X = X.drop(col, axis=1)
        
        return X
    
    def _evaluate_model(self, model, data):
        """评估模型性能"""
        X = self._prepare_features(data)
        y_true = data[self.target_column].values
        
        try:
            if hasattr(model, 'predict_proba'):
                y_pred = model.predict_proba(X)[:, 1]
            else:
                y_pred = model.predict(X)
        except Exception as e:
            logger.error(f"模型预测失败: {str(e)}")
            raise
        
        # 判断问题类型并计算指标
        is_classification = len(set(y_true)) <= 2
        metrics = {}
        
        if is_classification:
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            # 如果预测结果是概率，转换为类别
            if y_pred.min() >= 0 and y_pred.max() <= 1:
                y_pred_class = (y_pred >= 0.5).astype(int)
            else:
                y_pred_class = y_pred
            
            metrics['accuracy'] = accuracy_score(y_true, y_pred_class)
            metrics['precision'] = precision_score(y_true, y_pred_class, average='weighted')
            metrics['recall'] = recall_score(y_true, y_pred_class, average='weighted')
            metrics['f1_score'] = f1_score(y_true, y_pred_class, average='weighted')
        else:
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            metrics['mse'] = mean_squared_error(y_true, y_pred)
            metrics['rmse'] = np.sqrt(metrics['mse'])
            metrics['mae'] = mean_absolute_error(y_true, y_pred)
            metrics['r2'] = r2_score(y_true, y_pred)
        
        return metrics
    
    def _generate_test_data(self, test_type, params):
        """生成测试数据"""
        if test_type == 'noise_injection':
            # 注入噪声
            return self._inject_noise(params)
        elif test_type == 'feature_missing':
            # 模拟特征缺失
            return self._simulate_feature_missing(params)
        elif test_type == 'temporal_shift':
            # 模拟时间偏移
            return self._simulate_temporal_shift(params)
        elif test_type == 'distribution_shift':
            # 模拟分布偏移
            return self._simulate_distribution_shift(params)
        else:
            raise ValueError(f"不支持的测试类型: {test_type}")
    
    def _inject_noise(self, params):
        """向数据中注入噪声"""
        noise_level = params.get('noise_level', 0.1)
        affected_columns = params.get('columns', None)
        
        # 创建数据副本
        noisy_data = self.base_data.copy()
        
        # 选择要添加噪声的列（默认为所有数值列）
        if affected_columns is None:
            numeric_cols = noisy_data.select_dtypes(include=[np.number]).columns
            affected_columns = [col for col in numeric_cols if col != self.target_column]
        
        # 向选定的列添加高斯噪声
        for col in affected_columns:
            if col in noisy_data.columns:
                std = noisy_data[col].std() if noisy_data[col].std() > 0 else 1.0
                noise = np.random.normal(0, std * noise_level, size=len(noisy_data))
                noisy_data[col] = noisy_data[col] + noise
        
        return noisy_data
    
    def _simulate_feature_missing(self, params):
        """模拟特征缺失"""
        missing_rate = params.get('missing_rate', 0.1)
        affected_columns = params.get('columns', None)
        
        # 创建数据副本
        missing_data = self.base_data.copy()
        
        # 选择要缺失的列（默认为所有非目标列）
        if affected_columns is None:
            affected_columns = [col for col in missing_data.columns if col != self.target_column]
        
        # 在选定的列中随机设置缺失值
        for col in affected_columns:
            if col in missing_data.columns:
                # 随机选择要设置为缺失的行
                mask = np.random.rand(len(missing_data)) < missing_rate
                missing_data.loc[mask, col] = np.nan
        
        return missing_data
    
    def _simulate_temporal_shift(self, params):
        """模拟时间偏移（例如不同时期的数据）"""
        # 简化实现，实际应用中可能需要使用真实的不同时期的数据
        # 这里我们简单地对时间相关特征进行变换
        temporal_col = params.get('temporal_column', None)
        shift_percentage = params.get('shift_percentage', 0.1)
        
        if temporal_col is None or temporal_col not in self.base_data.columns:
            # 如果没有指定时间列，返回原始数据的随机子集
            return self.base_data.sample(frac=1.0, random_state=42)
        
        # 创建数据副本
        shifted_data = self.base_data.copy()
        
        # 对时间列进行变换
        col_data = shifted_data[temporal_col]
        
        # 尝试将列转换为数值（如果是日期时间）
        if pd.api.types.is_datetime64_any_dtype(col_data):
            # 对日期时间进行偏移
            days_to_shift = int(shift_percentage * (col_data.max() - col_data.min()).days)
            shifted_data[temporal_col] = col_data + pd.Timedelta(days=days_to_shift)
        elif pd.api.types.is_numeric_dtype(col_data):
            # 对数值进行比例偏移
            shifted_data[temporal_col] = col_data * (1 + shift_percentage)
        
        return shifted_data
    
    def _simulate_distribution_shift(self, params):
        """模拟分布偏移"""
        # 简化实现，通过修改某些特征的分布来模拟
        affected_columns = params.get('columns', None)
        shift_strength = params.get('shift_strength', 0.2)
        
        # 创建数据副本
        shifted_data = self.base_data.copy()
        
        # 选择要偏移的列（默认为所有数值列）
        if affected_columns is None:
            numeric_cols = shifted_data.select_dtypes(include=[np.number]).columns
            affected_columns = [col for col in numeric_cols if col != self.target_column]
        
        # 对选定的列进行分布偏移
        for col in affected_columns:
            if col in shifted_data.columns:
                # 改变均值（添加偏移）
                mean_shift = shifted_data[col].std() * shift_strength
                shifted_data[col] = shifted_data[col] + mean_shift
        
        return shifted_data
    
    def _analyze_performance_change(self, base_performance, test_performance, threshold):
        """分析性能变化"""
        analysis = {
            'changes': {},
            'passed': True
        }
        
        # 检查关键指标的变化
        key_metrics = ['accuracy', 'f1_score', 'r2', 'rmse']
        
        for metric in key_metrics:
            if metric in base_performance and metric in test_performance:
                base_value = base_performance[metric]
                test_value = test_performance[metric]
                
                # 计算相对变化
                if metric in ['rmse', 'mse', 'mae']:  # 误差指标，越小越好
                    relative_change = (test_value - base_value) / max(base_value, 0.001)
                else:  # 得分指标，越大越好
                    relative_change = (base_value - test_value) / max(base_value, 0.001)
                
                analysis['changes'][metric] = {
                    'base_value': base_value,
                    'test_value': test_value,
                    'absolute_change': test_value - base_value,
                    'relative_change': relative_change,
                    'exceeds_threshold': abs(relative_change) > threshold
                }
                
                # 如果变化超过阈值，测试失败
                if abs(relative_change) > threshold:
                    analysis['passed'] = False
        
        return analysis

# 稳定性测试配置示例
stability_test_configs = [
    {
        'name': '噪声注入测试',
        'type': 'noise_injection',
        'params': {
            'noise_level': 0.1,  # 10%的噪声
            'threshold': 0.05   # 性能下降不超过5%
        }
    },
    {
        'name': '特征缺失测试',
        'type': 'feature_missing',
        'params': {
            'missing_rate': 0.1,  # 10%的缺失率
            'threshold': 0.05
        }
    },
    {
        'name': '分布偏移测试',
        'type': 'distribution_shift',
        'params': {
            'shift_strength': 0.2,  # 20%的分布偏移
            'threshold': 0.05
        }
    }
]
