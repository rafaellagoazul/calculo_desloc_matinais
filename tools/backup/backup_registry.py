from pathlib import Path
from datetime import datetime

from tools.backup.backup_config import get_backup_dir


def listar_backups():
    pasta = get_backup_dir()
    backups = []

    for f in pasta.glob("*.zip"):
        stat = f.stat()
        backups.append({
            "path": f,
            "nome": f.name,
            "data": datetime.fromtimestamp(stat.st_mtime),
            "tamanho_mb": stat.st_size / (1024 * 1024)
        })

    backups.sort(key=lambda b: b["data"], reverse=True)
    return backups
