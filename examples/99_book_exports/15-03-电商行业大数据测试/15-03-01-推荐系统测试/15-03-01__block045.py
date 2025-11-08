## 推荐系统相关性和多样性测试


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
