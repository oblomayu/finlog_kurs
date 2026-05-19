import csv
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from app.db import fetch_all, execute

def export_zip(db_path, out_dir="."):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = Path(out_dir) / f"finlog_{ts}.zip"
    with zipfile.ZipFile(zip_path, 'w') as z:
        # CSV транзакций
        rows = fetch_all(db_path, "SELECT * FROM transactions")
        csv_path = Path(out_dir) / f"temp_{ts}.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        z.write(csv_path, "transactions.csv")
        csv_path.unlink()

        # Копия SQLite
        db_copy = Path(out_dir) / f"temp_{ts}.db"
        shutil.copy(db_path, db_copy)
        z.write(db_copy, "backup.sqlite")
        db_copy.unlink()

        # JSON бюджетов
        budgets = fetch_all(db_path, "SELECT * FROM budgets")
        if budgets:
            json_path = Path(out_dir) / f"temp_{ts}.json"
            with open(json_path, 'w') as f:
                json.dump(budgets, f)
            z.write(json_path, "budgets.json")
            json_path.unlink()
    return str(zip_path)

def import_zip(db_path, zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        if "transactions.csv" in z.namelist():
            with z.open("transactions.csv") as f:
                import_csv(db_path, f)
        if "budgets.json" in z.namelist():
            with z.open("budgets.json") as f:
                import_json(db_path, f)

def import_csv(db_path, fileobj):
    import io
    reader = csv.DictReader(io.TextIOWrapper(fileobj, 'utf-8'))
    for row in reader:
        execute(db_path,
            "INSERT OR REPLACE INTO transactions (id,type,amount,category,date,description) VALUES (?,?,?,?,?,?)",
            (row.get('id'), row['type'], row['amount'], row['category'], row['date'], row.get('description','')))

def import_json(db_path, fileobj):
    import io
    budgets = json.load(io.TextIOWrapper(fileobj, 'utf-8'))
    for b in budgets:
        execute(db_path, "INSERT OR REPLACE INTO budgets (category, monthly_limit) VALUES (?,?)",
                (b['category'], b['monthly_limit']))