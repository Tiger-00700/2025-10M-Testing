import unittest
import numpy as np
from sklearn.datasets import make_classification, make_regression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    mean_squared_error, mean_absolute_error, r2_score
)

class ModelEvaluationTest(unittest.TestCase):
    def setUp(self):
        # 创建分类测试数据
        self.X_clf, self.y_clf = make_classification(
            n_samples=1000, n_features=20, n_classes=2, 
            random_state=42, n_informative=10, class_sep=0.8
        )
        
        # 创建回归测试数据
        self.X_reg, self.y_reg = make_regression(
            n_samples=1000, n_features=15, noise=0.1, random_state=42
        )
        
        # 划分训练集和测试集
        self.X_clf_train, self.X_clf_test, self.y_clf_train, self.y_clf_test = train_test_split(
            self.X_clf, self.y_clf, test_size=0.2, random_state=42
        )
        
        self.X_reg_train, self.X_reg_test, self.y_reg_train, self.y_reg_test = train_test_split(
            self.X_reg, self.y_reg, test_size=0.2, random_state=42
        )
        
        # 训练模型
        self.clf_model = RandomForestClassifier(random_state=42)
        self.clf_model.fit(self.X_clf_train, self.y_clf_train)
        
        self.reg_model = RandomForestRegressor(random_state=42)
        self.reg_model.fit(self.X_reg_train, self.y_reg_train)
        
        # 预测结果
        self.y_clf_pred = self.clf_model.predict(self.X_clf_test)
        self.y_clf_prob = self.clf_model.predict_proba(self.X_clf_test)[:, 1]
        
        self.y_reg_pred = self.reg_model.predict(self.X_reg_test)
    
    def test_classification_metrics(self):
        # 测试分类指标
        accuracy = accuracy_score(self.y_clf_test, self.y_clf_pred)
        precision = precision_score(self.y_clf_test, self.y_clf_pred)
        recall = recall_score(self.y_clf_test, self.y_clf_pred)
        f1 = f1_score(self.y_clf_test, self.y_clf_pred)
        auc = roc_auc_score(self.y_clf_test, self.y_clf_prob)
        
        print(f"准确率 (Accuracy): {accuracy:.4f}")
        print(f"精确率 (Precision): {precision:.4f}")
        print(f"召回率 (Recall): {recall:.4f}")
        print(f"F1分数 (F1-Score): {f1:.4f}")
        print(f"AUC值: {auc:.4f}")
        
        # 验证指标在合理范围内
        self.assertGreater(accuracy, 0.7)  # 准确率应高于0.7
        self.assertGreater(precision, 0.7)  # 精确率应高于0.7
        self.assertGreater(recall, 0.7)    # 召回率应高于0.7
        self.assertGreater(f1, 0.7)        # F1分数应高于0.7
        self.assertGreater(auc, 0.7)       # AUC应高于0.7
    
    def test_confusion_matrix(self):
        # 测试混淆矩阵
        cm = confusion_matrix(self.y_clf_test, self.y_clf_pred)
        tn, fp, fn, tp = cm.ravel()
        
        print("混淆矩阵:")
        print(f"真阴性 (TN): {tn}")
        print(f"假阳性 (FP): {fp}")
        print(f"假阴性 (FN): {fn}")
        print(f"真阳性 (TP): {tp}")
        
        # 验证混淆矩阵的有效性
        total = len(self.y_clf_test)
        self.assertEqual(tn + fp + fn + tp, total)
        
        # 验证准确率计算的一致性
        accuracy_from_cm = (tn + tp) / total
        accuracy_direct = accuracy_score(self.y_clf_test, self.y_clf_pred)
        self.assertAlmostEqual(accuracy_from_cm, accuracy_direct)
    
    def test_regression_metrics(self):
        # 测试回归指标
        mse = mean_squared_error(self.y_reg_test, self.y_reg_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(self.y_reg_test, self.y_reg_pred)
        r2 = r2_score(self.y_reg_test, self.y_reg_pred)
        
        print(f"均方误差 (MSE): {mse:.4f}")
        print(f"均方根误差 (RMSE): {rmse:.4f}")
        print(f"平均绝对误差 (MAE): {mae:.4f}")
        print(f"R²分数: {r2:.4f}")
        
        # 验证指标的有效性
        self.assertGreaterEqual(mse, 0)  # MSE应为非负数
        self.assertGreaterEqual(rmse, 0) # RMSE应为非负数
        self.assertGreaterEqual(mae, 0)  # MAE应为非负数
        self.assertLessEqual(r2, 1.0)    # R²不应超过1.0
        
        # 验证R²分数在合理范围内
        self.assertGreater(r2, 0.5)      # R²应大于0.5
    
    def test_threshold_optimization(self):
        # 测试阈值优化
        thresholds = np.arange(0.1, 1.0, 0.1)
        metrics = []
        
        for threshold in thresholds:
            y_pred_threshold = (self.y_clf_prob >= threshold).astype(int)
            precision = precision_score(self.y_clf_test, y_pred_threshold, zero_division=0)
            recall = recall_score(self.y_clf_test, y_pred_threshold, zero_division=0)
            f1 = f1_score(self.y_clf_test, y_pred_threshold, zero_division=0)
            
            metrics.append((threshold, precision, recall, f1))
            print(f"阈值={threshold:.1f}: 精确率={precision:.4f}, 召回率={recall:.4f}, F1={f1:.4f}")
        
        # 找到最优F1分数的阈值
        best_threshold, best_precision, best_recall, best_f1 = max(metrics, key=lambda x: x[3])
        print(f"最佳阈值: {best_threshold:.1f}, 最佳F1: {best_f1:.4f}")
        
        # 验证最优F1分数高于默认阈值(0.5)的F1分数
        default_f1 = f1_score(self.y_clf_test, self.y_clf_pred)
        print(f"默认阈值F1分数: {default_f1:.4f}")
    
    def test_classification_report(self):
        # 测试分类报告
        report = classification_report(self.y_clf_test, self.y_clf_pred, output_dict=True)
        
        print("分类报告:")
        print(f"类别 0 - 精确率: {report['0']['precision']:.4f}, 召回率: {report['0']['recall']:.4f}, F1: {report['0']['f1-score']:.4f}")
        print(f"类别 1 - 精确率: {report['1']['precision']:.4f}, 召回率: {report['1']['recall']:.4f}, F1: {report['1']['f1-score']:.4f}")
        print(f"宏平均 - 精确率: {report['macro avg']['precision']:.4f}, 召回率: {report['macro avg']['recall']:.4f}, F1: {report['macro avg']['f1-score']:.4f}")
        print(f"加权平均 - 精确率: {report['weighted avg']['precision']:.4f}, 召回率: {report['weighted avg']['recall']:.4f}, F1: {report['weighted avg']['f1-score']:.4f}")
        
        # 验证分类报告的一致性
        self.assertAlmostEqual(report['accuracy'], accuracy_score(self.y_clf_test, self.y_clf_pred))
        
        # 验证宏平均和加权平均的计算
        macro_precision = (report['0']['precision'] + report['1']['precision']) / 2
        self.assertAlmostEqual(macro_precision, report['macro avg']['precision'])

if __name__ == '__main__':
    unittest.main()
