from pathlib import Path
import json

CONFIG_PATH = Path("data/backup_config.json")
DEFAULT_BACKUP_DIR = Path("data/backups")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"backup_dir": str(DEFAULT_BACKUP_DIR)}

    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def save_config(cfg: dict):
    CONFIG_PATH.parent.mkdir(exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def get_backup_dir() -> Path:
    cfg = load_config()
    return Path(cfg.get("backup_dir", DEFAULT_BACKUP_DIR))
