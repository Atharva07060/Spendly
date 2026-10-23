---
# Spec: Profile Page Design

## Overview
The Profile Page serves as the personalized dashboard for a logged-in user. At this stage of the Spendly roadmap, it provides a way for users to verify they are logged in and see their basic account information before the more complex expense tracking features are implemented.

## Depends on
- Registration
- Login and Logout

## Routes
- `GET /profile` — Displays the user's profile information — access level (logged-in)

## Database changes
No database changes.

## Templates
- **Modify:** `templates/profile.html` — Improve the layout and styling to match the Spendly brand, moving from a basic placeholder to a polished profile view.

## Files to change
- `templates/profile.html`
- `static/css/style.css`

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

## Definition of done
- [ ] Logging in redirects the user to the `/profile` page.
- [ ] The profile page correctly displays the logged-in user's name.
- [ ] Accessing `/profile` without being logged in redirects the user to the login page with an error message.
- [ ] The page is visually consistent with the landing and login pages (using `style.css` variables).
- [ ] The layout is responsive and looks professional.
---
