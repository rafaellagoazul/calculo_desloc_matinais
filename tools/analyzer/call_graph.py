import ast
from pathlib import Path
from typing import Dict, Set, Optional, Union

FuncNode = Union[ast.FunctionDef, ast.AsyncFunctionDef]


class FunctionNode:
    def __init__(self, name: str, file: Path):
        self.name = name
        self.file = file
        self.calls: Set[str] = set()
        self.called_by: Set[str] = set()
        self.reachable = False
        self.entry_point = False

    def __repr__(self):
        return f"<FunctionNode {self.name}>"


class CallGraphAnalyzer(ast.NodeVisitor):
    def __init__(self, root: Path):
        self.root = root
        self.files: dict = {}
        self.functions: Dict[str, FunctionNode] = {}
        self.current_function: Optional[str] = None
        self.current_file: Optional[Path] = None

    # ======================
    # Public API
    # ======================

    def analyze(self):
        for py in self._iter_py_files():
            self._analyze_file(py)

        self._link_reverse_edges()
        self._mark_entry_points()
        self._mark_reachable()

        return self._build_report()

    # ======================
    # File scanning
    # ======================

    def _iter_py_files(self):
        yield from self.root.rglob("*.py")

    def _analyze_file(self, path: Path):
        try:
            self.current_file = path
            tree = ast.parse(path.read_text(encoding="utf-8"))
            self.visit(tree)
        except Exception:
            pass
        finally:
            self.current_file = None

    # ======================
    # AST Visitors
    # ======================

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._handle_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._handle_function(node)

    def _handle_function(self, node: FuncNode):
        if not self.current_file:
            return

        name = self._qualname(node)

        fn = self.functions.setdefault(
            name,
            FunctionNode(name=name, file=self.current_file),
        )

        prev = self.current_function
        self.current_function = name
        self.generic_visit(node)
        self.current_function = prev

    def visit_Call(self, node: ast.Call):
        if self.current_function:
            called = self._resolve_call_name(node)
            if called:
                self.functions[self.current_function].calls.add(called)

        self.generic_visit(node)

    # ======================
    # Helpers
    # ======================

    def _qualname(self, node: FuncNode) -> str:
        return node.name

    def _resolve_call_name(self, node: ast.Call) -> Optional[str]:
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None

    # ======================
    # Graph logic
    # ======================

    def _link_reverse_edges(self):
        for fn in self.functions.values():
            for callee in fn.calls:
                if callee in self.functions:
                    self.functions[callee].called_by.add(fn.name)

    def _mark_entry_points(self):
        for name, fn in self.functions.items():
            if (
                name in {"main", "run", "start", "launch"}
                or name.startswith(("mount_", "open_", "load_"))
                or "__init__" in name
                or any(
                    cls in name
                    for cls in (
                        "App.",
                        "UI.",
                        "Window.",
                        "Dashboard.",
                        "Controller.",
                    )
                )
            ):
                fn.entry_point = True


    def _mark_reachable(self):
        stack = [f for f in self.functions.values() if f.entry_point]

        for fn in stack:
            fn.reachable = True

        while stack:
            current = stack.pop()
            for callee in current.calls:
                if callee in self.functions:
                    fn = self.functions[callee]
                    if not fn.reachable:
                        fn.reachable = True
                        stack.append(fn)

    # ======================
    # Report
    # ======================

    def _build_report(self):
        entry = []
        reachable = []
        orphan = []
        dead = []

        for fn in self.functions.values():
            if fn.entry_point:
                entry.append(fn)
            elif fn.reachable:
                reachable.append(fn)
            elif fn.called_by:
                orphan.append(fn)
            else:
                dead.append(fn)

        return {
            "entry": entry,
            "reachable": reachable,
            "orphan": orphan,
            "dead": dead,
        }

    def build_call_paths(self):
        paths = {}

        def dfs(fn, path):
            for callee in fn.calls:
                if callee in self.functions:
                    nxt = self.functions[callee]
                    if nxt.name not in path:
                        dfs(nxt, path + [nxt.name])

            paths.setdefault(fn.name, []).append(path)

        for fn in self.functions.values():
            if fn.entry_point:
                dfs(fn, [fn.name])

        return paths
