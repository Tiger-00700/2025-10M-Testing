# 发布准备与验证模板（必做，复制到发布 PR 描述）

## 3 条要点草稿

- > 【阅读提示】本章聚焦：发布准备与验证模板（必做，复制到发布 PR 描述）。建议先看结构，再带着问题阅读，关注关键术语、流程与案例，结合自身项目做对照。
- 目的：把"可复现性 + 验收证据"标准化，便于 reviewer 快速判定是否可定版。发布 PR 必须包含下列条目（或在 CI artifact 中自动填充）。
- 1) 发布 README/核验清单（PR 描述须包含） - 示例仓 URL 与 tag/commit（逐条列出）： - examples/03_environmentironment — repo: REPO_URL tag: TAG commit: SHA / runner: RUNNER - 附录 B/附录 E 中所有 Verified on 已填实 - 至少一次 smoke 运行日志链接（artifact）与运行命令（含 runner 信息） - markdownlint 报告（附件或 CI link） - HTML/PDF 预览链接（artifact） 2.

---

建议：对本章进行语言精简、添加 3 条要点小结与易错点说明。
