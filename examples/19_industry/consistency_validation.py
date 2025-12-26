#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流批一致性校验脚本
Stream-Batch Consistency Validation

此脚本演示如何验证流处理和批处理结果的一致性，
确保数据在不同处理模式下保持准确性和完整性。
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import statistics

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsistencyValidator:
    """流批一致性校验器"""

    def __init__(self, config: Dict):
        self.config = config
        self.validation_results = []

    def validate_consistency(self,
                           streaming_results: List[Dict],
                           batch_results: List[Dict],
                           window_start: datetime,
                           window_end: datetime) -> Dict:
        """
        执行一致性校验

        Args:
            streaming_results: 流处理结果
            batch_results: 批处理结果
            window_start: 时间窗口开始
            window_end: 时间窗口结束

        Returns:
            Dict: 校验结果
        """
        logger.info(f"Starting consistency validation for window: {window_start} to {window_end}")

        # 1. 数据对齐
        aligned_streaming, aligned_batch = self._align_data_by_window(
            streaming_results, batch_results, window_start, window_end
        )

        # 2. 基础统计校验
        stats_validation = self._validate_basic_statistics(aligned_streaming, aligned_batch)

        # 3. 记录级校验
        record_validation = self._validate_record_level_consistency(aligned_streaming, aligned_batch)

        # 4. 聚合校验
        aggregation_validation = self._validate_aggregation_consistency(aligned_streaming, aligned_batch)

        # 5. 完整性校验
        completeness_validation = self._validate_data_completeness(aligned_streaming, aligned_batch)

        # 综合结果
        overall_result = {
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
            "streaming_records": len(aligned_streaming),
            "batch_records": len(aligned_batch),
            "validations": {
                "statistics": stats_validation,
                "records": record_validation,
                "aggregation": aggregation_validation,
                "completeness": completeness_validation
            }
        }

        # 计算整体一致性评分
        overall_result["consistency_score"] = self._calculate_consistency_score(overall_result)

        # 记录结果
        self.validation_results.append(overall_result)

        logger.info(f"Consistency validation completed. Score: {overall_result['consistency_score']:.3f}")

        return overall_result

    def _align_data_by_window(self,
                            streaming_data: List[Dict],
                            batch_data: List[Dict],
                            window_start: datetime,
                            window_end: datetime) -> Tuple[List[Dict], List[Dict]]:
        """按时间窗口对齐数据"""

        def in_window(record: Dict) -> bool:
            record_time = datetime.fromisoformat(record.get("timestamp", record.get("ingestion_time", "")))
            return window_start <= record_time <= window_end

        aligned_streaming = [r for r in streaming_data if in_window(r)]
        aligned_batch = [r for r in batch_data if in_window(r)]

        logger.info(f"Data aligned - Streaming: {len(aligned_streaming)}, Batch: {len(aligned_batch)}")

        return aligned_streaming, aligned_batch

    def _validate_basic_statistics(self, streaming_data: List[Dict], batch_data: List[Dict]) -> Dict:
        """基础统计校验"""

        if not streaming_data or not batch_data:
            return {"status": "failed", "reason": "insufficient_data"}

        # 提取数值字段
        streaming_values = [r.get("value", 0) for r in streaming_data if "value" in r]
        batch_values = [r.get("value", 0) for r in batch_data if "value" in r]

        if not streaming_values or not batch_values:
            return {"status": "failed", "reason": "no_numeric_data"}

        # 计算统计指标
        streaming_stats = {
            "count": len(streaming_values),
            "sum": sum(streaming_values),
            "avg": statistics.mean(streaming_values),
            "min": min(streaming_values),
            "max": max(streaming_values)
        }

        batch_stats = {
            "count": len(batch_values),
            "sum": sum(batch_values),
            "avg": statistics.mean(batch_values),
            "min": min(batch_values),
            "max": max(batch_values)
        }

        # 计算差异
        differences = {}
        tolerance = self.config.get("tolerance_threshold", 0.01)

        for key in ["count", "sum", "avg"]:
            diff = abs(streaming_stats[key] - batch_stats[key])
            if streaming_stats[key] != 0:
                diff_ratio = diff / abs(streaming_stats[key])
            else:
                diff_ratio = 0 if batch_stats[key] == 0 else 1

            differences[key] = {
                "streaming": streaming_stats[key],
                "batch": batch_stats[key],
                "difference": diff,
                "ratio": diff_ratio,
                "within_tolerance": diff_ratio <= tolerance
            }

        all_within_tolerance = all(d["within_tolerance"] for d in differences.values())

        return {
            "status": "passed" if all_within_tolerance else "failed",
            "statistics": {
                "streaming": streaming_stats,
                "batch": batch_stats,
                "differences": differences
            }
        }

    def _validate_record_level_consistency(self, streaming_data: List[Dict], batch_data: List[Dict]) -> Dict:
        """记录级一致性校验"""

        # 使用关键字段进行匹配
        key_fields = self.config.get("key_fields", ["user_id", "event_type"])

        streaming_keys = {self._generate_key(r, key_fields) for r in streaming_data}
        batch_keys = {self._generate_key(r, key_fields) for r in batch_data}

        # 计算匹配情况
        matched_keys = streaming_keys & batch_keys
        streaming_only = streaming_keys - batch_keys
        batch_only = batch_keys - streaming_keys

        match_ratio = len(matched_keys) / max(len(streaming_keys), len(batch_keys)) if streaming_keys or batch_keys else 1.0

        threshold = self.config.get("match_threshold", 0.95)

        return {
            "status": "passed" if match_ratio >= threshold else "failed",
            "match_ratio": match_ratio,
            "matched_records": len(matched_keys),
            "streaming_only": len(streaming_only),
            "batch_only": len(batch_only),
            "threshold": threshold
        }

    def _validate_aggregation_consistency(self, streaming_data: List[Dict], batch_data: List[Dict]) -> Dict:
        """聚合一致性校验"""

        # 按用户聚合
        streaming_agg = self._aggregate_by_user(streaming_data)
        batch_agg = self._aggregate_by_user(batch_data)

        # 比较聚合结果
        all_users = set(streaming_agg.keys()) | set(batch_agg.keys())

        consistent_users = 0
        inconsistent_details = []

        for user in all_users:
            s_value = streaming_agg.get(user, 0)
            b_value = batch_agg.get(user, 0)

            if abs(s_value - b_value) <= self.config.get("aggregation_tolerance", 0.1):
                consistent_users += 1
            else:
                inconsistent_details.append({
                    "user": user,
                    "streaming": s_value,
                    "batch": b_value,
                    "difference": abs(s_value - b_value)
                })

        consistency_ratio = consistent_users / len(all_users) if all_users else 1.0

        return {
            "status": "passed" if consistency_ratio >= 0.99 else "failed",
            "consistency_ratio": consistency_ratio,
            "total_users": len(all_users),
            "consistent_users": consistent_users,
            "inconsistent_details": inconsistent_details[:10]  # 只显示前10个不一致的
        }

    def _validate_data_completeness(self, streaming_data: List[Dict], batch_data: List[Dict]) -> Dict:
        """数据完整性校验"""

        # 检查必需字段
        required_fields = self.config.get("required_fields", ["user_id", "timestamp", "value"])

        def check_completeness(data: List[Dict], source: str) -> Dict:
            total_records = len(data)
            complete_records = 0
            missing_fields = {}

            for record in data:
                missing = [field for field in required_fields if field not in record or record[field] is None]
                if not missing:
                    complete_records += 1
                else:
                    for field in missing:
                        missing_fields[field] = missing_fields.get(field, 0) + 1

            completeness_ratio = complete_records / total_records if total_records > 0 else 1.0

            return {
                "total_records": total_records,
                "complete_records": complete_records,
                "completeness_ratio": completeness_ratio,
                "missing_fields": missing_fields
            }

        streaming_completeness = check_completeness(streaming_data, "streaming")
        batch_completeness = check_completeness(batch_data, "batch")

        min_completeness = min(streaming_completeness["completeness_ratio"],
                              batch_completeness["completeness_ratio"])

        return {
            "status": "passed" if min_completeness >= 0.95 else "failed",
            "streaming_completeness": streaming_completeness,
            "batch_completeness": batch_completeness,
            "min_completeness_ratio": min_completeness
        }

    def _generate_key(self, record: Dict, key_fields: List[str]) -> str:
        """生成记录键"""
        return "_".join(str(record.get(field, "")) for field in key_fields)

    def _aggregate_by_user(self, data: List[Dict]) -> Dict[str, float]:
        """按用户聚合数据"""
        agg = {}
        for record in data:
            user = record.get("user_id", "unknown")
            value = record.get("value", 0)
            agg[user] = agg.get(user, 0) + value
        return agg

    def _calculate_consistency_score(self, result: Dict) -> float:
        """计算整体一致性评分"""
        validations = result["validations"]
        scores = []

        # 统计校验权重最高
        if validations["statistics"]["status"] == "passed":
            scores.append(1.0)
        else:
            scores.append(0.0)

        # 记录级校验
        if validations["records"]["status"] == "passed":
            scores.append(validations["records"]["match_ratio"])
        else:
            scores.append(0.0)

        # 聚合校验
        if validations["aggregation"]["status"] == "passed":
            scores.append(validations["aggregation"]["consistency_ratio"])
        else:
            scores.append(0.0)

        # 完整性校验
        scores.append(validations["completeness"]["min_completeness_ratio"])

        return statistics.mean(scores) if scores else 0.0

    def generate_validation_report(self) -> str:
        """生成校验报告"""
        report = "# 流批一致性校验报告\n\n"
        report += f"校验时间: {datetime.now().isoformat()}\n"
        report += f"总校验次数: {len(self.validation_results)}\n\n"

        if self.validation_results:
            latest = self.validation_results[-1]
            report += "## 最新校验结果\n\n"
            report += f"- 时间窗口: {latest['window_start']} 至 {latest['window_end']}\n"
            report += f"- 流处理记录数: {latest['streaming_records']}\n"
            report += f"- 批处理记录数: {latest['batch_records']}\n"
            report += f"- 一致性评分: {latest['consistency_score']:.3f}\n\n"

            # 详细校验结果
            for validation_name, validation_result in latest["validations"].items():
                report += f"### {validation_name.title()} 校验\n\n"
                report += f"- 状态: {validation_result['status']}\n"

                if validation_name == "statistics" and "differences" in validation_result:
                    report += "- 统计差异:\n"
                    for key, diff in validation_result["differences"].items():
                        report += f"  - {key}: 流处理={diff['streaming']:.2f}, 批处理={diff['batch']:.2f}, 差异={diff['difference']:.2f}\n"

                elif validation_name == "records":
                    report += f"- 匹配率: {validation_result['match_ratio']:.3f}\n"
                    report += f"- 匹配记录: {validation_result['matched_records']}\n"

                report += "\n"

        return report

