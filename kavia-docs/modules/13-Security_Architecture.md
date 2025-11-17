# Module Design — Security Architecture

## Purpose
Satisfy SEBI and internal information security directives by implementing robust controls across access, session, data, application, and infrastructure layers, including offline/mobile.

## Scope
- RBAC and SoD; maker-checker
- Session and token security; MFA readiness
- Data security (at rest/in transit), DLP
- Network and platform security; VA/PT readiness
- Logging, monitoring, SIEM integration
- Backup, DR, and BCP

## Access Management
- Password policy configurable (history, max age, complexity, lockout)
- 2FA for admin and privileged operations
- Directory integration (LDAP/AD) and SSO capability
- Role/permission matrices with SoD and least privilege

## Session Management
- Short-lived JWT access tokens; rotating refresh tokens
- Configurable session timeout; prevent concurrent sessions for the same user ID where mandated
- TLS termination with strong ciphers; HSTS
- Token revocation/blacklist on logout

## Data Security
- Encryption at rest (disk + field-level for PII)
- Encryption in transit (TLS 1.2+)
- Mask PII from logs/exports; field-level masking per role
- Idempotent API handling to prevent replay abuse

## Network Security
- Segmented networks (frontend, backend, database)
- WAF, firewall rules, DDoS controls where applicable
- SIEM integration; incident management with 2-hour notification SLA (per RFP)

## Hardening and Patching
- OS/DB/Application patch windows; documented periodicity
- VA/PT cadence and remediation SLAs
- Secure defaults; no plaintext secrets in repos

## Logging and Audit Trail
- Append-only audit logs for sensitive operations
- Unique error codes, structured logs with correlation IDs
- Retention policies and export for auditors (restricted access)

## Backup and DR
- Periodic backups (daily full, hourly WAL/incremental)
- Tested restore runbooks (restore_db.sh)
- RPO ≤ 15 minutes; RTO ≤ 2 hours (target)

## Mobile and Offline
- Encrypted local storage; remote wipe capability
- Role-based offline data provisioning; minimal footprint
- Session and device posture checks (e.g., jailbreak/root detection)

## Non-Functional Requirements
- 99.5% availability target; no single point of failure
- Minimal overhead of security controls on core flows

## Traceability
- RFP Information Security Specifications (Access, Session, Data, Network, Logging, Patching, Backup/DR, Mobile)
