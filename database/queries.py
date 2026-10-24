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

def get_summary_stats(user_id, start_date=None, end_date=None):
    """
    Calculates total spent, transaction count, and the top category for a user.
    Optional date range filtering.
    """
    conn = get_db()
    try:
        query = "SELECT SUM(amount) as total, COUNT(*) as count FROM expenses WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        stats = conn.execute(query, params).fetchone()

        total_spent = stats['total'] if stats['total'] else 0.0
        transaction_count = stats['count'] if stats['count'] else 0

        top_category = "—"
        if transaction_count > 0:
            cat_query = "SELECT category FROM expenses WHERE user_id = ?"
            cat_params = [user_id]
            if start_date:
                cat_query += " AND date >= ?"
                cat_params.append(start_date)
            if end_date:
                cat_query += " AND date <= ?"
                cat_params.append(end_date)

            cat_query += " GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1"
            top_cat_row = conn.execute(cat_query, cat_params).fetchone()
            if top_cat_row:
                top_category = top_cat_row['category']

        return {
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "top_category": top_category
        }
    finally:
        conn.close()

def get_recent_transactions(user_id, limit=10, start_date=None, end_date=None):
    """
    Retrieves the most recent transactions for a user, newest first.
    Optional date range filtering.
    """
    conn = get_db()
    try:
        query = "SELECT date, description, category, amount FROM expenses WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC, created_at DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()

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

def get_category_breakdown(user_id, start_date=None, end_date=None):
    """
    Retrieves a breakdown of spending by category with percentages.
    Optional date range filtering.
    """
    conn = get_db()
    try:
        # Get total spending first for percentage calculation
        query_total = "SELECT SUM(amount) as total FROM expenses WHERE user_id = ?"
        params_total = [user_id]
        if start_date:
            query_total += " AND date >= ?"
            params_total.append(start_date)
        if end_date:
            query_total += " AND date <= ?"
            params_total.append(end_date)

        total_row = conn.execute(query_total, params_total).fetchone()
        total_spent = total_row['total'] if total_row['total'] else 0.0

        if total_spent == 0:
            return []

        query_breakdown = "SELECT category as name, SUM(amount) as amount FROM expenses WHERE user_id = ?"
        params_breakdown = [user_id]
        if start_date:
            query_breakdown += " AND date >= ?"
            params_breakdown.append(start_date)
        if end_date:
            query_breakdown += " AND date <= ?"
            params_breakdown.append(end_date)

        query_breakdown += " GROUP BY category ORDER BY amount DESC"
        rows = conn.execute(query_breakdown, params_breakdown).fetchall()

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
