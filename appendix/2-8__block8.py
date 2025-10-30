# 模拟可视化类（实际应用中替换为真实的可视化库）
class SimpleChart:
    """简单图表类用于示例"""
    
    def __init__(self, data):
        self.data = data
        self.filtered = False
        self.filter_params = None
        
    def render(self):
        """模拟渲染图表"""
        if len(self.data) == 0:
            return "Empty chart"
        return "Chart rendered successfully"
    
    def get_data_range(self):
        """获取数据范围"""
        if len(self.data) == 0:
            return {'min': 0, 'max': 100}
        return {
            'min': self.data['value'].min() if 'value' in self.data.columns else 0,
            'max': self.data['value'].max() if 'value' in self.data.columns else 100
        }
    
    def get_y_range(self):
        """获取Y轴范围"""
        if len(self.data) == 0:
            return {'min': 0, 'max': 100}
        return {
            'min': min(0, self.data['value'].min()) if 'value' in self.data.columns else 0,
            'max': max(100, self.data['value'].max()) if 'value' in self.data.columns else 100
        }
    
    def filter(self, column, value):
        """模拟筛选操作"""
        if column not in self.data.columns:
            raise ValueError(f"Column {column} not found")
        
        self.filtered = True
        self.filter_params = {'column': column, 'value': value}
        return self.data[self.data[column] == value]

def run_visualization_test_suite():
    # 创建测试套件
    test_suite = DataAnalysisTestSuite()
    
    # 准备测试数据
    import pandas as pd
    import numpy as np
    
    test_data = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=30),
        'region': ['North', 'South', 'East', 'West'] * 7 + ['North', 'South'],
        'sales': np.random.randint(1000, 5000, size=30),
        'profit': np.random.randint(100, 2000, size=30)
    })
    
    # 创建可视化
    chart = SimpleChart(test_data)
    
    # 添加数据准确性测试
    accuracy_test = VisualizationDataAccuracyTest(
        "销售图表数据准确性测试",
        test_data,
        chart,
        mappings={'x': 'date', 'y': 'sales', 'color': 'region'}
    )
    test_suite.add_test(accuracy_test)
    
    # 添加交互功能测试
    interaction_test = VisualizationInteractionTest(
        "销售图表交互功能测试",
        chart,
        interaction_tests=interaction_test_cases
    )
    test_suite.add_test(interaction_test)
    
    # 添加边界情况测试
    boundary_test = VisualizationBoundaryTest(
        "销售图表边界情况测试",
        SimpleChart,
        boundary_cases=boundary_test_cases
    )
    test_suite.add_test(boundary_test)
    
    # 运行测试
    summary = test_suite.run_all(parallel=True)
    
    # 生成报告
    report = test_suite.generate_report("visualization_test_report.txt")
    print(report)
    
    return summary

## 8.4 数据挖掘结果验证

### 8.4.1 数据挖掘结果验证的重要性

数据挖掘模型在实际应用中扮演着越来越重要的角色，从市场预测到风险评估，从客户分群到异常检测，其结果直接影响业务决策的质量。然而，数据挖掘过程的复杂性和自动化特性使得结果验证变得尤为重要。一个看似准确的挖掘模型，如果没有经过充分验证，可能会在新数据上表现不佳，甚至产生误导性的结果。

数据挖掘结果验证不仅是确保模型准确性的手段，更是建立业务信任的关键环节。通过系统的验证过程，我们可以发现模型的局限性，识别潜在的偏差，并评估模型在实际业务场景中的适用性。

### 8.4.2 模型准确性验证

模型准确性验证是数据挖掘结果验证的基础，主要通过一系列指标来评估模型的预测能力。以下是一个基于前文框架实现的模型准确性验证类：

