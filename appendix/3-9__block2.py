import os
import subprocess
import time
import logging
import requests

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DockerBigDataEnvironment:
    """Docker 大数据测试环境管理类"""
    
    def __init__(self, compose_file='docker-compose.yml', env_file='hadoop.env'):
        self.compose_file = compose_file
        self.env_file = env_file
        self.services = ['hadoop-namenode', 'hadoop-datanode', 'hadoop-resourcemanager', 'hadoop-nodemanager']
    
    def create_env_file(self):
        """创建 Hadoop 环境配置文件"""
        env_content = """
CORE_CONF_fs_defaultFS=hdfs://hadoop-namenode:9000
CORE_CONF_hadoop_http_staticuser_user=root
CORE_CONF_hadoop_proxyuser_hue_hosts=*
CORE_CONF_hadoop_proxyuser_hue_groups=*

HDFS_CONF_dfs_webhdfs_enabled=true
HDFS_CONF_dfs_permissions_enabled=false

YARN_CONF_yarn_log___aggregation___enable=true
YARN_CONF_yarn_resourcemanager_recovery_enabled=true
YARN_CONF_yarn_resourcemanager_store_class=org.apache.hadoop.yarn.server.resourcemanager.recovery.FileSystemRMStateStore
YARN_CONF_yarn_resourcemanager_fs_state___store_uri=/rmstate
YARN_CONF_yarn_nodemanager_remote___app___log___dir=/app-logs
YARN_CONF_yarn_log_server_url=http://historyserver:8188/applicationhistory/logs/
YARN_CONF_yarn_timeline___service_enabled=true
YARN_CONF_yarn_timeline___service_generic___application___history_enabled=true
YARN_CONF_yarn_resourcemanager_system___metrics___publisher_enabled=true
YARN_CONF_yarn_resourcemanager_hostname=resourcemanager
YARN_CONF_yarn_timeline___service_hostname=historyserver
MAPRED_CONF_mapreduce_framework_name=yarn
MAPRED_CONF_mapred_child_java_opts=-Xmx400m
MAPRED_CONF_mapreduce_map_memory_mb=1024
MAPRED_CONF_mapreduce_reduce_memory_mb=1024
MAPRED_CONF_mapreduce_map_java_opts=-Xmx800m
MAPRED_CONF_mapreduce_reduce_java_opts=-Xmx800m
MAPRED_CONF_yarn_app_mapreduce_am_env=HADOOP_MAPRED_HOME=/opt/hadoop-3.2.1/
MAPRED_CONF_mapreduce_map_env=HADOOP_MAPRED_HOME=/opt/hadoop-3.2.1/
MAPRED_CONF_mapreduce_reduce_env=HADOOP_MAPRED_HOME=/opt/hadoop-3.2.1/,HADOOP_HDFS_HOME=/opt/hadoop-3.2.1/
        """
        
        with open(self.env_file, 'w') as f:
            f.write(env_content.strip())
        logger.info(f"已创建环境配置文件: {self.env_file}")
    
    def create_compose_file(self):
        """创建 Docker Compose 配置文件"""
        compose_content = """
version: '3'
services:
  hadoop-namenode:
    image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
    container_name: hadoop-namenode
    restart: always
    ports:
      - 9870:9870
      - 9000:9000
    volumes:
      - hadoop_namenode:/hadoop/dfs/name
      - ./input:/input
      - ./output:/output
    environment:
      - CLUSTER_NAME=test
    env_file:
      - ./hadoop.env

  hadoop-datanode:
    image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
    container_name: hadoop-datanode
    restart: always
    volumes:
      - hadoop_datanode:/hadoop/dfs/data
    environment:
      SERVICE_PRECONDITION: "hadoop-namenode:9870"
    env_file:
      - ./hadoop.env

  hadoop-resourcemanager:
    image: bde2020/hadoop-resourcemanager:2.0.0-hadoop3.2.1-java8
    container_name: hadoop-resourcemanager
    restart: always
    ports:
      - 8088:8088
    environment:
      SERVICE_PRECONDITION: "hadoop-namenode:9000 hadoop-datanode:9864"
    env_file:
      - ./hadoop.env

  hadoop-nodemanager:
    image: bde2020/hadoop-nodemanager:2.0.0-hadoop3.2.1-java8
    container_name: hadoop-nodemanager
    restart: always
    environment:
      SERVICE_PRECONDITION: "hadoop-namenode:9000 hadoop-datanode:9864 hadoop-resourcemanager:8088"
    env_file:
      - ./hadoop.env

volumes:
  hadoop_namenode:
  hadoop_datanode:
        """
        
        with open(self.compose_file, 'w') as f:
            f.write(compose_content.strip())
        logger.info(f"已创建 Docker Compose 配置文件: {self.compose_file}")
    
    def setup_directories(self):
        """创建必要的目录"""
        for dir_name in ['input', 'output']:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                logger.info(f"创建目录: {dir_name}")
    
    def start_environment(self):
        """启动 Docker 环境"""
        logger.info("开始启动大数据测试环境...")
        cmd = ['docker-compose', '-f', self.compose_file, 'up', '-d']
        
        try:
            subprocess.run(cmd, check=True)
            logger.info("环境启动命令已执行")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"启动环境失败: {e}")
            return False
    
    def wait_for_services(self, timeout=120):
        """等待服务启动完成"""
        logger.info("等待服务启动完成...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_running = True
            for service in self.services:
                cmd = ['docker', 'inspect', '-f', '{{.State.Running}}', service]
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    if result.stdout.strip() != 'true':
                        all_running = False
                        break
                except subprocess.CalledProcessError:
                    all_running = False
                    break
            
            if all_running:
                logger.info("所有服务已启动运行")
                # 额外等待一下，确保服务完全就绪
                time.sleep(10)
                return True
            
            time.sleep(5)
        
        logger.error("服务启动超时")
        return False
    
    def verify_environment(self):
        """验证环境是否正常工作"""
        logger.info("开始验证环境...")
        
        # 验证 HDFS Web UI 是否可访问
        try:
            response = requests.get("http://localhost:9870", timeout=10)
            if response.status_code == 200:
                logger.info("HDFS Web UI 验证通过")
            else:
                logger.error(f"HDFS Web UI 验证失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"HDFS Web UI 验证失败: {e}")
            return False
        
        # 验证 YARN ResourceManager 是否可访问
        try:
            response = requests.get("http://localhost:8088", timeout=10)
            if response.status_code == 200:
                logger.info("YARN ResourceManager 验证通过")
            else:
                logger.error(f"YARN ResourceManager 验证失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"YARN ResourceManager 验证失败: {e}")
            return False
        
        # 在 HDFS 上创建测试目录并上传文件
        try:
            # 创建测试文件
            test_file = 'input/test_data.txt'
            with open(test_file, 'w') as f:
                f.write("Hello, Big Data Testing!\nThis is a test file.")
            
            # 将文件上传到 HDFS
            cmd = ['docker', 'exec', 'hadoop-namenode', 
                  'hdfs', 'dfs', '-put', '/input/test_data.txt', '/test_data.txt']
            subprocess.run(cmd, check=True)
            
            # 列出 HDFS 根目录内容，验证文件是否上传成功
            cmd = ['docker', 'exec', 'hadoop-namenode', 
                  'hdfs', 'dfs', '-ls', '/']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if 'test_data.txt' in result.stdout:
                logger.info("HDFS 功能验证通过，文件上传成功")
            else:
                logger.error("HDFS 文件上传验证失败")
                return False
                
        except Exception as e:
            logger.error(f"HDFS 功能验证失败: {e}")
            return False
        
        logger.info("环境验证全部通过")
        return True
    
    def stop_environment(self):
        """停止 Docker 环境"""
        logger.info("停止大数据测试环境...")
        cmd = ['docker-compose', '-f', self.compose_file, 'down']
        
        try:
            subprocess.run(cmd, check=True)
            logger.info("环境已停止")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"停止环境失败: {e}")
            return False
    
    def cleanup(self):
        """清理环境"""
        logger.info("清理测试环境...")
        # 停止环境
        self.stop_environment()
        
        # 删除生成的文件
        for file_name in [self.compose_file, self.env_file]:
            if os.path.exists(file_name):
                os.remove(file_name)
                logger.info(f"删除文件: {file_name}")

# 使用示例
def main():
    # 创建环境管理器
    env_manager = DockerBigDataEnvironment()
    
    try:
        # 准备环境配置
        env_manager.create_env_file()
        env_manager.create_compose_file()
        env_manager.setup_directories()
        
        # 启动并验证环境
        if env_manager.start_environment():
            if env_manager.wait_for_services():
                env_manager.verify_environment()
        
        # 注意：这里可以添加实际的测试代码
        # 测试完成后，可以调用 env_manager.stop_environment() 停止环境
        
    except Exception as e:
        logger.error(f"执行过程中出现错误: {e}")
    finally:
        # 可选：是否自动清理环境
        # env_manager.cleanup()
        pass

if __name__ == "__main__":
    main()
