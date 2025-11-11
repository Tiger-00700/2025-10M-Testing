```markdown
# 优先级修复清单（缺失示例）

生成时间：2025-11-11

来源：`tools/reports/inventory-assets-20251110-162958.md`

概述：以下为基于 inventory 报表与已有缺失列表整理的优先级修复建议。每项包含是否在仓库中已存在（目录）、是否被书稿引用、建议的修复动作、优先级与估算工作量。

## 汇总表

| reference | exists_in_repo | referenced_in_book | priority | effort_estimate | suggested_action |
|---|---:|---:|---:|---:|---|
| examples/01_ecosystem | yes | yes | High | M (3-6h) | Create skeleton: `README.md`, `smoke.sh`/`smoke.ps1`, add one demo script (overview.md or demo.sh). |
| examples/07_batch | yes | yes | Medium | S (1-2h) | Create skeleton: `README.md`, simple batch example script (batch_demo.sh) and smoke script. |
| examples/08_analysis | yes | yes | High | M (3-6h) | Add EDA examples (e.g., `eda_pandas.py`), README and `requirements.txt`; ensure smoke test runs. |
| examples/10_tdms | yes | yes | Low | S (1-2h) | Create skeleton README + smoke script; add placeholder TDMS notes. |
| examples/11_automation | yes | yes | Medium | M (3-6h) | Add CI/automation snippets: pipeline sample, simple automation script, smoke test. |
| examples/17_practices | yes | yes | Low | S (1-2h) | Create README and short practice example(s); smoke script optional. |
| examples/18_performance | yes | yes | Medium | L (6-12h) | Add performance test harness (small JMH/locust/Spark example), README and smoke script. |
| examples/20_trends | yes | yes | Low | S (1-2h) | Create README and a short trends-analysis example (script + sample data). |
| examples/21_career_paths | yes | yes | Low | S (1-2h) | Create README and narrated examples or links (non-code); minimal smoke script. |

## 评分与说明
- "exists_in_repo" 列基于当前仓库目录结构（`examples/` 下存在对应目录）的快速检查。即：目录已存在，但书稿/导出流程仍将其标记为 placeholder（可能因为缺少 `.skeleton`、`README.md` 或 smoke test）。
- 优先级建议基于：书稿章节重要性（如生态/分析章节优先）、inventory 中的出现/引用频次，以及面向读者的实用性。
- 估算工作量为粗略预估，实际所需时间取决于示例的完备度与数据需求。

## 建议的短期动作（低风险、快速回报）
1. 为每个缺失目录生成最小 skeleton：
   - `examples/<name>/README.md`（一句话说明 + 运行方式）
   - `examples/<name>/smoke.sh`（跨平台可选：`smoke.ps1` 与 `smoke.sh`，只需打印成功或运行一个 tiny demo）
   - 可选：`examples/<name>/.skeleton/` 放入示例模板
2. 在 CI workflow 中临时设 `INVENTORY_FAIL_ON_MISSING=0` 以避免立即阻断 pipeline（保留报告写入）。
3. 对 `examples/08_analysis` 内添加至少一个可运行脚本（已存在 `eda_pandas.py` 的话，确保 `requirements.txt` 在 per-example requirements 中列出 `pandas` 并且 smoke script 安装并运行该脚本）。

## 建议的长期动作（质量更高）
- 对 High/Medium 项（尤其 `01_ecosystem`, `08_analysis`, `11_automation`, `18_performance`）分配开发者逐条实现：
  - 增加真实示例代码、必要的 sample data（或生成脚本）、README 的用例、以及自动化 smoke test。
  - 为每个示例补充 `requirements.txt` 或在 central requirements 列表中声明依赖，以方便 CI 安装。

## 下一步（我可以为你执行）
- 我可以自动为所有 Low/Medium 项生成 minimal skeleton 文件并提交到一个新分支（含 README + smoke scripts）。
- 我可以把 `INVENTORY_FAIL_ON_MISSING=0` 的变更以 patch 形式提交到 CI workflow（短期 unblock）。
- 我可以针对 High 优先级项生成更完整的示例实现（例如把 `eda_pandas.py` 的完善版和 `requirements.txt` 一并提交）。

如果你同意，我将把 `missing_examples_priority.csv` 与本文件加入版本控制并提交到新分支（默认分支名建议 `chore/missing-examples-placeholders`），然后创建 PR 草稿并在 PR 描述中附上本报告。请确认是否要：

- 仅生成并保存报告（当前已完成），或
- 生成 minimal skeleton 并提交为 PR（我会在开始前再次说明要做哪些文件/格式）。

## 已执行更新（2025-11-11）

2025-11-11: 已在仓库中为四个 High/Medium 优先级项添加 Minimal Runnable 占位示例并提交到分支 `feat/add-high-priority-examples`（草稿 PR: https://github.com/Tiger-00700/2025-10M-Testing/pull/24）。

已变更项（占位实现）:
- `examples/01_ecosystem` — 添加 `README.md`, `demo.py`, `smoke.sh`, `smoke.ps1`（可打印 Python 版本与平台）。
- `examples/08_analysis` — 添加 `README.md`, `sample.csv`, `analyze.py`, `smoke.sh`, `smoke.ps1`（示例使用 CSV 并输出统计摘要）。
- `examples/11_automation` — 添加 `README.md`, `ci_demo.ps1`, `smoke.sh`, `smoke.ps1`（演示最小自动化步骤）。
- `examples/18_performance` — 添加 `README.md`, `benchmark.py`, `smoke.sh`, `smoke.ps1`（简单 micro-benchmark）。

说明：这些占位示例旨在满足 CI smoke-tests 的最小要求，使 inventory 报表能继续生成并减少噪音。它们不是最终示例；后续应按优先级逐步增强为完整可教学的示例。

PR 与 issue 跟踪：
- Draft PR: https://github.com/Tiger-00700/2025-10M-Testing/pull/24 （分支：`feat/add-high-priority-examples`）
- 相关 Issue 已创建（编号示例）：`examples/01_ecosystem` (#15), `examples/08_analysis` (#17), `examples/11_automation` (#19), `examples/18_performance` (#21)。我会在这些 issue 下留下状态评论并附上 PR 链接（见仓库 issue）。

建议的下一步：在 triage 后将这些 issue 指派给责任人以完善例子；待真实示例合入后移除 CI 的 `INVENTORY_FAIL_ON_MISSING` 覆盖。

```
