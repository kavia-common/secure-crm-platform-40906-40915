# Screen Spec — Settings

## Purpose
Expose administrative and personal preferences including connectors, users/roles, profile, and app settings.

## Entry and Exit
- Entry: Sidebar → Settings; TopBar user menu → Settings
- Exit: Navigate to modules

## Layout
- Left settings nav (Users & Roles, Connectors, Preferences)
- Right content forms and lists

## Components
- Tabs or vertical nav, Forms, DataTable
- Modals for add/edit dialogs

## Responsive Rules
- Vertical nav collapses to dropdown on mobile

## Validation Rules
- Role/permission forms require unique names
- Connector secrets masked; test connection action

## Errors and Edge Cases
- Connection test failures surfaced with guidance

## Success/Empty States
- Save confirmation toasts

## Interactions and Shortcuts
- 'S' save; 'T' test connector

## Analytics Events
- settings.view {section}
- connectors.test {provider, result}
