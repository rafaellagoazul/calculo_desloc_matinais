from pathlib import Path
from tools.explorer.explorer_state import ExplorerState


class ExplorerActions:
    def __init__(self, root: Path, state: ExplorerState):
        self.ROOT = root
        self.state = state

    # ───────── FREEZE ─────────
    def freeze(self, target: Path):
        for py in self._iter_py(target):
            rel = str(py.relative_to(self.ROOT))
            self.state.state["frozen"][rel] = True

    def unfreeze(self, target: Path):
        for py in self._iter_py(target):
            rel = str(py.relative_to(self.ROOT))
            self.state.state["frozen"][rel] = False

    # ───────── FILE OPS ─────────
    def open_file(self, path: Path):
        import os, sys
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform.startswith("darwin"):
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
        except Exception:
            pass

    # ───────── HELPERS ─────────
    def _iter_py(self, base: Path):
        if base.is_file() and base.suffix == ".py":
            yield base
        elif base.is_dir():
            yield from base.rglob("*.py")
