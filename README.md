# 大数据全栈测试：从理论到实战

![TOC & Templates CI](https://github.com/<owner>/<repo>/actions/workflows/toc-check.yml/badge.svg)

- Canonical manuscript: book/1208.2025.newbook.md
- Full build: pwsh -NoLogo -NoProfile -File tools/pipeline/build_all.ps1
- Quick validation: python tools/inventory_referenced_assets.py && python tools/inventory_archive_status.py

## 目录（1208 重组版）
- 第一篇 大数据测试基础（入门）
    - 第1章 大数据与大数据系统概述【入门】
    - 第2章 大数据测试概念与目标【基础篇】
    - 第3章 大数据技术生态与架构基础【技术基础篇】
    - 第4章 大数据测试环境搭建基础【环境与运维篇】
    - 第5章 大数据测试数据管理基础【数据管理篇】
- 第二篇 大数据测试方法与技术（进阶）
    - 第6章 数据采集测试【采集与链路起点】
    - 第7章 数据存储与持久化测试【存储与可靠性篇】
    - 第8章 数据处理与计算测试【计算与作业篇】
    - 第9章 数据质量管理与测试【质量保障篇】
    - 第10章 大数据安全与合规测试【安全与合规篇】
    - 第11章 数据分析与可视化测试【分析与洞察篇】
- 第三篇 环境与数据治理（进阶）
    - 第12章 企业级大数据测试环境实践【环境工程与自动化】
    - 第13章 测试数据治理与生命周期管理【数据治理与可复现性】
    - 第14章 数据契约、语义层与指标目录/血缘治理【治理到自动化的桥接】
- 第四篇 自动化、工具与可观测性（进阶）
    - 第15章 契约驱动的自动化基础【原则与成熟度】
    - 第16章 大数据测试自动化框架设计【工程化与平台化】
    - 第17章 大数据测试工具与平台【工具与平台篇】
    - 第18章 大数据系统可观测性与监控测试【可观测性与运维保障】
- 第五篇 案例与性能（专家）
    - 第19章 通用大数据测试案例设计【方法与模板篇】
    - 第20章 行业大数据测试案例分析【行业篇】
    - 第22章 流批一体链路端到端案例【采存算全链路实战】
    - 第24章 大规模数据处理性能与容量测试实践【性能与容量篇】
- 第六篇 项目与治理（专家）
    - 第21章 大数据测试项目实施与实战经验【项目管理与团队协作】
    - 第23章 跨云/混合云迁移与演练案例【迁移与韧性】
    - 第25章 CI/CD、GitOps 与运维治理中的测试角色【自动化与治理篇】
- 第七篇 趋势与平台化（专家）
    - 第26章 技术与方法演进【趋势与未来篇】
    - 第27章 大数据测试人才与职业发展【成长与进阶篇】
    - 第28章 全链路质量平台与工具链实战【平台与工程篇】

### 建议阅读路径
- 入门：第1–5章 → 第6–8章的对应场景
- 进阶：第9–11章 → 第14–18章（契约/自动化/可观测）
- 专家：第19–25章按两篇主题选读 → 第26–28章做规划与平台落地

注：目录中的括注（如“第15章（原15章整合）”）仅为说明性提示，不属于正式章节标题；正文以精简标题为准。

## 模板与示例
- **SLI/SLO 基线模板**：examples/15_framework/sli_slo_baseline.yml
    - 用途：定义服务/数据管道的核心 SLI（可用性、时延、鲜度等）与 SLO（目标与误差预算），并指明度量来源与报告输出。
    - 快速使用：复制到你的案例目录，按需调整 `subject`、`slis`、`slos` 与 `reporting` 输出路径。
- **审计工件清单（模板）**：examples/18_cases/audit_artifacts_checklist.md
    - 用途：项目评审与合规核查的统一检查清单，覆盖指标目录/血缘、数据契约、语义层、质量规则、安全与访问控制、回放对账等。
    - 快速使用：复制并在每项下附“证据链接/报告”，作为评审材料。

### 平台化 KPI 与报告索引
- 预发布聚合报告：`pre_release_check_YYYYMMDD-HHMMSS.md`
- 对账与采样报告：`report_diff_*`、`ingest_*`
- 审计与评估：`templates/`（审计模板）与 `examples/20_evolution/`（评估打分/迁移清单）

- CI 联动（toc-check 工作流）：
    - 生成治理“策略命中摘要”：`python tools/strategy_hit_summary.py`
    - 预发布聚合（嵌入治理摘要）：`python tools/pipeline/pre_release_check.py`
    - 完备性门控：`python tools/check_report_completeness.py`（阈值环境变量 `COMPLETENESS_THRESHOLD=0.6`）
    - 其他：目录一致性、模板/契约/质量规则校验，示例 diff 生成

- 新增联动说明：
    - 环境工程与治理（见 第4篇-第12章）：工具链联动 IaC 基线、环境健康与漂移检查（examples/12_env、12_env_iac），治理模板（examples/12_governance），报告四段结构与完备性门控。
    - 可观测性与治理联动（见 第4篇-第13章）：信号标准化 → 统一报告 → 策略命中摘要 → 容差与完备性门控（tools/report_diff.py、tools/check_report_completeness.py）。
    - 人才与发展（见 第6篇-第21章）：L1–L5能力模型、评估表（examples/20_evolution/evaluation_scorecard.md）、与报告KPI绑定的CI阈值与豁免流程。

- **审计工件评估报告（模板）**：tools/reports/templates/audit_artifact_report.md
    - 用途：将清单与证据汇总为评估报告，沉淀发现、结论与签署记录。
    - 快速使用：按评审窗口填写并归档到 tools/reports/。
 - **数据契约（最小示例）**：examples/13_data_gov/contract_example.yml
     - 用途：定义入仓/消费的字段、约束、分区与质量门；包含版本与破坏性变更标记。
     - 快速使用：复制并根据业务字段与约束调整；配合 `tools/validate_contracts.py` 校验。
 - **质量规则（最小示例）**：examples/09_quality/quality_rules.yml
     - 用途：声明约束/分布类质量规则、阈值与失败处理策略。
     - 快速使用：复制并按数据域补充；配合 `tools/validate_quality_rules.py` 校验。
 - **治理策略模板（示例）**：
     - 访问控制与门禁策略：examples/12_governance/policy_access_control.md
     - 变更冻结与豁免：examples/12_governance/change_freeze_waiver.md
    - 漂移/审批/豁免表单：tools/reports/templates/drift_approval_form.md
 - **技术评估打分表（模板）**：examples/20_evolution/evaluation_scorecard.md
     - 用途：对候选技术/方案进行多维打分（适配度、复杂度、生态、可观测、成本与风险、安全与合规），用于采纳决策与金丝雀试点评估。
     - 快速使用：复制并按权重与评分标准调整，配合 `tools/report_diff.py` 以报告方式固化试点结果。
 - **迁移清单（模板）**：examples/20_evolution/migration_checklist.md
     - 用途：迁移过程的关键步骤与风险控制（资产清点、双写与对账、兼容层、回滚与退出、验证与报告、审批与豁免）。
     - 快速使用：在迁移方案与执行前置阶段填写，并将验证报告归档到 tools/reports/。

### 本地快速操作
```powershell
# 复制模板到案例或报告路径
Copy-Item examples/15_framework/sli_slo_baseline.yml .\examples\18_cases\sli_slo_baseline.yml
Copy-Item tools/reports/templates/audit_artifact_report.md .\tools\reports\audit_artifact_report_$(Get-Date -Format yyyyMMdd).md

# 运行模板/契约/质量规则校验
E:/DONT_TOUCH/10M-2025-Testing/.venv311/Scripts/python.exe -m pip install pyyaml
E:/DONT_TOUCH/10M-2025-Testing/.venv311/Scripts/python.exe tools/validate_templates.py
E:/DONT_TOUCH/10M-2025-Testing/.venv311/Scripts/python.exe tools/validate_contracts.py
E:/DONT_TOUCH/10M-2025-Testing/.venv311/Scripts/python.exe tools/validate_quality_rules.py

# 运行目录一致性检查（已接入 CI）
E:/DONT_TOUCH/10M-2025-Testing/.venv311/Scripts/python.exe tools/check_toc_consistency.py
```
