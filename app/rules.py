import re
from app.db import execute, fetch_all

def add_rule(db_path, pattern, field, category, priority=0, is_active=True):
    execute(db_path,
        "INSERT INTO rules (pattern, field, category, priority, is_active) VALUES (?,?,?,?,?)",
        (pattern, field, category, priority, int(is_active)))

def get_all_rules(db_path):
    return fetch_all(db_path, "SELECT * FROM rules ORDER BY priority DESC")

def get_rule_by_id(db_path, rid):
    rows = fetch_all(db_path, "SELECT * FROM rules WHERE id=?", (rid,))
    return rows[0] if rows else None

def update_rule(db_path, rid, **kwargs):
    allowed = ['pattern', 'field', 'category', 'priority', 'is_active']
    set_clause = ", ".join([f"{k}=?" for k in kwargs if k in allowed])
    if not set_clause:
        return
    params = [kwargs[k] for k in kwargs if k in allowed] + [rid]
    execute(db_path, f"UPDATE rules SET {set_clause} WHERE id=?", params)

def delete_rule(db_path, rid):
    execute(db_path, "DELETE FROM rules WHERE id=?", (rid,))

def apply_rules(db_path, description, amount=None):
    """Применяет правила и возвращает (category, rule_id) или (None, None)."""
    rules = fetch_all(db_path,
        "SELECT id, pattern, field, category FROM rules WHERE is_active=1 ORDER BY priority DESC")
    for rule in rules:
        pattern = rule['pattern']
        field = rule['field']
        field_value = description if field == 'description' else str(amount or '')
        # сначала пробуем как регулярное выражение
        try:
            if re.search(pattern, field_value, re.IGNORECASE):
                return rule['category'], rule['id']
        except re.error:
            pass
        # иначе ищем простое вхождение подстроки (без учёта регистра)
        if pattern.lower() in field_value.lower():
            return rule['category'], rule['id']
    return None, None