class ModelRobustnessTest(DataAnalysisTestBase):
    """AI模型鲁棒性测试"""
    
    def __init__(self, test_name, model, test_data, target_column, robustness_tests):
        super().__init__(test_name, "测试AI模型在不同条件下的鲁棒性")
        self.model = model  # 训练好的模型
        self.test_data = test_data  # 测试数据
        self.target_column = target_column  # 目标列
        self.robustness_tests = robustness_tests  # 鲁棒性测试配置
        
    def run(self):
        start_time = time.time()
        
        try:
            # 验证输入
            self.validate_input(self.test_data)
            
            # 准备基础测试数据
            X_base, y_base = self._prepare_data(self.test_data)
            
            # 计算基准性能
            base_performance = self._evaluate_performance(X_base, y_base)
            
            # 执行各项鲁棒性测试
            test_results = []
            all_passed = True
            
            for test_config in self.robustness_tests:
                test_name = test_config.get('name', 'Unnamed Robustness Test')
                test_type = test_config.get('type', '')
                params = test_config.get('params', {})
                threshold = params.get('threshold', 0.1)  # 默认阈值为10%
                
                try:
                    logger.info(f"执行鲁棒性测试: {test_name} ({test_type})")
                    
                    # 生成测试数据
                    X_test = self._generate_test_data(test_type, X_base.copy(), params)
                    
                    # 评估模型在测试数据上的性能
                    test_performance = self._evaluate_performance(X_test, y_base)
                    
                    # 分析性能变化
                    analysis = self._analyze_performance_change(
                        base_performance, 
                        test_performance, 
                        threshold
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
                    logger.error(f"鲁棒性测试执行失败: {test_name}, 错误: {str(e)}")
            
            # 判断整体是否通过
            self.passed = all_passed
            self.results = {
                'base_performance': base_performance,
                'test_results': test_results,
                'passed_count': sum(1 for r in test_results if r['passed']),
                'failed_count': sum(1 for r in test_results if not r['passed'])
            }
            
        except Exception as e:
            logger.error(f"模型鲁棒性测试执行失败: {str(e)}")
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
    
    def _evaluate_performance(self, X, y):
        """评估模型性能"""
        try:
            # 进行预测
            if hasattr(self.model, 'predict_proba'):
                y_pred = self.model.predict_proba(X)[:, 1] if len(self.model.classes_) == 2 else self.model.predict_proba(X)
            else:
                y_pred = self.model.predict(X)
            
            # 判断问题类型
            is_classification = len(set(y)) <= 2 or (hasattr(y_pred, 'shape') and len(y_pred.shape) > 1)
            
            metrics = {}
            
            if is_classification:
                # 对于分类问题，计算准确性指标
                from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
                
                # 将概率转换为类别（如果需要）
                if hasattr(y_pred, 'shape') and len(y_pred.shape) > 1 and y_pred.shape[1] > 1:
                    y_pred_class = np.argmax(y_pred, axis=1)
                elif y_pred.min() >= 0 and y_pred.max() <= 1 and len(set(y)) == 2:
                    y_pred_class = (y_pred >= 0.5).astype(int)
                else:
                    y_pred_class = y_pred
                
                metrics['accuracy'] = accuracy_score(y, y_pred_class)
                metrics['precision'] = precision_score(y, y_pred_class, average='weighted', zero_division=0)
                metrics['recall'] = recall_score(y, y_pred_class, average='weighted', zero_division=0)
                metrics['f1_score'] = f1_score(y, y_pred_class, average='weighted', zero_division=0)
            else:
                # 对于回归问题，计算误差指标
                from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
                
                metrics['mse'] = mean_squared_error(y, y_pred)
                metrics['rmse'] = np.sqrt(metrics['mse'])
                metrics['mae'] = mean_absolute_error(y, y_pred)
                metrics['r2'] = r2_score(y, y_pred)
            
            return metrics
        
        except Exception as e:
            logger.error(f"评估模型性能失败: {str(e)}")
            raise
    
    def _generate_test_data(self, test_type, X, params):
        """生成测试数据"""
        if test_type == 'noise_injection':
            # 注入噪声
            return self._inject_noise(X, params)
        elif test_type == 'adversarial_attack':
            # 生成对抗样本
            return self._generate_adversarial_samples(X, params)
        elif test_type == 'distribution_shift':
            # 模拟分布偏移
            return self._simulate_distribution_shift(X, params)
        elif test_type == 'extreme_values':
            # 测试极值
            return self._introduce_extreme_values(X, params)
        else:
            raise ValueError(f"不支持的测试类型: {test_type}")
    
    def _inject_noise(self, X, params):
        """向数据中注入噪声"""
        noise_level = params.get('noise_level', 0.1)
        affected_columns = params.get('columns', None)
        noise_type = params.get('noise_type', 'gaussian')
        
        # 创建数据副本
        noisy_X = X.copy()
        
        # 选择要添加噪声的列（默认为所有数值列）
        if affected_columns is None:
            numeric_cols = noisy_X.select_dtypes(include=[np.number]).columns
            affected_columns = numeric_cols.tolist()
        
        # 向选定的列添加噪声
        for col in affected_columns:
            if col in noisy_X.columns:
                col_data = noisy_X[col]
                std = col_data.std() if col_data.std() > 0 else 1.0
                
                if noise_type == 'gaussian':
                    # 添加高斯噪声
                    noise = np.random.normal(0, std * noise_level, size=len(noisy_X))
                    noisy_X[col] = col_data + noise
                elif noise_type == 'uniform':
                    # 添加均匀噪声
                    noise = np.random.uniform(-std * noise_level, std * noise_level, size=len(noisy_X))
                    noisy_X[col] = col_data + noise
                elif noise_type == 'salt_pepper':
                    # 添加椒盐噪声（随机将一些值设为最大值或最小值）
                    mask = np.random.rand(len(noisy_X)) < noise_level
                    noise = np.random.choice([col_data.min(), col_data.max()], size=len(noisy_X))
                    noisy_X.loc[mask, col] = noise[mask]
        
        return noisy_X
    
    def _generate_adversarial_samples(self, X, params):
        """生成对抗样本（简化版）"""
        epsilon = params.get('epsilon', 0.1)
        attack_type = params.get('attack_type', 'fast_gradient')
        num_samples = params.get('num_samples', min(100, len(X)))
        
        # 创建数据副本
        adv_X = X.copy()
        
        # 随机选择样本进行攻击
        sample_indices = np.random.choice(len(adv_X), num_samples, replace=False)
        sample_data = adv_X.iloc[sample_indices] if hasattr(adv_X, 'iloc') else adv_X[sample_indices]
        
        try:
            # 对于不同的攻击类型
            if attack_type == 'fast_gradient':
                # 简化版快速梯度符号法（FGSM）
                # 由于我们没有模型的梯度，我们使用启发式方法
                for idx in sample_indices:
                    row = adv_X.iloc[idx] if hasattr(adv_X, 'iloc') else adv_X[idx]
                    
                    # 对每个特征添加扰动
                    for col in adv_X.columns:
                        if col in row:
                            col_std = adv_X[col].std() if adv_X[col].std() > 0 else 1.0
                            # 随机添加正负扰动
                            perturbation = np.random.choice([-1, 1]) * epsilon * col_std
                            if hasattr(adv_X, 'iloc'):
                                adv_X.at[idx, col] = row[col] + perturbation
                            else:
                                adv_X[idx][col] = row[col] + perturbation
            
            elif attack_type == 'random_attack':
                # 随机攻击：随机改变特征值
                for idx in sample_indices:
                    # 随机选择一些特征进行修改
                    num_features_to_change = max(1, int(len(adv_X.columns) * 0.3))  # 修改30%的特征
                    features_to_change = np.random.choice(adv_X.columns, num_features_to_change, replace=False)
                    
                    for col in features_to_change:
                        if hasattr(adv_X, 'iloc') and col in adv_X.columns:
                            col_data = adv_X[col]
                            # 在该列的范围内随机选择一个新值
                            min_val, max_val = col_data.min(), col_data.max()
                            if min_val != max_val:
                                new_val = np.random.uniform(min_val, max_val)
                                adv_X.at[idx, col] = new_val
        
        except Exception as e:
            logger.warning(f"生成对抗样本时出错: {str(e)}，使用原始数据")
        
        return adv_X
    
    def _simulate_distribution_shift(self, X, params):
        """模拟分布偏移"""
        shift_strength = params.get('shift_strength', 0.2)
        affected_columns = params.get('columns', None)
        
        # 创建数据副本
        shifted_X = X.copy()
        
        # 选择要偏移的列（默认为所有数值列）
        if affected_columns is None:
            numeric_cols = shifted_X.select_dtypes(include=[np.number]).columns
            affected_columns = numeric_cols.tolist()
        
        # 对选定的列进行分布偏移
        for col in affected_columns:
            if col in shifted_X.columns:
                col_data = shifted_X[col]
                
                # 改变均值
                mean_shift = col_data.std() * shift_strength
                shifted_X[col] = col_data + mean_shift
                
                # 改变方差
                if params.get('change_variance', True):
                    std_multiplier = 1.0 + shift_strength * 0.5  # 增加或减少方差
                    # 重新标准化并应用新的方差
                    mean = shifted_X[col].mean()
                    shifted_X[col] = (shifted_X[col] - mean) * std_multiplier + mean
        
        return shifted_X
    
    def _introduce_extreme_values(self, X, params):
        """引入极值"""
        extreme_ratio = params.get('extreme_ratio', 0.05)  # 5%的数据点设为极值
        multiple = params.get('multiple', 3)  # 极值的倍数（基于标准差）
        
        # 创建数据副本
        extreme_X = X.copy()
        
        # 对每列引入极值
        for col in extreme_X.columns:
            if pd.api.types.is_numeric_dtype(extreme_X[col]):
                col_data = extreme_X[col]
                std = col_data.std() if col_data.std() > 0 else 1.0
                
                # 选择要设为极值的行
                num_extreme = max(1, int(len(extreme_X) * extreme_ratio))
                extreme_indices = np.random.choice(len(extreme_X), num_extreme, replace=False)
                
                # 随机设为极大值或极小值
                for idx in extreme_indices:
                    if np.random.random() > 0.5:
                        # 极大值
                        new_value = col_data.max() + std * multiple
                    else:
                        # 极小值
                        new_value = col_data.min() - std * multiple
                    
                    if hasattr(extreme_X, 'iloc'):
                        extreme_X.at[idx, col] = new_value
                    else:
                        extreme_X[idx][col] = new_value
        
        return extreme_X
    
    def _analyze_performance_change(self, base_performance, test_performance, threshold):
        """分析性能变化"""
        analysis = {
            'changes': {},
            'passed': True
        }
        
        # 检查关键指标的变化
        for metric, base_value in base_performance.items():
            if metric in test_performance:
                test_value = test_performance[metric]
                
                # 计算相对变化
                if metric in ['mse', 'rmse', 'mae']:  # 误差指标，越小越好
                    # 性能下降 = 测试误差增加
                    if base_value > 0:
                        relative_change = (test_value - base_value) / base_value
                    else:
                        relative_change = abs(test_value - base_value)
                else:  # 得分指标，越大越好
                    # 性能下降 = 测试得分减少
                    if base_value > 0:
                        relative_change = (base_value - test_value) / base_value
                    else:
                        relative_change = abs(base_value - test_value)
                
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

# 鲁棒性测试配置示例
robustness_test_configs = [
    {
        'name': '高斯噪声测试',
        'type': 'noise_injection',
        'params': {
            'noise_level': 0.1,  # 10%的噪声
            'noise_type': 'gaussian',
            'threshold': 0.05   # 性能下降不超过5%
        }
    },
    {
        'name': '对抗样本测试',
        'type': 'adversarial_attack',
        'params': {
            'epsilon': 0.1,
            'attack_type': 'fast_gradient',
            'num_samples': 50,
            'threshold': 0.1   # 性能下降不超过10%
        }
    },
    {
        'name': '分布偏移测试',
        'type': 'distribution_shift',
        'params': {
            'shift_strength': 0.2,
            'change_variance': True,
            'threshold': 0.08   # 性能下降不超过8%
        }
    },
    {
        'name': '极值测试',
        'type': 'extreme_values',
        'params': {
            'extreme_ratio': 0.05,
            'multiple': 3,
            'threshold': 0.05   # 性能下降不超过5%
        }
    }
]
