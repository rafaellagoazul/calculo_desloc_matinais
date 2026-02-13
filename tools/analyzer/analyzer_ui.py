import customtkinter as ctk


class AnalyzerUI(ctk.CTkFrame):

    def __init__(self, master, actions):
        super().__init__(master)
        self.actions = actions

        self.pack(fill="both", expand=True)

        # ======================================================
        # TOPO – BARRA DE AÇÕES
        # ======================================================

        top = ctk.CTkFrame(self)
        top.pack(fill="x", pady=5)

        # Lado esquerdo
        ctk.CTkButton(top, text="📊 Estratégia",
                      command=self.show_strategy).pack(side="left", padx=5)

        ctk.CTkButton(top, text="🧟 Órfãos",
                      command=self.show_orphans).pack(side="left", padx=5)

        ctk.CTkButton(top, text="🧹 Funções Mortas",
                      command=self.show_dead).pack(side="left", padx=5)

        ctk.CTkButton(top, text="🕸 Grafo",
                      command=self.show_graph).pack(side="left", padx=5)

        # Lado direito
        ctk.CTkButton(top, text="📦 Mover SUSPECT",
                      command=self.move_suspects).pack(side="right", padx=5)

        ctk.CTkButton(top, text="♻ Restaurar",
                      command=self.restore).pack(side="right", padx=5)

        ctk.CTkButton(top, text="🔎 Simular",
                      command=self.simulate).pack(side="right", padx=5)

        # ======================================================
        # BARRA DE SAÚDE
        # ======================================================

        self.health_bar = ctk.CTkProgressBar(self)
        self.health_bar.pack(fill="x", padx=10, pady=(5, 0))
        self.health_bar.set(0)

        self.health_label = ctk.CTkLabel(self, text="")
        self.health_label.pack(pady=(0, 5))

        # ======================================================
        # ÁREA DE RESULTADO
        # ======================================================

        self.output = ctk.CTkTextbox(self)
        self.output.pack(fill="both", expand=True, padx=10, pady=10)

    # ======================================================
    # ESTRATÉGIA + SAÚDE
    # ======================================================

    def show_strategy(self):

        self.output.delete("1.0", "end")

        report = self.actions.strategy_report()
        health = self.actions.structural_health()

        # Atualiza barra
        self.health_bar.set(health["health_score"] / 100)

        self.health_label.configure(
            text=(
                f"Saúde Estrutural: {health['health_score']}%  |  "
                f"🟢 {health['essential']}  "
                f"🟡 {health['relevant']}  "
                f"🟠 {health['neutral']}  "
                f"🔴 {health['suspect']}"
            )
        )

        for item in report:

            icon = {
                "ESSENTIAL": "🟢",
                "RELEVANT": "🟡",
                "NEUTRAL": "🟠",
                "SUSPECT": "🔴"
            }[item["level"]]

            self.output.insert(
                "end",
                f"{icon} {item['level']} | {item['file']}\n"
                f"   Score: {item['score']}  "
                f"(Layer: {item['layer_bonus']})  "
                f"Imports: {item['imports']}\n\n"
            )

    # ======================================================
    # ÓRFÃOS
    # ======================================================

    def show_orphans(self):

        self.output.delete("1.0", "end")
        self.health_label.configure(text="")
        self.health_bar.set(0)

        files = self.actions.orphan_files()

        if not files:
            self.output.insert("end", "Nenhum arquivo órfão encontrado.")
            return

        for f in files:
            self.output.insert("end", f"🔴 {f}\n")

    # ======================================================
    # FUNÇÕES MORTAS
    # ======================================================

    def show_dead(self):

        self.output.delete("1.0", "end")
        self.health_label.configure(text="")
        self.health_bar.set(0)

        dead = self.actions.dead_functions()

        if not dead:
            self.output.insert("end", "Nenhuma função morta encontrada.")
            return

        for fn in dead:
            self.output.insert("end", f"💀 {fn}\n")

    # ======================================================
    # GRAFO
    # ======================================================

    def show_graph(self):

        self.output.delete("1.0", "end")
        self.health_label.configure(text="")
        self.health_bar.set(0)

        graph = self.actions.technical_graph()

        for fn, calls in graph.items():
            self.output.insert("end", f"{fn} → {calls}\n")

    # ======================================================
    # SIMULAÇÃO
    # ======================================================

    def simulate(self):

        suspects = self.actions.simulate_quarantine()
        self.output.delete("1.0", "end")

        if not suspects:
            self.output.insert("end", "Nenhum arquivo SUSPECT encontrado.")
            return

        self.output.insert("end", "Arquivos que seriam movidos:\n\n")

        for f in suspects:
            self.output.insert("end", f"⚠ {f}\n")

    # ======================================================
    # MOVER SUSPECT
    # ======================================================

    def move_suspects(self):

        moved = self.actions.quarantine_suspects()
        self.output.delete("1.0", "end")

        if not moved:
            self.output.insert("end", "Nenhum arquivo movido.")
            return

        self.output.insert("end", "Arquivos movidos para __quarantine__:\n\n")

        for f in moved:
            self.output.insert("end", f"📦 {f}\n")

        # Atualiza estratégia depois de mover
        self.show_strategy()

    # ======================================================
    # RESTORE
    # ======================================================

    def restore(self):

        restored = self.actions.rollback_quarantine()
        self.output.delete("1.0", "end")

        if not restored:
            self.output.insert("end", "Nada para restaurar.")
            return

        self.output.insert("end", "Arquivos restaurados:\n\n")

        for f in restored:
            self.output.insert("end", f"♻ {f}\n")

        # Atualiza estratégia depois de restaurar
        self.show_strategy()
