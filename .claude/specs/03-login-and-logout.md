# Spec: Login and Logout

## Overview
This feature implements the authentication lifecycle, allowing users to securely enter their account via a login page and terminate their session via a logout action. This ensures that expense tracking is private and tied to a specific authenticated session.

## Depends on
- 02-registration

## Routes
- `POST /login` — Verify credentials and establish session — public
- `GET /logout` — Clear session and redirect to landing — logged-in
- `GET /profile` — Display user-specific greeting (as a landing for logged-in users) — logged-in

## Database changes
No database changes.

## Templates
- **Modify:** `templates/base.html` — Update navbar to show "Logout" and "Profile" when authenticated, and "Sign in" / "Get started" when anonymous.
- **Modify:** `templates/login.html` — Ensure consistency with the authentication style.
- **Create:** `templates/profile.html` — A simple page displaying the logged-in user's name.

## Files to change
- `app.py` — Implement full login verification, session management, and the logout route.
- `templates/base.html` — Implement conditional navigation based on session state.

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- [ ] User can log in with correct email and password.
- [ ] User is redirected to `/profile` upon successful login.
- [ ] User sees "Incorrect email or password" in the login box upon failure.
- [ ] Navbar changes from "Sign in" to "Profile" and "Logout" when logged in.
- [ ] Clicking "Logout" clears the session and redirects to the landing page.
- [ ] Navigating to `/profile` while logged out redirects to the login page.
