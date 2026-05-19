from flask import Blueprint, render_template, request, redirect, url_for, current_app
from app.transactions import add, get_all, get_by_id, update, delete
from app.rules import apply_rules
from app.backup import create as backup_create

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/')
def list():
    db_path = current_app.config['DB_PATH']
    filters = {}
    for key in ['type', 'category', 'date_from', 'date_to']:
        val = request.args.get(key)
        if val:
            filters[key] = val
    transactions = get_all(db_path, filters if filters else None)
    return render_template('transactions.html', transactions=transactions, filters=filters)

@transactions_bp.route('/add', methods=['GET', 'POST'])
def add_transaction():
    db_path = current_app.config['DB_PATH']
    if request.method == 'POST':
        typ = request.form['type']
        amount = float(request.form['amount'])
        date = request.form['date']
        description = request.form.get('description', '')
        category = request.form.get('category', '').strip()
        rule_id = None

        if typ == 'expense' and not category:
            # Автоматическая категоризация
            cat, rule_id = apply_rules(db_path, description, amount)
            category = cat if cat else 'Без категории'
        elif typ == 'income' and not category:
            category = 'Доход'

        add(db_path, typ, amount, category, date, description, rule_id)
        backup_create(db_path, current_app.config['BACKUP_DIR'])
        return redirect(url_for('transactions.list'))
    return render_template('transaction_form.html', transaction=None)

@transactions_bp.route('/<int:tid>/edit', methods=['GET', 'POST'])
def edit_transaction(tid):
    db_path = current_app.config['DB_PATH']
    transaction = get_by_id(db_path, tid)
    if not transaction:
        return redirect(url_for('transactions.list'))
    if request.method == 'POST':
        typ = request.form['type']
        amount = float(request.form['amount'])
        date = request.form['date']
        description = request.form.get('description', '')
        category = request.form.get('category', '').strip()
        update(db_path, tid, type=typ, amount=amount, date=date, description=description, category=category)
        backup_create(db_path, current_app.config['BACKUP_DIR'])
        return redirect(url_for('transactions.list'))
    return render_template('transaction_form.html', transaction=transaction)

@transactions_bp.route('/<int:tid>/delete', methods=['POST'])
def delete_transaction(tid):
    db_path = current_app.config['DB_PATH']
    delete(db_path, tid)
    backup_create(db_path, current_app.config['BACKUP_DIR'])
    return redirect(url_for('transactions.list'))