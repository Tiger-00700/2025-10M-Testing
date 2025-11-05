
## MongoDB数据存储测试示例

# 【阅读提示】本篇聚焦：MongoDB数据存储测试示例。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。

def test_mongodb_document_storage():
    # 1. 连接MongoDB
    client = connect_to_mongodb("test_db")
    collection = client["test_collection"]

    # 2. 准备测试数据
    documents = generate_complex_documents(count=1000)

    # 3. 插入文档
    result = collection.insert_many(documents)

    # 4. 验证插入
    assert len(result.inserted_ids) == len(documents), "插入失败"

    # 5. 执行查询
    query_result = collection.find({"category": "electronics"})

    # 6. 验证查询结果
    expected_count = sum(1 for doc in documents if doc["category"] == "electronics")
    assert query_result.count() == expected_count, "查询结果不正确"

    # 7. 验证索引使用
    assert verify_query_uses_index(collection, {"category": 1}), "未使用索引"