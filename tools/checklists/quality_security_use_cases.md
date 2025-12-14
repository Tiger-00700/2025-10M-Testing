# Quality & Security Use Case Checklist

## Data Quality Core
- Contract/Schema: schema registry compatibility (backward/forward), required fields present, enum/range/regex, timezone/encoding.
- Reconciliation: source→target row/partition counts, hash/sample diff, stream vs batch parity, idempotency and dedupe.
- Completeness/Duplicates: NULL/default spikes, missing partitions/batches, duplicate keys/partitions, misrouted partitions.
- Timeliness/Freshness: end-to-end latency vs SLA/SLO, late arrival ratio, watermark/window alignment, backlog growth.
- Anomalies/Drift: distribution/quantile/boxplot, trend break, seasonality deviation, schema/metric drift alerts.
- Quality Gates & Alerts: pre-deploy contract test, scheduled rules, dynamic baselines, alert dedupe/suppression, runbook link.
- RCA & Fix: lineage + recent changes, replay/backfill scripts, compensation outputs, rollback notes and change log.

## Security & Compliance Core
- Identity & Auth: MFA/strong auth, ticket lifetime, replay/session fixation checks, service-account rotation and scoping.
- Authorization/Least Privilege: role/user/job matrices, grant/inherit/revoke flow with audit, row/column masking, multi-tenant isolation.
- Encryption & Key Management: TLS1.2+ in transit, at-rest/KMS enabled, key rotation/expiry/revocation, plaintext leak scan (logs/tmp/export).
- Masking/Tokenization: irreversible masking types, consistent tokenization for joins, automatic policy inheritance on new tables/partitions, synthetic data viability.
- Audit & Logging: subject/object/time/source/result recorded, immutability (WORM/signature), retention/backups, anomaly alerting and ticketing.
- Compliance & Residency: data minimization, consent lifecycle, subject rights (access/export/delete/correct/freeze), residency/cross-border controls, evidence pack.
- Resilience & DR: backup/restore RPO-RTO drills, cross-region copy controls, key-leak/credential-loss playbooks, failover and rollback tests.

## Automation Hooks
- CI/CD: auto-run contract/quality gates and security baselines on new tables/partitions/jobs before deploy.
- Scheduled Patrols: periodic regression of quality rules, permission drift check, key/secret expiry scan, audit log gap detection.
- Reporting: SLI/SLO dashboards for quality and security, exception trend reports, unresolved issue backlog with owners.
