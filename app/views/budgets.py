from flask import Blueprint, render_template, request, redirect, url_for, current_app
from app.budgets import set_limit, get_all_limits, delete_limit, get_summary
from datetime import datetime

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/')
def list_budgets():
    db_path = current_app.config['DB_PATH']
    limits = get_all_limits(db_path)
    # Сводка за текущий месяц, если передан параметр, иначе текущий
    ym = request.args.get('month', datetime.now().strftime('%Y-%m'))
    summary = get_summary(db_path, ym)
    return render_template('budgets.html', limits=limits, summary=summary, month=ym)

@budgets_bp.route('/set', methods=['POST'])
def set_budget():
    db_path = current_app.config['DB_PATH']
    category = request.form['category']
    limit = float(request.form['limit'])
    set_limit(db_path, category, limit)
    return redirect(url_for('budgets.list_budgets'))

@budgets_bp.route('/delete/<category>', methods=['POST'])
def delete_budget(category):
    db_path = current_app.config['DB_PATH']
    delete_limit(db_path, category)
    return redirect(url_for('budgets.list_budgets'))