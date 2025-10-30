class ModelDriftDetectionTest(DataAnalysisTestBase):
    """AI模型漂移检测测试"""
    
    def __init__(self, test_name, model, reference_data, current_data, target_column):
        super().__init__(test_name, "检测模型在新数据上是否出现性能下降")
        self.model = model  # 训练好的模型
        self.reference_data = reference_data  # 参考数据（例如，训练时使用的数据）
        self.current_data = current_data  # 当前数据（新数据）
        self.target_column = target_column  # 目标列
        
    def run(self):
        start_time = time.time()
        
        try:
            # 验证输入
            self.validate_input(self.reference_data)
            self.validate_input(self.current_data)
            
            # 准备参考数据和当前数据
            X_ref, y_ref = self._prepare_data(self.reference_data)
            X_curr, y_curr = self._prepare_data(self.current_data)
            
            # 检测特征分布漂移
            feature_drift_results = self._detect_feature_drift(X_ref, X_curr)
            
            # 检测模型性能漂移
            performance_drift_results = self._detect_performance_drift(X_ref, y_ref, X_curr, y_curr)
            
            # 检测预测分布漂移
            prediction_drift_results = self._detect_prediction_drift(X_ref, X_curr)
            
            # 综合分析
            analysis = self._analyze_drift_results(
                feature_drift_results,
                performance_drift_results,
                prediction_drift_results
            )
            
            # 判断是否通过
            self.passed = analysis['passed']
            self.results = {
                'feature_drift': feature_drift_results,
                'performance_drift': performance_drift_results,
                'prediction_drift': prediction_drift_results,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"模型漂移检测失败: {str(e)}")
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
    
    def _detect_feature_drift(self, X_ref, X_curr):
        """检测特征分布漂移"""
        feature_drift = {}
        
        # 对每列特征进行分布漂移检测
        for col in X_ref.columns:
            if col in X_curr.columns:
                try:
                    ref_data = X_ref[col]
                    curr_data = X_curr[col]
                    
                    # 检查是否为数值型特征
                    if pd.api.types.is_numeric_dtype(ref_data) and pd.api.types.is_numeric_dtype(curr_data):
                        # 使用统计测试检测分布差异
                        from scipy.stats import ks_2samp
                        
                        # Kolmogorov-Smirnov测试
                        ks_statistic, ks_pvalue = ks_2samp(ref_data, curr_data)
                        
                        feature_drift[col] = {
                            'method': 'kolmogorov_smirnov',
                            'statistic': float(ks_statistic),
                            'p_value': float(ks_pvalue),
                            'drift_detected': ks_pvalue < 0.05,  # p值小于0.05认为存在显著差异
                            'distribution_change_score': 1.0 - ks_pvalue  # 值越高表示变化越大
                        }
                    else:
                        # 对于类别特征，使用卡方检验
                        from scipy.stats import chi2_contingency
                        
                        # 创建列联表
                        ref_counts = ref_data.value_counts()
                        curr_counts = curr_data.value_counts()
                        
                        # 合并两个分布的所有唯一值
                        all_values = sorted(set(ref_counts.index) | set(curr_counts.index))
                        
                        # 构建观测频率矩阵
                        observed = []
                        for val in all_values:
                            observed.append([
                                ref_counts.get(val, 0),
                                curr_counts.get(val, 0)
                            ])
                        
                        # 执行卡方检验
                        chi2_statistic, chi2_pvalue, dof, expected = chi2_contingency(observed)
                        
                        feature_drift[col] = {
                            'method': 'chi_square',
                            'statistic': float(chi2_statistic),
                            'p_value': float(chi2_pvalue),
                            'drift_detected': chi2_pvalue < 0.05,
                            'distribution_change_score': 1.0 - chi2_pvalue
                        }
                
                except Exception as e:
                    logger.warning(f"检测特征 {col} 的分布漂移时出错: {str(e)}")
                    feature_drift[col] = {
                        'error': str(e),
                        'drift_detected': False
                    }
        
        # 计算总体特征漂移分数
        drift_scores = [f['distribution_change_score'] for f in feature_drift.values() if 'distribution_change_score' in f]
        if drift_scores:
            overall_drift_score = np.mean(drift_scores)
            feature_drift['overall'] = {
                'drift_score': float(overall_drift_score),
                'num_features_drifted': sum(1 for f in feature_drift.values() if f.get('drift_detected', False) and f != 'overall'),
                'total_features': len([f for f in feature_drift.keys() if f != 'overall'])
            }
        
        return feature_drift
    
    def _detect_performance_drift(self, X_ref, y_ref, X_curr, y_curr):
        """检测模型性能漂移"""
        performance_drift = {}
        
        try:
            # 在参考数据上评估模型性能
            ref_performance = self._evaluate_model(X_ref, y_ref)
            
            # 在当前数据上评估模型性能
            curr_performance = self._evaluate_model(X_curr, y_curr)
            
            # 计算性能差异
            performance_changes = {}
            performance_drift_detected = False
            
            for metric, ref_value in ref_performance.items():
                if metric in curr_performance:
                    curr_value = curr_performance[metric]
                    
                    # 计算相对变化
                    if metric in ['mse', 'rmse', 'mae']:  # 误差指标，越小越好
                        if ref_value > 0:
                            relative_change = (curr_value - ref_value) / ref_value
                            performance_deterioration = relative_change > 0
                        else:
                            relative_change = abs(curr_value - ref_value)
                            performance_deterioration = curr_value > ref_value
                    else:  # 得分指标，越大越好
                        if ref_value > 0:
                            relative_change = (ref_value - curr_value) / ref_value
                            performance_deterioration = relative_change > 0
                        else:
                            relative_change = abs(ref_value - curr_value)
                            performance_deterioration = curr_value < ref_value
                    
                    performance_changes[metric] = {
                        'reference_value': ref_value,
                        'current_value': curr_value,
                        'absolute_change': curr_value - ref_value,
                        'relative_change': relative_change,
                        'deteriorated': performance_deterioration,
                        'significant_deterioration': abs(relative_change) > 0.1  # 变化超过10%认为显著
                    }
                    
                    if performance_changes[metric]['significant_deterioration'] and performance_deterioration:
                        performance_drift_detected = True
            
            performance_drift = {
                'reference_performance': ref_performance,
                'current_performance': curr_performance,
                'changes': performance_changes,
                'drift_detected': performance_drift_detected
            }
        
        except Exception as e:
            logger.error(f"检测性能漂移时出错: {str(e)}")
            performance_drift['error'] = str(e)
            performance_drift['drift_detected'] = False
        
        return performance_drift
    
    def _evaluate_model(self, X, y):
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
    
    def _detect_prediction_drift(self, X_ref, X_curr):
        """检测预测分布漂移"""
        prediction_drift = {}
        
        try:
            # 在参考数据上进行预测
            ref_predictions = self.model.predict(X_ref)
            
            # 在当前数据上进行预测
            curr_predictions = self.model.predict(X_curr)
            
            # 如果预测是概率分布，取主要类别或概率
            if hasattr(ref_predictions, 'shape') and len(ref_predictions.shape) > 1:
                if ref_predictions.shape[1] > 1:  # 多类别分类
                    ref_pred_classes = np.argmax(ref_predictions, axis=1)
                    curr_pred_classes = np.argmax(curr_predictions, axis=1)
                else:  # 二分类概率
                    ref_pred_classes = (ref_predictions[:, 0] >= 0.5).astype(int)
                    curr_pred_classes = (curr_predictions[:, 0] >= 0.5).astype(int)
            else:
                ref_pred_classes = ref_predictions
                curr_pred_classes = curr_predictions
            
            # 使用统计测试检测预测分布差异
            from scipy.stats import ks_2samp, chi2_contingency
            
            # 检查预测值是否为连续型
            if len(set(ref_pred_classes)) > 10:  # 假设超过10个不同值为连续型
                # 使用KS检验
                ks_statistic, ks_pvalue = ks_2samp(ref_pred_classes, curr_pred_classes)
                
                prediction_drift = {
                    'method': 'kolmogorov_smirnov',
                    'statistic': float(ks_statistic),
                    'p_value': float(ks_pvalue),
                    'drift_detected': ks_pvalue < 0.05,
                    'distribution_change_score': 1.0 - ks_pvalue
                }
            else:
                # 使用卡方检验
                ref_counts = pd.Series(ref_pred_classes).value_counts()
                curr_counts = pd.Series(curr_pred_classes).value_counts()
                
                # 合并两个分布的所有唯一值
                all_values = sorted(set(ref_counts.index) | set(curr_counts.index))
                
                # 构建观测频率矩阵
                observed = []
                for val in all_values:
                    observed.append([
                        ref_counts.get(val, 0),
                        curr_counts.get(val, 0)
                    ])
                
                # 执行卡方检验
                chi2_statistic, chi2_pvalue, dof, expected = chi2_contingency(observed)
                
                prediction_drift = {
                    'method': 'chi_square',
                    'statistic': float(chi2_statistic),
                    'p_value': float(chi2_pvalue),
                    'drift_detected': chi2_pvalue < 0.05,
                    'distribution_change_score': 1.0 - chi2_pvalue
                }
            
            # 计算预测分布的一些基本统计量
            prediction_drift['reference_distribution'] = {
                'mean': float(np.mean(ref_pred_classes)),
                'std': float(np.std(ref_pred_classes)),
                'unique_values': len(set(ref_pred_classes))
            }
            
            prediction_drift['current_distribution'] = {
                'mean': float(np.mean(curr_pred_classes)),
                'std': float(np.std(curr_pred_classes)),
                'unique_values': len(set(curr_pred_classes))
            }
            
        except Exception as e:
            logger.error(f"检测预测漂移时出错: {str(e)}")
            prediction_drift['error'] = str(e)
            prediction_drift['drift_detected'] = False
        
        return prediction_drift
    
    def _analyze_drift_results(self, feature_drift, performance_drift, prediction_drift):
        """综合分析漂移结果"""
        analysis = {
            'drift_summary': {},
            'passed': True,
            'recommendations': []
        }
        
        # 总结各类漂移检测结果
        analysis['drift_summary'] = {
            'feature_drift_detected': feature_drift.get('overall', {}).get('num_features_drifted', 0) > 0,
            'performance_drift_detected': performance_drift.get('drift_detected', False),
            'prediction_drift_detected': prediction_drift.get('drift_detected', False),
            'num_features_drifted': feature_drift.get('overall', {}).get('num_features_drifted', 0),
            'total_features': feature_drift.get('overall', {}).get('total_features', 0)
        }
        
        # 判断是否存在严重漂移
        has_severe_drift = False
        
        # 检查性能漂移
        if performance_drift.get('drift_detected', False):
            has_severe_drift = True
            analysis['passed'] = False
            analysis['recommendations'].append("模型性能显著下降，建议重新训练模型")
            
            # 识别哪些指标下降最严重
            worst_metric = None
            worst_change = 0
            
            for metric, change_info in performance_drift.get('changes', {}).items():
                if change_info.get('significant_deterioration', False):
                    if abs(change_info.get('relative_change', 0)) > worst_change:
                        worst_change = abs(change_info.get('relative_change', 0))
                        worst_metric = metric
            
            if worst_metric:
                analysis['recommendations'].append(f"重点关注 {worst_metric} 指标，相对变化: {worst_change:.2%}")
        
        # 检查特征漂移
        num_drifted = feature_drift.get('overall', {}).get('num_features_drifted', 0)
        total_features = feature_drift.get('overall', {}).get('total_features', 0)
        
        if total_features > 0:
            drift_percentage = (num_drifted / total_features) * 100
            
            if drift_percentage > 30:  # 超过30%的特征发生漂移
                has_severe_drift = True
                analysis['passed'] = False
                analysis['recommendations'].append(f"超过30%的特征分布发生变化 ({drift_percentage:.1f}%)，建议更新数据预处理流程")
            elif num_drifted > 0:
                analysis['recommendations'].append(f"有 {num_drifted} 个特征分布发生变化，建议监控这些特征")
        
        # 检查预测漂移
        if prediction_drift.get('drift_detected', False) and not has_severe_drift:
            analysis['recommendations'].append("预测分布发生变化，建议进一步调查原因")
        
        # 如果没有检测到漂移
        if analysis['passed']:
            analysis['recommendations'].append("未检测到明显的模型漂移，可以继续使用当前模型")
            analysis['recommendations'].append("建议定期执行漂移检测，特别是当业务环境发生变化时")
        
        return analysis
