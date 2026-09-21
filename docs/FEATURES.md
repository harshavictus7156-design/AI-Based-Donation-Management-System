# Implemented Features

This page summarizes features visible in the current frontend and supported by the current Django backend. It intentionally excludes unverified product claims.

## Donor Workspace

- Donor registration and login.
- Dashboard with donation totals and status summaries.
- Item donation creation, editing, deletion of eligible pending donations, item details, condition, quantity, location, and optional image.
- My Donations and My Activity views.
- Donation status tracking for `Pending`, `Accepted`, `Rejected`, and `Collected`.
- NGO exploration and NGO detail views.
- AI-assisted donation image analysis.
- Matching NGO lookup and AI recommendation based on approved NGO requirements, item/category compatibility, remaining need, priority, and quantity compatibility.
- Donation allocation to one or more compatible NGO requirements through the existing allocation endpoint.
- Pickup request creation, pickup listing, and donor cancellation support.
- Notifications, unread count, mark-read, mark-all-read, and delete actions.
- Donor profile, profile image upload, account settings, appearance/theme controls, and notification preferences presented by the current frontend.
- Donor ranking and current-rank display.
- Browser voice assistant navigation for supported application destinations.

## NGO Workspace

- NGO registration and login.
- NGO dashboard and profile management.
- NGO picture and certificate upload paths.
- Incoming donation review.
- Requirement creation, editing, deletion, category, quantity, priority, description, active state, and fulfillment tracking.
- Allocation review for donations assigned to NGO requirements.
- Donation and allocation status actions supported by the existing NGO workflow.
- Pickup request listing and status updates: `Pending`, `Confirmed`, `Dispatched`, `Delivered`, and `Cancelled`.
- Notifications and unread notification management.
- Analytics, impact, settings, and theme controls exposed by the frontend workspace.

## Administrator Workspace

- Admin login and protected admin route handling in the frontend.
- Dashboard statistics for donors, NGOs, donations, requirements, allocations, and pickups.
- NGO listing, detail review, approval, and rejection.
- Donor management.
- Donation, requirement, allocation, and pickup management views.
- Ranking, notifications, analytics, and settings views.
- Backend management endpoints for aggregate dashboard data and recent donation data.

## Intelligent Features

### Image analysis

The backend AI package uses Google Gemini and Pillow to analyze uploaded donation images and return structured item, category, quantity, and confidence information for donation assistance.

### Matching and allocation

The backend compares donations with active requirements belonging to approved NGOs. Matching considers normalized item names and categories, remaining requirement quantity, priority, and quantity compatibility. The AI matching endpoint returns a recommended NGO requirement plus other matching NGOs; allocation remains subject to the existing validation rules.

## Notifications

The notifications app stores recipient-scoped notifications for donors and NGOs. Current notification types include donation submitted, approved, rejected, collected, matched, requirement matched, resource allocated, pickup created, pickup confirmed, pickup dispatched, donation delivered, and pickup cancelled.

## Current Status Vocabulary

| Entity | Values |
| --- | --- |
| Donation | `Pending`, `Accepted`, `Rejected`, `Collected` |
| Donation allocation | `Pending`, `Accepted`, `Rejected`, `Collected` |
| Donation/allocation pickup fields | `Not Scheduled`, `Scheduled`, `Accepted`, `Picked Up`, `Cancelled` |
| Pickup request | `Pending`, `Confirmed`, `Dispatched`, `Delivered`, `Cancelled` |
| NGO review | `Pending`, `Approved`, `Rejected` |
| Requirement priority | `Low`, `Medium`, `High`, `Urgent` |
