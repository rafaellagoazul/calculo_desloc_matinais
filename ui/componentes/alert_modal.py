import customtkinter as ctk
from ui.modal_base import ModalBase


class AlertModal(ModalBase):

    def __init__(
        self,
        parent,
        titulo,
        mensagem,
        tipo="info",
        on_confirm=None,
        on_cancel=None,
        confirm_text="OK",
        cancel_text="Cancelar"
    ):
        super().__init__(parent, titulo, 420, 220)

        cores = {
            "info": "#3b82f6",
            "erro": "#ef4444",
            "warning": "#f59e0b",
            "success": "#22c55e",
            "question": "#6366f1"
        }

        cor = cores.get(tipo, "#3b82f6")

        # Mensagem
        lbl = ctk.CTkLabel(
            self.container,
            text=mensagem,
            wraplength=360,
            justify="left"
        )
        lbl.pack(pady=(30, 25))

        # Container dos botões
        frame_botoes = ctk.CTkFrame(self.container, fg_color="transparent")
        frame_botoes.pack(pady=(0, 15))

        # 👉 MODO CONFIRMAÇÃO
        if on_confirm:
            btn_confirmar = ctk.CTkButton(
                frame_botoes,
                text=confirm_text,
                fg_color=cor,
                command=lambda: self._confirmar(on_confirm)
            )
            btn_confirmar.pack(side="left", padx=10)

            btn_cancelar = ctk.CTkButton(
                frame_botoes,
                text=cancel_text,
                fg_color="#9ca3af",
                command=lambda: self._cancelar(on_cancel)
            )
            btn_cancelar.pack(side="left", padx=10)

        # 👉 MODO PADRÃO (OK)
        else:
            btn_ok = ctk.CTkButton(
                frame_botoes,
                text="OK",
                fg_color=cor,
                command=self.destroy
            )
            btn_ok.pack()

    def _confirmar(self, callback):
        try:
            callback()
        finally:
            self.destroy()

    def _cancelar(self, callback):
        if callback:
            callback()
        self.destroy()