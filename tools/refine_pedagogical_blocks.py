import re
from pathlib import Path
from typing import List, Tuple

TARGET = Path(__file__).resolve().parents[1] / "book" / "1022.2025.newbook.md"

heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

class Node:
    def __init__(self, level: int, idx: int, title: str):
        self.level = level
        self.idx = idx
        self.title = title
        self.end = None  # exclusive


def load_lines(path: Path):
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return text.split("\n")


def save_lines(path: Path, lines: List[str]):
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_nodes(lines: List[str]) -> List[Node]:
    nodes: List[Node] = []
    for i, line in enumerate(lines):
        m = heading_re.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2)
            nodes.append(Node(level, i, title))
    for i in range(len(nodes)):
        end = len(lines)
        for j in range(i + 1, len(nodes)):
            if nodes[j].level <= nodes[i].level:
                end = nodes[j].idx
                break
        nodes[i].end = end
    return nodes


def ensure_blank_after(lines: List[str], pos: int):
    ins = pos + 1
    if ins >= len(lines) or lines[ins].strip() != "":
        lines.insert(ins, "")


def contains_any(s: str, kws: List[str]) -> bool:
    return any(k in s for k in kws)


def tailored_content(title: str, level: int) -> Tuple[List[str], List[str]]:
    scope = "本节" if level >= 3 else ("本章" if level == 2 else "本篇")

    def tip(msg: str) -> List[str]:
        return [f"> 【阅读提示】{scope}聚焦：{title}。{msg}", ""]

    # Defaults
    rt = tip("建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。")
    se = [
        "> 【章节重点难点总结】",
        "",
        "- 本节要点：梳理关键概念、流程与方法；明确输入输出与成功标准",
        "- 难点：落地实施的约束（性能/数据质量/安全/成本）的取舍与平衡",
        "",
        "> 【课后思考/练习题】",
        "",
        "1. 结合你的项目，描述本节主题的一个实践场景，并给出验证要点。",
        "2. 列出2-3个风险点/常见陷阱，并给出可操作的规避建议。",
        "",
    ]

    t = title
    if contains_any(t, ["概念", "特点", "概述"]):
        rt = tip("建议把握5V特性与典型业务场景映射，区分术语边界，建立统一词汇表。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：5V 特性（体量/多样/速度/价值/真实性）、数据来源与形态、处理范式",
            "- 难点：真实性与价值密度低的应对（采样、画像、特征工程、校验规则）",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 选取你的领域数据，分别对应 5V 给出例子并量化指标。",
            "2. 如何验证一份含噪数据集的真实性与可用性？给出步骤与判据。",
            "",
        ]
    elif contains_any(t, ["测试定义", "目标"]):
        rt = tip("建议以质量模型为框架（功能/性能/可靠/安全/可扩展/可观测）梳理覆盖面。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：质量属性到指标的映射（吞吐/延迟/正确率/RPO/RTO/SLO）",
            "- 难点：在资源与时限下的测试优先级与样本代表性",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 为某数据管道定义可量化的质量目标与验收标准。",
            "2. 在预算固定时，如何在功能、性能、安全测试间做优先级取舍？",
            "",
        ]
    elif contains_any(t, ["区别", "联系", "对比"]):
        rt = tip("建议从数据规模、计算范式、环境复杂度与观测手段四维对比传统测试。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：分布式/并行、批/流一体、数据驱动测试、统计性验证",
            "- 难点：在不可复现实验的分布式场景进行正确性与性能归因",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 对比单体系统与大数据系统的性能测试设计差异。",
            "2. 如何为分布式作业设计幂等性与重试验证？",
            "",
        ]
    elif contains_any(t, ["发展", "趋势"]):
        rt = tip("建议关注湖仓一体、云原生、实时化与AI for Testing的融合趋势。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：湖仓、流批一体、Serverless、数据治理、安全合规",
            "- 难点：多云/混部环境的基准对齐与成本可视化",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 设计一个能跨云对比的存算分离基准测试方案。",
            "2. 如何衡量实时化改造对业务SLO的提升？",
            "",
        ]
    elif contains_any(t, ["挑战", "机遇"]):
        rt = tip("建议从环境、数据、技术、流程四类挑战入手给出可操作对策。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：环境复刻、数据准备、观测可用、自动化回归",
            "- 难点：低成本获取具代表性的TB/PB级数据样本",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 列出你当前项目的前三大挑战，并给出可量化缓解方案。",
            "2. 如何用数据子集+统计性断言替代全量比对？",
            "",
        ]
    elif contains_any(t, ["Hadoop", "HDFS", "MapReduce", "YARN"]):
        rt = tip("建议聚焦 HDFS/YARN/MapReduce 协同机制与可靠性/容错验证。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：副本机制、心跳/调度、作业容错与重试策略",
            "- 难点：故障注入与数据一致性验证的边界与方法",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 设计一次NameNode Failover下的数据正确性验证。",
            "2. 给出MapReduce长尾任务定位与优化步骤。",
            "",
        ]
    elif contains_any(t, ["Spark", "RDD", "DataFrame", "Streaming"]):
        rt = tip("建议结合内存计算、窄宽依赖与Shuffle机制分析性能与稳定性。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：Executor/Driver资源、Shuffle溢写、数据倾斜与调优",
            "- 难点：Structured Streaming Exactly-Once 与一致性验证",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 如何识别并缓解数据倾斜？列出3种可操作手段。",
            "2. 设计一个验证Structured Streaming端到端幂等性的用例。",
            "",
        ]
    elif contains_any(t, ["实时", "流处理", "Kafka", "Flink", "Pulsar", "Storm"]):
        rt = tip("建议从延迟、吞吐、状态一致性与背压治理四个维度制定用例。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：事件时间/水位线、状态快照、反压与容灾",
            "- 难点：Exactly-Once端到端语义的可验证性",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 给出端到端延迟SLA的测量与告警方案。",
            "2. 如何通过故障注入验证状态一致性？",
            "",
        ]
    elif contains_any(t, ["云原生", "Kubernetes", "容器", "Serverless"]):
        rt = tip("建议关注调度、资源隔离、弹性伸缩与亲和/反亲和策略对测试的影响。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：容器化部署、HPA/VPAs、节点失效演练",
            "- 难点：多租户隔离与限流下的性能基准一致性",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 设计一次在K8s上的弹性伸缩基准测试。",
            "2. 如何验证多租户下资源隔离与SLA？",
            "",
        ]
    elif contains_any(t, ["数据存储", "HDFS", "NoSQL", "图数据库", "时序", "列式"]):
        rt = tip("建议按访问模式与一致性需求进行选型对比与基准验证。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：读写模式、索引/压缩、分区与分片、冷热分层",
            "- 难点：一致性/可用性/分区容错（CAP）的取舍验证",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 为时序场景设计写多读多的压力模型与指标。",
            "2. 如何评估列式存储在不同压缩算法下的代价与收益？",
            "",
        ]
    elif contains_any(t, ["环境", "搭建", "配置", "验证", "部署"]):
        rt = tip("建议用基础镜像+IaC标准化环境，先Smoke后深测，最小路径闭环。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：容量规划、配置基线、自动化部署、健康检查",
            "- 难点：与生产一致性的抽象与差异控制",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 输出一份你的环境最小可用清单（组件/版本/参数）。",
            "2. 设计一套环境验收的自动化Smoke脚本清单。",
            "",
        ]
    elif contains_any(t, ["测试数据", "脱敏", "生成", "版本", "共享", "数据质量"]):
        rt = tip("建议区分合成/采样/变换三类数据策略，建立可追溯与可重现流程。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：覆盖/真实性/隔离/可重现、元数据与血缘管理",
            "- 难点：隐私合规与可用性之间的平衡（k匿名、差分隐私）",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 为某敏感字段设计兼顾业务可用的脱敏规则。",
            "2. 如何建立测试数据版本化与回滚机制？",
            "",
        ]
    elif contains_any(t, ["安全", "加密", "权限", "认证", "合规"]):
        rt = tip("建议从身份、授权、传输/存储加密、审计四层制定测试矩阵。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：RBAC/ABAC、KMS、密钥轮换、审计与告警",
            "- 难点：性能与安全的权衡、跨组件信任链验证",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 设计一次端到端数据加密（At-Rest/In-Transit）的验证方案。",
            "2. 如何验证最低权限原则在数据湖的落地有效？",
            "",
        ]
    elif contains_any(t, ["BI", "可视化", "报表", "分析测试", "挖掘", "AI"]):
        rt = tip("建议将正确性（口径/口算）与可用性（可达性/响应）分层验证。")
        se = [
            "> 【章节重点难点总结】",
            "",
            "- 要点：口径一致、采样校验、可视化断言、回归基线",
            "- 难点：模型可解释性与漂移检测",
            "",
            "> 【课后思考/练习题】",
            "",
            "1. 为某关键指标设计采样比对与容差策略。",
            "2. 如何监控AI模型在生产中的数据/概念漂移？",
            "",
        ]
    return rt, se


