class TestDataGenerator:
    def __init__(self, config):
        self.config = config
    
    def generate_structured_data(self, schema, count):
        """生成结构化测试数据"""
        data = []
        for _ in range(count):
            record = {}
            for field_name, field_type in schema.items():
                if field_type == "string":
                    record[field_name] = self._generate_string()
                elif field_type == "integer":
                    record[field_name] = self._generate_integer()
                elif field_type == "timestamp":
                    record[field_name] = self._generate_timestamp()
                # 更多数据类型支持
            data.append(record)
        return data
    
    def _generate_string(self):
        # 实现字符串生成逻辑
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    def _generate_integer(self):
        # 实现整数生成逻辑
        import random
        return random.randint(1, 1000000)
    
    def _generate_timestamp(self):
        # 实现时间戳生成逻辑
        import datetime
        import random
        start_date = datetime.datetime(2020, 1, 1)
        end_date = datetime.datetime(2023, 12, 31)
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        return (start_date + datetime.timedelta(days=random_days)).isoformat()
