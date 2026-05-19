import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_file
from app.files import export_zip, import_zip
from app.backup import create as backup_create

export_bp = Blueprint('export_import', __name__)

@export_bp.route('/')
def page():
    return render_template('export_import.html')

@export_bp.route('/export')
def do_export():
    db_path = current_app.config['DB_PATH']
    out_dir = current_app.config.get('EXPORT_DIR', '.')
    zip_path = export_zip(db_path, out_dir)
    return send_file(zip_path, as_attachment=True)

@export_bp.route('/import', methods=['POST'])
def do_import():
    db_path = current_app.config['DB_PATH']
    if 'file' not in request.files:
        return redirect(url_for('export_import.page'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('export_import.page'))
    # Сохраняем во временный файл
    temp_path = os.path.join('/tmp', file.filename)
    file.save(temp_path)
    import_zip(db_path, temp_path)
    os.remove(temp_path)
    backup_create(db_path, current_app.config['BACKUP_DIR'])
    return redirect(url_for('export_import.page'))