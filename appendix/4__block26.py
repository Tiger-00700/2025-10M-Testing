def verify_audit_logs(ranger_url, admin_user, admin_password, user_name, resource, action, start_time, end_time):
    """验证安全审计日志"""
    auth = (admin_user, admin_password)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # 构建查询参数
    params = {
        "query": f"access_user={user_name} AND resource_path={resource} AND access_type={action}",
        "startTime": start_time,
        "endTime": end_time,
        "limit": 100
    }
    
    response = requests.get(
        f"{ranger_url}/service/xusers/auditlog",
        auth=auth,
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        logs = response.json()
        return len(logs) > 0
    else:
        print(f"Failed to query audit logs: {response.status_code}")
        return False

# 使用示例
import time

start_time = int(time.time() * 1000) - 3600000  # 1小时前
end_time = int(time.time() * 1000)  # 当前时间

audit_verified = verify_audit_logs(
    "http://ranger-server:6080",
    "admin",
    "admin_password",
    "test_user",
    "db.test_table",
    "select",
    start_time,
    end_time
)

print(f"Audit log verification: {audit_verified}")
