import subprocess
import os
import time

class KerberosTester:
    def __init__(self, kinit_path="kinit", klist_path="klist", kdestroy_path="kdestroy"):
        self.kinit_path = kinit_path
        self.klist_path = klist_path
        self.kdestroy_path = kdestroy_path
    
    def kinit_test(self, principal, keytab=None, password=None):
        """测试kinit命令，获取Kerberos票据"""
        # 确保之前没有票据
        self._run_command([self.kdestroy_path])
        
        # 构建命令
        if keytab:
            # 使用keytab
            cmd = [self.kinit_path, "-kt", keytab, principal]
        elif password:
            # 使用密码（注意：在生产环境中应避免在命令行中使用密码）
            # 这里仅作为测试示例
            cmd = [self.kinit_path, principal]
            # 使用echo管道传递密码
            p1 = subprocess.Popen(["echo", password], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p1.stdout.close()  # 关闭p1的stdout以避免死锁
            stdout, stderr = p2.communicate()
            return p2.returncode == 0
        else:
            raise ValueError("Either keytab or password must be provided")
        
        # 执行命令
        return self._run_command(cmd) == 0
    
    def verify_ticket(self, principal=None):
        """验证是否成功获取票据"""
        cmd = [self.klist_path]
        stdout, stderr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        
        if stderr:
            return False
        
        output = stdout.decode('utf-8')
        if principal:
            return principal in output
        
        return "Default principal" in output
    
    def hdfs_access_test(self, hdfs_path, operation="ls"):
        """测试HDFS访问权限"""
        if operation == "ls":
            cmd = ["hdfs", "dfs", "-ls", hdfs_path]
        elif operation == "mkdir":
            cmd = ["hdfs", "dfs", "-mkdir", hdfs_path]
        elif operation == "put":
            # 创建临时文件
            temp_file = f"/tmp/test_{int(time.time())}.txt"
            with open(temp_file, "w") as f:
                f.write("test content")
            cmd = ["hdfs", "dfs", "-put", temp_file, hdfs_path]
        elif operation == "get":
            cmd = ["hdfs", "dfs", "-get", hdfs_path, "/tmp/"]
        else:
            raise ValueError(f"Unsupported operation: {operation}")
        
        return self._run_command(cmd) == 0
    
    def hive_access_test(self, query, principal=None, keytab=None):
        """测试Hive访问权限"""
        cmd = ["beeline", "-u", "jdbc:hive2://hive-server:10000/default;principal=" + principal, "-e", query]
        return self._run_command(cmd) == 0
    
    def _run_command(self, cmd):
        """执行系统命令"""
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return 0
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {cmd}")
            print(f"Error: {e.stderr.decode('utf-8')}")
            return e.returncode

# 使用示例
tester = KerberosTester()

# 测试1：使用keytab获取票据
keytab_test = tester.kinit_test("user1@EXAMPLE.COM", keytab="/path/to/user1.keytab")
print(f"Keytab authentication test: {keytab_test}")

if keytab_test:
    # 验证票据
    ticket_verified = tester.verify_ticket("user1@EXAMPLE.COM")
    print(f"Ticket verification: {ticket_verified}")
    
    # 测试HDFS访问
    hdfs_test = tester.hdfs_access_test("/user/user1")
    print(f"HDFS access test: {hdfs_test}")
    
    # 测试Hive访问
    hive_test = tester.hive_access_test("SELECT * FROM default.test_table LIMIT 10", principal="user1@EXAMPLE.COM")
    print(f"Hive access test: {hive_test}")

# 清理票据
tester._run_command([tester.kdestroy_path])