```python
class MiningModelAccuracyTest(DataAnalysisTestBase):
    """数据挖掘模型准确性验证测试"""
    
    def __init__(self, test_name, model, test_data, target_column):
        super().__init__(test_name, "验证数据挖掘模型的预测准确性")
        self.model = model  # 数据挖掘模型
        self.test_data = test_data  # 测试数据集
        self.target_column = target_column  # 目标列
        
    def run(self):
        start_time = time.time()
        
        try:
            # 验证输入
            self.validate_input(self.test_data)
            
            # 准备特征和目标
            X_test = self._prepare_features(self.test_data)
            y_true = self.test_data[self.target_column].values
            
            # 进行预测
            y_pred = self._predict(X_test)
            
            # 计算评估指标
            metrics = self._calculate_metrics(y_true, y_pred)
            
            # 判断是否通过
            self.passed = self._evaluate_metrics(metrics)
            self.results = metrics
            
        except Exception as e:
            logger.error(f"模型准确性验证测试执行失败: {str(e)}")
            self.passed = False
            self.results['error'] = str(e)
        
        self.execution_time = time.time() - start_time
    
    def _prepare_features(self, data):
        """准备特征数据"""
        # 移除目标列和ID列等非特征列
        X = data.drop([self.target_column] + [col for col in data.columns if col.lower() in ['id', 'index']], axis=1)
        
        # 处理缺失值
        X = X.fillna(0)  # 简单处理，实际应用中应根据具体情况处理
        
        # 处理类别特征
        for col in X.select_dtypes(include=['object']).columns:
            try:
                # 尝试将类别特征编码为数值
                X[col] = pd.factorize(X[col])[0]
            except Exception as e:
                logger.warning(f"编码特征 {col} 时出错: {str(e)}")
                X = X.drop(col, axis=1)
        
        return X
    
    def _predict(self, X_test):
        """使用模型进行预测"""
        try:
            # 尝试使用不同的预测方法
            if hasattr(self.model, 'predict_proba'):
                # 对于分类问题，可能需要获取概率
                y_pred = self.model.predict_proba(X_test)[:, 1]  # 二分类取正类概率
            else:
                # 默认使用predict方法
                y_pred = self.model.predict(X_test)
            return y_pred
        except Exception as e:
            logger.error(f"模型预测失败: {str(e)}")
            raise
    
    def _calculate_metrics(self, y_true, y_pred):
        """计算评估指标"""
        metrics = {}
        
        try:
            # 判断问题类型（分类或回归）
            is_classification = len(set(y_true)) <= 2  # 简化判断，实际应用中应根据问题类型确定
            
            if is_classification:
                # 分类问题指标
                from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
                
                # 如果预测结果是概率，转换为类别
                if y_pred.min() >= 0 and y_pred.max() <= 1:
                    y_pred_class = (y_pred >= 0.5).astype(int)
                else:
                    y_pred_class = y_pred
                
                metrics['accuracy'] = accuracy_score(y_true, y_pred_class)
                metrics['precision'] = precision_score(y_true, y_pred_class, average='weighted')
                metrics['recall'] = recall_score(y_true, y_pred_class, average='weighted')
                metrics['f1_score'] = f1_score(y_true, y_pred_class, average='weighted')
                
                # 计算ROC AUC（如果可能）
                try:
                    if y_pred.min() >= 0 and y_pred.max() <= 1:
                        metrics['roc_auc'] = roc_auc_score(y_true, y_pred)
                    else:
                        metrics['roc_auc'] = roc_auc_score(y_true, y_pred_class)
                except Exception:
                    metrics['roc_auc'] = None
            else:
                # 回归问题指标
                from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
                
                metrics['mse'] = mean_squared_error(y_true, y_pred)
                metrics['rmse'] = np.sqrt(metrics['mse'])
                metrics['mae'] = mean_absolute_error(y_true, y_pred)
                metrics['r2'] = r2_score(y_true, y_pred)
            
            # 计算混淆矩阵（对于分类问题）
            if is_classification:
                from sklearn.metrics import confusion_matrix
                cm = confusion_matrix(y_true, y_pred_class)
                metrics['confusion_matrix'] = cm.tolist()
            
        except Exception as e:
            logger.error(f"计算指标失败: {str(e)}")
            raise
        
        return metrics
    
    def _evaluate_metrics(self, metrics):
        """评估指标是否满足要求"""
        # 这里可以根据业务需求设置不同的阈值
        # 简化实现，实际应用中应根据具体问题调整
        
        # 分类问题
        if 'accuracy' in metrics:
            # 要求准确率至少达到0.7
            return metrics['accuracy'] >= 0.7
        # 回归问题
        elif 'r2' in metrics:
            # 要求R²至少达到0.6
            return metrics['r2'] >= 0.6
        
        return False
