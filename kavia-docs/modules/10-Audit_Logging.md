# Module Design — Audit Logging

## Purpose
Create immutable audit trails for sensitive and operational actions across the platform.

## Scope
- Append-only logging of security and business events
- Optional hash chaining for tamper-evidence

## Responsibilities
- Persist logs, ensure integrity, and provide search interfaces

## Data Models
- audit_logs(id, actor_id, action, entity_type, entity_id, diff_json, ip, user_agent, created_at)
- audit_hash_chain(id, log_id, prev_hash, curr_hash) (optional)

## APIs
- GET /audit?filters (restricted)
- Admin export endpoints for audits

## Error Handling
- Fallback buffer if DB unavailable
- Backpressure and batch inserts

## Security & Compliance
- No PII in audit messages; references by IDs
- Access restricted to auditors/admins; complete journaling

## Non-Functional Requirements
- Write-optimized inserts
- Retention and archival policies

## Traceability
- RFP: Full audit and compliance readiness

## Repository References
- Backend baseline: crm_backend/src/api/main.py
- Database operations and backup policies: crm_database/startup.sh, backup_db.sh, restore_db.sh
