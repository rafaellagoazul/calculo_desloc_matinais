import customtkinter as ctk
from tools.tools_manifest import TOOLS


class ToolsHub(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Tools Hub")
        self.geometry("1100x650")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_container()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=240)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        for tool in TOOLS:
            ctk.CTkButton(
                sidebar,
                text=tool["name"],
                command=lambda t=tool: self.load_tool(t)
            ).pack(fill="x", padx=15, pady=6)

    def _build_container(self):
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            self.container,
            text="Selecione uma ferramenta",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=80)

    def load_tool(self, tool):
        # limpa o container
        for w in self.container.winfo_children():
            w.destroy()

        # monta a ferramenta
        tool["mount"](self.container)

def main():
    app = ToolsHub()
    app.mainloop()
