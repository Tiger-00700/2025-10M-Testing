import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book" / "1022.2025.newbook.md"
GLOSS = ROOT / "book" / "附录-术语与缩略语表.md"
REPORTS = ROOT / "tools" / "reports"

# Extended known term briefs (can be expanded)
KNOW: Dict[str, str] = {
    "SLA": "服务级别协议：面向业务的可用性与性能承诺，常以SLO/SLI衡量并落地至告警阈值与运维流程。",
    "SLI": "服务级别指标：用于度量SLO达成的可观测指标，如延迟、错误率、吞吐等。",
    "SLO": "服务级别目标：对SLI的目标阈值设定，例如P95延迟≤200ms、可用性≥99.9%。",
    "RPO": "恢复点目标：容灾场景中可接受的数据丢失窗口（时间范围），决定备份与复制策略。",
    "RTO": "恢复时间目标：故障发生到恢复服务的时间上限，影响高可用架构与演练频率。",
    "ACID": "数据库事务四要素：原子性、一致性、隔离性、持久性；保证强一致写入与读写隔离。",
    "BASE": "分布式领域的最终一致性取向：基本可用、软状态、最终一致性，与ACID形成对照。",
    "CAP": "一致性/可用性/分区容错性的权衡定理；实际工程常选CP/AP并通过补偿实现业务一致性。",
    "Kafka": "分布式日志与消息系统，支持高吞吐顺序写入，常用于数据采集与流处理管道。",
    "Flink": "流批一体计算引擎，支持事件时间/状态快照/Exactly-Once，适配实时计算与CEP场景。",
    "Spark": "通用大数据计算引擎，RDD/Dataset/Structured Streaming，批流均可，生态丰富。",
    "Hadoop": "早期大数据生态核心：HDFS存储+MapReduce计算+YARN资源管理，现多与湖仓/云原生融合。",
    "Iceberg": "数据湖表格式：支持ACID、Schema演进、Time Travel、分区进化，方便批流与多引擎共享。",
    "Hudi": "数据湖表格式：支持Upsert/CDC与增量拉取，适合近实时入湖与湖仓一体。",
    "Delta Lake": "表格式：ACID、版本化与时光回溯，搭配Spark生态广泛应用于湖仓一体。",
    "Lakehouse": "湖仓一体：统一数据湖与数仓的存储/管理/治理，支持批流融合与多引擎共享。",
    "OLAP": "联机分析处理：面向聚合/多维分析与长查询，强调列存、并行与向量化。",
    "OLTP": "联机事务处理：面向高并发小事务，强调低延迟强一致与索引优化。",
    "Kubernetes": "容器编排（K8s）：弹性伸缩、调度与隔离；大数据计算常在K8s上云原生化部署。",
    "OpenTelemetry": "可观测性标准：统一采集Trace/Metric/Log，便于跨组件与跨语言的端到端观测。",
}

WORD_RE = re.compile(r"[\w\-\+\.]+", re.UNICODE)


def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def count_term_freq(book_text: str, terms: List[str]) -> Dict[str, int]:
    freq: Dict[str, int] = {}
    for t in terms:
        if not t:
            continue
        # heuristic: whole word for ASCII-ish terms; simple contains for others
        if re.match(r"^[A-Za-z0-9_+\-\.]+$", t):
            pat = re.compile(rf"\b{re.escape(t)}\b")
        else:
            pat = re.compile(re.escape(t))
        freq[t] = len(pat.findall(book_text))
    return freq


def parse_glossary_rows(gloss_text: str) -> Tuple[List[str], List[List[str]]]:
    lines = gloss_text.split("\n")
    # find header and rows; assume simple pipe table
    header_idx = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("| 术语 |"):
            header_idx = i
            break
    if header_idx is None:
        raise SystemExit("Glossary table header not found")
    rows = []
    for ln in lines[header_idx+2:]:
        if not ln.strip().startswith("|"):
            break
        # split keeping inner content
        cols = [c.strip() for c in ln.strip().strip('|').split('|')]
        rows.append(cols)
    return lines, rows


def write_glossary(gloss_lines: List[str], rows: List[List[str]]) -> str:
    # Reconstruct the table by replacing the body rows
    out = []
    # find header start
    header_idx = None
    for i, ln in enumerate(gloss_lines):
        out.append(ln)
        if ln.strip().startswith("| 术语 |"):
            header_idx = i
            break
    if header_idx is None:
        return "\n".join(out)
    # alignment line
    out.append(gloss_lines[header_idx+1])
    # body
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    # append the rest (if any trailing sections)
    tail_start = header_idx + 2
    while tail_start < len(gloss_lines) and gloss_lines[tail_start].strip().startswith("|"):
        tail_start += 1
    out.extend(gloss_lines[tail_start:])
    return "\n".join(out)


def enhance_brief(term: str, current: str) -> str:
    if current and len(current) >= 10:
        return current
    if term in KNOW:
        return KNOW[term]
    # generic draft
    return (
        "草案：本书语境中常用术语，典型用途涵盖数据采集/存储/计算/分析/治理。"
        "建议结合上下文明确其边界与测试关注点（功能/性能/一致性/安全/可观测性）。"
    )


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    if not BOOK.exists():
        raise SystemExit(f"Book not found: {BOOK}")
    if not GLOSS.exists():
        raise SystemExit(f"Glossary not found: {GLOSS}")

    book_text = load_text(BOOK)
    gloss_text = load_text(GLOSS)
    gloss_lines, rows = parse_glossary_rows(gloss_text)

    terms = [r[0].strip() for r in rows if r and len(r) >= 5]
    freq = count_term_freq(book_text, terms)
    top50 = sorted(terms, key=lambda t: freq.get(t, 0), reverse=True)[:50]

    updated = 0
    new_rows: List[List[str]] = []
    for r in rows:
        if len(r) < 5:
            new_rows.append(r)
            continue
        term = r[0].strip()
        brief = r[4].strip()
        if term in top50:
            new_brief = enhance_brief(term, brief)
            if new_brief != brief:
                r[4] = new_brief
                updated += 1
        new_rows.append(r)

    new_text = write_glossary(gloss_lines, new_rows)
    GLOSS.write_text(new_text, encoding="utf-8")

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    report = REPORTS / f"glossary-enhance-{ts}.md"
    report.write_text(
        "\n".join([
            "# Glossary Enhancement Report",
            "",
            f"Top50 terms updated: {updated}",
        ]),
        encoding="utf-8",
    )
    print(f"Enhanced {updated} glossary entries. Report: {report}")

if __name__ == "__main__":
    main()
