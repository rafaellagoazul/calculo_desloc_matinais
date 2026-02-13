from pathlib import Path

IGNORED_DIRS = {
    ".venv",
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".cache",
    ".backups",
    ".backups_code_fixer",
    ".backups_full_project",
    "tools_old",
}

def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)
