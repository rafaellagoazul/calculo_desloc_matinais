import json
from pathlib import Path
import shutil


class QuarantineManager:

    def __init__(self, root: Path):
        self.root = root
        self.quarantine_dir = root / "__quarantine__"
        self.meta_file = self.quarantine_dir / "meta.json"

        self.quarantine_dir.mkdir(exist_ok=True)

    def move_files(self, files):

        moved = {}
        for file in files:

            original = Path(file)

            if not original.exists():
                continue

            target = self.quarantine_dir / original.name
            shutil.move(str(original), str(target))

            moved[str(target)] = str(original)

        self._save_meta(moved)
        return list(moved.keys())

    def restore_all(self):

        if not self.meta_file.exists():
            return []

        with open(self.meta_file, "r") as f:
            moved = json.load(f)

        restored = []

        for quarantined, original in moved.items():

            q = Path(quarantined)
            o = Path(original)

            if q.exists():
                o.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(q), str(o))
                restored.append(original)

        self.meta_file.unlink()
        return restored

    def _save_meta(self, moved):

        with open(self.meta_file, "w") as f:
            json.dump(moved, f, indent=4)
