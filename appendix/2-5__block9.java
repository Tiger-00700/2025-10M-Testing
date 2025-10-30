import org.apache.flink.api.common.functions.ReduceFunction;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.assigners.SlidingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.util.KeyedOneInputStreamOperatorTestHarness;
import org.apache.flink.streaming.util.WindowOperatorTestHarness;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class WindowOperationTest {
    
    private WindowOperatorTestHarness<String, Tuple2<String, Integer>, Integer, ?, TimeWindow>
            tumblingWindowHarness;
    
    @BeforeEach
    void setUp() throws Exception {
        // 创建滚动窗口测试Harness
        tumblingWindowHarness = new WindowOperatorTestHarness<>(
                TumblingProcessingTimeWindows.of(Time.seconds(5)),
                new WindowFunction<String, Tuple2<String, Integer>, Integer, TimeWindow>() {
                    @Override
                    public void apply(String key, TimeWindow window, Iterable<Tuple2<String, Integer>> input,
                                     Collector<Integer> out) throws Exception {
                        int sum = 0;
                        for (Tuple2<String, Integer> value : input) {
                            sum += value.f1;
                        }
                        out.collect(sum);
                    }
                },
                new KeySelector<Tuple2<String, Integer>, String>() {
                    @Override
                    public String getKey(Tuple2<String, Integer> value) throws Exception {
                        return value.f0;
                    }
                },
                String.class,
                new ValueStateDescriptor<>("window-contents", Types.TUPLE(Types.STRING, Types.INT)),
                new ReduceFunction<Tuple2<String, Integer>>() {
                    @Override
                    public Tuple2<String, Integer> reduce(Tuple2<String, Integer> value1,
                                                         Tuple2<String, Integer> value2) {
                        return new Tuple2<>(value1.f0, value1.f1 + value2.f1);
                    }
                }
        );
        
        // 初始化测试Harness
        tumblingWindowHarness.open();
    }
    
    @Test
    void testTumblingWindow() throws Exception {
        // 发送测试数据到不同窗口
        tumblingWindowHarness.processElement(new Tuple2<>("key1", 1), 0L);  // 窗口[0,5)
        tumblingWindowHarness.processElement(new Tuple2<>("key1", 2), 3L);  // 窗口[0,5)
        tumblingWindowHarness.processElement(new Tuple2<>("key1", 3), 5L);  // 窗口[5,10)
        tumblingWindowHarness.processElement(new Tuple2<>("key1", 4), 7L);  // 窗口[5,10)
        
        // 触发第一个窗口计算
        tumblingWindowHarness advanceProcessingTime(5L);
        
        // 获取结果
        List<Integer> results = new ArrayList<>();
        for (Integer result : tumblingWindowHarness.extractOutputValues()) {
            results.add(result);
        }
        
        // 验证第一个窗口结果
        assertEquals(1, results.size());
        assertEquals(3, results.get(0));  // 1+2=3
        
        // 触发第二个窗口计算
        tumblingWindowHarness.advanceProcessingTime(10L);
        
        // 获取更多结果
        results.clear();
        for (Integer result : tumblingWindowHarness.extractOutputValues()) {
            results.add(result);
        }
        
        // 验证第二个窗口结果
        assertEquals(1, results.size());
        assertEquals(7, results.get(0));  // 3+4=7
    }
    
    @Test
    void testSlidingWindow() throws Exception {
        // 创建滑动窗口测试Harness
        WindowOperatorTestHarness<String, Tuple2<String, Integer>, Integer, ?, TimeWindow>
                slidingWindowHarness = new WindowOperatorTestHarness<>(
                SlidingProcessingTimeWindows.of(Time.seconds(5), Time.seconds(2)),
                new WindowFunction<String, Tuple2<String, Integer>, Integer, TimeWindow>() {
                    @Override
                    public void apply(String key, TimeWindow window, Iterable<Tuple2<String, Integer>> input,
                                     Collector<Integer> out) throws Exception {
                        int sum = 0;
                        for (Tuple2<String, Integer> value : input) {
                            sum += value.f1;
                        }
                        out.collect(sum);
                    }
                },
                new KeySelector<Tuple2<String, Integer>, String>() {
                    @Override
                    public String getKey(Tuple2<String, Integer> value) throws Exception {
                        return value.f0;
                    }
                },
                String.class,
                new ValueStateDescriptor<>("window-contents", Types.TUPLE(Types.STRING, Types.INT)),
                new ReduceFunction<Tuple2<String, Integer>>() {
                    @Override
                    public Tuple2<String, Integer> reduce(Tuple2<String, Integer> value1,
                                                         Tuple2<String, Integer> value2) {
                        return new Tuple2<>(value1.f0, value1.f1 + value2.f1);
                    }
                }
        );
        
        slidingWindowHarness.open();
        
        // 发送测试数据
        slidingWindowHarness.processElement(new Tuple2<>("key1", 1), 0L);  // 窗口[0,5), [2,7)
        slidingWindowHarness.processElement(new Tuple2<>("key1", 2), 2L);  // 窗口[0,5), [2,7), [4,9)
        slidingWindowHarness.processElement(new Tuple2<>("key1", 3), 4L);  // 窗口[2,7), [4,9), [6,11)
        
        // 触发窗口计算
        slidingWindowHarness.advanceProcessingTime(5L);
        slidingWindowHarness.advanceProcessingTime(7L);
        slidingWindowHarness.advanceProcessingTime(9L);
        
        // 获取结果
        List<Integer> results = new ArrayList<>();
        for (Integer result : slidingWindowHarness.extractOutputValues()) {
            results.add(result);
        }
        
        // 验证滑动窗口结果
        assertEquals(3, results.size());
        // 窗口[0,5)结果: 1+2=3
        // 窗口[2,7)结果: 2+3=5
        // 窗口[4,9)结果: 3
        assertTrue(results.contains(3));
        assertTrue(results.contains(5));
        assertTrue(results.contains(3));
    }
}

