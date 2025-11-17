# Screen Spec — Service Request Detail

## Purpose
Allow agents to work the SR lifecycle with full context, status transitions, notes, and attachments.

## Entry and Exit
- Entry: From lists, search, creation redirect
- Exit: Navigate back to list or related entities

## Layout
- Header: SR id, status pill, priority, SLA due, customer link
- Side: Assignee card, watchers, quick actions
- Tabs: Overview, Activity, Attachments, Related

## Components
- StatusPill; TransitionButtons; Timeline; DataTable; AttachmentList; AssigneePicker

## Responsive Rules
- Side panel collapses to bottom on xs
- Tabs horizontally scrollable on xs

## Validation Rules
- Status transitions must be legal; disallow Closed→InProgress
- Notes required on certain transitions (Escalate)

## Errors and Edge Cases
- Conflict (409) on illegal transition: explain allowed transitions
- SLA past due: highlight in error color

## Success/Empty States
- Activity empty: “No activity yet” with hint

## Interactions and Shortcuts
- 'A' assigns to me
- 'N' adds note
- 'E' escalate (if permitted)

## Analytics Events
- sr.view {id}
- sr.transition {from,to}
- sr.assign {user_id}

## Test Scenarios
- Transition guards enforced
- Timeline renders newest first
