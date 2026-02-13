import zipfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from tools.backup.backup_config import get_backup_dir


EXCLUDE = {"venv", "__pycache__", ".git", "data/backups"}


def criar_backup(project_root: Path, progress_cb=None) -> Path:
    pasta = get_backup_dir()
    nome = f"backup_{project_root.name}_{datetime.now():%Y-%m-%d_%H-%M-%S}.zip"
    zip_path = pasta / nome

    arquivos = [
        p for p in project_root.rglob("*")
        if p.is_file() and not any(x in p.parts for x in EXCLUDE)
    ]

    total = len(arquivos)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for i, file in enumerate(arquivos, 1):
            zipf.write(file, file.relative_to(project_root))
            if progress_cb:
                progress_cb(i, total, file.name)

    return zip_path


def limpar_backups_antigos(dias=15):
    pasta = get_backup_dir()
    limite = datetime.now() - timedelta(days=dias)

    for f in pasta.glob("*.zip"):
        if datetime.fromtimestamp(f.stat().st_mtime) < limite:
            f.unlink()


def restaurar_modo_seguro(zip_path: Path) -> Path:
    destino = Path(tempfile.mkdtemp(prefix="restore_backup_"))

    with zipfile.ZipFile(zip_path, "r") as zipf:
        zipf.extractall(destino)

    return destino
