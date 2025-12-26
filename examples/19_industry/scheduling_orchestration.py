#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流批一体调度编排脚本
Stream-Batch Unified Scheduling Orchestration

此脚本演示如何实现流批一体架构的调度编排，
协调流处理和批处理任务的执行顺序和依赖关系。
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import logging
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

class TaskType(Enum):
    """任务类型枚举"""
    STREAMING = "streaming"
    BATCH = "batch"
    VALIDATION = "validation"

class StreamBatchTask:
    """流批一体任务"""

    def __init__(self, task_id: str, task_type: TaskType, dependencies: List[str] = None):
        self.task_id = task_id
        self.task_type = task_type
        self.dependencies = dependencies or []
        self.status = TaskStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.retry_count = 0
        self.max_retries = 3

    def execute(self) -> bool:
        """执行任务"""
        self.status = TaskStatus.RUNNING
        self.start_time = datetime.now()

        try:
            logger.info(f"Executing task: {self.task_id} ({self.task_type.value})")

            # 模拟任务执行
            success = self._run_task_logic()

            if success:
                self.status = TaskStatus.SUCCESS
                logger.info(f"Task {self.task_id} completed successfully")
            else:
                self.status = TaskStatus.FAILED
                logger.error(f"Task {self.task_id} failed")

            return success

        except Exception as e:
            self.status = TaskStatus.FAILED
            logger.error(f"Task {self.task_id} failed with exception: {e}")
            return False

        finally:
            self.end_time = datetime.now()

    def _run_task_logic(self) -> bool:
        """任务具体逻辑"""
        # 模拟不同类型任务的执行时间
        if self.task_type == TaskType.STREAMING:
            time.sleep(2)  # 流处理相对较快
        elif self.task_type == TaskType.BATCH:
            time.sleep(5)  # 批处理需要更长时间
        elif self.task_type == TaskType.VALIDATION:
            time.sleep(1)  # 校验较快

        # 模拟随机失败（10%概率）
        import random
        return random.random() > 0.1

    def can_execute(self, completed_tasks: set) -> bool:
        """检查是否可以执行（依赖满足）"""
        return all(dep in completed_tasks for dep in self.dependencies)

class StreamBatchOrchestrator:
    """流批一体编排器"""

    def __init__(self):
        self.tasks: Dict[str, StreamBatchTask] = {}
        self.completed_tasks: set = set()
        self.failed_tasks: set = set()

    def add_task(self, task: StreamBatchTask) -> None:
        """添加任务"""
        self.tasks[task.task_id] = task
        logger.info(f"Added task: {task.task_id}")

    def execute_pipeline(self) -> Dict[str, TaskStatus]:
        """
        执行完整流水线

        Returns:
            Dict[str, TaskStatus]: 所有任务的最终状态
        """
        logger.info("Starting stream-batch unified pipeline execution")

        execution_order = self._resolve_dependencies()

        for task_id in execution_order:
            task = self.tasks[task_id]

            if task.can_execute(self.completed_tasks):
                success = task.execute()
                if success:
                    self.completed_tasks.add(task_id)
                else:
                    self.failed_tasks.add(task_id)
                    # 失败时不继续执行下游任务
                    break
            else:
                task.status = TaskStatus.SKIPPED
                logger.warning(f"Task {task_id} skipped due to unsatisfied dependencies")

        return {task_id: task.status for task_id, task in self.tasks.items()}

    def _resolve_dependencies(self) -> List[str]:
        """解析任务依赖关系，返回执行顺序"""
        # 简单的拓扑排序实现
        visited = set()
        temp_visited = set()
        order = []

        def visit(task_id: str):
            if task_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving {task_id}")
            if task_id in visited:
                return

            temp_visited.add(task_id)

            for dep in self.tasks[task_id].dependencies:
                visit(dep)

            temp_visited.remove(task_id)
            visited.add(task_id)
            order.append(task_id)

        for task_id in self.tasks:
            if task_id not in visited:
                visit(task_id)

        return order

    def get_pipeline_status(self) -> Dict:
        """获取流水线状态"""
        return {
            "total_tasks": len(self.tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            "task_details": {
                task_id: {
                    "status": task.status.value,
                    "type": task.task_type.value,
                    "dependencies": task.dependencies,
                    "start_time": task.start_time.isoformat() if task.start_time else None,
                    "end_time": task.end_time.isoformat() if task.end_time else None,
                    "duration": (task.end_time - task.start_time).total_seconds() if task.start_time and task.end_time else None
                }
                for task_id, task in self.tasks.items()
            }
        }

def create_sample_pipeline() -> StreamBatchOrchestrator:
    """创建示例流水线"""
    orchestrator = StreamBatchOrchestrator()

    # 数据采集任务（流处理）
    streaming_ingestion = StreamBatchTask(
        "streaming_ingestion",
        TaskType.STREAMING
    )

    # 实时聚合任务（流处理，依赖采集）
    streaming_aggregation = StreamBatchTask(
        "streaming_aggregation",
        TaskType.STREAMING,
        dependencies=["streaming_ingestion"]
    )

    # 批量历史数据处理（批处理）
    batch_historical = StreamBatchTask(
        "batch_historical",
        TaskType.BATCH
    )

    # 批量聚合任务（批处理，依赖历史数据）
    batch_aggregation = StreamBatchTask(
        "batch_aggregation",
        TaskType.BATCH,
        dependencies=["batch_historical"]
    )

    # 流批一致性校验（校验，依赖所有处理任务）
    consistency_validation = StreamBatchTask(
        "consistency_validation",
        TaskType.VALIDATION,
        dependencies=["streaming_aggregation", "batch_aggregation"]
    )

    # 添加所有任务
    orchestrator.add_task(streaming_ingestion)
    orchestrator.add_task(streaming_aggregation)
    orchestrator.add_task(batch_historical)
    orchestrator.add_task(batch_aggregation)
    orchestrator.add_task(consistency_validation)

    return orchestrator

# 使用示例
if __name__ == "__main__":
    # 创建并执行示例流水线
    pipeline = create_sample_pipeline()

    print("Starting Stream-Batch Unified Pipeline...")
    results = pipeline.execute_pipeline()

    print("\nPipeline Execution Results:")
    for task_id, status in results.items():
        print(f"  {task_id}: {status.value}")

    print("\nDetailed Pipeline Status:")
    status = pipeline.get_pipeline_status()
    print(json.dumps(status, indent=2, default=str))