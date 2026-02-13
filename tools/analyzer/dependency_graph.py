from pathlib import Path
import ast
from collections import defaultdict


class DependencyGraph:
    def __init__(self, root: Path):
        self.root = root
        self.graph = defaultdict(set)

    def build(self):
        for py in self.root.rglob("*.py"):
            if ".venv" in py.parts or ".quarantine" in py.parts:
                continue
            self._parse_file(py)
        return self.graph

    def _parse_file(self, file: Path):
        try:
            tree = ast.parse(file.read_text(encoding="utf-8"))
        except Exception:
            return

        src = file.relative_to(self.root).as_posix()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    self.graph[src].add(n.name.split(".")[0])

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.graph[src].add(node.module.split(".")[0])
