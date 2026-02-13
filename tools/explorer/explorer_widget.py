import customtkinter as ctk
from pathlib import Path

from explorer.explorer_state import ExplorerState
from explorer.explorer_actions import iter_py, open_file
from tools.explorer.project_explorer import ExplorerView

class ExplorerActions:
    ROOT = Path(__file__).resolve().parents[3]
    iter_py = staticmethod(iter_py)
    open_file = staticmethod(open_file)

class ExplorerWidget(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.set_appearance_mode("dark")

        state = ExplorerState()
        view = ExplorerView(self, state, ExplorerActions)
        view.pack(fill="both", expand=True)
