from database.db import get_db

def get_user_by_id(user_id):
    """
    Retrieves a user by their ID.
    Returns a dict with name, email, and member_since formatted as 'Month YYYY'.
    """
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        if user:
            # Format created_at (YYYY-MM-DD HH:MM:SS) to 'Month YYYY'
            import datetime
            dt = datetime.datetime.strptime(user['created_at'], '%Y-%m-%d %H:%M:%S')
            member_since = dt.strftime('%B %Y')
            return {
                "name": user['name'],
                "email": user['email'],
                "member_since": member_since
            }
        return None
    finally:
        conn.close()

def get_summary_stats(user_id):
    """
    Calculates total spent, transaction count, and the top category for a user.
    """
    conn = get_db()
    try:
        stats = conn.execute(
            "SELECT SUM(amount) as total, COUNT(*) as count FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        total_spent = stats['total'] if stats['total'] else 0.0
        transaction_count = stats['count'] if stats['count'] else 0

        top_category = "—"
        if transaction_count > 0:
            top_cat_row = conn.execute(
                "SELECT category FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
                (user_id,)
            ).fetchone()
            if top_cat_row:
                top_category = top_cat_row['category']

        return {
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "top_category": top_category
        }
    finally:
        conn.close()

def get_recent_transactions(user_id, limit=10):
    """
    Retrieves the most recent transactions for a user, newest first.
    """
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC, created_at DESC LIMIT ?",
            (user_id, limit)
        ).fetchall()

        return [
            {
                "date": row['date'],
                "description": row['description'],
                "category": row['category'],
                "amount": row['amount']
            } for row in rows
        ]
    finally:
        conn.close()

def get_category_breakdown(user_id):
    """
    Retrieves a breakdown of spending by category with percentages.
    """
    conn = get_db()
    try:
        # Get total spending first for percentage calculation
        total_row = conn.execute(
            "SELECT SUM(amount) as total FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        total_spent = total_row['total'] if total_row['total'] else 0.0

        if total_spent == 0:
            return []

        rows = conn.execute(
            "SELECT category as name, SUM(amount) as amount FROM expenses WHERE user_id = ? GROUP BY category ORDER BY amount DESC",
            (user_id,)
        ).fetchall()

        breakdown = []
        for row in rows:
            pct = round((row['amount'] / total_spent) * 100)
            breakdown.append({
                "name": row['name'],
                "amount": row['amount'],
                "pct": pct
            })

        # Adjust the largest category to ensure percentages sum to 100
        current_sum = sum(item['pct'] for item in breakdown)
        if current_sum != 100 and breakdown:
            diff = 100 - current_sum
            breakdown[0]['pct'] += diff

        return breakdown
    finally:
        conn.close()
