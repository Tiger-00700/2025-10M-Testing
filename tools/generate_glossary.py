import re
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime

BOOK = Path(__file__).resolve().parents[1] / "book" / "1022.2025.newbook.md"
OUT = Path(__file__).resolve().parents[1] / "book" / "附录-术语与缩略语表.md"
REPORT_DIR = Path(__file__).resolve().parents[1] / "tools" / "reports"

heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
code_fence_re = re.compile(r"^\s*(```|~~~)")
anchor_re = re.compile(r'^\s*<a\s+id="([^"]+)"\s*></a>\s*$', re.IGNORECASE)

# Known terms and mappings to Chinese and brief defs (extendable)
KNOWN: Dict[str, Tuple[str, str]] = {
    "Hadoop": ("Hadoop", "分布式存储与计算生态，含HDFS/MapReduce/YARN"),
    "Spark": ("Spark", "内存优先的大数据计算框架，支持批流处理"),
    "Flink": ("Flink", "流批一体的分布式流处理框架"),
    "Kafka": ("Kafka", "分布式消息与日志系统，常用于数据管道"),
    "Hive": ("Hive", "数据仓库工具，提供类SQL的查询能力"),
    "HBase": ("HBase", "分布式列式NoSQL数据库，基于HDFS"),
    "Presto": ("Presto/Trino", "分布式SQL查询引擎"),
    "Trino": ("Presto/Trino", "分布式SQL查询引擎"),
    "ClickHouse": ("ClickHouse", "列式数据库，擅长OLAP分析"),
    "Iceberg": ("Iceberg", "开源表格式，支持Schema演进/时光回溯"),
    "Hudi": ("Hudi", "开源表格式，支持增量数据/CDC"),
    "Delta Lake": ("Delta Lake", "表格式，支持ACID/时光回溯"),
    "Lakehouse": ("湖仓一体", "融合数据湖与数据仓库的架构范式"),
    "Data Lake": ("数据湖", "存放原始数据的集中式存储"),
    "ETL": ("ETL", "Extract-Transform-Load 数据处理流程"),
    "ELT": ("ELT", "Extract-Load-Transform 数据处理流程"),
    "CDC": ("CDC", "Change Data Capture 变更数据捕获"),
    "OLAP": ("OLAP", "联机分析处理，面向复杂查询与聚合"),
    "OLTP": ("OLTP", "联机事务处理，面向高并发小事务"),
    "SLA": ("SLA", "Service Level Agreement 服务级别协议"),
    "SLI": ("SLI", "Service Level Indicator 服务级别指标"),
    "SLO": ("SLO", "Service Level Objective 服务级别目标"),
    "RPO": ("RPO", "恢复点目标，数据可接受丢失窗口"),
    "RTO": ("RTO", "恢复时间目标，服务可接受中断时长"),
    "CAP": ("CAP", "一致性/可用性/分区容错性权衡定理"),
    "BASE": ("BASE", "基本可用/软状态/最终一致性"),
    "ACID": ("ACID", "原子性/一致性/隔离性/持久性"),
    "GDPR": ("GDPR", "欧盟通用数据保护条例"),
    "PII": ("PII", "Personally Identifiable Information 可识别个人信息"),
    "RBAC": ("RBAC", "基于角色的访问控制"),
    "ABAC": ("ABAC", "基于属性的访问控制"),
    "Kubernetes": ("Kubernetes", "容器编排平台，简称K8s"),
    "K8s": ("K8s", "Kubernetes 的常用简称"),
    "Docker": ("Docker", "容器运行时与镜像生态"),
    "Helm": ("Helm", "K8s 包管理工具"),
    "Airflow": ("Airflow", "工作流编排平台"),
    "NiFi": ("NiFi", "数据流处理与编排工具"),
    "Superset": ("Superset", "数据可视化与BI平台"),
    "Grafana": ("Grafana", "可视化与监控平台"),
    "Prometheus": ("Prometheus", "时序监控与告警系统"),
    "OpenTelemetry": ("OpenTelemetry/OTel", "可观测性数据采集标准"),
    "OTel": ("OpenTelemetry/OTel", "可观测性数据采集标准"),
}

ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,9}\b")

class Node:
    def __init__(self, level: int, idx: int, title: str):
        self.level = level
        self.idx = idx
        self.title = title
        # end will be set to an int index later; annotate as Optional[int] for mypy
        self.end: int | None = None