# 配置示例
validation_config = {
    "tolerance_threshold": 0.01,
    "match_threshold": 0.95,
    "aggregation_tolerance": 0.1,
    "key_fields": ["user_id", "event_type"],
    "required_fields": ["user_id", "timestamp", "value"]
}

# 使用示例
if __name__ == "__main__":
    # 初始化校验器
    validator = ConsistencyValidator(validation_config)

    # 模拟流处理和批处理结果
    base_time = datetime.now() - timedelta(hours=1)

    streaming_results = [
        {
            "user_id": f"user_{i % 10}",
            "event_type": "click",
            "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
            "value": float(i % 100)
        }
        for i in range(100)
    ]

    # 批处理结果略有差异（模拟真实场景）
    batch_results = [
        {
            "user_id": f"user_{i % 10}",
            "event_type": "click",
            "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
            "value": float(i % 100) + (0.01 if i % 20 == 0 else 0)  # 5%的数据有小差异
        }
        for i in range(95)  # 批处理少5条记录
    ]

    # 执行校验
    result = validator.validate_consistency(
        streaming_results,
        batch_results,
        base_time,
        base_time + timedelta(hours=1)
    )

    print("Consistency Validation Result:")
    print(json.dumps(result, indent=2, default=str))

    # 生成报告
    report = validator.generate_validation_report()
    print("\nValidation Report:")
    print(report)