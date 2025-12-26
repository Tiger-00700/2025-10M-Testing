# 测试数据工厂

这个模块提供了生成测试数据的工具函数，用于大数据测试场景。

```python
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta

class DataFactory:
    """测试数据生成工厂"""

    def __init__(self, locale='zh_CN'):
        self.fake = Faker(locale)

    def generate_user_behavior_data(self, num_records=1000):
        """
        生成用户行为数据
        """
        data = []
        for _ in range(num_records):
            user = {
                'user_id': self.fake.uuid4(),
                'session_id': self.fake.uuid4(),
                'timestamp': self.fake.date_time_this_year(),
                'page_url': self.fake.url(),
                'action': np.random.choice(['view', 'click', 'purchase', 'search']),
                'device_type': np.random.choice(['mobile', 'desktop', 'tablet']),
                'browser': np.random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                'ip_address': self.fake.ipv4(),
                'user_agent': self.fake.user_agent()
            }
            data.append(user)

        return pd.DataFrame(data)

    def generate_product_data(self, num_records=500):
        """
        生成产品数据
        """
        categories = ['electronics', 'clothing', 'books', 'home', 'sports']

        data = []
        for _ in range(num_records):
            product = {
                'product_id': self.fake.uuid4(),
                'name': self.fake.word().capitalize(),
                'category': np.random.choice(categories),
                'price': round(np.random.uniform(10, 1000), 2),
                'stock_quantity': np.random.randint(0, 1000),
                'rating': round(np.random.uniform(1, 5), 1),
                'created_date': self.fake.date_this_year()
            }
            data.append(product)

        return pd.DataFrame(data)

    def generate_transaction_data(self, num_records=2000):
        """
        生成交易数据
        """
        data = []
        for _ in range(num_records):
            transaction = {
                'transaction_id': self.fake.uuid4(),
                'user_id': self.fake.uuid4(),
                'product_id': self.fake.uuid4(),
                'quantity': np.random.randint(1, 10),
                'unit_price': round(np.random.uniform(10, 500), 2),
                'total_amount': 0,  # 计算得出
                'payment_method': np.random.choice(['credit_card', 'debit_card', 'paypal', 'alipay']),
                'transaction_date': self.fake.date_time_this_year(),
                'status': np.random.choice(['completed', 'pending', 'failed'], p=[0.9, 0.05, 0.05])
            }
            transaction['total_amount'] = transaction['quantity'] * transaction['unit_price']
            data.append(transaction)

        return pd.DataFrame(data)

# 使用示例
if __name__ == "__main__":
    factory = DataFactory()

    # 生成用户行为数据
    user_data = factory.generate_user_behavior_data(100)
    print("用户行为数据样例:")
    print(user_data.head())

    # 生成产品数据
    product_data = factory.generate_product_data(50)
    print("\n产品数据样例:")
    print(product_data.head())

    # 生成交易数据
    transaction_data = factory.generate_transaction_data(200)
    print("\n交易数据样例:")
    print(transaction_data.head())
```