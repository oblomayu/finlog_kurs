import sqlite3
import logging

logger = logging.getLogger(__name__)

def init_db(db_path):
    """Создаёт таблицы, если их нет."""
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      type TEXT NOT NULL,
                      amount REAL NOT NULL,
                      category TEXT,
                      date TEXT NOT NULL,
                      description TEXT,
                      rule_id INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS budgets
                     (category TEXT PRIMARY KEY,
                      monthly_limit REAL NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS rules
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      pattern TEXT NOT NULL,
                      field TEXT DEFAULT 'description',
                      category TEXT NOT NULL,
                      priority INTEGER DEFAULT 0,
                      is_active INTEGER DEFAULT 1)''')
        conn.commit()

def execute(db_path, sql, params=()):
    """Выполняет INSERT/UPDATE/DELETE."""
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute(sql, params)
            conn.commit()
            return c
    except Exception as e:
        logger.error(str(e))
        raise

def fetch_all(db_path, sql, params=()):
    """Возвращает список словарей."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(sql, params)
        return [dict(row) for row in c.fetchall()]