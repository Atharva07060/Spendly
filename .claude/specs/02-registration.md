# Spec: Registration

## Overview
This feature allows new users to create an account on the Spendly platform. It is a critical early step in the roadmap, enabling personalized expense tracking by associating data with a specific user identity.

## Depends on
- 01-database-setup

## Routes
- `GET /register` — Display the registration form — public
- `POST /register` — Process the registration form and create the user — public

## Database changes
No database changes (the `users` table was created in Step 01).

## Templates
- **Create:** `templates/register.html` (if not already present)
- **Modify:** `templates/base.html` (to add registration links/navigation)

## Files to change
- `app.py` — Implement the `POST /register` logic and update `GET /register`
- `database/db.py` — Add a helper function to create a user

## Files to create
- None (assuming `register.html` exists as a placeholder)

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- [ ] User can navigate to `/register` and see a form
- [ ] User can submit the form with name, email, and password
- [ ] A new user is successfully inserted into the `users` table
- [ ] Passwords are stored as hashes, not plain text
- [ ] Duplicate emails result in a user-friendly error message
- [ ] Successful registration redirects the user to the login page
