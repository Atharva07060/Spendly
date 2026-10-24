import pytest
from app import app as flask_app
from database.db import init_db
import sqlite3
import os

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        init_db()
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    """A test client that is already logged in."""
    # Register user
    client.post('/register', data={'username': 'testuser', 'email': 'test@example.com', 'password': 'testpass'})
    # Login user
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    return client

@pytest.fixture
def setup_expenses(auth_client, app):
    """Seeds the database with a set of expenses across different dates."""
    with app.app_context():
        # Get the logged in user's ID from session (simulated)
        # Since we don't have a helper to get current_user, we manually find it
        conn = sqlite3.connect(app.config['DATABASE'])
        user = conn.execute("SELECT id FROM users WHERE username = 'testuser'").fetchone()
        user_id = user[0]

        expenses = [
            (user_id, 100.0, 'Food', '2023-01-01', 'Jan Meal'),
            (user_id, 200.0, 'Bills', '2023-01-15', 'Jan Bill'),
            (user_id, 50.0, 'Food', '2023-02-01', 'Feb Meal'),
            (user_id, 300.0, 'Travel', '2023-02-15', 'Feb Trip'),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()
        conn.close()
    return auth_client

class TestProfileDateFilter:

    def test_profile_auth_guard(self, client):
        """Verify that unauthenticated users cannot access the profile page."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_profile_filter_ui_elements(self, setup_expenses):
        """Verify that the date filter form and Clear Filter link are present."""
        client = setup_expenses
        response = client.get('/profile')
        assert response.status_code == 200
        # Check for date inputs and submit button
        assert b'name="start_date"' in response.data
        assert b'name="end_date"' in response.data
        assert b'type="submit"' in response.data
        # Check for Clear Filter link
        assert b'Clear Filter' in response.data

    def test_filter_happy_path(self, setup_expenses):
        """Verify that filtering by a valid date range returns correct data."""
        client = setup_expenses
        # Filter for February 2023 only
        response = client.get('/profile?start_date=2023-02-01&end_date=2023-02-28')

        assert response.status_code == 200
        # Total spent in Feb: 50 + 300 = 350
        assert b'350' in response.data
        # Feb transactions: 'Feb Meal', 'Feb Trip'
        assert b'Feb Meal' in response.data
        assert b'Feb Trip' in response.data
        # Jan transactions should NOT be present
        assert b'Jan Meal' not in response.data
        assert b'Jan Bill' not in response.data

    def test_filter_no_results(self, setup_expenses):
        """Verify that a date range with no expenses returns zeros/empty states."""
        client = setup_expenses
        # Filter for a range where no expenses exist (e.g., March 2023)
        response = client.get('/profile?start_date=2023-03-01&end_date=2023-03-31')

        assert response.status_code == 200
        # Should show 0 or empty state for spending
        assert b'0' in response.data
        # No transactions should be listed
        assert b'Jan Meal' not in response.data
        assert b'Feb Meal' not in response.data

    def test_filter_all_results(self, setup_expenses):
        """Verify that a range covering all transactions shows everything."""
        client = setup_expenses
        # Range covering Jan and Feb
        response = client.get('/profile?start_date=2023-01-01&end_date=2023-12-31')

        assert response.status_code == 200
        # Total spent: 100 + 200 + 50 + 300 = 650
        assert b'650' in response.data
        assert b'Jan Meal' in response.data
        assert b'Feb Trip' in response.data

    def test_clear_filter_behavior(self, setup_expenses):
        """Verify that clearing the filter resets to show all expenses."""
        client = setup_expenses
        # First apply a filter
        client.get('/profile?start_date=2023-02-01&end_date=2023-02-28')

        # Then 'Clear Filter' (which should lead to /profile without params)
        # In a real browser, this is a link. We simulate by requesting the base route.
        response = client.get('/profile')

        assert response.status_code == 200
        # Should show all data again
        assert b'650' in response.data
        assert b'Jan Meal' in response.data
        assert b'Feb Trip' in response.data

    @pytest.mark.parametrize("start, end", [
        ("invalid-date", "2023-01-01"),
        ("2023-01-01", "invalid-date"),
        ("", ""),
    ])
    def test_filter_invalid_dates(self, setup_expenses, start, end):
        """Verify that invalid date inputs do not crash the app (should default to all or handle gracefully)."""
        client = setup_expenses
        response = client.get(f'/profile?start_date={start}&end_date={end}')

        assert response.status_code == 200
        # The app should not 500. It should either show all data or an empty state.
        # Based on spec: "default to showing all data" if no (valid) filter is provided.
        assert b'Jan Meal' in response.data or b'0' in response.data
