# 设备故障预测模型测试
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
