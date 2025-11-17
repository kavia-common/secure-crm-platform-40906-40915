# Secure CRM Frontend — Styles and Tokens

## Document Control
- Version: 1.0.0
- Date: 2025-11-17
- Owners: UX Design + Frontend

## 1. Theme Overview
ApplicationTheme: Heritage Brown
ApplicationStyle: Classic
Palette:
- primary: #92400E
- secondary: #FEF3C7
- success: #059669
- error: #DC2626
- background: #FFFBEB
- surface: #FFFFFF
- text: #111827

## 2. Semantic Color Tokens
- color.primary: #92400E
- color.primary.on: #FFFFFF
- color.secondary: #FEF3C7
- color.secondary.on: #111827
- color.success: #059669
- color.error: #DC2626
- surface.default: #FFFFFF
- surface.alt: #FFFBEB
- surface.muted: #FEF3C7
- text.primary: #111827
- text.secondary: rgba(17,24,39,0.7)
- text.muted: rgba(17,24,39,0.55)
- border.default: rgba(17,24,39,0.12)
- border.muted: rgba(17,24,39,0.08)
- focus.outline: #111827
- focus.fill: #FEF3C7
- overlay.backdrop: rgba(17,24,39,0.4)

## 3. Typography Scale
Font Family: system-ui, Segoe UI, Inter, Roboto, Helvetica, Arial

- Display (H1): 32/40, 700
- Heading (H2): 24/32, 600
- Heading (H3): 20/28, 600
- Title (H4): 18/24, 600
- Body (Base): 16/24, 400–500
- Body (Small): 14/20, 400–500
- Caption: 12/16, 400

Usage:
- H1 for page titles
- H2 for section headers
- Body for tables and forms
- Caption for help text and metadata

## 4. Spacing Scale (4px base)
- 0: 0
- 1: 4px
- 2: 8px
- 3: 12px
- 4: 16px
- 5: 24px
- 6: 32px
- 7: 48px
- 8: 64px

## 5. Radii
- radius.sm: 4px
- radius.md: 8px
- radius.lg: 12px
- radius.full: 9999px

## 6. Shadows
- shadow.card: 0 1px 2px rgba(0,0,0,0.05)
- shadow.hover: 0 4px 8px rgba(0,0,0,0.08)
- shadow.dialog: 0 16px 32px rgba(0,0,0,0.15)
- shadow.focus: 0 0 0 3px #FEF3C7

## 7. Grid and Breakpoints
- xs: <480px (single column)
- sm: ≥480px
- md: ≥768px (8 columns)
- lg: ≥1024px (12 columns)
- xl: ≥1280px (12 columns, max container 1280px)

Gutters:
- xs: 12px
- md: 16px
- lg+: 24px

## 8. Component Tokens
Buttons:
- button.bg: color.primary
- button.text: color.primary.on
- button.hover.bg: #7A350C
- button.disabled.bg: rgba(146,64,14,0.4)
- button.focus.outline: focus.outline

Inputs:
- input.bg: surface.default
- input.border: border.default
- input.focus.outline: focus.outline

Status:
- status.new: #2563EB
- status.inprogress: #92400E
- status.pending: #F59E0B
- status.escalated: #DC2626
- status.resolved: #059669
- status.closed: #6B7280

## 9. Motion
- duration.fast: 120ms
- duration.base: 180ms
- duration.slow: 300ms
- easing.standard: cubic-bezier(0.2, 0.0, 0.2, 1)
- prefers-reduced-motion: honor system setting

## 10. Example CSS Variables
```css
:root {
  --color-primary: #92400E;
  --color-primary-on: #FFFFFF;
  --color-secondary: #FEF3C7;
  --color-text: #111827;
  --surface-default: #FFFFFF;
  --surface-alt: #FFFBEB;
  --border-default: rgba(17,24,39,0.12);
  --radius-md: 8px;
  --shadow-card: 0 1px 2px rgba(0,0,0,0.05);
}
```
