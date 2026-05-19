import shutil
from pathlib import Path
from datetime import datetime

def create(db_path, backup_dir):
    Path(backup_dir).mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = Path(backup_dir) / f"backup_{ts}.sqlite"
    shutil.copy(db_path, dest)
    # Оставляем только 5 последних
    backups = sorted(Path(backup_dir).glob("backup_*.sqlite"), key=lambda p: p.stat().st_mtime)
    for old in backups[:-5]:
        old.unlink()
    return str(dest)