## 5.4 机器学习模型测试

机器学习模型测试是确保模型质量和可靠性的关键环节，涵盖从数据准备到模型监控的全生命周期。本节将详细介绍机器学习测试的各个方面和最佳实践。

### 5.4.1 特征工程测试
特征工程是机器学习流程中至关重要的一步，直接影响模型的性能。特征工程测试确保特征能够有效表达数据的关键信息，并适用于后续的模型训练。

- **特征提取测试**：验证从原始数据中提取的特征是否准确、完整，包括文本特征、图像特征、时序特征等。
- **特征转换测试**：测试特征的各种转换操作，如独热编码、标签编码、标准化、归一化等的正确性。
- **特征选择验证**：确认特征选择方法的有效性，验证所选特征是否包含足够的信息来预测目标变量。
- **特征缩放测试**：验证特征缩放的实现，确保不同量级的特征能够公平参与模型训练。
- **特征重要性分析**：测试特征重要性评估方法，验证模型对各个特征的依赖程度。
- **处理缺失值测试**：验证缺失值处理逻辑，确保缺失值的处理不会引入偏差或错误。

**特征工程测试示例**：
```python
import unittest
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer, KNNImputer

class FeatureEngineeringTest(unittest.TestCase):
    def setUp(self):
        # 创建测试数据集
        np.random.seed(42)
        n_samples = 100
        
        # 创建基础特征
        self.X = pd.DataFrame({
            'numeric1': np.random.normal(0, 1, n_samples),
            'numeric2': np.random.normal(10, 5, n_samples),  # 不同量级的数值特征
            'category': np.random.choice(['A', 'B', 'C'], n_samples),
            'binary': np.random.choice([0, 1], n_samples)
        })
        
        # 添加一些缺失值
        mask = np.random.rand(n_samples, 4) < 0.1  # 10%的缺失率
        self.X_missing = self.X.copy()
        self.X_missing[mask] = np.nan
        
        # 创建目标变量（与numeric1和category有一定相关性）
        self.y = ((self.X['numeric1'] > 0) & (self.X['category'] != 'C')).astype(int)
    
    def test_feature_extraction(self):
        # 测试特征提取（例如从类别变量提取特征）
        # 使用get_dummies进行独热编码
        X_encoded = pd.get_dummies(self.X, columns=['category'], drop_first=True)
        
        print("原始特征数量:", self.X.shape[1])
        print("编码后特征数量:", X_encoded.shape[1])
        
        # 验证独热编码的结果
        self.assertTrue('category_B' in X_encoded.columns)
        self.assertTrue('category_C' in X_encoded.columns)
        self.assertFalse('category_A' in X_encoded.columns)  # drop_first=True
        
        # 验证编码后的数据类型
        for col in X_encoded.columns:
            self.assertTrue(np.issubdtype(X_encoded[col].dtype, np.number))
    
    def test_feature_scaling(self):
        # 测试特征缩放
        numeric_cols = ['numeric1', 'numeric2']
        
        # 测试StandardScaler（标准化）
        scaler_std = StandardScaler()
        X_std = scaler_std.fit_transform(self.X[numeric_cols])
        
        # 验证标准化后的数据均值接近0，标准差接近1
        self.assertTrue(np.allclose(X_std.mean(axis=0), 0, atol=1e-10))
        self.assertTrue(np.allclose(X_std.std(axis=0), 1, atol=1e-10))
        
        # 测试MinMaxScaler（归一化）
        scaler_minmax = MinMaxScaler()
        X_minmax = scaler_minmax.fit_transform(self.X[numeric_cols])
        
        # 验证归一化后的数据范围在[0,1]之间
        self.assertTrue(np.all(X_minmax >= 0))
        self.assertTrue(np.all(X_minmax <= 1))
        
        print(f"标准化后的均值: {X_std.mean(axis=0)}")
        print(f"标准化后的标准差: {X_std.std(axis=0)}")
        print(f"归一化后的最小值: {X_minmax.min(axis=0)}")
        print(f"归一化后的最大值: {X_minmax.max(axis=0)}")
    
    def test_feature_selection(self):
        # 测试特征选择
        # 先对类别特征进行独热编码
        X_encoded = pd.get_dummies(self.X, columns=['category'], drop_first=True)
        
        # 使用SelectKBest选择最佳的3个特征
        selector = SelectKBest(f_classif, k=3)
        X_selected = selector.fit_transform(X_encoded, self.y)
        
        # 获取选中的特征索引
        selected_indices = selector.get_support(indices=True)
        selected_features = X_encoded.columns[selected_indices]
        
        print("选中的特征:", list(selected_features))
        
        # 验证选择的特征数量
        self.assertEqual(X_selected.shape[1], 3)
        
        # 验证最重要的特征应该包含numeric1（我们的构造数据中，这个特征与目标变量高度相关）
        self.assertTrue('numeric1' in selected_features)
        
        # 验证特征得分
        scores = selector.scores_
        print("特征得分:", dict(zip(X_encoded.columns, scores)))
        self.assertGreater(scores.max(), 10)  # 最强特征的得分应该显著高于0
    
    def test_missing_value_handling(self):
        # 测试缺失值处理
        numeric_cols = ['numeric1', 'numeric2']
        
        # 测试均值填充
        imputer_mean = SimpleImputer(strategy='mean')
        X_imputed_mean = imputer_mean.fit_transform(self.X_missing[numeric_cols])
        
        # 测试中位数填充
        imputer_median = SimpleImputer(strategy='median')
        X_imputed_median = imputer_median.fit_transform(self.X_missing[numeric_cols])
        
        # 测试KNN填充
        imputer_knn = KNNImputer(n_neighbors=5)
        X_imputed_knn = imputer_knn.fit_transform(self.X_missing[numeric_cols])
        
        # 验证填充后没有缺失值
        self.assertFalse(np.isnan(X_imputed_mean).any())
        self.assertFalse(np.isnan(X_imputed_median).any())
        self.assertFalse(np.isnan(X_imputed_knn).any())
        
        # 比较不同填充方法的结果
        print("均值填充与中位数填充的差异:", 
              np.mean(np.abs(X_imputed_mean - X_imputed_median)))
        print("均值填充与KNN填充的差异:", 
              np.mean(np.abs(X_imputed_mean - X_imputed_knn)))
    
    def test_feature_importance(self):
        # 测试特征重要性分析
        # 对类别特征进行独热编码
        X_encoded = pd.get_dummies(self.X, columns=['category'], drop_first=True)
        
        # 训练随机森林模型
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_encoded, self.y)
        
        # 获取特征重要性
        importances = model.feature_importances_
        feature_importance = dict(zip(X_encoded.columns, importances))
        
        # 按重要性排序
        sorted_importance = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        print("特征重要性（排序）:")
        for feature, importance in sorted_importance:
            print(f"  {feature}: {importance:.4f}")
        
        # 验证最重要的特征应该是numeric1（在我们的构造数据中）
        most_important_feature = sorted_importance[0][0]
        print(f"最重要的特征: {most_important_feature}")
        
        # 验证特征重要性的总和
        self.assertAlmostEqual(sum(importances), 1.0, places=5)
        
        # 验证重要特征的重要性得分明显高于其他特征
        self.assertGreater(importances.max(), 0.2)  # 最重要特征的重要性应大于0.2

if __name__ == '__main__':
    unittest.main()
