import json
from pathlib import Path
from datetime import datetime


class HealthHistory:

    def __init__(self, root: Path):
        self.file = root / ".analyzer_history.json"

    def save_snapshot(self, data):

        history = self.load()

        data["timestamp"] = datetime.now().isoformat()

        history.append(data)

        with open(self.file, "w") as f:
            json.dump(history, f, indent=4)

    def load(self):

        if not self.file.exists():
            return []

        with open(self.file, "r") as f:
            return json.load(f)
