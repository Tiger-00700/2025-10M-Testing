#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流批一体数据采集管道
Stream-Batch Unified Data Ingestion Pipeline

此脚本演示如何实现流批一体的数据采集架构，
支持实时流处理和批量数据导入的统一管道。
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamBatchIngestionPipeline:
    """流批一体数据采集管道"""

    def __init__(self, config: Dict):
        self.config = config
        self.streaming_buffer = []
        self.batch_buffer = []
        self.last_checkpoint = datetime.now()

    def ingest_streaming_data(self, data: Dict) -> bool:
        """
        实时数据采集入口

        Args:
            data: 实时数据记录

        Returns:
            bool: 是否成功处理
        """
        try:
            # 添加时间戳和处理标记
            enriched_data = {
                **data,
                "ingestion_time": datetime.now().isoformat(),
                "processing_mode": "streaming",
                "event_id": f"stream_{int(time.time() * 1000)}"
            }

            # 实时写入缓冲区
            self.streaming_buffer.append(enriched_data)

            # 检查是否需要触发微批处理
            if len(self.streaming_buffer) >= self.config.get("micro_batch_size", 100):
                self._process_micro_batch()

            logger.info(f"Streaming data ingested: {enriched_data['event_id']}")
            return True

        except Exception as e:
            logger.error(f"Failed to ingest streaming data: {e}")
            return False

    def ingest_batch_data(self, data_list: List[Dict]) -> bool:
        """
        批量数据采集入口

        Args:
            data_list: 批量数据记录列表

        Returns:
            bool: 是否成功处理
        """
        try:
            # 批量数据 enrichment
            enriched_batch = []
            for data in data_list:
                enriched_data = {
                    **data,
                    "ingestion_time": datetime.now().isoformat(),
                    "processing_mode": "batch",
                    "batch_id": f"batch_{int(time.time() * 1000)}"
                }
                enriched_batch.append(enriched_data)

            # 添加到批处理缓冲区
            self.batch_buffer.extend(enriched_batch)

            # 检查是否需要触发批处理
            if len(self.batch_buffer) >= self.config.get("batch_size", 10000):
                self._process_batch()

            logger.info(f"Batch data ingested: {len(enriched_batch)} records")
            return True

        except Exception as e:
            logger.error(f"Failed to ingest batch data: {e}")
            return False

    def _process_micro_batch(self) -> None:
        """处理微批数据"""
        if not self.streaming_buffer:
            return

        try:
            # 微批写入数据湖
            batch_data = self.streaming_buffer.copy()
            self._write_to_data_lake(batch_data, "streaming_micro_batch")

            # 清空缓冲区
            self.streaming_buffer.clear()

            # 更新检查点
            self.last_checkpoint = datetime.now()

            logger.info(f"Processed micro-batch: {len(batch_data)} records")

        except Exception as e:
            logger.error(f"Failed to process micro-batch: {e}")

    def _process_batch(self) -> None:
        """处理批量数据"""
        if not self.batch_buffer:
            return

        try:
            # 批量写入数据湖
            batch_data = self.batch_buffer.copy()
            self._write_to_data_lake(batch_data, "batch_historical")

            # 清空缓冲区
            self.batch_buffer.clear()

            logger.info(f"Processed batch: {len(batch_data)} records")

        except Exception as e:
            logger.error(f"Failed to process batch: {e}")

    def _write_to_data_lake(self, data: List[Dict], table_suffix: str) -> None:
        """
        写入数据湖

        Args:
            data: 数据记录列表
            table_suffix: 表后缀标识
        """
        # 这里应该是实际的数据湖写入逻辑
        # 例如：Delta Lake, Hudi, Iceberg 等

        table_name = f"events_{table_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"Writing {len(data)} records to data lake table: {table_name}")

        # 模拟写入操作
        # 实际实现会使用 Spark, Flink 或其他框架

    def get_pipeline_status(self) -> Dict:
        """获取管道状态"""
        return {
            "streaming_buffer_size": len(self.streaming_buffer),
            "batch_buffer_size": len(self.batch_buffer),
            "last_checkpoint": self.last_checkpoint.isoformat(),
            "config": self.config
        }

# 配置示例
pipeline_config = {
    "micro_batch_size": 100,
    "batch_size": 10000,
    "data_lake_format": "delta",
    "checkpoint_interval": 300,  # 5分钟
    "retention_days": 30
}

# 使用示例
if __name__ == "__main__":
    # 初始化管道
    pipeline = StreamBatchIngestionPipeline(pipeline_config)

    # 模拟实时数据采集
    for i in range(150):
        streaming_data = {
            "user_id": f"user_{i % 100}",
            "event_type": "click" if i % 2 == 0 else "view",
            "timestamp": datetime.now().isoformat(),
            "value": i * 1.5
        }
        pipeline.ingest_streaming_data(streaming_data)
        time.sleep(0.01)  # 模拟实时间隔

    # 模拟批量数据采集
    batch_data = [
        {
            "user_id": f"user_{j}",
            "event_type": "purchase",
            "timestamp": (datetime.now() - timedelta(days=j)).isoformat(),
            "value": j * 10.0
        }
        for j in range(500)
    ]
    pipeline.ingest_batch_data(batch_data)

    # 获取状态
    status = pipeline.get_pipeline_status()
    print("Pipeline Status:", json.dumps(status, indent=2, default=str))