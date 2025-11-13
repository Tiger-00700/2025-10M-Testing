# tools/ 目录说明与归档建议

本仓库已将 `book/1022.2025.newbook.md` 作为唯一的规范内容来源；工具链围绕以下流程：

- pipeline/build_all.ps1：一键运行（增强 newbook、生成附录、质量检查）
- pipeline/augment_book.ps1、generate_appendices.ps1、check_markdown.ps1：核心步骤的子命令

建议保留（核心）：

- pipeline/ 目录下的脚本（build_all、augment_book、generate_appendices、check_markdown 等）
- apply_markdown_autofixes、auto_apply_md036、generate_md013_patch*（配合质量修复）

建议观察/可选：

- 统计与报告类：inventory_*、consistency-report.*、emit_editorial_issues.py
- 书稿组织相关：organize_by_outline、update_latest（已由 CI 切换为 newbook-only，可按需启用）

建议归档/后续删除：

- tmp/ 目录（例如：tmp/write_ssh_config.ps1 为一次性脚本，可移除）

说明：当前变更以“最小风险”为原则，仅给出归档建议与分层说明，避免误删影响历史溯源或后续扩展。若确认无需保留，请在评审后删除对应脚本/目录。
