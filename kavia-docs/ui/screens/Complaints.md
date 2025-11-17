# Screen Spec — Complaints

## Purpose
Register, track, and escalate complaints with regulatory alignment.

## Entry and Exit
- Entry: Sidebar → Complaints; from Customer 360
- Exit: Detail, Escalation, Close

## Layout
- Filters: severity, category, regulator_flag, status
- List: DataTable with columns [id, customer, category, severity, status, assignee, created_at]
- Detail: mirrors SR detail with Escalation panel

## Components
- Filters Drawer, DataTable, StatusPill, EscalationModal(level,to_team,reason)

## Responsive Rules
- Filters drawer on mobile
- Dense table variant under 768px

## Validation Rules
- Escalation requires level and reason
- regulator_flag cases require regulator note

## Errors and Edge Cases
- Warn on escalation conflicts with guidance

## Success/Empty States
- Empty list: prompt to adjust filters

## Interactions and Shortcuts
- 'E' opens Escalation when on detail
- Enter opens selected row

## Analytics Events
- complaint.list.view
- complaint.escalate {id, level}

## Test Scenarios
- Filters apply and persist via URL params
- Escalation form validates inputs
