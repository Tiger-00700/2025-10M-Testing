import mlflow
import mlflow.sklearn
import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import tempfile
import os

# 启用自动日志记录
mlflow.autolog()

class MLModelTest:
    def __init__(self):
        # 准备测试数据
        iris = load_iris()
        self.X = iris.data
        self.y = iris.target
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
    
    def test_model_training_and_evaluation(self):
        # 设置实验名称
        mlflow.set_experiment("Iris_Classification_Test")
        
        # 开始MLflow跟踪
        with mlflow.start_run(run_name="RandomForest_Test") as run:
            # 定义和训练模型
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
            model.fit(self.X_train, self.y_train)
            
            # 进行预测
            y_pred = model.predict(self.X_test)
            
            # 计算评估指标
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred, average='macro')
            recall = recall_score(self.y_test, y_pred, average='macro')
            f1 = f1_score(self.y_test, y_pred, average='macro')
            
            # 记录自定义指标
            mlflow.log_metric("test_accuracy", accuracy)
            mlflow.log_metric("test_precision", precision)
            mlflow.log_metric("test_recall", recall)
            mlflow.log_metric("test_f1", f1)
            
            # 记录模型参数
            mlflow.log_param("n_estimators", 100)
            mlflow.log_param("max_depth", 5)
            mlflow.log_param("random_state", 42)
            
            # 创建并记录测试数据集的摘要
            with tempfile.TemporaryDirectory() as tmpdir:
                np.savetxt(os.path.join(tmpdir, "test_data.csv"), self.X_test[:5], delimiter=",")
                mlflow.log_artifact(os.path.join(tmpdir, "test_data.csv"), "test_samples")
            
            # 记录模型
            mlflow.sklearn.log_model(model, "random_forest_model")
            
            print(f"\n模型评估结果:")
            print(f"准确率: {accuracy:.4f}")
            print(f"精确率: {precision:.4f}")
            print(f"召回率: {recall:.4f}")
            print(f"F1分数: {f1:.4f}")
            print(f"\n运行ID: {run.info.run_id}")
            print(f"可在MLflow UI中查看完整实验结果")
            
            # 验证模型性能
            assert accuracy > 0.9, f"模型准确率低于阈值: {accuracy:.4f}"
            assert f1 > 0.9, f"模型F1分数低于阈值: {f1:.4f}"
    
    def test_model_loading_and_prediction(self):
        # 设置实验并开始新的运行
        mlflow.set_experiment("Iris_Classification_Test")
        with mlflow.start_run(run_name="Model_Load_Test") as run:
            # 训练一个简单模型用于测试
            model = RandomForestClassifier(n_estimators=50, random_state=42)
            model.fit(self.X_train, self.y_train)
            
            # 保存模型
            model_uri = mlflow.sklearn.log_model(model, "model_to_test")
            
            # 加载保存的模型
            loaded_model = mlflow.sklearn.load_model(model_uri)
            
            # 用原始模型和加载的模型进行预测
            original_pred = model.predict(self.X_test)
            loaded_pred = loaded_model.predict(self.X_test)
            
            # 验证模型加载是否正确（预测结果应该一致）
            predictions_match = np.array_equal(original_pred, loaded_pred)
            print(f"模型加载测试 - 预测结果一致: {predictions_match}")
            
            # 记录测试结果
            mlflow.log_param("test_type", "model_loading")
            mlflow.log_metric("predictions_match", int(predictions_match))
            
            # 断言测试通过
            assert predictions_match, "加载的模型预测结果与原始模型不一致"
    
    def test_hyperparameter_optimization(self):
        # 设置实验
        mlflow.set_experiment("Iris_Hyperparameter_Optimization")
        
        # 超参数搜索空间
        n_estimators_list = [50, 100, 200]
        max_depth_list = [3, 5, 10]
        
        best_accuracy = 0
        best_params = {}
        
        # 进行超参数优化测试
        for n_estimators in n_estimators_list:
            for max_depth in max_depth_list:
                with mlflow.start_run(run_name=f"RF_n{n_estimators}_d{max_depth}") as run:
                    # 训练模型
                    model = RandomForestClassifier(
                        n_estimators=n_estimators,
                        max_depth=max_depth,
                        random_state=42
                    )
                    model.fit(self.X_train, self.y_train)
                    
                    # 评估模型
                    y_pred = model.predict(self.X_test)
                    accuracy = accuracy_score(self.y_test, y_pred)
                    
                    # 记录参数和指标
                    mlflow.log_param("n_estimators", n_estimators)
                    mlflow.log_param("max_depth", max_depth)
                    mlflow.log_metric("accuracy", accuracy)
                    
                    # 更新最佳模型
                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_params = {"n_estimators": n_estimators, "max_depth": max_depth}
                        # 记录最佳模型
                        mlflow.sklearn.log_model(model, "best_model")
        
        print(f"\n超参数优化结果:")
        print(f"最佳准确率: {best_accuracy:.4f}")
        print(f"最佳参数: {best_params}")

# 运行测试
if __name__ == "__main__":
    tester = MLModelTest()
    
    print("=== 测试1: 模型训练和评估 ===")
    tester.test_model_training_and_evaluation()
    
    print("\n=== 测试2: 模型加载和预测 ===")
    tester.test_model_loading_and_prediction()
    
    print("\n=== 测试3: 超参数优化 ===")
    tester.test_hyperparameter_optimization()
    
    print("\n所有测试完成，请在MLflow UI中查看详细结果。")
    print("运行命令: mlflow ui")
