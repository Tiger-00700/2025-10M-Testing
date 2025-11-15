# MongoDB自动化测试示例
from pymongo import MongoClient
import pytest
import time

class TestMongoDB:
    def setup_method(self):
        """每个测试方法前的设置"""
        # 连接MongoDB
        self.client = MongoClient(
            host=self.config['host'],
            port=self.config['port'],
            username=self.config['username'],
            password=self.config['password']
        )

        # 获取数据库和集合
        self.db = self.client[self.config['database']]
        self.collection = self.db[self.config['collection']]

        # 清理测试数据
        self.collection.delete_many({})

        # 插入测试数据
        self.test_data = [
            {"_id": 1, "name": "Product 1", "price": 10.99, "category": "Electronics"},
            {"_id": 2, "name": "Product 2", "price": 24.99, "category": "Clothing"},
            {"_id": 3, "name": "Product 3", "price": 5.99, "category": "Food"},
            {"_id": 4, "name": "Product 4", "price": 19.99, "category": "Electronics"},
            {"_id": 5, "name": "Product 5", "price": 15.99, "category": "Clothing"}
        ]
        self.collection.insert_many(self.test_data)

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 清理测试数据
        self.collection.delete_many({})
        # 关闭连接
        self.client.close()

    @pytest.fixture
    def config(self):
        """测试配置"""
        return {
            'host': 'localhost',
            'port': 27017,
            'username': 'test_user',
            'password': 'test_password',
            'database': 'test_db',
            'collection': 'test_collection'
        }

    def test_insert_and_find(self):
        """测试插入和查询操作"""
        # 插入新文档
        new_doc = {"_id": 6, "name": "Product 6", "price": 29.99, "category": "Books"}
        result = self.collection.insert_one(new_doc)

        # 验证插入成功
        assert result.inserted_id == 6

        # 查询文档
        found_doc = self.collection.find_one({"_id": 6})

        # 验证查询结果
        assert found_doc is not None
        assert found_doc["name"] == "Product 6"
        assert found_doc["price"] == 29.99

    def test_update_operation(self):
        """测试更新操作"""
        # 更新文档
        result = self.collection.update_one(
            {"_id": 1},
            {"$set": {"price": 12.99, "stock": 100}}
        )

        # 验证更新成功
        assert result.matched_count == 1
        assert result.modified_count == 1

        # 验证更新后的值
        updated_doc = self.collection.find_one({"_id": 1})
        assert updated_doc["price"] == 12.99
        assert updated_doc["stock"] == 100

    def test_delete_operation(self):
        """测试删除操作"""
        # 删除文档
        result = self.collection.delete_one({"_id": 2})

        # 验证删除成功
        assert result.deleted_count == 1

        # 验证文档已被删除
        deleted_doc = self.collection.find_one({"_id": 2})
        assert deleted_doc is None

    def test_query_with_filters(self):
        """测试带过滤条件的查询"""
        # 查询电子产品
        electronics = list(self.collection.find({"category": "Electronics"}))

        # 验证查询结果
        assert len(electronics) == 2
        categories = [doc["category"] for doc in electronics]
        assert all(cat == "Electronics" for cat in categories)

        # 查询价格大于15的产品
        expensive_products = list(self.collection.find({"price": {"$gt": 15}}))
        assert len(expensive_products) == 3
        prices = [doc["price"] for doc in expensive_products]
        assert all(price > 15 for price in prices)

    def test_performance_test(self):
        """简单的性能测试"""
        # 插入大量文档
        bulk_data = [
            {"name": f"Test Product {i}", "price": i * 0.99, "category": f"Category {i % 5}"}
            for i in range(10000)
        ]

        # 测量插入时间
        start_time = time.time()
        self.collection.insert_many(bulk_data)
        insert_time = time.time() - start_time

        # 验证插入数量
        total_docs = self.collection.count_documents({})
        assert total_docs == len(self.test_data) + 10000

        # 测量查询时间
        start_time = time.time()
        result = list(self.collection.find({"category": "Category 1"}))
        query_time = time.time() - start_time

        # 验证查询结果数量
        assert len(result) == 2000  # 10000个文档，5个类别，预期每个类别2000个

        print(f"插入性能: {insert_time:.2f}秒 for 10000条记录")
        print(f"查询性能: {query_time:.2f}秒 for {len(result)}条记录")