def load_lines(p: Path) -> List[str]:
    text = p.read_text(encoding="utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.split("\n")


def parse_nodes(lines: List[str]) -> List[Node]:
    nodes: List[Node] = []
    for i, line in enumerate(lines):
        m = heading_re.match(line)
        if m:
            nodes.append(Node(len(m.group(1)), i, m.group(2)))
    for i in range(len(nodes)):
        end = len(lines)
        for j in range(i + 1, len(nodes)):
            if nodes[j].level <= nodes[i].level:
                end = nodes[j].idx
                break
        nodes[i].end = end
    return nodes


def build_anchor_map(lines: List[str]) -> Dict[Tuple[str, ...], str]:
    path_stack: List[str] = []
    anchors: Dict[Tuple[str, ...], str] = {}


    def slugify(text: str) -> str:
        punct_pattern = (
            r"[!\"#$%&'()*+,\./:;<=>?@\[\\\]^_`{|}~"
            "，。、《》？；：‘’“”（）【】·—…]"
            "+"
        )
        t = text.strip().lower()
        t = re.sub(punct_pattern, "", t)
        t = re.sub(r"\s+", "-", t)
        return re.sub(r"-{2,}", "-", t)

    def update_stack(title: str, level: int):
        nonlocal path_stack
        if level == 1:
            path_stack = [title]
        elif level == 2:
            if len(path_stack) >= 1:
                path_stack = [path_stack[0], title]
            else:
                path_stack = ["", title]
        elif level == 3:
            while len(path_stack) < 2:
                path_stack.append("")
            if len(path_stack) == 2:
                path_stack.append(title)
            else:
                path_stack[2] = title
        else:
            if len(path_stack) == 0:
                path_stack = [title]
            elif len(path_stack) == 1:
                path_stack.append(title)
            elif len(path_stack) == 2:
                path_stack.append(title)
            else:
                path_stack[-1] = title

    # walk lines and capture anchors paired to subsequent H3/H4 headings
    seen_anchor = None
    for i, line in enumerate(lines):
        m = heading_re.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2)
            update_stack(title, level)
            if level in (3, 4):
                key = tuple([seg for seg in path_stack if seg])
                if seen_anchor:
                    anchors[key] = seen_anchor
                    seen_anchor = None
                else:
                    # fallback to slug
                    base = slugify(title)
                    count = sum(1 for v in anchors.values() if v.startswith(base))
                    aid = base if count == 0 else f"{base}-{count+1}"
                    anchors[key] = aid
        else:
            am = anchor_re.match(line)
            if am:
                seen_anchor = am.group(1)
            elif line.strip() != "":
                seen_anchor = None
    return anchors


def collect_terms(lines: List[str]) -> Dict[str, Dict[str, str]]:
    anchors = build_anchor_map(lines)
    path_stack: List[str] = []

    def current_key() -> Tuple[str, ...]:
        return tuple([seg for seg in path_stack if seg])

    def update_stack(title: str, level: int):
        nonlocal path_stack
        if level == 1:
            path_stack = [title]
        elif level == 2:
            if len(path_stack) >= 1:
                path_stack = [path_stack[0], title]
            else:
                path_stack = ["", title]
        elif level == 3:
            while len(path_stack) < 2:
                path_stack.append("")
            if len(path_stack) == 2:
                path_stack.append(title)
            else:
                path_stack[2] = title
        else:
            if len(path_stack) == 0:
                path_stack = [title]
            elif len(path_stack) == 1:
                path_stack.append(title)
            elif len(path_stack) == 2:
                path_stack.append(title)
            else:
                path_stack[-1] = title

    glossary: Dict[str, Dict[str, str]] = {}

    inside_code = False
    for i, line in enumerate(lines):
        s = line.strip()
        if code_fence_re.match(s):
            inside_code = not inside_code
            continue
        m = heading_re.match(line)
        if m:
            update_stack(m.group(2), len(m.group(1)))
            continue
        if inside_code or s.startswith(">"):
            continue
        # extract acronyms
        for token in set(ACRONYM_RE.findall(line)):
            if len(token) == 1:
                continue
            if token.isdigit():
                continue
            term = token
            if term not in glossary:
                zh, brief = KNOWN.get(term, ("", ""))
                key = current_key()
                anchor = anchors.get(key, "")
                glossary[term] = {
                    "term": term,
                    "zh": zh,
                    "brief": brief,
                    "path": " > ".join(list(key)),
                    "anchor": anchor,
                }
        # extract known terms by substring
        for k in KNOWN.keys():
            if re.search(r"\b" + re.escape(k) + r"\b", line):
                term = k
                if term not in glossary:
                    zh, brief = KNOWN.get(term, ("", ""))
                    key = current_key()
                    anchor = anchors.get(key, "")
                    glossary[term] = {
                        "term": term,
                        "zh": zh,
                        "brief": brief,
                        "path": " > ".join(list(key)),
                        "anchor": anchor,
                    }
    return glossary


def render_glossary(gloss: Dict[str, Dict[str, str]]) -> List[str]:
    lines: List[str] = []
    lines.append("# 附录 术语与缩略语表")
    lines.append("")
    lines.append("> 说明：本表自动汇总书中出现的常见术语与缩略语，包含中文对照、首次出现位置与跳转。")
    lines.append("")
    lines.append("| 术语 | 中文 | 首次出现 | 跳转 | 简要释义 |")
    lines.append("|---|---|---|---|---|")
    for term in sorted(gloss.keys(), key=lambda x: x.lower()):
        g = gloss[term]
        path = g["path"]
        anchor = g["anchor"]
        link = f"[链接](./1022.2025.newbook.md#{anchor})" if anchor else ""
        zh = g["zh"] or ""
        brief = g["brief"] or ""
        lines.append(f"| {term} | {zh} | {path} | {link} | {brief} |")
    return lines


def main():
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lines = load_lines(BOOK)
    gloss = collect_terms(lines)
    OUT.write_text("\n".join(render_glossary(gloss)), encoding="utf-8")
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    stats = "Total terms: " + str(len(gloss)) + "\n\n" + "\n".join(sorted(gloss.keys()))
    (REPORT_DIR / f"glossary-stats-{ts}.md").write_text(stats, encoding="utf-8")
    print(f"Wrote glossary with {len(gloss)} terms to {OUT}")


if __name__ == "__main__":
    main()
