## 风险模型准确性测试示例


import pandas as pd
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score

def test_risk_model_accuracy(model, test_data, test_labels):
    # 模型预测
    predictions = model.predict(test_data)
    probabilities = model.predict_proba(test_data)[:, 1] if hasattr(model, 'predict_proba') else None

    # 计算评估指标
    precision, recall, f1, _ = precision_recall_fscore_support(test_labels, predictions, average='binary')
    auc_score = roc_auc_score(test_labels, probabilities) if probabilities is not None else None

    results = {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'auc_score': auc_score
    }

    # 验证指标是否符合业务要求
    assert f1 >= 0.85, "F1分数未达到业务要求"
    assert precision >= 0.80, "精确率未达到业务要求"

    return results

## 阈值灵敏度测试


def test_threshold_sensitivity(model, test_data, test_labels, thresholds=[0.1, 0.3, 0.5, 0.7, 0.9]):
    results = []
    for threshold in thresholds:
        predictions = (model.predict_proba(test_data)[:, 1] >= threshold).astype(int)
        precision, recall, f1, _ = precision_recall_fscore_support(test_labels, predictions, average='binary')
        results.append({
            'threshold': threshold,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        })
    return pd.DataFrame(results)
