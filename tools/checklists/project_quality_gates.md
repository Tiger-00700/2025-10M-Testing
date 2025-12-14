# 项目质量门清单（第21章配套）

## 目标
- 将合同/质量/性能/安全/合规/成本六类门前置到项目节奏，阻断高风险发布。

## 清单结构
- 门ID/类型：Contract | Quality | Performance | Security | Compliance | Cost
- 信号来源：脚本/指标/日志/追踪/告警/外部报告。
- 阈值与策略：阻断/警告；豁免流程与有效期。
- 责任人：R/A/C/I；通知渠道与值班信息。
- 证据：报告路径（tools/reports/...）、日志/截图、工单链接。

## 示例占位
- Contract: Schema 兼容性扫描（阻断），信号=contract_check.md，Owner=数据/测试。
- Quality: P95 延迟<=5s，准确率>=99.5%（阻断），信号=quality_gate_scan.md。
- Security: AuthN/AuthZ/审计/脱敏巡检（警告→阻断），信号=security_patrol.md。
- Compliance: 驻留/跨境/主体权利检查（阻断），信号=合规策略扫描输出。
- Cost: 成本/GB 超阈值告警（警告），信号=成本报表或监控。

## 流程
- 在每次发布/灰度前执行门检查，未通过则阻断或降级；豁免需审批并留档。
- 将门结果写入 automation_summary.md；高风险项自动生成工单。