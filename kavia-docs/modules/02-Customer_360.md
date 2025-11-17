# Module Design — Customer 360

## Purpose
Provide a unified 360-degree view of customer data across accounts, interactions, tickets, and insights.

## Scope
- Identity resolution by customer_id/phone/email
- Aggregation of profile, contact points, interactions, open SRs and complaints
- KPI computation and context signals

## Responsibilities
- Orchestrate reads from CRM DB and integrations
- Enforce field-level security and masking for PII

## Inputs and Outputs
- Input: customer_id, phone, or email
- Output: Customer360 DTO including profile, relationships, interactions, open items, KPIs

## Data Models
- customers, contact_points, interactions, relationships, service_requests, complaints

## APIs
- GET /customers?query=
- GET /customers/{id}/360

## Workflow
```mermaid
flowchart LR
  A["Resolve identity"] --> B["Fetch profile/contacts"]
  B --> C["Fetch open SRs/complaints"]
  C --> D["Fetch interactions"]
  D --> E["Compute KPIs"]
  E --> F["Return DTO"]
```

## Error Handling
- 404 if not found
- Partial responses with warnings when upstreams unavailable

## Security & Compliance
- PII encryption, masking by role
- Access logged to audit logs

## Non-Functional Requirements
- p95 < 600ms with caching
- High availability and graceful degradation

## Traceability
- RFP: Case 360 view, history visibility, multiple account/policy display

## Repository References
- Backend baseline: crm_backend/src/api/main.py (service entry)
- Database scripts (for schema evolution): crm_database/startup.sh; refer to Data Architecture module for schema outline
