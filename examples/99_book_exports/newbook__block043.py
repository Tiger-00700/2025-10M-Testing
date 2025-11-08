
# 【章节重点难点总结】

# - 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准
# - 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡

# 【小结】
# - 用 3~5 条项目化要点复盘本章内容
# - 指出易错点/反模式与纠正建议
# - 给出可延伸阅读或下一步实践方向

# 【课后思考/练习题】

# 1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
# 2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。


# - 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准
# - 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡

# 【课后思考/练习题】

# 1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
# 2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。

## 风险模型准确性测试示例

# 【阅读提示】本篇聚焦：风险模型准确性测试示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

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

# 【阅读提示】本篇聚焦：阈值灵敏度测试。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

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