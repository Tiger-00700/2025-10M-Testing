import requests
import json

class RangerSecurityTester:
    def __init__(self, ranger_url, admin_user, admin_password):
        self.ranger_url = ranger_url
        self.auth = (admin_user, admin_password)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def create_test_user(self, user_name, password, groups=None):
        """创建测试用户"""
        if groups is None:
            groups = []
        
        user_data = {
            "name": user_name,
            "password": password,
            "groups": groups,
            "status": 1
        }
        
        response = requests.post(
            f"{self.ranger_url}/service/xusers/users",
            auth=self.auth,
            headers=self.headers,
            data=json.dumps(user_data)
        )
        
        return response.status_code == 200
    
    def create_test_policy(self, policy_name, resource_type, resource, accesses):
        """创建测试访问策略"""
        policy_data = {
            "name": policy_name,
            "service": "hive",  # 根据实际情况修改
            "description": "Test policy",
            "resources": {
                resource_type: resource
            },
            "accesses": accesses,
            "isEnabled": True,
            "isAuditEnabled": True
        }
        
        response = requests.post(
            f"{self.ranger_url}/service/public/v2/api/policy",
            auth=self.auth,
            headers=self.headers,
            data=json.dumps(policy_data)
        )
        
        return response.status_code == 200
    
    def test_permission(self, user_name, user_password, resource_type, resource, action):
        """测试用户对资源的访问权限"""
        # 这里需要根据实际的服务类型（Hive/HDFS等）调整验证方式
        # 以下是Hive验证的示例
        import pyhive
        from pyhive import hive
        
        try:
            # 根据用户权限尝试连接和操作
            conn = hive.Connection(
                host="hive-server",
                port=10000,
                username=user_name,
                password=user_password,
                database="default"
            )
            
            cursor = conn.cursor()
            
            # 根据操作类型执行不同的命令
            if action == "select":
                cursor.execute(f"SELECT * FROM {resource} LIMIT 1")
            elif action == "insert":
                cursor.execute(f"INSERT INTO {resource} VALUES (1, 'test')")
            elif action == "create":
                cursor.execute(f"CREATE TABLE {resource}_test (id INT)")
            
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Permission test failed: {str(e)}")
            return False
    
    def cleanup_test_user(self, user_name):
        """清理测试用户"""
        response = requests.delete(
            f"{self.ranger_url}/service/xusers/users/{user_name}",
            auth=self.auth
        )
        return response.status_code == 200
    
    def cleanup_test_policy(self, policy_id):
        """清理测试策略"""
        response = requests.delete(
            f"{self.ranger_url}/service/public/v2/api/policy/{policy_id}",
            auth=self.auth
        )
        return response.status_code == 200

# 使用示例
tester = RangerSecurityTester(
    ranger_url="http://ranger-server:6080",
    admin_user="admin",
    admin_password="admin_password"
)

# 创建测试用户
tester.create_test_user("test_user", "test_password")

# 创建测试策略
tester.create_test_policy(
    "test_policy",
    "table",
    "db.test_table",
    [
        {
            "users": ["test_user"],
            "accesses": [
                {"type": "select", "isAllowed": True}
            ]
        }
    ]
)

# 测试权限（应该成功）
select_result = tester.test_permission("test_user", "test_password", "table", "db.test_table", "select")
print(f"SELECT permission test: {select_result}")

# 测试权限（应该失败）
insert_result = tester.test_permission("test_user", "test_password", "table", "db.test_table", "insert")
print(f"INSERT permission test: {insert_result}")

# 清理资源
tester.cleanup_test_user("test_user")
# 注意：需要先获取policy_id再清理策略
