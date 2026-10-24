# Spec: Date Filter for Profile Page

## Overview
This feature adds a date range filter to the user's profile page, allowing them to view their spending statistics and transactions for a specific time period. This enhances the profile page from a simple "recent activity" view to a more useful financial reporting tool, enabling users to analyze their spending habits over custom intervals.

## Depends on
- 04-profile-backend-routes

## Routes
- `GET /profile` — Modified to accept optional `start_date` and `end_date` query parameters. — logged-in

## Database changes
No database changes.

## Templates
- **Modify:** `templates/profile.html` — Add a date filter form (two date inputs and a submit button) and a "Clear Filter" link.

## Files to change
- `app.py` — Update the `/profile` route to handle date filter query parameters and pass them to query functions.
- `database/queries.py` — Update `get_summary_stats`, `get_recent_transactions`, and `get_category_breakdown` to accept optional `start_date` and `end_date` parameters and apply them in the SQL `WHERE` clauses.
- `templates/profile.html` — Add the UI for date selection.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Dates should be handled in `YYYY-MM-DD` format (standard for HTML date inputs).
- If no date filter is provided, default to showing all data.

## Definition of done
- [ ] The profile page displays a date range filter form.
- [ ] Selecting a valid date range and submitting the form updates the total spent, transaction count, and top category to reflect only expenses within that range.
- [ ] The transaction list updates to show only expenses within the selected range.
- [ ] The category breakdown updates to reflect only spending within the selected range.
- [ ] Clicking "Clear Filter" resets the view to show all expenses.
- [ ] Entering a date range with no expenses returns zeros/empty states without crashing.
