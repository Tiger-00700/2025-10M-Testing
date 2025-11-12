# MD013 行长（换行）建议索引

此索引列出由 `tools/generate_md013_patch2.py` 生成的保守换行建议（以 `.md013.suggest` 后缀写出的文件）。这些建议仅作为人工审阅的参考；它们不会覆盖原文件。请编辑按照下面的流程逐个审阅并决定是否接受。

审阅步骤（建议）
1. 在编辑器中打开原始文件（例如 `PR_DESCRIPTION.md`）与对应的建议文件（例如 `PR_DESCRIPTION.md.md013.suggest`）并对比。
2. 对于每处建议：
   - 若同意整文件建议，可将 `.md013.suggest` 的内容复制回原文件并提交到一个预览分支；
   - 若只接受部分 hunks，请手动拣选并合并到原文；
   - 若不接受，请在 review 注记并说明理由（例如保留原句以便印刷版排版更紧凑）。
3. 完成后请把决定记录在对应的 issue 模板（`tools/editorial-issues/` 下的 md013-... 文件），并把相关人设为 assignee。

推荐审阅顺序（优先级由高到低）：MD013 在目录和重要摘要段落处优先处理；随后按章节顺序处理正文细节。

建议索引（6 个建议文件）

- `PR_DESCRIPTION.md`  → `PR_DESCRIPTION.md.md013.suggest`
- `chapter/第1篇-第2章-大数据技术生态与架构.md`  → `chapter/第1篇-第2章-大数据技术生态与架构.md.md013.suggest`
- `chapter/第2篇-第3章-数据采集测试【进阶】.md`  → `chapter/第2篇-第3章-数据采集测试【进阶】.md.md013.suggest`
- `chapter/第2篇-第4章-数据存储测试【进阶】.md`  → `chapter/第2篇-第4章-数据存储测试【进阶】.md.md013.suggest`
- `chapter/第4篇-第13章-大数据系统可观测性与监控测试【进阶】.md`  → `chapter/第4篇-第13章-大数据系统可观测性与监控测试【进阶】.md.md013.suggest`
- `chapter/附录.md`  → `chapter/附录.md.md013.suggest`

希望这份索引能为编辑团队节省比对时间；如果你希望我把某些文件直接应用到预览分支（并生成 bundle）我可以在得到确认后做这一步。

---

文件生成说明：这些 `.md013.suggest` 文件由 `tools/generate_md013_patch2.py` 生成，位于仓库根路径或相应章节路径下。若需自动化应用，请告知我是否创建并运行一个“应用脚本”来把选定的 `.md013.suggest` 合并回原文件并提交为一个预览分支。
