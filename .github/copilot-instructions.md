
# 2025-10M-Testing Copilot 指南

## 项目概览
- **主书稿**：`book/1208.2025.newbook.md`（所有内容以此为源，增强版见 `book/1022.2025.newbook.augmented.md`）
- **构建输出**：生成的书稿、附录、代码/数据导出位于 `book/` 和 `examples/99_book_exports/`
- **附录/示例**：所有引用的脚本、数据、代码块均在 `appendix/` 和 `examples/` 下

## 架构与数据流
- **书籍构建流水线**：由 `tools/pipeline/` 下 PowerShell 脚本编排
  - `build_all.ps1` 执行：organize → augment → appendices → QA → export
  - 输出/日志均带时间戳，存于 `tools/reports/`
- **CI/CD**：`tools/` 下 Python 脚本校验引用资产、归档合规与报告完整性
  - `inventory_referenced_assets.py` 校验所有引用文件存在
  - `inventory_archive_status.py` 强制 `chapter/` 归档模式
  - `check_report_completeness.py`/`check_toc_consistency.py`/`strategy_hit_summary.py` 用于完整性、目录和治理校验
- **归档规范**：所有 `chapter/*.md` 须以 `<!-- markdownlint-disable MD025 -->` 开头，且用单一 `archived-content` 包裹旧内容

## 开发者工作流
- **全量构建（Windows PowerShell）：**
  ```powershell
  pwsh -NoLogo -NoProfile -File tools/pipeline/build_all.ps1
  ```
- **快速校验（Python）：**
  ```powershell
  python tools/inventory_referenced_assets.py
  python tools/inventory_archive_status.py
  ```
- **手动流水线步骤：**
  - Organize: `tools/pipeline/organize_by_outline.ps1`
  - Augment: `tools/pipeline/augment_book.ps1`
  - Appendices: `tools/pipeline/generate_appendices.ps1`
  - QA: `tools/pipeline/check_markdown.ps1`
- **模板/代码校验：**
  - `tools/validate_templates.py`、`tools/validate_contracts.py`、`tools/validate_quality_rules.py`（用法见 README）
- **导出代码块与冒烟测试：**
  ```powershell
  python tools/export_code_blocks.py
  python tools/run_exports_smoke.py
  ```
- **链接校验/修复（links-only book）：**
  ```powershell
  python tools/update_links_from_examples.py --dry-run --fail-on-ambiguous
  ```

## 项目约定与模式
- **换行符**：代码/文本用 LF，Windows 脚本用 CRLF（CI 检查但不阻断）
- **附录脚本**：须轻依赖、可在 CI 运行（见 `appendix/`）
- **链接**：所有 `examples/` 链接可用 `tools/update_links_from_examples.py` 自动校验修复
- **报告**：所有校验/构建脚本输出带时间戳，存于 `tools/reports/`
- **锚点/自动化**：所有“建议”“锚点”“自动”内容已标准化，详见 `appendix/锚点明细表.md` 和 `appendix/建议明细表.md`
- **模板**：SLI/SLO、契约、质量规则、审计清单、迁移/打分模板见 `examples/` 和 `tools/reports/templates/`
- **CI/CD**：治理、完整性、契约/质量校验全自动，结果见报告

## 关键文件与目录
- `book/` — 主书稿及生成内容
- `chapter/` — 归档旧章节（须遵循归档规范）
- `examples/`、`appendix/` — 引用脚本、数据、代码导出
- `tools/` — 构建、校验、CI 脚本
- `tools/pipeline/` — 流水线编排脚本
- `tools/reports/` — 所有构建/校验日志与报告

## 示例与模板
- **SLI/SLO 基线**：`examples/15_framework/sli_slo_baseline.yml`
- **审计工件清单**：`examples/18_cases/audit_artifacts_checklist.md`
- **契约/质量规则模板**：`examples/13_data_gov/contract_example.yml`、`examples/09_quality/quality_rules.yml`
- **治理/策略模板**：`examples/12_governance/`、`tools/reports/templates/drift_approval_form.md`
- **打分卡/迁移清单**：`examples/20_evolution/evaluation_scorecard.md`、`examples/20_evolution/migration_checklist.md`

## 故障排查与参考
- 架构、工作流、模板用法见 `README.md`
- 所有校验/构建失败均带时间戳，见 `tools/reports/`
- 如有不明约定，优先查阅根目录 `README.md` 和 `tools/README.md`（如有）

---

For any unclear or missing conventions, review the root `README.md` and `tools/README.md` for up-to-date workflow and policy details.
