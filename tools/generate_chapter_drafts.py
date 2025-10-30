#!/usr/bin/env python3
"""Generate 1-example + 1-exercise + 1-figure placeholder drafts for selected chapters.

Produces files under: tools/editorial-drafts/<sanitized-chapter-title>.md

Selected chapters (priority):
- chapter/第1篇-第1章-大数据测试概述.md
- chapter/第1篇-第3章-大数据测试环境搭建【入门】.md
- chapter/第2篇-第5章-数据处理测试【进阶】.md

These drafts are suggestions only — they do NOT modify original chapter files.
"""
from pathlib import Path
import re

ROOT = Path('.')
OUT_DIR = ROOT / 'tools' / 'editorial-drafts'

TARGETS = [
    'chapter/第1篇-第1章-大数据测试概述.md',
    'chapter/第1篇-第3章-大数据测试环境搭建【入门】.md',
    'chapter/第2篇-第5章-数据处理测试【进阶】.md',
]

def sanitize(name: str) -> str:
    s = re.sub(r"[\\/:*?\"<>|]+", '_', name)
    s = re.sub(r"\s+", '_', s)
    return s[:120]

def read_title(path: Path) -> str:
    try:
        txt = path.read_text(encoding='utf-8')
    except Exception:
        return path.name
    for ln in txt.splitlines()[:50]:
        m = re.match(r'^\s{0,3}#\s+(.*)', ln)
        if m:
            return m.group(1).strip()
    return path.name

def make_draft_for(path: Path) -> str:
    title = read_title(path)
    # Create a simple, relevant example/exercise/figure depending on chapter
    if '概述' in title or '概念' in title:
        example = (
            '示例：检查 HDFS 中某路径文件数与大小（Python + hdfs client 示例）\n\n'
            '```python\nfrom hdfs import InsecureClient\nclient = InsecureClient("http://namenode:50070", user="hdfs")\nfiles = client.list("/data/sample")\nprint(f"Found {len(files)} items")\nfor p in files[:10]:\n    print(p)\n```\n'
        )
        exercise = (
            '练习：请写一个脚本，验证两次数据导入结果记录数一致，并在发现差异时输出不一致的记录 ID 列表。\n\n'
            '提示：可用 pandas 比对或按 key 做哈希比较。'
        )
        figure = '图示占位：大数据测试流程图（建议：数据流 → 测试点 → 验证指标），格式 SVG/PNG。'
    elif '环境' in title or '搭建' in title:
        example = (
            '示例：使用 Docker Compose 快速搭建本地 Spark+HDFS 测试环境（简化）\n\n'
            '```yaml\nversion: "3"\nservices:\n  namenode:\n    image: bde2020/hadoop-namenode:2.0.0-hadoop2.7.4-java8\n    environment:\n      - CLUSTER_NAME=test\n  spark:\n    image: bitnami/spark:3\n    depends_on:\n      - namenode\n```\n'
        )
        exercise = (
            '练习：在本地环境中运行一个小型 Spark 作业，计算样本数据的行数并报告执行时间。\n\n'
            '提示：可用 spark-submit 或 pyspark。'
        )
        figure = '图示占位：测试环境拓扑图（节点、网络、端口），建议 PNG/SVG。'
    else:
        # 数据处理相关
        example = (
            '示例：用 PySpark 做 ETL：读取 CSV，做简单转换并写出 Parquet（含断言）\n\n'
            '```python\nfrom pyspark.sql import SparkSession\nspark = SparkSession.builder.appName("etl-sample").getOrCreate()\ndf = spark.read.csv("/data/input.csv", header=True)\nassert df.count() > 0, "输入为空"\nout = df.filter("amount > 0").select("id","amount")\nout.write.parquet("/data/out.parquet")\n```\n'
        )
        exercise = (
            '练习：设计一个验证步骤，确保转换后数值字段没有出现负值并与来源表的关键字段一一对应。\n\n'
            '提示：准备一组带边界值的测试数据并验证。'
        )
        figure = '图示占位：ETL 流程图（数据源 → 转换 → 验证 → 输出），建议 SVG。'

    md = []
    md.append(f'# Draft: {title}')
    md.append(f'Source: `{path.as_posix()}`')
    md.append('\n---\n')
    md.append('## Proposed example\n')
    md.append(example)
    md.append('## Proposed exercise\n')
    md.append(exercise)
    md.append('\n**Suggested answer / hints (for editor review):**\n')
    if '概述' in title:
        md.append('- Use HDFS client or hdfs CLI; include sample outputs and expected counts.\n')
    elif '环境' in title:
        md.append('- Provide exact docker-compose commands and verification steps (e.g., curl to Namenode UI).\n')
    else:
        md.append('- Include test dataset and expected assertions; provide small unit test examples.\n')
    md.append('\n## Figure placeholder\n')
    md.append(f'- {figure}\n')
    md.append('\n## Notes\n')
    md.append('- This file is a draft proposal. Please adapt code snippets to the project environment and add runtime instructions.\n')

    return '\n'.join(md)

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    created = []
    for t in TARGETS:
        p = ROOT / t
        if not p.exists():
            print('Missing', t)
            continue
        title = read_title(p)
        fname = sanitize(title) + '.md'
        outp = OUT_DIR / fname
        outp.write_text(make_draft_for(p), encoding='utf-8')
        created.append(outp)
    print('Wrote', len(created), 'drafts to', OUT_DIR)

if __name__ == '__main__':
    main()
