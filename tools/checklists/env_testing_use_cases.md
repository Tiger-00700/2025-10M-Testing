# Environment Testing & Automation Checklist

## Architecture & Baseline
- Map environments (dev/test/stage/preprod/prod/special drills) with data/perm/config parity notes; record RPO/RTO and key SLI/SLO.
- Define naming + tagging for clusters/regions/tenants; document baseline versions (platform/components), configs, sample data, permissions.
- For shadow/production-like data, confirm masking/sampling/consent and residency constraints.

## Multi-Cluster/Region Validation
- Cross-cluster/region replication: mode (full/inc/async/sync), RPO/RTO, encryption/key residency; run latency/loss reconciliation.
- Preprod parity: same region/spec as prod; validate critical pipelines end-to-end with delay/loss/error budgets.
- DR drills: failover/failback playbooks, traffic cutover rehearsal, key/credential rollover.

## IaC/GitOps Gates
- IaC plans linted/validated; policy-as-code for network/perms/KMS/IMDS settings; drift detection enabled.
- Pre-deploy checks: health of dependencies (metastore, queue, storage), schema/contract checks, quality gates on test data.
- Post-deploy smoke: service health, permission baselines, data contract reconciliation, SLI/SLO dashboards refreshed.

## Isolation, Quota, Cost
- Isolation controls: network ACL/security groups, namespace/queue/resource pool, KMS/key domains; verify no cross-env read.
- Quotas: CPU/mem/storage/bandwidth/concurrency/queue; approval + audit on changes; alert on overrun and budget burn.
- Cost guardrails: tag enforcement, idle cleanup, right-sizing suggestions; reports per env/tenant/team.

## Monitoring & Recovery
- Monitored: CPU/mem/disk/net, queue wait, job SLA, data delay/loss, config/perm drift, cert/key expiry, cost anomalies.
- Alerts: dedup/suppress, SLO-based (latency/loss/availability); runbooks linked.
- Backup/restore tested; snapshots per env; validate restores; RPO/RTO documented; periodic DR/fire drills.

## Validation Use Cases (can automate)
- UC1: Environment bootstrap via IaC → health check suite → contract/quality gate run → baseline report emitted.
- UC2: Cross-region pipeline → measure latency/loss → compare against SLO → auto ticket if breach.
- UC3: Permission baseline → run least-privilege matrix tests (tables/partitions/objects) → audit log check.
- UC4: Config drift scan → detect unauthorized changes → auto rollback or ticket.
- UC5: Backup/restore drill → recover to point-in-time → verify data/perm parity → log RPO/RTO achieved.
- UC6: Cost/quota guard → simulate peak load → ensure throttling/priority + alerting work; no spillover to prod.

## Automation Hints
- Wire UC1/UC3/UC4 into CI/CD pipelines; UC2/UC5/UC6 as scheduled patrols.
- Emit results to dashboards (Grafana/Prometheus) + ticket system; keep artifacts in `tools/reports/` with timestamps.
