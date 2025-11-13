"""第5篇-第15章-15.2.1 风险模型轻量示例

此文件为轻量示例，不依赖 sklearn 等库；只演示接口与断言结构。
"""

def dummy_model_predict(data):
    # 简单阈值模型：当 value > 0.5 返回 1
    return [1 if d.get('score', 0) > 0.5 else 0 for d in data]


def evaluate_predictions(preds, labels):
    correct = sum(1 for p, l in zip(preds, labels) if p == l)
    return correct / len(labels) if labels else 0.0


def test_risk_model_accuracy():
    # 1. 构造假数据
    test_data = [{'score': s} for s in [0.9, 0.1, 0.6, 0.4]]
    labels = [1, 0, 1, 0]

    preds = dummy_model_predict(test_data)
    acc = evaluate_predictions(preds, labels)
    assert acc >= 0.5


if __name__ == '__main__':
    test_risk_model_accuracy()
    print('第15章 15.2.1 示例运行成功')
