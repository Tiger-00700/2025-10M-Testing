# 测试案例设计清单（Chapter 14 配套）

## 一、范围与风险
- 明确业务关键指标与SLA/SLI；识别高风险路径与隐私合规点。
- 标注标签：risk:{high|medium|low}, privacy:{none|pseudonymized|masked}, pipeline:{batch|stream}。

## 二、合同与数据
- 在CI中校验Schema/Contract兼容性（backward/forward/full）。
- 合成数据：结构/分布拟合；固定seed与窗口/水位；指纹与水印可验证。
- 质量门：准确性/一致性/完整性/时效性阈值与阻断策略。

## 三、用例设计模式
- 等价类/边界值/判定表/组合测试；控制维度扩散（采样策略）。
- 变更驱动：Schema Diff、配置漂移、版本灰度发布与回滚验证。

## 四、可观测性与追踪
- 端到端追踪键：TraceID/BatchID/Watermark；日志、指标、告警分级。
- 报告输出：差异报告与审计线索归档到 tools/reports/。

## 五、自动化钩子
- contract 测试、质量门规则扫描、漂移比较脚本注册到CI/CD。
- 幂等与重放：固定seed/窗口/分区，确保复现与对比。

## 六、示例占位（可复制）
- UC-Contract: 路径=examples/06_ingest/batch_reconciliation.py；策略=backward；阈值=严格。
- UC-QualityGate: 数据门=P95延迟<=5s；准确性>=99.5%；阻断=开启。
- UC-DriftScan: 基线=commit abc123；比较=当前配置；输出=tools/reports/drift_diff.md。
