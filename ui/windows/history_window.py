# ==========================================================
# 🔒 CORE ESTÁVEL — HISTORY WINDOW
# ==========================================================

import customtkinter as ctk
from tkinter import ttk
from tkcalendar import DateEntry

from ui.modal_base import ModalBase
from ui.deslocamentos_queries import buscar_deslocamentos_avancado


class HistoryWindow(ModalBase):

    def __init__(self, master):
        super().__init__(
            master,
            titulo="Histórico de Deslocamentos",
            width=1150,
            height=560
        )

        self._criar_filtros()
        self._criar_tabela()
        self._carregar_dados()

    # --------------------------------------------------------
    # 🔍 FILTROS
    # --------------------------------------------------------

    def _criar_filtros(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=10, pady=10)

        # 🔎 Texto livre (arquivo)
        self.txt_busca = ctk.CTkEntry(
            frame,
            placeholder_text="Pesquisar arquivo..."
        )
        self.txt_busca.pack(side="left", padx=5)

        # 👤 Vendedor (futuro)
        self.txt_vendedor = ctk.CTkEntry(
            frame,
            placeholder_text="Vendedor"
        )
        self.txt_vendedor.pack(side="left", padx=5)

        # 📅 Data inicial
        self.data_ini = DateEntry(
            frame,
            width=12,
            date_pattern="yyyy-mm-dd"
        )
        self.data_ini.pack(side="left", padx=5)

        # 📅 Data final
        self.data_fim = DateEntry(
            frame,
            width=12,
            date_pattern="yyyy-mm-dd"
        )
        self.data_fim.pack(side="left", padx=5)

        # 🔎 Botão pesquisar
        btn = ctk.CTkButton(
            frame,
            text="Pesquisar",
            command=self._aplicar_filtro
        )
        btn.pack(side="left", padx=10)

    # --------------------------------------------------------
    # 📊 TABELA
    # --------------------------------------------------------

    def _criar_tabela(self):
        cols = (
            "id",
            "cod_vendedor",
            "dia",
            "dist_casa_cli",
            "dist_casa_dist_cli",
            "diferenca",
            "origem_arquivo",
        )

        self.tree = ttk.Treeview(self, columns=cols, show="headings")

        headers = {
            "id": "ID",
            "cod_vendedor": "Vendedor",
            "dia": "Dia",
            "dist_casa_cli": "Casa → Cliente (km)",
            "dist_casa_dist_cli": "Casa → Dist → Cliente (km)",
            "diferenca": "Diferença (km)",
            "origem_arquivo": "Arquivo",
        }

        widths = {
            "id": 60,
            "cod_vendedor": 90,
            "dia": 90,
            "dist_casa_cli": 160,
            "dist_casa_dist_cli": 200,
            "diferenca": 140,
            "origem_arquivo": 320,
        }

        for col in cols:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # --------------------------------------------------------
    # 🔁 DADOS
    # --------------------------------------------------------

    def _carregar_dados(self):
        dados = buscar_deslocamentos_avancado()
        self._popular_tabela(dados)

    def _aplicar_filtro(self):
        data_ini = self.data_ini.get_date()
        data_fim = self.data_fim.get_date()

        print("🧪 DEBUG UI")
        print("data_ini raw:", data_ini)
        print("data_fim raw:", data_fim)

        data_ini = data_ini.strftime("%Y-%m-%d")
        data_fim = data_fim.strftime("%Y-%m-%d")

        print("data_ini fmt:", data_ini)
        print("data_fim fmt:", data_fim)

        dados = buscar_deslocamentos_avancado(
            texto=self.txt_busca.get().strip() or None,
            vendedor=self.txt_vendedor.get().strip() or None,
            data_ini=data_ini,
            data_fim=data_fim
        )

        self._popular_tabela(dados)

  
    def _popular_tabela(self, dados):
        self.tree.delete(*self.tree.get_children())

        for row in dados:
            self.tree.insert("", "end", values=row)
