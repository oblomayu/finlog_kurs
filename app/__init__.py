import os
import logging
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv

from app.db import init_db
from app.backup import create as backup_create

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
    app.config['DB_PATH'] = os.getenv('DB_PATH', 'data/finlog.db')
    app.config['BACKUP_DIR'] = os.getenv('BACKUP_DIR', 'backups')

    # Создаём папку для БД и резервных копий
    Path(app.config['DB_PATH']).parent.mkdir(exist_ok=True)
    Path(app.config['BACKUP_DIR']).mkdir(exist_ok=True)

    # Инициализируем БД и делаем первое резервное копирование
    init_db(app.config['DB_PATH'])
    backup_create(app.config['DB_PATH'], app.config['BACKUP_DIR'])

    # Настройка логирования
    logging.basicConfig(
        filename='app.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Регистрация blueprint'ов
    from app.views.transactions import transactions_bp
    from app.views.budgets import budgets_bp
    from app.views.rules import rules_bp
    from app.views.export_import import export_bp
    from app.views.reports import reports_bp

    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(budgets_bp, url_prefix='/budgets')
    app.register_blueprint(rules_bp, url_prefix='/rules')
    app.register_blueprint(export_bp, url_prefix='/export-import')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    # Главная страница — перенаправление на транзакции
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('transactions.list'))

    return app