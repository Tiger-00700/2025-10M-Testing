# examples/13_data_gov/data_cleanup.py
# 测试数据清理工具示例

import os
import shutil
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class CleanupStrategy(Enum):
    SOFT_DELETE = "soft_delete"
    HARD_DELETE = "hard_delete"
    ARCHIVE = "archive"

@dataclass
class CleanupRule:
    """清理规则"""
    name: str
    condition: str
    action: CleanupStrategy
    retention_days: int
    requires_approval: bool
    priority: int

class DataCleanupManager:
    """数据清理管理器"""

    def __init__(self, base_path: str = "test_data"):
        self.base_path = base_path
        self.logger = logging.getLogger(__name__)

        # 默认清理规则
        self.cleanup_rules = [
            CleanupRule(
                name="expired_test_data",
                condition="age > retention_period",
                action=CleanupStrategy.ARCHIVE,
                retention_days=90,
                requires_approval=False,
                priority=1
            ),
            CleanupRule(
                name="orphaned_temp_files",
                condition="is_temp_file and age > 7",
                action=CleanupStrategy.HARD_DELETE,
                retention_days=7,
                requires_approval=False,
                priority=2
            ),
            CleanupRule(
                name="failed_test_artifacts",
                condition="test_status == 'failed' and age > 30",
                action=CleanupStrategy.SOFT_DELETE,
                retention_days=30,
                requires_approval=False,
                priority=3
            ),
            CleanupRule(
                name="sensitive_data_cleanup",
                condition="contains_sensitive_data and age > 365",
                action=CleanupStrategy.ARCHIVE,
                retention_days=365,
                requires_approval=True,
                priority=4
            )
        ]

    def scan_and_cleanup(self, dry_run: bool = True) -> Dict:
        """扫描并清理数据"""
        self.logger.info(f"Starting data cleanup scan in {self.base_path}")

        scan_results = {
            'scanned_files': 0,
            'candidates_for_cleanup': [],
            'cleanup_actions': [],
            'errors': []
        }

        try:
            # 扫描目录
            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    scan_results['scanned_files'] += 1

                    # 评估清理候选
                    cleanup_candidate = self._evaluate_cleanup_candidate(file_path)
                    if cleanup_candidate:
                        scan_results['candidates_for_cleanup'].append(cleanup_candidate)

            # 按优先级排序清理候选
            scan_results['candidates_for_cleanup'].sort(key=lambda x: x['priority'])

            # 执行清理
            for candidate in scan_results['candidates_for_cleanup']:
                try:
                    action_result = self._execute_cleanup_action(candidate, dry_run)
                    scan_results['cleanup_actions'].append(action_result)
                except Exception as e:
                    scan_results['errors'].append({
                        'file': candidate['file_path'],
                        'error': str(e)
                    })

        except Exception as e:
            scan_results['errors'].append({
                'operation': 'scan',
                'error': str(e)
            })

        self.logger.info(f"Cleanup scan completed. Processed {scan_results['scanned_files']} files")
        return scan_results

    def add_cleanup_rule(self, rule: CleanupRule):
        """添加清理规则"""
        self.cleanup_rules.append(rule)
        self.cleanup_rules.sort(key=lambda x: x.priority)

    def remove_cleanup_rule(self, rule_name: str) -> bool:
        """移除清理规则"""
        for i, rule in enumerate(self.cleanup_rules):
            if rule.name == rule_name:
                del self.cleanup_rules[i]
                return True
        return False

    def _evaluate_cleanup_candidate(self, file_path: str) -> Optional[Dict]:
        """评估文件是否为清理候选"""
        if not os.path.exists(file_path):
            return None

        file_stat = os.stat(file_path)
        file_age_days = (datetime.now() - datetime.fromtimestamp(file_stat.st_mtime)).days
        file_size = file_stat.st_size

        # 检查每个清理规则
        for rule in self.cleanup_rules:
            if self._matches_condition(file_path, rule.condition, file_age_days):
                return {
                    'file_path': file_path,
                    'rule_name': rule.name,
                    'action': rule.action.value,
                    'age_days': file_age_days,
                    'size_bytes': file_size,
                    'requires_approval': rule.requires_approval,
                    'priority': rule.priority
                }

        return None

    def _matches_condition(self, file_path: str, condition: str, age_days: int) -> bool:
        """检查文件是否匹配清理条件"""
        # 简化条件检查（实际应使用更复杂的表达式解析器）
        if "age > retention_period" in condition:
            # 假设保留期为90天
            return age_days > 90
        elif "is_temp_file and age > 7" in condition:
            return file_path.endswith('.tmp') and age_days > 7
        elif "test_status == 'failed' and age > 30" in condition:
            return 'failed' in file_path.lower() and age_days > 30
        elif "contains_sensitive_data and age > 365" in condition:
            return 'sensitive' in file_path.lower() and age_days > 365

        return False

    def _execute_cleanup_action(self, candidate: Dict, dry_run: bool) -> Dict:
        """执行清理动作"""
        action = candidate['action']
        file_path = candidate['file_path']

        result = {
            'file_path': file_path,
            'action': action,
            'success': False,
            'dry_run': dry_run
        }

        if dry_run:
            result['success'] = True
            self.logger.info(f"[DRY RUN] Would {action} {file_path}")
            return result

        try:
            if action == CleanupStrategy.SOFT_DELETE.value:
                # 移动到回收站目录
                trash_path = self._get_trash_path(file_path)
                os.makedirs(os.path.dirname(trash_path), exist_ok=True)
                shutil.move(file_path, trash_path)

            elif action == CleanupStrategy.HARD_DELETE.value:
                # 永久删除
                os.remove(file_path)

            elif action == CleanupStrategy.ARCHIVE.value:
                # 移动到归档目录
                archive_path = self._get_archive_path(file_path)
                os.makedirs(os.path.dirname(archive_path), exist_ok=True)
                shutil.move(file_path, archive_path)

            result['success'] = True
            self.logger.info(f"Successfully {action}d {file_path}")

        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Failed to {action} {file_path}: {e}")

        return result

    def _get_trash_path(self, file_path: str) -> str:
        """获取回收站路径"""
        relative_path = os.path.relpath(file_path, self.base_path)
        return os.path.join(self.base_path, ".trash", relative_path)

    def _get_archive_path(self, file_path: str) -> str:
        """获取归档路径"""
        relative_path = os.path.relpath(file_path, self.base_path)
        return os.path.join(self.base_path, ".archive", relative_path)

    def generate_cleanup_report(self, scan_results: Dict) -> str:
        """生成清理报告"""
        report = []
        report.append("# 数据清理报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        report.append("## 扫描统计")
        report.append(f"- 扫描文件数: {scan_results['scanned_files']}")
        report.append(f"- 清理候选数: {len(scan_results['candidates_for_cleanup'])}")
        report.append(f"- 执行清理数: {len(scan_results['cleanup_actions'])}")
        report.append(f"- 错误数: {len(scan_results['errors'])}")
        report.append("")

        if scan_results['candidates_for_cleanup']:
            report.append("## 清理候选列表")
            for candidate in scan_results['candidates_for_cleanup'][:10]:  # 最多显示10个
                report.append(f"- {candidate['file_path']} ({candidate['age_days']}天前, {candidate['action']})")
            if len(scan_results['candidates_for_cleanup']) > 10:
                report.append(f"- ... 还有{len(scan_results['candidates_for_cleanup']) - 10}个文件")
            report.append("")

        return "\n".join(report)


# 使用示例
if __name__ == "__main__":
    cleanup_manager = DataCleanupManager("test_data")

    # 执行清理扫描（试运行）
    results = cleanup_manager.scan_and_cleanup(dry_run=True)

    # 生成报告
    report = cleanup_manager.generate_cleanup_report(results)
    print(report)

    # 添加自定义清理规则
    custom_rule = CleanupRule(
        name="old_log_files",
        condition="file_extension == '.log' and age > 30",
        action=CleanupStrategy.ARCHIVE,
        retention_days=30,
        requires_approval=False,
        priority=5
    )
    cleanup_manager.add_cleanup_rule(custom_rule)