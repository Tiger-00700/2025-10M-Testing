from locust import HttpUser, task, between
import json
import time
import random

class SparkJobUser(HttpUser):
    wait_time = between(1, 3)  # 用户操作间隔时间
    
    def on_start(self):
        # 初始化，用户开始时执行
        self.job_ids = []
    
    @task(1)
    def submit_job(self):
        # 提交Spark作业任务
        job_name = f"test-job-{random.randint(1000, 9999)}"
        
        with self.client.post("/api/v1/submit", 
                             json={
                                 "jobName": job_name,
                                 "parameters": {
                                     "input": "/data/input",
                                     "output": "/data/output",
                                     "partitions": random.randint(1, 100)
                                 }
                             }, 
                             catch_response=True) as response:
            if response.status_code == 200:
                job_id = response.json()["jobId"]
                self.job_ids.append(job_id)
                response.success()
            else:
                response.failure(f"Failed to submit job: {response.text}")
    
    @task(2)
    def check_status(self):
        # 检查作业状态任务
        if not self.job_ids:
            return
            
        job_id = random.choice(self.job_ids)
        with self.client.get(f"/api/v1/job/{job_id}/status", 
                           catch_response=True) as response:
            if response.status_code == 200:
                status = response.json()["status"]
                if status in ["COMPLETED", "FAILED"]:
                    # 作业已完成或失败，从列表中移除
                    self.job_ids.remove(job_id)
                response.success()
            else:
                response.failure(f"Failed to check status: {response.text}")

# 分布式运行命令：
# 主节点: locust -f spark_job_test.py --master
# 工作节点: locust -f spark_job_test.py --worker --master-host=<master-ip>
