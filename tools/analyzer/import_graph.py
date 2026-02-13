from pathlib import Path
import ast
from collections import defaultdict

from tools.shared.ignore_rules import is_ignored
from tools.analyzer.entry_points import ENTRY_POINTS


class ImportGraph:

    def __init__(
        self,
        root: Path,
        frozen: set[str] | None = None,
        mode: str = "conservative",  # ← NOVO
    ):
        self.root = root
        self.mode = mode
        self.frozen = frozen or set()

        self.files: set[str] = set()
        self.imports: dict[str, set[str]] = defaultdict(set)
        self.reverse: dict[str, set[str]] = defaultdict(set)

        self.entry_files = {
            str((self.root / p).resolve().relative_to(self.root))
            for p in ENTRY_POINTS
            if (self.root / p).exists()
        }

    # ───────── PUBLIC ─────────
    def build(self):
        self._scan_files()
        self._scan_imports()
        self._build_reverse()

    def unused_files(self) -> set[str]:
        used = set(self.entry_files)

        stack = list(self.entry_files)
        visited = set(stack)

        while stack:
            current = stack.pop()
            for dep in self.imports.get(current, []):
                if dep not in visited:
                    visited.add(dep)
                    stack.append(dep)

        used |= visited
        used |= self.frozen

        return {
            f for f in self.files
            if f not in used
        }

    # ───────── INTERNAL ─────────
    def _scan_files(self):
        for file in self.root.rglob("*.py"):
            if is_ignored(file):
                continue
            try:
                self.files.add(str(file.relative_to(self.root)))
            except ValueError:
                pass

    def _scan_imports(self):
        for rel in self.files:
            path = self.root / rel

            # 🔒 REGRA OPERACIONAL
            if self.mode == "operational":
                if rel.endswith("run_tools.py"):
                    continue

            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except Exception:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        self._register_import(rel, name.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._register_import(rel, node.module)

    def _register_import(self, src: str, module: str):
        parts = module.split(".")
        for i in range(len(parts), 0, -1):
            candidate = "/".join(parts[:i]) + ".py"
            if candidate in self.files:
                self.imports[src].add(candidate)
                break

    def _build_reverse(self):
        for src, targets in self.imports.items():
            for t in targets:
                self.reverse[t].add(src)
