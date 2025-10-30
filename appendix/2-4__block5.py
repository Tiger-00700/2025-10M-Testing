import redis
import time
import random
import string

def setup_redis():
    """连接Redis服务器"""
    r = redis.Redis(host='localhost', port=6379, db=0)
    return r

def test_basic_crud_operations(r):
    """测试基本CRUD操作"""
    print("=== 测试基本CRUD操作 ===")
    
    # 测试字符串类型
    r.set("user:1:name", "张三")
    r.set("user:1:age", "30")
    assert r.get("user:1:name") == b"张三"
    assert r.get("user:1:age") == b"30"
    
    # 测试列表类型
    r.lpush("users:recent", "user1", "user2", "user3")
    assert r.llen("users:recent") == 3
    assert r.lrange("users:recent", 0, -1) == [b"user3", b"user2", b"user1"]
    
    # 测试哈希类型
    r.hset("user:2", mapping={
        "name": "李四",
        "age": 28,
        "email": "lisi@example.com"
    })
    assert r.hget("user:2", "name") == b"李四"
    assert r.hgetall("user:2") == {
        b"name": b"李四",
        b"age": b"28",
        b"email": b"lisi@example.com"
    }
    
    # 测试集合类型
    r.sadd("users:online", "user1", "user2", "user3", "user4")
    assert r.scard("users:online") == 4
    assert r.sismember("users:online", "user1") == True
    
    print("基本CRUD操作测试通过")

def test_performance(r, record_count=10000):
    """测试性能"""
    print(f"=== 测试性能: {record_count}条记录 ===")
    
    # 测试写入性能
    start_time = time.time()
    for i in range(record_count):
        key = f"perf:key:{i}"
        value = ''.join(random.choices(string.ascii_letters + string.digits, k=100))
        r.set(key, value)
    write_time = time.time() - start_time
    print(f"写入性能: {record_count}条记录耗时 {write_time:.4f} 秒, 每秒约 {record_count/write_time:.2f} 条")
    
    # 测试读取性能
    start_time = time.time()
    for i in range(record_count):
        key = f"perf:key:{i}"
        r.get(key)
    read_time = time.time() - start_time
    print(f"读取性能: {record_count}条记录耗时 {read_time:.4f} 秒, 每秒约 {record_count/read_time:.2f} 条")

def test_persistence(r):
    """测试持久化"""
    print("=== 测试持久化 ===")
    
    # 设置一个测试键值
    r.set("persistence_test_key", "persistence_test_value")
    
    # 手动触发持久化
    r.save()  # 或者使用 r.bgsave() 异步保存
    print("已触发持久化，重启Redis后验证数据是否存在")
    print("注意：实际测试时需要重启Redis服务并重新连接验证")

# 运行测试
if __name__ == "__main__":
    r = setup_redis()
    test_basic_crud_operations(r)
    test_performance(r, 10000)
    test_persistence(r)
