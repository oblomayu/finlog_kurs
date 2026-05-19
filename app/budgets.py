from app.db import execute, fetch_all
from app.transactions import get_expenses_by_category

def set_limit(db_path, category, limit):
    execute(db_path,
        "INSERT OR REPLACE INTO budgets (category, monthly_limit) VALUES (?,?)",
        (category, limit))

def get_all_limits(db_path):
    rows = fetch_all(db_path, "SELECT * FROM budgets")
    return {r['category']: r['monthly_limit'] for r in rows}

def delete_limit(db_path, category):
    execute(db_path, "DELETE FROM budgets WHERE category=?", (category,))

def get_summary(db_path, year_month):
    limits = get_all_limits(db_path)
    actual = get_expenses_by_category(db_path, year_month)
    summary = []
    for cat, limit in limits.items():
        spent = actual.get(cat, 0)
        pct = (spent / limit * 100) if limit > 0 else 0
        # прогресс-бар в виде текста (для отображения в шаблоне)
        w = 20
        filled = int(w * min(pct, 100) / 100)
        bar = '[' + '=' * filled + '>' + ' ' * (w - filled - 1) + ']'
        summary.append({
            'category': cat,
            'limit': limit,
            'spent': spent,
            'remaining': limit - spent,
            'percent': min(pct, 100),
            'bar': bar
        })
    summary.sort(key=lambda x: x['percent'], reverse=True)
    return summary