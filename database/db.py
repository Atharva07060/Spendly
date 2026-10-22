import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "spendly.db"

def get_db():
    """
    Returns a SQLite connection with row_factory and foreign keys enabled.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """
    Creates the users and expenses tables if they don't exist.
    """
    conn = get_db()
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
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
    finally:
        conn.close()

def seed_db():
    """
    Inserts demo data into the database if it's empty.
    """
    conn = get_db()
    try:
        with conn:
            # Check if users table is already seeded
            cursor = conn.execute("SELECT 1 FROM users LIMIT 1")
            if cursor.fetchone():
                return

            # Insert demo user
            password_hash = generate_password_hash("demo123")
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Demo User", "demo@spendly.com", password_hash)
            )
            user_id = cursor.lastrowid

            # Insert 8 sample expenses across different categories
            expenses = [
                (user_id, 12.50, 'Food', '2023-10-01', 'Lunch at Cafe'),
                (user_id, 45.00, 'Transport', '2023-10-02', 'Gas refill'),
                (user_id, 120.00, 'Bills', '2023-10-03', 'Internet Bill'),
                (user_id, 30.00, 'Health', '2023-10-04', 'Pharmacy'),
                (user_id, 60.00, 'Entertainment', '2023-10-05', 'Movie tickets'),
                (user_id, 85.20, 'Shopping', '2023-10-06', 'Clothes'),
                (user_id, 15.00, 'Other', '2023-10-07', 'Gift wrap'),
                (user_id, 22.00, 'Food', '2023-10-08', 'Dinner'),
            ]
            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )
    finally:
        conn.close()
