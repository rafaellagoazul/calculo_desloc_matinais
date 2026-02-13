from tkinter import ttk
from core.calculador import CalculadorDeslocamentos
from ui.modal_base import ModalBase
from ui.componentes.alert_modal import AlertModal
import pandas as pd
import customtkinter as ctk

class PreviewWindow(ModalBase):

    def __init__(self, parent, arquivo_excel):
        super().__init__(parent, "Preview do Excel", 900, 500)
        self.arquivo_excel = arquivo_excel
        self._montar()

    def _montar(self):
        try:
            df = pd.read_excel(self.arquivo_excel)

            # 🔁 USANDO A MESMA VALIDAÇÃO DO CALCULADOR
            calc = CalculadorDeslocamentos(
                arquivo_excel=self.arquivo_excel,
                ors_api_key="preview"
            )
            df = calc._validar_colunas(df)

        except Exception as e:
            AlertModal(
                self,
                "Excel inválido",
                f"Não foi possível gerar o preview:\n\n{e}",
                "erro"
            )
            self.destroy()
            return

        self._criar_tabela(df)

    def _criar_tabela(self, df: pd.DataFrame):
        frame = ctk.CTkFrame(self.container)
        frame.pack(fill="both", expand=True)

        cols = list(df.columns)

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=24
        )

        style.configure(
            "Treeview.Heading",
            background="#444",
            foreground="white"
        )

        tree = ttk.Treeview(
            frame,
            columns=cols,
            show="headings"
        )

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        for _, row in df.iterrows():
            values = ["" if pd.isna(v) else v for v in row.tolist()]
            tree.insert("", "end", values=values)

        tree.pack(fill="both", expand=True)

        # 📐 AUTO-AJUSTE DE COLUNAS
        for col in cols:
            largura = max(len(col) * 10, 120)
            tree.column(col, width=largura)