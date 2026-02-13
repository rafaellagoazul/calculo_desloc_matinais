import customtkinter as ctk
# ui/layout/status_bar.py
from ui.componentes.progress_glow import ProgressGlow


class StatusBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="x", pady=(6, 8))

        # ─── LAYOUT BASE ─────────────────────────────
        self.grid_columnconfigure(0, weight=0)  # label
        self.grid_columnconfigure(1, weight=1)  # progress

        # ─── STATUS LABEL ────────────────────────────
        self.lbl_status = ctk.CTkLabel(
            self,
            text="Pronto",
            anchor="w"
        )
        self.lbl_status.grid(
            row=0, column=0,
            padx=(10, 12),
            sticky="w"
        )

        # ─── CONTAINER DA BARRA ──────────────────────
        self.progress_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.progress_container.grid(
            row=0, column=1,
            sticky="ew",
            padx=(0, 10)
        )

        self.progress_container.grid_columnconfigure(0, weight=1)

        # ─── PROGRESS BAR ────────────────────────────
        self.progress = ctk.CTkProgressBar(self.progress_container)
        self.progress.grid(sticky="ew")
        self.progress.set(0)

        # ─── GLOW ───────────────────────────────────
        self.glow = ProgressGlow(
            self.progress_container,
            self.progress
        )

    # ───────────────────────────────────────────────
    # API PÚBLICA (usada pelo StatusController)
    # ───────────────────────────────────────────────

    def set_status(self, texto: str):
        self.lbl_status.configure(text=texto)

    def set_progress(self, valor: float):
        self.progress.set(max(0, min(1, valor)))

    def reset_progress(self):
        self.progress.set(0)
