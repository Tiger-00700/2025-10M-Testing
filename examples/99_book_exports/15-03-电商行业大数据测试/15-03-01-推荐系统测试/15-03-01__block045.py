> 【章节重点难点总结】

- 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准
- 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡

> 【课后思考/练习题】

1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。
2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。


## 推荐系统相关性和多样性测试

> 【阅读提示】本篇聚焦：推荐系统相关性和多样性测试。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

import numpy as np
from scipy.spatial.distance import cosine

def test_recommendation_relevance(recommender, user_id, expected_topics):
    # 获取推荐结果
    recommendations = recommender.get_recommendations(user_id, top_k=20)

    # 计算主题覆盖率
    covered_topics = set()
    for item in recommendations:
        covered_topics.update(item['topics'])

    # 计算相关主题覆盖率
    relevant_topics_covered = covered_topics.intersection(expected_topics)
    relevance_score = len(relevant_topics_covered) / len(expected_topics) if expected_topics else 0

    # 验证相关性
    assert relevance_score >= 0.7, f"推荐相关性不足: {relevance_score:.2f}"

    return {
        'relevance_score': relevance_score,
        'covered_topics': covered_topics
    }

def test_recommendation_diversity(recommender, user_id, top_k=20):
    # 获取推荐结果
    recommendations = recommender.get_recommendations(user_id, top_k=top_k)

    # 计算项目间的相似度矩阵
    similarities = []
    for i in range(len(recommendations)):
        for j in range(i + 1, len(recommendations)):
            # 使用项目特征向量计算相似度
            sim = 1 - cosine(recommendations[i]['features'], recommendations[j]['features'])
            similarities.append(sim)

    # 计算平均相似度（多样性的反面）
    avg_similarity = np.mean(similarities) if similarities else 0
    diversity_score = 1 - avg_similarity

    # 验证多样性
    assert diversity_score >= 0.6, f"推荐多样性不足: {diversity_score:.2f}"

    return {
        'diversity_score': diversity_score,
        'avg_similarity': avg_similarity
    }
