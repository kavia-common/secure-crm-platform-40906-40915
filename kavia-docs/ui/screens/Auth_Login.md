# Screen Spec — Auth Login

## Purpose
Authenticate users via secure login with optional MFA (future).

## Entry and Exit
- Entry: Unauthenticated route
- Exit: On success → Dashboard

## Layout
- Centered card with logo, title, fields (username/email, password), Login button, Forgot link

## Components
- Form: Input (email), Input (password), Button (primary), Alert (error)

## Responsive Rules
- Full-width card on mobile; constrained width on desktop (max 400px)

## Validation Rules
- Required fields; email format if applicable
- Lockout on repeated failures (server-driven)

## Errors and Edge Cases
- Invalid credentials: generic message
- Network errors: retry guidance

## Success/Empty States
- Success toast “Welcome back” and redirect

## Interactions and Shortcuts
- Enter submits; Tab order correct; show password toggle

## Analytics Events
- auth.login.submit
- auth.login.success|error
