import pytest
from app import app as flask_app
from database.db import init_db
from database.queries import get_user_by_id, get_summary_stats, get_recent_transactions, get_category_breakdown
import sqlite3
import os

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret",
    })
    with flask_app.app_context():
        init_db()
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_conn():
    # Use a separate test database to avoid collisions and IntegrityErrors
    test_db_path = "test_spendly.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    import database.db as db
    original_db_path = db.DB_PATH
    db.DB_PATH = test_db_path

    # Initialize the test database
    conn = sqlite3.connect(test_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")

    # Create tables
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    # IMPORTANT: We must ensure the helper functions use THIS connection or the updated DB_PATH
    import database.db
    database.db.DB_PATH = test_db_path


    yield conn
    conn.close()
    db.DB_PATH = original_db_path
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


def test_get_user_by_id(db_conn):
    # Seed a user
    cursor = db_conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Test User", "test@example.com", "hashed_pass")
    )
    user_id = cursor.lastrowid

    user = get_user_by_id(user_id)
    assert user is not None
    assert user["name"] == "Test User"
    assert user["email"] == "test@example.com"
    assert "202" in user["member_since"]  # Check for year 202x

def test_get_summary_stats(db_conn):
    # Seed user and expenses
    cursor = db_conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Stats User", "stats@example.com", "hashed_pass")
    )
    user_id = cursor.lastrowid
    db_conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        [
            (user_id, 100.0, 'Food', '2023-10-01', 'Lunch'),
            (user_id, 200.0, 'Bills', '2023-10-02', 'Electricity'),
            (user_id, 50.0, 'Food', '2023-10-03', 'Coffee'),
        ]
    )
    db_conn.commit()

    stats = get_summary_stats(user_id)
    assert stats["total_spent"] == 350.0
    assert stats["transaction_count"] == 3
    assert stats["top_category"] == "Bills"

def test_get_recent_transactions(db_conn):
    cursor = db_conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Tx User", "tx@example.com", "hashed_pass")
    )
    user_id = cursor.lastrowid
    db_conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        [
            (user_id, 10.0, 'Other', '2023-01-01', 'Old'),
            (user_id, 20.0, 'Other', '2023-12-31', 'New'),
        ]
    )
    db_conn.commit()

    txs = get_recent_transactions(user_id)
    assert len(txs) == 2
    assert txs[0]["amount"] == 20.0  # Newest first

def test_get_category_breakdown(db_conn):
    cursor = db_conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Cat User", "cat@example.com", "hashed_pass")
    )
    user_id = cursor.lastrowid
    db_conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        [
            (user_id, 100.0, 'Food', '2023-10-01', 'Lunch'),
            (user_id, 100.0, 'Bills', '2023-10-02', 'Net'),
            (user_id, 100.0, 'Travel', '2023-10-03', 'Bus'),
        ]
    )
    db_conn.commit()

    breakdown = get_category_breakdown(user_id)
    assert len(breakdown) == 3
    assert sum(item["pct"] for item in breakdown) == 100

def test_profile_route_unauthenticated(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.location

def test_profile_route_authenticated(client, db_conn):
    # Create a user and log them in via session
    cursor = db_conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Auth User", "auth@example.com", "hashed_pass")
    )
    user_id = cursor.lastrowid
    db_conn.commit()

    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = "Auth User"

    response = client.get("/profile")
    assert response.status_code == 200
    assert b"Auth User" in response.data
    assert b"auth@example.com" in response.data
    assert b"\xe2\x82\xb9" in response.data
