from pathlib import Path
from tools.explorer.explorer_state import ExplorerState
from tools.analyzer.import_graph import ImportGraph
from tools.analyzer.call_graph import CallGraphAnalyzer
from tools.analyzer.quarantine_manager import QuarantineManager
from tools.analyzer.health_history import HealthHistory


class Analyzer:
    """
    ANALYZER ESTRATÉGICO DO PROJETO

    Objetivo:
    - Identificar o que é essencial
    - Identificar o que pode ser descartado
    - Identificar risco estrutural
    - Medir saúde arquitetural
    """

    def __init__(self, root: Path, explorer_state: ExplorerState):
        self.root = root
        self.explorer_state = explorer_state
        self.quarantine = QuarantineManager(self.root)
        self.history = HealthHistory(self.root)

    # ==========================================================
    # 1️⃣ ESTRATÉGIA DO PROJETO (PRINCIPAL)
    # ==========================================================

    def strategy_report(self):

        call = CallGraphAnalyzer(self.root)
        report = call.analyze()

        reachable = report.get("reachable", [])
        entry_functions = report.get("entry", [])

        used_files = {
            str(fn.file)
            for fn in reachable
            if hasattr(fn, "file")
        }

        # ⚠️ Certifique-se que CallGraphAnalyzer possui self.files
        all_files = set(str(f) for f in getattr(call, "files", {}).keys())

        # -------- Import Graph --------
        graph = ImportGraph(self.root)
        graph.build()

        import_count = {file: 0 for file in all_files}

        for file, data in getattr(graph, "graph", {}).items():
            for imp in data:
                if imp in import_count:
                    import_count[imp] += 1

        results = []

        for file in all_files:

            score = 0
            is_entry = any(
                getattr(fn, "file", None) == file
                for fn in entry_functions
            )

            is_used = file in used_files
            imports = import_count.get(file, 0)

            # -------- Pontuação Base --------
            if is_entry:
                score += 60

            if is_used:
                score += 30
            else:
                score -= 50

            if imports >= 3:
                score += 10

            if imports == 0:
                score -= 20

            # -------- Peso Arquitetural --------
            layer_bonus = self._layer_weight(file)
            score += layer_bonus

            # -------- Classificação Final --------
            if score >= 90:
                level = "ESSENTIAL"
            elif score >= 60:
                level = "RELEVANT"
            elif score >= 20:
                level = "NEUTRAL"
            else:
                level = "SUSPECT"

            results.append({
                "file": file,
                "score": score,
                "level": level,
                "is_entry": is_entry,
                "is_used": is_used,
                "imports": imports,
                "layer_bonus": layer_bonus
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        return results

    # ==========================================================
    # PESO POR CAMADA (INTELIGÊNCIA ARQUITETURAL)
    # ==========================================================

    def _layer_weight(self, file: str) -> int:

        path = str(file).lower()

        if "core/" in path:
            return 40
        if "ui/" in path:
            return 25
        if "tools/" in path:
            return 20
        if "admin/" in path:
            return 15
        if "tests/" in path:
            return -10
        if "old" in path or "backup" in path:
            return -20

        return 0

    # ==========================================================
    # 2️⃣ SAÚDE ESTRUTURAL + HISTÓRICO
    # ==========================================================

    def structural_health(self):

        report = self.strategy_report()

        total = len(report)

        essential = len([f for f in report if f["level"] == "ESSENTIAL"])
        relevant = len([f for f in report if f["level"] == "RELEVANT"])
        neutral = len([f for f in report if f["level"] == "NEUTRAL"])
        suspect = len([f for f in report if f["level"] == "SUSPECT"])

        health_score = int(
            ((essential * 2 + relevant) / total) * 100
        ) if total else 0

        data = {
            "total": total,
            "essential": essential,
            "relevant": relevant,
            "neutral": neutral,
            "suspect": suspect,
            "health_score": health_score
        }

        # salva histórico automaticamente
        self.history.save_snapshot(data)

        return data

    # ==========================================================
    # 3️⃣ ARQUIVOS ÓRFÃOS
    # ==========================================================

    def orphan_files(self):

        graph = ImportGraph(self.root)
        graph.build()

        return graph.unused_files()

    # ==========================================================
    # 4️⃣ FUNÇÕES MORTAS
    # ==========================================================

    def dead_functions(self):

        call = CallGraphAnalyzer(self.root)
        report = call.analyze()

        reachable = {
            fn.name
            for fn in report.get("reachable", [])
        }

        all_functions = set(getattr(call, "functions", {}).keys())

        dead = all_functions - reachable

        return sorted(dead)

    # ==========================================================
    # 5️⃣ GRAFO TÉCNICO
    # ==========================================================

    def technical_graph(self):

        call = CallGraphAnalyzer(self.root)
        call.analyze()

        return {
            fn.name: fn.calls
            for fn in getattr(call, "functions", {}).values()
        }

    # ==========================================================
    # 6️⃣ SIMULAÇÃO DE QUARENTENA
    # ==========================================================

    def simulate_quarantine(self):

        report = self.strategy_report()

        return [
            str(self.root / item["file"])
            for item in report
            if item["level"] == "SUSPECT"
        ]

    # ==========================================================
    # 7️⃣ QUARENTENA REAL
    # ==========================================================

    def quarantine_suspects(self):

        suspects = self.simulate_quarantine()

        moved = self.quarantine.move_files(suspects)

        return moved

    # ==========================================================
    # 8️⃣ ROLLBACK
    # ==========================================================

    def rollback_quarantine(self):

        return self.quarantine.restore_all()
