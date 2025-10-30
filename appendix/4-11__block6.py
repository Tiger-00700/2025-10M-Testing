# 测试数据生成器示例
import random
from datetime import datetime, timedelta

class TestDataGenerator:
    
    @staticmethod
    def generate_user_data(count=1):
        """生成用户测试数据"""
        users = []
        for i in range(count):
            user = {
                'id': f'user_{i:05d}',
                'name': f'User {random.randint(1000, 9999)}',
                'email': f'test_user_{i}@example.com',
                'age': random.randint(18, 70),
                'registration_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
            }
            users.append(user)
        return users
    
    @staticmethod
    def generate_transaction_data(user_ids, count=1):
        """生成交易测试数据"""
        transactions = []
        for i in range(count):
            transaction = {
                'id': f'tx_{i:08d}',
                'user_id': random.choice(user_ids),
                'amount': round(random.uniform(10.0, 10000.0), 2),
                'currency': random.choice(['USD', 'EUR', 'CNY']),
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(1, 43200))).isoformat(),
                'status': random.choice(['success', 'pending', 'failed'])
            }
            transactions.append(transaction)
        return transactions
