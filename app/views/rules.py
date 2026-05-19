from flask import Blueprint, render_template, request, redirect, url_for, current_app
from app.rules import add_rule, get_all_rules, get_rule_by_id, update_rule, delete_rule

rules_bp = Blueprint('rules', __name__)

@rules_bp.route('/')
def list_rules():
    db_path = current_app.config['DB_PATH']
    rules = get_all_rules(db_path)
    return render_template('rules.html', rules=rules)

@rules_bp.route('/add', methods=['POST'])
def add_new_rule():
    db_path = current_app.config['DB_PATH']
    pattern = request.form['pattern']
    field = request.form.get('field', 'description')
    category = request.form['category']
    priority = int(request.form.get('priority', 0))
    is_active = request.form.get('is_active') == 'on'
    add_rule(db_path, pattern, field, category, priority, is_active)
    return redirect(url_for('rules.list_rules'))

@rules_bp.route('/<int:rid>/edit', methods=['POST'])
def edit_rule(rid):
    db_path = current_app.config['DB_PATH']
    rule = get_rule_by_id(db_path, rid)
    if not rule:
        return redirect(url_for('rules.list_rules'))
    pattern = request.form['pattern']
    field = request.form.get('field', 'description')
    category = request.form['category']
    priority = int(request.form.get('priority', 0))
    is_active = request.form.get('is_active') == 'on'
    update_rule(db_path, rid, pattern=pattern, field=field, category=category,
                priority=priority, is_active=int(is_active))
    return redirect(url_for('rules.list_rules'))

@rules_bp.route('/<int:rid>/delete', methods=['POST'])
def delete_rule_route(rid):
    db_path = current_app.config['DB_PATH']
    delete_rule(db_path, rid)
    return redirect(url_for('rules.list_rules'))