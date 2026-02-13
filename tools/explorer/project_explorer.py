import customtkinter as ctk
from tkinter import ttk
from pathlib import Path
from tools.explorer.explorer_state import ExplorerState


IGNORED = {".venv", "__pycache__", ".git", ".backups_code_fixer"}

class ProjectExplorer(ctk.CTkFrame):

    def __init__(self, master, state, actions):
        super().__init__(master)
        self.state = state
        self.actions = actions
        self.selected: Path | None = None

        self._build_ui()
        self.render()

    def _build_ui(self):
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=10, pady=6)

        self.counter = ctk.CTkLabel(top, text="")
        self.counter.pack(side="right")

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#1e1e1e",
            fieldbackground="#1e1e1e",
            foreground="#e5e5e5",
            rowheight=22
        )

        style.map(
            "Treeview",
            background=[("selected", "#2563eb")],
            foreground=[("selected", "#ffffff")]
        )
    
        actions = ctk.CTkFrame(self)
        actions.pack(fill="x", padx=10, pady=(0, 6))

        ctk.CTkButton(
            actions,
            text="❄️ Congelar",
            command=self._freeze_selected,
            width=120
        ).pack(side="right", padx=4)

        ctk.CTkButton(
            actions,
            text="🔥 Descongelar",
            command=self._unfreeze_selected,
            width=120
        ).pack(side="right", padx=4)


        self.tree = ttk.Treeview(
            self,
            show="tree",
            selectmode="browse",
            height=18
        )
        self.tree.pack(fill="both", expand=True, padx=10, pady=6)

        self.tree.bind("<<TreeviewSelect>>", self._select)
        self.tree.bind("<Double-1>", self._double)

    def render(self):
        self.tree.delete(*self.tree.get_children())
        self._add_dir(Path(self.actions.ROOT), "")

        total = sum(1 for v in self.state.state["frozen"].values() if v)
        self.counter.configure(text=f"❄️ {total} congelados")

    def _add_dir(self, path: Path, parent):
        if path.name in IGNORED:
            return

        node = parent
        if parent != "" or path != Path(self.actions.ROOT):
            icon = "📂" if self.state.is_expanded(path) else "📁"
            node = self.tree.insert(parent, "end", text=f"{icon} {path.name}", open=self.state.is_expanded(path))

        for item in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            if item.is_dir():
                self._add_dir(item, node)
            elif item.suffix == ".py":
                rel = str(item.relative_to(self.actions.ROOT))
                icon = "❄️" if self.state.is_frozen(rel) else "🔥"
                self.tree.insert(node, "end", text=f"{icon} {item.name}", values=(rel,))

    def _select(self, _):
        sel = self.tree.selection()
        if not sel:
            return

        item = sel[0]
        values = self.tree.item(item, "values")
        if values:
            self.selected = self.actions.ROOT / values[0]
        else:
            self.selected = self._resolve(item)

    def _double(self, _):
        if not self.selected:
            return

        if self.selected.is_dir():
            if self.state.is_expanded(self.selected):
                self.state.collapse(self.selected)
            else:
                self.state.expand(self.selected)
            self.state.save()
            self.render()
        else:
            self.actions.open_file(self.selected)

    def _resolve(self, item):
        parts = []
        while item:
            text = self.tree.item(item, "text")[2:]
            parts.append(text)
            item = self.tree.parent(item)
        return self.actions.ROOT.joinpath(*reversed(parts))
    
    def _freeze_selected(self):
        if not self.selected:
            return
        self.actions.freeze(self.selected)
        self.state.save()
        self.render()

    def _unfreeze_selected(self):
        if not self.selected:
            return
        self.actions.unfreeze(self.selected)
        self.state.save()
        self.render()



