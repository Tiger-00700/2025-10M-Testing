import unittest
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

class ModelTrainingTest(unittest.TestCase):
    def setUp(self):
        # 创建测试数据集
        self.X, self.y = make_classification(
            n_samples=1000, n_features=20, n_classes=2, 
            random_state=42, n_informative=10, n_redundant=5
        )
        
        # 划分训练集和测试集
        from sklearn.model_selection import train_test_split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
    
    def test_training_parameters(self):
        # 测试不同训练参数的影响
        parameters = [
            {'n_estimators': 50, 'max_depth': 10},
            {'n_estimators': 100, 'max_depth': 10},
            {'n_estimators': 100, 'max_depth': None}
        ]
        
        results = {}
        for param in parameters:
            key = f"n_estimators={param['n_estimators']},max_depth={param['max_depth']}"
            model = RandomForestClassifier(**param, random_state=42)
            model.fit(self.X_train, self.y_train)
            
            train_acc = accuracy_score(self.y_train, model.predict(self.X_train))
            test_acc = accuracy_score(self.y_test, model.predict(self.X_test))
            
            results[key] = {'train_acc': train_acc, 'test_acc': test_acc}
            print(f"{key}: 训练准确率={train_acc:.4f}, 测试准确率={test_acc:.4f}")
        
        # 验证增加树的数量通常会提高性能
        self.assertGreater(
            results["n_estimators=100,max_depth=10"]['test_acc'],
            results["n_estimators=50,max_depth=10"]['test_acc']
        )
    
    def test_training_convergence(self):
        # 测试训练收敛性
        from sklearn.ensemble import GradientBoostingClassifier
        import warnings
        warnings.filterwarnings('ignore')
        
        # 跟踪每棵树的训练损失
        model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, 
                                         random_state=42, validation_fraction=0.2, 
                                         n_iter_no_change=5)
        
        model.fit(self.X_train, self.y_train)
        
        # 获取训练和验证损失
        train_score = model.train_score_
        
        # 验证损失函数是否单调递减（准确率是否单调递增）
        self.assertTrue(np.all(np.diff(train_score) >= 0))
        
        print(f"初始训练准确率: {train_score[0]:.4f}")
        print(f"最终训练准确率: {train_score[-1]:.4f}")
        print(f"训练是否提前停止: {model.n_estimators_ < 100}")
        print(f"使用的树数量: {model.n_estimators_}")
    
    def test_overfitting_detection(self):
        # 测试过拟合/欠拟合检测
        # 使用不同深度的决策树来模拟欠拟合和过拟合
        from sklearn.tree import DecisionTreeClassifier
        
        depths = [1, 5, 10, None]  # None表示完全生长
        results = {}
        
        for depth in depths:
            model = DecisionTreeClassifier(max_depth=depth, random_state=42)
            model.fit(self.X_train, self.y_train)
            
            train_acc = accuracy_score(self.y_train, model.predict(self.X_train))
            test_acc = accuracy_score(self.y_test, model.predict(self.X_test))
            
            results[depth] = {'train_acc': train_acc, 'test_acc': test_acc}
            print(f"深度={depth}: 训练准确率={train_acc:.4f}, 测试准确率={test_acc:.4f}")
        
        # 验证过拟合模式：当深度增加时，训练准确率提高但测试准确率可能下降
        shallow_depth = 1
        deep_depth = None
        
        self.assertGreater(results[deep_depth]['train_acc'], results[shallow_depth]['train_acc'])
        
        # 计算过拟合程度
        overfitting_gap = results[deep_depth]['train_acc'] - results[deep_depth]['test_acc']
        print(f"过拟合程度（训练-测试准确率差距）: {overfitting_gap:.4f}")
        
        # 验证过拟合程度在合理范围内
        self.assertLess(overfitting_gap, 0.3)  # 差距不应过大
    
    def test_cross_validation(self):
        # 测试不同交叉验证策略
        from sklearn.model_selection import KFold, StratifiedKFold, ShuffleSplit
        
        model = RandomForestClassifier(random_state=42)
        
        # 标准KFold
        kf_scores = cross_val_score(model, self.X_train, self.y_train, cv=5, scoring='accuracy')
        
        # 分层KFold（对于分类问题更合适）
        skf_scores = cross_val_score(model, self.X_train, self.y_train, 
                                   cv=StratifiedKFold(5), scoring='accuracy')
        
        # 随机打乱分割
        ss_scores = cross_val_score(model, self.X_train, self.y_train, 
                                  cv=ShuffleSplit(5, test_size=0.2), scoring='accuracy')
        
        print(f"标准KFold: 均值={np.mean(kf_scores):.4f}, 标准差={np.std(kf_scores):.4f}")
        print(f"分层KFold: 均值={np.mean(skf_scores):.4f}, 标准差={np.std(skf_scores):.4f}")
        print(f"随机打乱: 均值={np.mean(ss_scores):.4f}, 标准差={np.std(ss_scores):.4f}")
        
        # 验证交叉验证的稳定性
        self.assertLess(np.std(skf_scores), 0.05)  # 标准差应小于5%
    
    def test_hyperparameter_optimization(self):
        # 测试超参数优化
        model = RandomForestClassifier(random_state=42)
        
        # 定义参数网格
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10]
        }
        
        # 网格搜索
        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
        grid_search.fit(self.X_train, self.y_train)
        
        print(f"最佳参数: {grid_search.best_params_}")
        print(f"最佳交叉验证准确率: {grid_search.best_score_:.4f}")
        
        # 验证调优后的模型性能
        best_model = grid_search.best_estimator_
        test_accuracy = accuracy_score(self.y_test, best_model.predict(self.X_test))
        print(f"测试集准确率: {test_accuracy:.4f}")
        
        # 验证交叉验证分数和测试分数的一致性
        self.assertAlmostEqual(grid_search.best_score_, test_accuracy, places=2)

if __name__ == '__main__':
    unittest.main()
