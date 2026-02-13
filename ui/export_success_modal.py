import os


from ui.modal_base import ModalBase


import customtkinter as ctk
class ExportSuccessModal(ModalBase):

    def __init__(self, parent, arquivo):
        super().__init__(
            parent,
            titulo="Exportado",
            width=420,
            height=180
        )

        self.arquivo = arquivo

        ctk.CTkLabel(
            self.container,
            text="Histórico exportado com sucesso.",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(30, 10))

        box = ctk.CTkFrame(self.container, fg_color="transparent")
        box.pack(pady=10)

        ctk.CTkButton(
            box,
            text="📂 Abrir arquivo",
            width=140,
            command=self._abrir
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            box,
            text="Fechar",
            width=120,
            fg_color="#555",
            command=self.destroy
        ).pack(side="left", padx=6)

    def _abrir(self):
        try:
            if os.path.exists(self.arquivo):
                os.startfile(self.arquivo)
        finally:
            self.destroy()
