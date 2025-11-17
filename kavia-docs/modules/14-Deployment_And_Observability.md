# Module Design — Deployment and Observability

## Purpose
Define environments, deployment and release workflows, and end-to-end observability (logs, metrics, traces, SLOs) to operate the CRM reliably.

## Scope
- Environments (dev, test, staging, prod)
- Build and deploy workflows; OpenAPI generation
- Logging/metrics/tracing baselines
- Alerts and runbooks

## Environments and Networking
- Isolated DBs and credentials per environment
- Backend connects to PostgreSQL over restricted network segments
- Frontend served statically via CDN/edge (future consideration)

## Deployment
- Backend: FastAPI app (src/api/main.py), OpenAPI export tool (src/api/generate_openapi.py)
- Database: startup.sh initializes DB, backup_db.sh and restore_db.sh for DR
- Frontend: React SPA, CI builds and static deploy

## Observability
- Logs: Structured JSON, correlation IDs; no PII
- Metrics: latency (p50/p95), error rate, SLA breach counts, queue depths, connector health
- Traces: OpenTelemetry planned
- Dashboards for auth, 360, SR/complaints, connectors, DB health

## SLOs and Alerts
- Auth p95 < 300ms; 360 p95 < 600ms; 99.5% availability
- Alerts on SLO errors, sustained 5xx, connector failures, DB replication lag
- Paging policies and escalation matrix

## Runbooks
- OpenAPI regen and contract checks
- Backup/restore validation
- Connector outage handling (circuit breaker, replay DLQ)
- DR failover steps and verification

## Traceability
- RFP: HA/DR, monitoring, SLAs and governance
