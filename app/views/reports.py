from flask import Blueprint, render_template, current_app
from app.transactions import get_all
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
def show():
    db_path = current_app.config['DB_PATH']
    transactions = get_all(db_path)  # без фильтров — все записи
    incomes = [t for t in transactions if t['type'] == 'income']
    expenses = [t for t in transactions if t['type'] == 'expense']
    total_income = sum(t['amount'] for t in incomes)
    total_expense = sum(t['amount'] for t in expenses)
    balance = total_income - total_expense
    return render_template('reports.html',
                           total_income=total_income,
                           total_expense=total_expense,
                           balance=balance,
                           now=datetime.now().strftime('%Y-%m-%d %H:%M'))