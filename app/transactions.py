from app.db import execute, fetch_all

def add(db_path, typ, amount, category, date, description="", rule_id=None):
    execute(db_path,
        "INSERT INTO transactions (type, amount, category, date, description, rule_id) VALUES (?,?,?,?,?,?)",
        (typ, amount, category, date, description, rule_id))

def get_all(db_path, filters=None):
    sql = "SELECT * FROM transactions"
    params = []
    if filters:
        conds = []
        if filters.get('type'):
            conds.append("type=?")
            params.append(filters['type'])
        if filters.get('category'):
            conds.append("category=?")
            params.append(filters['category'])
        if filters.get('date_from'):
            conds.append("date>=?")
            params.append(filters['date_from'])
        if filters.get('date_to'):
            conds.append("date<=?")
            params.append(filters['date_to'])
        if conds:
            sql += " WHERE " + " AND ".join(conds)
    return fetch_all(db_path, sql + " ORDER BY date DESC", params)

def get_by_id(db_path, tid):
    rows = fetch_all(db_path, "SELECT * FROM transactions WHERE id=?", (tid,))
    return rows[0] if rows else None

def update(db_path, tid, **kwargs):
    allowed = ['type', 'amount', 'category', 'date', 'description']
    set_clause = ", ".join([f"{k}=?" for k in kwargs if k in allowed])
    if not set_clause:
        return
    params = [kwargs[k] for k in kwargs if k in allowed] + [tid]
    execute(db_path, f"UPDATE transactions SET {set_clause} WHERE id=?", params)

def delete(db_path, tid):
    execute(db_path, "DELETE FROM transactions WHERE id=?", (tid,))

def get_expenses_by_category(db_path, year_month):
    rows = fetch_all(db_path,
        "SELECT category, SUM(amount) as total FROM transactions "
        "WHERE type='expense' AND strftime('%Y-%m', date)=? GROUP BY category",
        (year_month,))
    return {r['category']: r['total'] for r in rows}