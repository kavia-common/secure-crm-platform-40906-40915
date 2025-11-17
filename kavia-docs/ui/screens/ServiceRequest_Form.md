# Screen Spec — Service Request Form (Wizard)

## Purpose
Capture all necessary details to create a new Service Request with validation and SLA metadata.

## Entry and Exit
- Entry: Quick Create, Customer 360, SR List “New”
- Exit: On submit navigates to SR Detail; on cancel returns to previous

## Layout
Wizard steps:
1. Customer (auto-filled if coming from 360)
2. Details (type, priority, subject, description)
3. Attachments (upload)
4. Review
5. Submit

## Components
- Stepper(steps,active,onNext,onBack)
- Form controls: Input, Select, DatePicker, RichTextEditor
- AttachmentUploader(files, onAdd, onRemove)
- Buttons: Next, Back, Submit

## Responsive Rules
- Single column on mobile; dual columns on desktop for Details

## Validation Rules
- Required: customer_id, type, priority, subject
- Constraints: subject ≤ 120 chars; description sanitized; attachment size ≤ 10MB

## Errors and Edge Cases
- Inline errors with aria-describedby links
- Upload failures: retry with specific error messages

## Success/Empty States
- Success toast “Service Request created” then route to detail
- Draft support (future): save progress

## Interactions and Shortcuts
- Enter on form advances if valid
- Esc closes modal (if opened as modal)

## Analytics Events
- sr.create.start
- sr.create.submit {type,priority}
- sr.create.error {field}
## Test Scenarios
- Validates required fields
- Submits and navigates to detail
