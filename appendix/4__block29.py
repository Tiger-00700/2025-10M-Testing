import re
import pandas as pd
from pyatlas.client import AtlasClient

class SensitiveDataScanner:
    def __init__(self, atlas_client=None):
        self.atlas_client = atlas_client
        self.sensitive_patterns = {
            "credit_card": re.compile(r'\b(?:\d[ -]*?){13,16}\b'),
            "social_security": re.compile(r'\b\d{3}[- ]?\d{2}[- ]?\d{4}\b'),
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            "ip_address": re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            "date_of_birth": re.compile(r'\b(?:0[1-9]|1[0-2])[-/.](?:0[1-9]|[12][0-9]|3[01])[-/.](?:19|20)\d\d\b')
        }
    
    def scan_dataframe(self, df, sample_size=1000):
        """扫描DataFrame中的敏感数据"""
        # 如果DataFrame太大，采样处理
        if len(df) > sample_size:
            df_sample = df.sample(sample_size)
        else:
            df_sample = df
        
        sensitive_columns = {}
        
        # 对每列进行扫描
        for column in df_sample.columns:
            sensitive_types = set()
            column_data = df_sample[column].astype(str)
            
            # 应用每种敏感模式
            for pattern_name, pattern in self.sensitive_patterns.items():
                matches = column_data.apply(lambda x: bool(pattern.search(x)))
                match_ratio = matches.sum() / len(matches)
                
                # 如果匹配率超过阈值，认为该列包含此类敏感数据
                if match_ratio > 0.1:  # 10%的匹配率
                    sensitive_types.add((pattern_name, match_ratio))
            
            if sensitive_types:
                sensitive_columns[column] = sorted(sensitive_types, key=lambda x: x[1], reverse=True)
        
        return sensitive_columns
    
    def scan_hive_table(self, database, table, sample_size=1000):
        """扫描Hive表中的敏感数据"""
        import pyhive
        from pyhive import hive
        
        # 连接Hive
        conn = hive.Connection(host="hive-server", port=10000, database=database)
        
        # 采样数据
        query = f"SELECT * FROM {table} TABLESAMPLE ({sample_size} ROWS)"
        df = pd.read_sql(query, conn)
        
        conn.close()
        
        # 扫描敏感数据
        return self.scan_dataframe(df)
    
    def classify_in_atlas(self, entity_guid, classifications):
        """在Atlas中分类实体"""
        if not self.atlas_client:
            raise ValueError("Atlas client not initialized")
        
        # 构建分类请求
        classification_requests = []
        for classification in classifications:
            classification_requests.append({
                "typeName": classification,
                "entityGuid": entity_guid,
                "propagate": True
            })
        
        # 应用分类
        return self.atlas_client.classify_entity(classification_requests)

# 使用示例
from pyatlas.client import AtlasClient

# 初始化Atlas客户端
atlas = AtlasClient(
    base_url="http://atlas-server:21000",
    username="admin",
    password="admin_password"
)

# 初始化扫描器
scanner = SensitiveDataScanner(atlas_client=atlas)

# 扫描Hive表
sensitive_columns = scanner.scan_hive_table("customer_db", "customer_data")

print("敏感数据扫描结果:")
for column, sensitive_types in sensitive_columns.items():
    print(f"列名: {column}")
    for sensitive_type, ratio in sensitive_types:
        print(f"  - 类型: {sensitive_type}, 匹配率: {ratio:.2%}")

# 假设我们已经有实体GUID，可以应用分类
# scanner.classify_in_atlas("entity-guid", ["PII", "FinancialData"])
