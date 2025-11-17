# Module Design — Integration Architecture

## Purpose
Define standards and mechanisms for integrating external systems: CTI/dialers, BOT frameworks, social channels, email/SMS, logistics, internal portals, and regulatory portals (e.g., SEBI/IGMS).

## Scope
- Connector abstraction and provider adapters
- Authentication (OAuth2, API keys), secret handling
- Retry, backoff, idempotency, DLQ and replay
- Rate limiting and circuit breaking
- Regulatory interfaces and SLAs

## Responsibilities
- Normalize payloads to internal schemas
- Verify signatures and ensure message authenticity
- Provide observability and auditability per integration

## Connector Abstraction
- connectors(id, type, name, config_ref, enabled)
- connector_runs(id, connector_id, status, started_at, completed_at, error)
- dead_letters(id, connector_id, payload_json, error, created_at)

## Protocols and Security
- HTTPS REST with OAuth2 for social/BOT; signed webhooks with HMAC
- CTI via provider SDKs/APIs; SIP integrations as applicable
- Store secrets in vault/KMS; rotate regularly

## Reliability Patterns
- Exponential backoff with jitter and max retries
- Circuit breaker on persistent failure to protect upstreams
- Idempotency keys to prevent duplicate processing
- DLQ tables and replay utilities with supervision

## Rate Limits
- Per-connector and global quotas with 429 handling
- Token bucket or leaky bucket implementations at gateway

## Regulatory Portals (IGMS/SEBI)
- Complaint submission and status polling endpoints (server-to-server)
- SLA tracking and escalation rules aligned with regulator timelines
- Full audit trail of payloads and responses (no PII in logs)

## Observability
- Per-connector metrics: success/error rates, latency, throttling events
- Structured logs with correlation IDs
- Alerts on sustained failures and SLA risk

## Non-Functional Requirements
- Availability ≥ 99%; graceful degradation when providers are down
- End-to-end p95 latency budgets per integration

## Traceability
- RFP Annexure I/II: Dialer integration, voice blaster, social plugins, email/SMS, logistics; Information Security specifications
