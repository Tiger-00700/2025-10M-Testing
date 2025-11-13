#!/usr/bin/env python3
"""Generate reference topology among book/*.md files.

Scans all markdown files under book/ (top-level .md) and finds markdown links
whose target path includes 'book/' and ends with a .md filename. Produces:
    - tools/reports/book-reference-topology-<ts>.md (adjacency list, stats)
    - tools/reports/book-reference-topology-<ts>.dot (Graphviz DOT)

Edges: source_file -> target_file (filename only). Self-links ignored.

Optional: transitive closure from a given file using --from with --direction
(out/in/both) and --max-depth. Outputs closure MD and DOT alongside
the main reports.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import re
import argparse

ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / 'book'
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

def extract_book_links(text: str) -> set[str]:
    targets: set[str] = set()
    for m in LINK_RE.finditer(text):
        raw = m.group(1).strip()
        raw = raw.split('#',1)[0].split('?',1)[0]
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', raw):  # skip absolute schemes
            continue
        t = raw.replace('\\','/')
        parts = [p for p in t.split('/') if p]
        if 'book' not in parts:
            continue
        if not t.lower().endswith('.md'):
            continue
        from pathlib import Path as _P
        name = _P(t).name
        targets.add(name)
    return targets

def build_graph() -> tuple[
    dict[str, set[str]],
    dict[str, set[str]],
    list[Path],
]:
    files = sorted([p for p in BOOK_DIR.glob('*.md') if p.is_file()])
    adjacency: dict[str, set[str]] = {}
    for f in files:
        text = f.read_text(encoding='utf-8')
        targets = extract_book_links(text)
        fname = f.name
        adjacency[fname] = set(t for t in targets if t != fname)
    # Reverse adjacency
    reverse: dict[str, set[str]] = {f.name:set() for f in files}
    for src, tgts in adjacency.items():
        for t in tgts:
            reverse.setdefault(t, set()).add(src)
    return adjacency, reverse, files

def compute_closure(
    start: str,
    graph: dict[str, set[str]],
    max_depth: int,
) -> dict[str, int]:
    # BFS to compute minimal depth to each reachable node
    depth: dict[str,int] = {}
    frontier = [(start, 0)]
    seen = {start}
    while frontier:
        node, d = frontier.pop(0)
        if node != start:
            depth[node] = d
        if d >= max_depth:
            continue
        for nxt in sorted(graph.get(node, set())):
            if nxt not in seen:
                seen.add(nxt)
                frontier.append((nxt, d+1))
    return depth

def main() -> int:
    desc = (
        'Generate book reference topology and optional closure reports.'
    )
    ap = argparse.ArgumentParser(description=desc)
    help_from = (
        'Start filename (e.g., 1022.2025.newbook.cleaned.md) for closure report'
    )
    ap.add_argument('--from', dest='from_file', help=help_from)
    help_dir = 'Closure direction: out (default), in (reverse), both'
    ap.add_argument(
        '--direction',
        choices=['out', 'in', 'both'],
        default='out',
        help=help_dir,
    )
    ap.add_argument(
        '--max-depth',
        type=int,
        default=999,
        help='Max depth for closure (default: 999)',
    )
    args = ap.parse_args()

    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    reports = ROOT / 'tools' / 'reports'
    reports.mkdir(parents=True, exist_ok=True)
    md_out = reports / f'book-reference-topology-{ts}.md'
    dot_out = reports / f'book-reference-topology-{ts}.dot'

    adjacency, reverse, files = build_graph()

    # Compute reverse edges & stats
    in_deg: dict[str,int] = {f.name:0 for f in files}
    for src, tgts in adjacency.items():
        for t in tgts:
            if t in in_deg:
                in_deg[t] += 1
    out_deg: dict[str,int] = {f: len(adjacency.get(f, set())) for f in in_deg}

    lines = [f'# Book Reference Topology ({ts})','']
    lines.append('## Adjacency List')
    for f in sorted(adjacency.keys()):
        tlist = sorted(adjacency[f])
        tstr = ", ".join(tlist) if tlist else "(none)"
        lines.append(f'- {f}: {tstr}')
    lines.append('')
    lines.append('## Degree Stats')
    lines.append('| File | Out-Degree | In-Degree |')
    lines.append('|------|-----------:|----------:|')
    for f in sorted(in_deg.keys()):
        lines.append(f'| {f} | {out_deg[f]} | {in_deg[f]} |')
    lines.append('')
    # Identify isolated files (no in or out edges)
    isolated = [f for f in in_deg if in_deg[f]==0 and out_deg[f]==0]
    if isolated:
        lines.append('## Isolated Files')
        for f in isolated:
            lines.append(f'- {f}')
        lines.append('')

    # Cycle detection (simple DFS for directed cycles)
    def find_cycles(graph: dict[str,set[str]]) -> list[list[str]]:
        """Detect directed cycles (normalized rotation) in a graph.

        This function was defined earlier in the file as well; keep a single
        canonical implementation to avoid mypy 'redefinition' warnings.
        """
        cycles: list[list[str]] = []
        path: list[str] = []
        visited: set[str] = set()
        in_path: set[str] = set()

        def dfs(node: str) -> None:
            visited.add(node)
            path.append(node)
            in_path.add(node)
            for nxt in graph.get(node, set()):
                if nxt not in visited:
                    dfs(nxt)
                elif nxt in in_path:
                    # Found a cycle; extract subpath
                    try:
                        idx = path.index(nxt)
                        cycle = path[idx:] + [nxt]
                        # Normalize rotation based on smallest string to avoid
                        # duplicates
                        min_idx = min(range(len(cycle)-1), key=lambda i: cycle[i])
                        norm = cycle[min_idx:-1] + cycle[:min_idx] + [cycle[min_idx]]
                        if norm not in cycles:
                            cycles.append(norm)
                    except ValueError:
                        pass
            in_path.remove(node)
            path.pop()

        for n in graph.keys():
            if n not in visited:
                dfs(n)
        return cycles

    cycles = find_cycles(adjacency)
    if cycles:
        lines.append('## Detected Cycles')
        for cyc in cycles:
            lines.append('- ' + ' -> '.join(cyc))
        lines.append(f'\nTotal cycles: {len(cycles)}')
    else:
        lines.append('## Detected Cycles')
        lines.append('- None')
        lines.append('')
    md_out.write_text('\n'.join(lines)+'\n', encoding='utf-8')

    # DOT output
    dot_lines = ['digraph book_refs {']
    dot_lines.append('  rankdir=LR;')
    for f in sorted(adjacency.keys()):
        if not adjacency[f]:
            dot_lines.append(f'  "{f}";')
        for t in sorted(adjacency[f]):
            dot_lines.append(f'  "{f}" -> "{t}";')
    dot_lines.append('}')
    dot_out.write_text('\n'.join(dot_lines)+'\n', encoding='utf-8')

    # Cycle detection (simple DFS for directed cycles)
    # Optional closure reports
    if args.from_file:
        start = Path(args.from_file).name
        if start not in in_deg:
            print(f"WARN: start file not found in book dir: {start}")
        else:
            want_out = args.direction in ('out','both')
            want_in = args.direction in ('in','both')
            if want_out:
                out_depths = compute_closure(start, adjacency, args.max_depth)
                md_clo = reports / f'book-ref-closure-out-{start}-{ts}.md'
                lines = [
                    '# Reference Closure (out) for ' + start +
                    ' (max-depth=' + str(args.max_depth) + ')',
                    '',
                ]
                for node, d in sorted(out_depths.items(), key=lambda kv:(kv[1],kv[0])):
                    lines.append(f"{'  '*d}- {node} (depth {d})")
                md_clo.write_text('\n'.join(lines)+'\n', encoding='utf-8')
                dot_clo = reports / f'book-ref-closure-out-{start}-{ts}.dot'
                dotc = ['digraph closure_out {','  rankdir=LR;']
                for src, tgts in adjacency.items():
                    if src==start or src in out_depths:
                        for t in tgts:
                            if t in out_depths or src==start:
                                dotc.append(f'  "{src}" -> "{t}";')
                dotc.append('}')
                dot_clo.write_text('\n'.join(dotc)+'\n', encoding='utf-8')
            if want_in:
                in_depths = compute_closure(start, reverse, args.max_depth)
                md_clo = reports / f'book-ref-closure-in-{start}-{ts}.md'
                lines = [
                    '# Reference Closure (in) for ' + start +
                    ' (max-depth=' + str(args.max_depth) + ')',
                    '',
                ]
                for node, d in sorted(in_depths.items(), key=lambda kv:(kv[1],kv[0])):
                    lines.append(f"{'  '*d}- {node} (depth {d})")
                md_clo.write_text('\n'.join(lines)+'\n', encoding='utf-8')
                dot_clo = reports / f'book-ref-closure-in-{start}-{ts}.dot'
                dotc = ['digraph closure_in {','  rankdir=LR;']
                for src, tgts in reverse.items():
                    if src==start or src in in_depths:
                        for t in tgts:
                            if t in in_depths or src==start:
                                dotc.append(f'  "{src}" -> "{t}";')
                dotc.append('}')
                dot_clo.write_text('\n'.join(dotc)+'\n', encoding='utf-8')

    # cycles and highlighted DOT already produced above

    # Strongly Connected Components (Tarjan)
    index = 0
    stack: list[str] = []
    onstack: set[str] = set()
    indices: dict[str,int] = {}
    lowlink: dict[str,int] = {}
    sccs: list[list[str]] = []
    def strongconnect(v: str):
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        onstack.add(v)
        for w in adjacency.get(v, set()):
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in onstack:
                lowlink[v] = min(lowlink[v], indices[w])
        if lowlink[v] == indices[v]:
            comp = []
            while True:
                w = stack.pop()
                onstack.remove(w)
                comp.append(w)
                if w == v:
                    break
            sccs.append(sorted(comp))
    for v in adjacency.keys():
        if v not in indices:
            strongconnect(v)

    # SCC report and DAG
    scc_md = ['# Strongly Connected Components','']
    for i, comp in enumerate(sorted(sccs, key=lambda c:(-len(c), c)) , start=1):
        label = f'C{i}'
        scc_md.append(f'- {label}: size={len(comp)} -> ' + ', '.join(comp))
    scc_md_path = reports / f'book-reference-scc-{ts}.md'
    scc_md_path.write_text('\n'.join(scc_md)+'\n', encoding='utf-8')

    # Build component map and DAG edges
    comp_index: dict[str,int] = {}
    for i, comp in enumerate(sccs):
        for n in comp:
            comp_index[n] = i
    dag_edges: set[tuple[int,int]] = set()
    for src, tgts in adjacency.items():
        csrc = comp_index[src]
        for t in tgts:
            cdst = comp_index[t]
            if csrc != cdst:
                dag_edges.add((csrc, cdst))
    # DOT DAG
    dag = ['digraph scc_dag {','  rankdir=LR;','  node [shape=box];']
    for i, comp in enumerate(sccs, start=0):
        label = f'C{i+1}\n' + '\n'.join(comp)
        style = 'style=filled, fillcolor=lightyellow' if len(comp)>1 else ''
        dag.append(f'  "C{i+1}" [label="{label}" {style}];')
    for a,b in sorted(dag_edges):
        dag.append(f'  "C{a+1}" -> "C{b+1}";')
    dag.append('}')
    dag_path = reports / f'book-reference-dag-{ts}.dot'
    dag_path.write_text('\n'.join(dag)+'\n', encoding='utf-8')

    print(f'Topology reports written: {md_out.name}, {dot_out.name}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
