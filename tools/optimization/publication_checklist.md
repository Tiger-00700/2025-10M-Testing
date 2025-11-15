**Phase3 — 出版校验与审阅清单（草案）**

目标：在发布前完成一套可执行的校验与审阅流程，确保稿件格式、示例与附录可复现、法律/版权合规、以及 CI/Artifact 验证到位。

一、稿件与格式校验
- Markdown 格式：运行 `markdownlint`（或 CI 的等效规则），修正 MD036/MD041/MD032 等常见警告。
- 标题层级：确保文件首行为 H1（书名或章标题），各章标题层级一致。
- 行尾/编码：文本文件保持 LF，Windows 脚本保持 CRLF。运行 `git ls-files -z | xargs -0 file`（手工核对）。
- 图片与浮动对象：所有图片/表格需存在于仓库并使用相对路径，图注说明清楚。

二、引用与版权
- 检查所有外部引用与引文，确保有明确来源和许可说明（必要时添加引用脚注）。
- 确认示例代码的第三方库许可，必要时在附录列出许可声明。

三、示例与附录可执行性
- 自动化 smoke：在 CI 或本地 runner 上运行 `tools/smoke_run_examples.py`，收集 `smoke_report.txt`。
- 验证 `examples/*` 中每个高优先级脚本的运行前置条件并在示例旁标注（`requirements.txt`、服务依赖）。
- 将外部系统依赖的示例标为 `EXTERNAL` 并在 README 中提供替代或 mock 指南。

四、元数据与发布工件
- 在 PR 描述中包含 `Verified-on` 信息（Runner / commit / artifact link）。
- 生成 HTML/PDF 预览并上传为 artifact 以供审阅。
- 附录 B 的工具清单需包含快速验证命令和 `Verified-on` 占位，发布前由 Owner 在 CI 上验证并填写。

五、CI 与发布流程
- CI Job 建议：`examples-smoke`（运行示例 smoke）、`markdown-lint`、`build-preview`（生成 HTML/PDF）、`artifact-uploader`。
- Smoke 失败策略：SKIPPED 不算失败（用标签区分），但 High-priority 示例必须通过 smoke。

六、审阅与发布检查表（Reviewer Checklist）
1. 是否存在未解析的内部链接？
2. 所有示例是否标注运行前提及依赖？
3. 所有代码片段是否已抽取到 `examples/`（或在附件中说明原因）？
4. 是否存在版权/许可冲突？
5. 是否生成并上传了 HTML/PDF 预览？
6. 是否在 PR 中包含至少一条 smoke 运行日志（artifact link）？

七、交付清单（PR 模板段落建议）
```
## 发布核验清单
- Examples repo: `<examples path>`
- Smoke log: `<artifact link>`
- Verified-on: `YYYY-MM-DD (runner) / repo:REPO_URL / tag:TAG / commit:SHA / artifact:ARTIFACT_PATH`
- MarkdownLint: `<artifact link>`
- HTML/PDF preview: `<artifact link>`
```

下一步（我可以执行）：
1. 运行仓库内的 markdownlint 并生成报告（若您允许我在本机或 CI runner 上执行）。
2. 基于 `examples/` 生成 `examples/requirements-review.txt` 聚合依赖清单。
