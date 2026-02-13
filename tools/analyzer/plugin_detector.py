import ast
from pathlib import Path

class PluginDetector:
    def __init__(self, root: Path):
        self.root = root
        self.found = []

    def scan(self):
        for py in self.root.rglob("*.py"):
            if "plugin" in py.parts:
                self.found.append((py, "folder"))
                continue
            self._scan_file(py)
        return self.found

    def _scan_file(self, py):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except Exception:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if node.attr == "entry_points":
                    self.found.append((py, "entry_point"))
