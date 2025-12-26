#!/usr/bin/env python3
# hdfs_consistency_check.py
# HDFS存储副本一致性检查脚本

import subprocess
import hashlib
import os
import sys
from datetime import datetime
import json
import argparse

class HDFSConsistencyChecker:
    def __init__(self, namenode_host="localhost", namenode_port=9000):
        self.namenode = f"{namenode_host}:{namenode_port}"
        self.hadoop_cmd = "hadoop"
        self.hdfs_cmd = "hdfs"

    def run_hdfs_command(self, cmd):
        """执行HDFS命令"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def get_file_replicas(self, file_path):
        """获取文件的副本信息"""
        cmd = f"{self.hdfs_cmd} fsck {file_path} -files -blocks -locations"
        success, stdout, stderr = self.run_hdfs_command(cmd)

        if not success:
            return None

        replicas = []
        for line in stdout.split('\n'):
            if 'blk_' in line and 'DatanodeInfoWithStorage' in line:
                # 解析副本位置信息
                parts = line.split()
                if len(parts) >= 3:
                    block_id = parts[0].split(':')[0]
                    datanodes = [part.split(':')[0] for part in parts[2:] if ':' in part]
                    replicas.append({
                        'block_id': block_id,
                        'datanodes': datanodes
                    })

        return replicas

    def calculate_file_hash(self, local_file):
        """计算本地文件的哈希值"""
        hash_md5 = hashlib.md5()
        with open(local_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def download_and_hash_block(self, block_info, output_dir="/tmp/hdfs_check"):
        """下载并计算块的哈希值"""
        os.makedirs(output_dir, exist_ok=True)

        block_file = os.path.join(output_dir, f"{block_info['block_id']}.block")

        # 从第一个可用的datanode下载块
        for datanode in block_info['datanodes']:
            try:
                # 实际实现需要使用HDFS API或直接从datanode下载
                # 这里是简化示例
                cmd = f"dd if=/dev/urandom of={block_file} bs=1M count=1"  # 模拟下载
                success, _, _ = self.run_hdfs_command(cmd)

                if success and os.path.exists(block_file):
                    file_hash = self.calculate_file_hash(block_file)
                    os.remove(block_file)  # 清理临时文件
                    return file_hash

            except Exception as e:
                continue

        return None

    def check_file_consistency(self, file_path, expected_hash=None):
        """检查文件一致性"""
        print(f"检查文件: {file_path}")

        # 获取文件状态
        cmd = f"{self.hdfs_cmd} fsck {file_path} -files -blocks"
        success, stdout, stderr = self.run_hdfs_command(cmd)

        if not success:
            return {
                'file': file_path,
                'status': 'ERROR',
                'error': stderr,
                'consistent': False
            }

        # 检查副本数量
        replicas = self.get_file_replicas(file_path)
        if not replicas:
            return {
                'file': file_path,
                'status': 'NO_REPLICAS',
                'consistent': False
            }

        # 检查每个块的副本一致性
        block_hashes = {}
        inconsistent_blocks = []

        for replica in replicas:
            block_hash = self.download_and_hash_block(replica)
            if block_hash:
                block_id = replica['block_id']
                if block_id not in block_hashes:
                    block_hashes[block_id] = block_hash
                elif block_hashes[block_id] != block_hash:
                    inconsistent_blocks.append(block_id)

        result = {
            'file': file_path,
            'total_blocks': len(replicas),
            'inconsistent_blocks': len(inconsistent_blocks),
            'consistent': len(inconsistent_blocks) == 0,
            'replica_count': len(replicas[0]['datanodes']) if replicas else 0
        }

        if inconsistent_blocks:
            result['inconsistent_block_ids'] = inconsistent_blocks

        return result

    def batch_consistency_check(self, file_list, output_file=None):
        """批量一致性检查"""
        results = []
        total_files = len(file_list)
        consistent_files = 0

        print(f"开始批量检查 {total_files} 个文件...")

        for i, file_path in enumerate(file_list, 1):
            print(f"[{i}/{total_files}] 检查: {file_path}")
            result = self.check_file_consistency(file_path)
            results.append(result)

            if result['consistent']:
                consistent_files += 1

            # 每10个文件显示一次进度
            if i % 10 == 0:
                progress = (i / total_files) * 100
                print(".1f")

        summary = {
            'total_files': total_files,
            'consistent_files': consistent_files,
            'inconsistent_files': total_files - consistent_files,
            'consistency_rate': consistent_files / total_files if total_files > 0 else 0,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            print(f"结果已保存到: {output_file}")

        return summary

def main():
    parser = argparse.ArgumentParser(description='HDFS一致性检查工具')
    parser.add_argument('--files', nargs='+', required=True, help='要检查的文件列表')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--namenode', default='localhost:9000', help='NameNode地址')

    args = parser.parse_args()

    checker = HDFSConsistencyChecker(args.namenode)
    summary = checker.batch_consistency_check(args.files, args.output)

    print("\n一致性检查完成:")
    print(f"总文件数: {summary['total_files']}")
    print(f"一致文件数: {summary['consistent_files']}")
    print(f"不一致文件数: {summary['inconsistent_files']}")
    print(f"一致性率: {summary['consistency_rate']:.2%}")

    if summary['inconsistent_files'] > 0:
        print("\n不一致文件列表:")
        for result in summary['results']:
            if not result['consistent']:
                print(f"  - {result['file']} (不一致块数: {result['inconsistent_blocks']})")

if __name__ == "__main__":
    main()