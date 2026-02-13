from pathlib import Path
from tools.explorer.explorer_state import ExplorerState
from tools.analyzer.analyzer import Analyzer


class AnalyzerAdapter:
    """
    Adapter simples entre UI e Analyzer real.
    Apenas repassa chamadas.
    """

    def __init__(self, root: Path, explorer_state: ExplorerState):
        self.analyzer = Analyzer(root, explorer_state)

    # ======================================================
    # Estratégia
    # ======================================================

    def strategy_report(self):
        return self.analyzer.strategy_report()

    def structural_health(self):
        return self.analyzer.structural_health()

    # ======================================================
    # Arquivos órfãos
    # ======================================================

    def orphan_files(self):
        return self.analyzer.orphan_files()

    # ======================================================
    # Funções mortas
    # ======================================================

    def dead_functions(self):
        return self.analyzer.dead_functions()

    # ======================================================
    # Grafo técnico
    # ======================================================

    def technical_graph(self):
        return self.analyzer.technical_graph()

    # ======================================================
    # Quarentena
    # ======================================================

    def simulate_quarantine(self):
        return self.analyzer.simulate_quarantine()

    def quarantine_suspects(self):
        return self.analyzer.quarantine_suspects()

    def rollback_quarantine(self):
        return self.analyzer.rollback_quarantine()