def replace_reading_tip(lines: List[str], nd: Node, new_tip: List[str]) -> bool:
    for i in range(nd.idx + 1, min(nd.idx + 12, nd.end)):
        if i < len(lines) and lines[i].strip().startswith("> 【阅读提示】"):
            lines[i] = new_tip[0]
            ensure_blank_after(lines, i)
            return True
        if i < len(lines) and heading_re.match(lines[i]):
            break
    return False


def replace_summary_and_exercises(lines: List[str], nd: Node, new_block: List[str]) -> bool:
    start = None
    for i in range(nd.idx + 1, nd.end):
        if lines[i].strip().startswith("> 【章节重点难点总结】"):
            start = i
            break
    if start is None:
        return False
    end = nd.end
    for j in range(start + 1, nd.end):
        if heading_re.match(lines[j]):
            end = j
            break
    lines[start:end] = new_block
    ensure_blank_after(lines, start + len(new_block) - 1)
    return True


def main():
    if not TARGET.exists():
        raise SystemExit(f"Target not found: {TARGET}")
    lines = load_lines(TARGET)
    nodes = parse_nodes(lines)
    changes = 0
    for nd in nodes:
        if nd.level not in (1, 2, 3):
            continue
        rt, se = tailored_content(nd.title, nd.level)
        if replace_reading_tip(lines, nd, rt):
            changes += 1
        if nd.level == 3 and replace_summary_and_exercises(lines, nd, se):
            changes += 1
    save_lines(TARGET, lines)
    print(f"Refined {changes} sections in {TARGET}")

if __name__ == "__main__":
    main()
