# Secure CRM Frontend — Components Library

## Document Control
- Version: 1.0.0
- Date: 2025-11-17
- Owners: UX Design + Frontend
- Status: Draft

## 1. AppShell
AppShell composes Sidebar, TopBar, and Content. It controls layout, responsive behavior, and theming.

Props:
- sidebarCollapsed: boolean
- user: {name, role, avatarUrl}
- onToggleSidebar(): void
- children: ReactNode

Accessibility:
- Landmarks: <header>, <nav>, <main>
- Skip link to #main-content
- Sidebar toggle is focusable and labeled

Usage:
```jsx
<AppShell sidebarCollapsed={false} user={u} onToggleSidebar={toggle}>
  <Dashboard />
</AppShell>
```

## 2. Sidebar
Props:
- items: Array<{key, label, icon, path, children?}>
- activeKey: string
- onNavigate(key): void

Variants:
- Expanded (default), Collapsed (icons), Off-canvas (mobile)

Accessibility:
- nav role="navigation", aria-label="Primary"
- Roving tabindex for menu items
- Expand/collapse submenus via keyboard

## 3. TopBar
Props:
- onSearch(query)
- notifications: Array<{id, text, date, tone}>
- onQuickCreate(type)
- userMenu: {onProfile, onSettings, onLogout}

A11y:
- Search input with label
- Notification button has aria-haspopup

## 4. DataTable
Props:
- columns: [{key, header, width?, render?, sortable?}]
- data: any[]
- sort: {key, dir}
- selection: 'none' | 'single' | 'multi'
- pagination: {page, pageSize, total}
- density: 'comfortable' | 'compact'
- loading, error, emptyMessage

A11y:
- table with thead/tbody; header scope="col"
- aria-busy during loading
- Keyboard row navigation

## 5. Filters
Props:
- fields: [{key,type,label,options?}]
- values: Record<string, any>
- onApply(values), onReset()

Variants:
- Inline, Drawer

## 6. Forms
Common controls:
- Input, Select, DatePicker, TextArea, RichTextEditor, Checkbox, Radio, Switch

Props:
- label, name, value, onChange, required, helpText, error

A11y:
- label for/id; aria-describedby for help/error; aria-invalid on error
- Keyboard accessible; large touch targets

## 7. Modals
Props:
- open, title, onClose, footer, size ('sm'|'md'|'lg')

A11y:
- role="dialog", aria-modal="true"; focus trap and return focus

## 8. Tabs
Props:
- items: [{key,label,content}]
- activeKey, onChange

A11y:
- role="tablist", tab/tabpanel pattern; arrow key navigation

## 9. Cards
Props:
- title, subtitle, actions, footer, elevation

## 10. Stepper
Props:
- steps: string[], active: number, onNext, onBack, onGoTo

## 11. Toasts
Props:
- message, tone ('info'|'success'|'warning'|'error'), autoDismiss, duration=4000

A11y:
- role="status" (info/success), role="alert" (errors)

## 12. Pagination
Props:
- page, pageSize, total, onChange

## 13. Search
Props:
- placeholder, value, onChange, onSubmit

Keyboard:
- '/' focuses search, 'Esc' clears

## 14. DatePicker
Props:
- value, onChange, min, max, disabledDays

A11y:
- Keyboard navigation for calendar; aria-live for month changes

## 15. RichTextEditor
Props:
- value, onChange, toolbarOptions

Security:
- Sanitize output; disable dangerous HTML

## 16. Avatar, Badge, Tag, StatusPill
Props:
- Avatar: {src, alt, initials}
- Badge/Tag: {label, color, onDismiss?}
- StatusPill: {status: 'New'|'InProgress'|'Pending'|'Escalated'|'Resolved'|'Closed'}

## 17. Accessibility Notes
- Maintain 44px touch target heights
- Clear focus outlines that pass contrast
- Error messages paired with inputs via aria-describedby

## 18. Usage Guidelines
- Use DataTable for datasets > 10 rows with server-side pagination
- Prefer Drawer Filters for complex criteria on smaller screens
- Use Stepper for > 2-step forms
- Use Toasts for ephemeral confirmation; Dialogs for destructive actions

## 19. Examples
SR List:
```jsx
<DataTable
  columns={[
    {key:'id', header:'ID', sortable:true},
    {key:'customer', header:'Customer'},
    {key:'priority', header:'Priority'},
    {key:'status', header:'Status', render:(r)=><StatusPill status={r.status}/>},
    {key:'sla', header:'SLA Due', sortable:true},
  ]}
  data={rows}
  pagination={{page, pageSize, total}}
  loading={loading}
/>
```
