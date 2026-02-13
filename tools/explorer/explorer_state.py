from pathlib import Path
import json

class ExplorerState:
    FILE = Path(".project_explorer_state.json")

    def __init__(self):
        self.state = {
            "frozen": {},     # { "core/file.py": true }
            "expanded": []    # [ "core", "tools/code_fixer" ]
        }
        self.load()

    # ───────── persistence ─────────
    def load(self):
        if self.FILE.exists():
            self.state.update(
                json.loads(self.FILE.read_text(encoding="utf-8"))
            )

    def save(self):
        self.FILE.write_text(
            json.dumps(self.state, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    # ───────── frozen ─────────
    def is_frozen(self, rel: str) -> bool:
        return self.state["frozen"].get(rel, False)

    def freeze(self, rel: str):
        self.state["frozen"][rel] = True

    def unfreeze(self, rel: str):
        self.state["frozen"][rel] = False

    # ───────── expanded folders ─────────
    def is_expanded(self, path: Path) -> bool:
        return str(path) in self.state["expanded"]

    def expand(self, path: Path):
        key = str(path)
        if key not in self.state["expanded"]:
            self.state["expanded"].append(key)

    def collapse(self, path: Path):
        key = str(path)
        if key in self.state["expanded"]:
            self.state["expanded"].remove(key)
