> 【章节重点难点总结】

> 【小结】

- 用 3~5 条项目化要点复盘本章内容
- 指出易错点/反模式与纠正建议
- 给出可延伸阅读或下一步实践方向


- 要点：覆盖/真实性/隔离/可重现、元数据与血缘管理
- 难点：隐私合规与可用性之间的平衡（k匿名、差分隐私）

> 【课后思考/练习题】

1. 为某敏感字段设计兼顾业务可用的脱敏规则。
2. 如何建立测试数据版本化与回滚机制？


1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。

## 设备故障预测模型测试

> 【阅读提示】本篇聚焦：设备故障预测模型测试。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report

def test_fault_prediction_accuracy(model, test_data, test_labels, time_windows):
    results = {}

    for window in time_windows:
        # 获取指定时间窗口内的预测
        window_test_data = test_data[test_data['time_to_failure'] <= window]
        window_test_labels = test_labels[test_data['time_to_failure'] <= window]

        # 模型预测
        predictions = model.predict(window_test_data.drop(['time_to_failure'], axis=1))

        # 计算混淆矩阵和分类报告
        cm = confusion_matrix(window_test_labels, predictions)
        report = classification_report(window_test_labels, predictions, output_dict=True)

        # 计算提前预警有效性指标
        true_positives = cm[1, 1]
        false_negatives = cm[1, 0]
        early_warning_effectiveness = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0

        results[f'window_{window}h'] = {
            'confusion_matrix': cm,
            'report': report,
            'early_warning_effectiveness': early_warning_effectiveness
        }

        # 验证提前预警有效性
        assert early_warning_effectiveness >= 0.8, f"{window}小时提前预警有效性不足"

    return results

def test_anomaly_detection(sensor_data, anomaly_detector, known_anomalies):
    # 检测异常
    anomaly_results = anomaly_detector.detect(sensor_data)

    # 评估异常检测效果
    detected_anomalies = set(anomaly_results['anomaly_indices'])
    actual_anomalies = set(known_anomalies['indices'])

    # 计算检测指标
    true_positives = len(detected_anomalies.intersection(actual_anomalies))
    false_positives = len(detected_anomalies - actual_anomalies)
    false_negatives = len(actual_anomalies - detected_anomalies)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    results = {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives
    }

    # 验证异常检测性能
    assert f1 >= 0.75, "异常检测F1分数不足"

    return results
