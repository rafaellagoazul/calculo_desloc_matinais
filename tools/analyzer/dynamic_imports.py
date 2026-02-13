import ast
from pathlib import Path


class DynamicImportDetector:
    def __init__(self, root: Path):
        self.root = root
        self.findings = []

    def scan(self):
        for py in self.root.rglob("*.py"):
            if ".venv" in py.parts or ".quarantine" in py.parts:
                continue
            self._scan_file(py)
        return self.findings

    def _scan_file(self, file: Path):
        try:
            tree = ast.parse(file.read_text(encoding="utf-8"))
        except Exception:
            return

        rel = file.relative_to(self.root).as_posix()

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = self._call_name(node)

                if name in {
                    "__import__",
                    "importlib.import_module",
                    "getattr",
                }:
                    self.findings.append((rel, name, node.lineno))

    def _call_name(self, node):
        import ast

        # chamada direta: importlib.import_module(...)
        if isinstance(node, ast.Call):
            return self._call_name(node.func)

        # nome simples: importlib
        if isinstance(node, ast.Name):
            return node.id

        # atributo encadeado: importlib.import_module
        if isinstance(node, ast.Attribute):
            base = self._call_name(node.value)
            if base:
                return f"{base}.{node.attr}"
            return node.attr

        return None

